#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";

my %RESPONSE = (
	"error" => 0
);

sub sendResponse {
	&IOG::CGI::sendJson(\%RESPONSE);
	exit;
}
sub sendError {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&sendResponse();
}

my %in = ();
ReadParse(\%in);

if (exists($in{query})) {
	if ($in{query} eq "set") {
		if (! exists $in{date} or ! exists $in{time}) {
			&sendError("Must specify date and time");
		}
		if ($in{date} !~ /^[0-9\/]+$/) {
			&sendError("Invalid date");
		}
		if ($in{time} !~ /^[0-9:]+$/) {
			&sendError("Invalid time");
		}

		chomp( $RESPONSE{message} = `/bin/date -s "$in{date} $in{time}" 2>&1` );

		if ($RESPONSE{message} =~ /invalid/i) {
			$RESPONSE{error} = 1;
			&sendResponse();
		}

		system("hwclock --systohc");
	}
	elsif ($in{query} eq "get") {
		chomp( $RESPONSE{datetime} = `/bin/date "+%m/%d/%Y - %H:%M:%S"` );
	}
	else {
		&sendError("Unrecognized query");
	}
}
else {
	&sendError("Must specify a query");
}

&sendResponse();
