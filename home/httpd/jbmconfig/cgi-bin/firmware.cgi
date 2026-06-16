#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Script to handle all firmware page functions

require "./cgi-lib.pl";
require "./jsonlib.pl";
my $sdcard_path = "/media/sdcard/";
my $media_path = "/media/";

my %JSON_RESPONSE = (
	"error" => 0
);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%JSON_RESPONSE);
	exit
}
sub send_error {
	my $msg = shift;
	$JSON_RESPONSE{error} = 1;
	$JSON_RESPONSE{message} = $msg;
	&send_response();
}

my @FILE_LIST = ();

sub get_file_list {
	if (open my $cmd, "find $sdcard_path -type f |") {
		my $relative_path;
		while (<$cmd>) {
			$relative_path = $_;
			$relative_path =~ s/.*media\/|\s*$//g;
			if ($relative_path =~ /(bootfs|rootfs)\.jffs2$/) {
				push(@FILE_LIST, $relative_path);
			}
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

if (exists($in{query})) {
	if ($in{query} eq "cleantmp") {
		&cleanTMP();
	}
	elsif ($in{query} eq "list") {
		if (`mount | grep sdcard`) {
			&get_file_list();
			#&recursive_append("/media/sdcard");
			$JSON_RESPONSE{data} = \@FILE_LIST;
		}
		else {
			&send_error("SD card is not inserted, please insert your SD card");
		}
	}
	elsif (exists($in{bootf}) && exists($in{rootf}) && exists($in{savecfg}) && $in{query} eq "install") {
		if ($in{savecfg} !~ /^[yn]$/) {
			&send_error("Invalid savecfg option");
		}
		if (-f "$media_path$in{bootf}" && -f "$media_path$in{rootf}") {
			&cleanTMP();
			system("/bin/cp -f $media_path$in{bootf} /tmp");
			if ( 0 != $? ) {
				&send_error("Unable to copy $in{bootf} images to /tmp/ directory");
			}
			system("/bin/cp -f $media_path$in{rootf} /tmp");
			if ( 0 != $? ) {
				&send_error("Unable to copy $in{rootf} images to /tmp/ directory");
			}
			system("sync; /bin/cliflash.sh -b $media_path$in{bootf} -r $media_path$in{rootf} -s $in{savecfg} &> /dev/null");
			if ( 0 != $? ) {
				&send_error("Unable to flash the unit with $in{bootf} and $in{rootf} images");
			}
		}
		else {
			&send_error("Cannot find selected images");
		}
	}
	else {
		&send_error("Unrecognized query");
	}
}
else {
	&send_error("Must specify a query");
}

sub cleanTMP
{
	system("grep -q bt6k /etc/version");
	if ($? == 0) {
		system("/home/httpd/jbmconfig/bin/prepfs.sh &>/dev/console");
	}
	system("/bin/rm -f "
		. "/tmp/*.bin "
		. "/tmp/*.jffs2 "
		. "/tmp/*.zip "
		. "/tmp/flash.sh "
		. "/tmp/lighttpd-upload* "
		. ">>/var/log/messages 2>&1");
}

&send_response();

exit 0;
