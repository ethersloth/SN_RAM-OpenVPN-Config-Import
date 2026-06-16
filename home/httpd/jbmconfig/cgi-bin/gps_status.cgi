#!/usr/bin/perl
# (C)2016 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./jsonlib.pl";

my $VERSION_FILE = "/etc/version";

my %RESPONSE = ();

if (open(GPSCURRENT, "/var/log/wireless.gpscurrent")) {
	while (<GPSCURRENT>) {
		if ($_ =~ /CURRENT_GPS_TIMESTAMP=(.*)$/) {
			$RESPONSE{time} = $1;
		}
		elsif ($_ =~ /CURRENT_GPS_LAT=(.*)$/) {
			$RESPONSE{lat} = $1;
		}
		elsif ($_ =~ /CURRENT_GPS_LONG=(.*)$/) {
			$RESPONSE{lon} = $1;
		}
		elsif ($_ =~ /LOCKDOWN_ENGINESTATE_NUM=(.*)$/) {
			$RESPONSE{state} = $1;
		}
		elsif ($_ =~ /CURRENT_GPS_VALID=(.*)$/) {
			$RESPONSE{valid} = $1;
		}
		elsif ($_ =~ /GPSSource=(.*)$/) {
			$RESPONSE{source} = $1;
		}
	}
	close(GPSCURRENT);
}

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%RESPONSE);
