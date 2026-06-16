#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";
my $sdcard_path  = "/media/sdcard/";
my $erase_path  = "/media/sdcard/*";
my $configs_dir  = "/media/sdcard/configs/"; 
my $stats_dir    = "/media/sdcard/stats/"; 
my $packages_dir = "/media/sdcard/packages/"; 
my $firmware_dir = "/media/sdcard/firmware/"; 
my $datalog_dir  = "/media/sdcard/datalog/"; 
my $configs_readme  = "This directory contains all gatherconfigs generated on the device";
my $stats_readme    = "This directory contains all gatherstats generated on the device";
my $packages_readme = "This directory contains packages to be installed on the device";
my $firmware_readme = "This directory contains firmware images or directories that contains firmware images.";
my $datalog_readme  = "This directory contains files containing data logging";

my %JSON_RESPONSE = (
	"error" => 0
);

sub send_response {
	&IOG::CGI::sendJson(\%JSON_RESPONSE);
	exit
}
sub send_error {
	my $msg = shift;
	$JSON_RESPONSE{error} = 1;
	$JSON_RESPONSE{message} = $msg;
	&send_response();
}

sub readFile
{
	my $file = shift;
	open(FILE,"$file") or return "";
	$/ = undef;
	$tmp = <FILE>;
	$/ = "\n";
	close (FILE);
	return $tmp;
}

sub export {
	my $filename = shift;
	my $saveas = $filename;
	$saveas =~ s/$sdcard_path[0-9A-Za-z]+\///g;
	&IOG::CGI::printHeaders({
		"Content-type" => "application/x-download",
		"Content-Disposition" => "attachment;filename=$saveas"
	});
	# Bail out to prevent any further data from being sent as the file
	if (open(my $dlfh, $filename)) {
		local $/ = undef;
		print <$dlfh>;
		close($dlfh);
	}
	exit 0;
}
                                                                                                                                

my @FILE_LIST = ();

sub get_file_list {
	my $sdcard_escaped = $sdcard_path;
	$sdcard_escaped =~ s/\//\\\//g;
	if (open my $cmd, "find $sdcard_path -type f |") {
		my $relative_path;
		while (<$cmd>) {
			$relative_path = $_;
			$relative_path =~ s/$sdcard_escaped\/?|\s*$//g;
			push(@FILE_LIST, "sdcard/$relative_path");
		}
		close($cmd);
	}
}

sub recursive_append {
	my $dirPath = shift;
	my $pathToItem = "";

	if (opendir my $dir, $dirPath) {
		while (my $item = readdir($dir)) {
			$pathToItem = "$dirPath/$item";
			if ( -f $pathToItem) {
				push(@FILE_LIST, $item);
			}
			elsif ( -d $pathToItem) {
				&recursive_append($pathToItem);
			}
		}
		closedir($dir);
	}
}

my %in = ();
ReadParse(\%in);

if (`mount | grep sdcard`) {
	if (exists($in{query})) {
		if ($in{query} eq "list") {
			&get_file_list();
			#&recursive_append("/media/sdcard");
			$JSON_RESPONSE{data} = \@FILE_LIST;
		}
		elsif ($in{query} eq "erase") {
			#Remove all directories
			system("rm -rf $erase_path &> /dev/null");
			if ( 0 != $? ) {
				&send_error("Unable to erase all directories");
			}
			&buildFolderStructure();
		}
		elsif ($in{query} eq "apply") {
			&buildFolderStructure();
		}
		elsif ($in{query} eq "unmount") {
			system("sync; /sbin/udev-auto-unmount.sh /dev/mmcblk*p1 &> /dev/null");
			if ( 0 != $? ) {
				&send_error("Unable to unmount the SD card");
			}
			system("echo 0 > /sys/devices/platform/at91_leds/leds/sd/brightness");
		}
		elsif (exists($in{file}) && $in{file} =~ /^[\/0-9A-Za-z-._ ]+$/ && $in{file} !~ /\.\./) {
			# compensate for adding sdcard/ prefix in get_file_list	
			my $media_path = $sdcard_path;                                     
			$media_path =~ s/sdcard\/?//;
			if ($in{query} eq "delete") {
				if (-f "$media_path$in{file}") {
					system("rm -f $media_path$in{file} &> /dev/null");
					if ( 0 != $? ) {
						&send_error("Unable to delete $in{content} file");
					}
				}
				else {
					&send_error("Cannot find file $in{file}");
				}
			}
			elsif ($in{query} eq "view") {
				if (-f "$media_path$in{file}") {
					$JSON_RESPONSE{data} = &readFile("$media_path$in{file}");
				}
				else {
					&send_error("Cannot find file $in{file}");
				}
			}
			elsif ($in{query} eq "export") {
				if (-f "$media_path$in{file}") {
					&export("$media_path$in{file}");
				}
				else {
					&send_error("Cannot find file $in{file} for download");
				}
			}
		}
		else {
			&send_error("Unrecognized query");
		}
	}
	else {
		&send_error("Must specify a query");
	}
}
else {
		&send_error("SD card is not inserted! Please insert an SD Card and click refresh");
}

&send_response();

sub buildFolderStructure {
	#Create configs directory
	system("sync; mkdir -p $configs_dir &> /dev/null");
	if ( 0 != $? ) {
		&send_error("Unable to create $configs_dir directory");
	}
	system("echo $configs_readme &> $configs_dir/README");
	#Create stats directory
	system("mkdir -p $stats_dir &> /dev/null");
	if ( 0 != $? ) {
		&send_error("Unable to create $stats_dir directory");
	}
	system("echo $stats_readme &> $stats_dir/README");
	#Create packages directory
	system("mkdir -p $packages_dir &> /dev/null");
	if ( 0 != $? ) {
		&send_error("Unable to create $packages_dir directory");
	}
	system("echo $packages_readme &> $packages_dir/README");
	#Create firmware directory
	system("mkdir -p $firmware_dir &> /dev/null");
	if ( 0 != $? ) {
		&send_error("Unable to create $firmware_dir directory");
	}
	system("echo '$firmware_readme' &> $firmware_dir/README");
	#Create datalog directory
	system("mkdir -p $datalog_dir &> /dev/null");
	if ( 0 != $? ) {
		&send_error("Unable to create $datalog_dir directory");
	}
	system("echo $datalog_readme &> $datalog_dir/README");
}

exit 0;
