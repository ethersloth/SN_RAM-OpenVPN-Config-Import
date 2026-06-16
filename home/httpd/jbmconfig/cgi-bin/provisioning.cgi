#!/usr/bin/perl

# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "/etc/env2/env2.pl";

my $SIERRA_INFO = "/var/log/wireless.sierra.info";
my $UPDATE_STATUS = &ENV2_get("ENV2_FILE_MODEM_UPDATE_STATUS");

sub read_file {
	my $filename = shift;
	my $content = "";
	local $/ = undef;
	if (open FH, $filename) {
		$content = <FH>;
		close FH;
	}
	return $content;
}

my $sierra_content = &read_file($SIERRA_INFO);
my $update_content = &read_file($UPDATE_STATUS);

print "Content-type: text/html; charset=utf8\n\n";
if ($sierra_content !~ /^\s*$/) {
	print $sierra_content;
}
if ($update_content !~ /^\s*$/) {
	print "\n======= Results from last carrier reflash =======\n";
	print $update_content;
}
