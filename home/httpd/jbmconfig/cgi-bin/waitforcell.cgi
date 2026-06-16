#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"
.     "Last-Modified: " . gmtime() . " GMT\n"
.     "Cache-Control: no-store, no-cache, must-revalidate\n"
.     "Cache-Control: post-check=0, pre-check=0\n"
.     "Pragma: no-cache\n"
.     "Content-type: text/html; charset=utf8\n\n";


my $cardstats_file = "/var/log/wireless.cardstats";
my $search_string = "CELLMODEM_SIM_CARRIER=";
my $RET_COUNT = 60;

#When resetting the cellmodem, it takes some time for /var/log/wireless.cardstats to be available.
while ( $RET_COUNT-- >= 0 and ! -e "$cardstats_file" ) {
	sleep 1;
}

if ( ! -e "$cardstats_file" ) {
	system("logger -t 'waitforcell.cgi' 'Timed out waiting for $cardstats_file file to be available'");
	exit(0);
}
else {
	chomp(my $CARRIER = `cat $cardstats_file | grep $search_string | sed 's/$search_string//g' 2>&1`);
	$RET_COUNT = 45;

	#Wait for wireless.cardstats items to be configured
	while ( $RET_COUNT-- >= 0 and "$CARRIER" eq "Unknown" ) {
	sleep 1;
	chomp($CARRIER = `cat $cardstats_file | grep $search_string | sed 's/$search_string//g' 2>&1`);
}

	if ( "$CARRIER" eq "Unknown" ) {
		system("logger -t 'waitforcell.cgi' 'Timed out waiting for $search_string to be configured, now showing $CARRIER'");
	}
}

exit(0);
