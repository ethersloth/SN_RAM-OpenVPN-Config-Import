#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";
my $sdcard_path = "/media/sdcard/";

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

my @FILE_LIST = ();

sub get_file_list {
	my $sdcard_escaped = $sdcard_path;
	$sdcard_escaped =~ s/\//\\\//g;
	if (open my $cmd, "find $sdcard_path -type f |") {
		my $relative_path;
		while (<$cmd>) {
			$relative_path = $_;
			$relative_path =~ s/$sdcard_escaped\/?|\s*$//g;
			if ($relative_path =~ /(configs|packages)\/[0-9A-Za-z\-._ ]+\.zip/) {
				push(@FILE_LIST, "sdcard/$relative_path");
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
	if ($in{query} eq "list") {
		if (`mount | grep sdcard`) {
			&get_file_list();
			#&recursive_append("/media/sdcard");
			$JSON_RESPONSE{data} = \@FILE_LIST;
		}
		else {
			&send_error("SD card is not inserted, please insert your SD card");
		}
	}
	elsif (exists($in{content}) && $in{query} eq "install") {
		# compensate for adding sdcard/ prefix in get_file_list
		my $media_path = $sdcard_path;
		$media_path =~ s/sdcard\/?//;
		if (-f "$media_path$in{content}") {
			system("snupdate $media_path$in{content} &> /dev/null");
			if ( 0 != $? ) {
				&send_error("Unable to install $in{content} package");
			}
		}
		else {
			&send_error("Cannot find package $in{content}");
		}
	}
	else {
		&send_error("Unrecognized query");
	}
}
else {
	&send_error("Must specify a query");
}

&send_response();

exit 0;
