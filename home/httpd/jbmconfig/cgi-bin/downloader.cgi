#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# CGI File downloader
# Parameters:
#     file - name of file to download (no path)
#     ext - extension to append to the file name (no .)

# Map of filename regex => path to pair incoming filenames to where they exist on device
my %ALLOWED_FILES_MAP = (
	'^(configs|stats)[0-9A-Za-z\-._]+\.zip$' => '/tmp',
	'^[0-9]+-stats[0-9A-Za-z\-._]+\.zip$' => '/storage',
	'^messages$' => '/var/log',
	'^tags\.csv$' => '/home/httpd/jbmconfig/txt',
	'^RED-LION-RAM-MIB$' => '/usr/share/snmp/mibs',
	'^config\.xml$' => '/home/httpd/jbmconfig/conf'
);



sub send_error {
	my $message = shift;
	system("logger -t 'download.cgi' '$message'");
	print "Content-type: text/html; charset=utf8\n\n";
	print "$message";
	exit;
}

require "./cgi-lib.pl";

my $FULL_FILE_PATH = "";
my $FILE_NAME = "";
my %in = ();
ReadParse(\%in);

if (! exists($in{file}) || "" eq $in{file}) {
	print "Content-type: text/html; charset=utf8\n\n";
	print "No file specified.";
	exit;
}
# These characters are dangerous to a potential system/bash call to log the name
if ($in{file} =~ /[\\&|;><\$=]/) {
	&send_error("Invalid file name detected");
}
foreach $key (keys(%ALLOWED_FILES_MAP)) {
	if ($in{file} =~ /$key/) {
		$FULL_FILE_PATH = "$ALLOWED_FILES_MAP{$key}/$in{file}";
		last;
	}
}
if ("" eq $FULL_FILE_PATH) {
	&send_error("Access to file \"$in{file}\" not allowed");
}
if (! -f "$FULL_FILE_PATH") {
	&send_error("File \"$in{file}\" does not exist");
}
$FILE_NAME = $in{file};
if (exists($in{ext}) && $in{ext} =~ /^[a-z]+$/) {
	$FILE_NAME .= ".$in{ext}";
}

system("logger -t 'download.cgi' 'Sending file $in{file}(.$in{ext}) for download'");
print "Content-Type:application/x-download\n";
print "Content-Disposition:attachment;filename=$FILE_NAME\n\n";
open(DLFILE, "$FULL_FILE_PATH");
while (<DLFILE>) {
	print $_;
}
close (DLFILE);
