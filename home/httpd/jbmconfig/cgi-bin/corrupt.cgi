#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# corrupt.cgi simply checks for presence of a flag file signaling that the
# device configuration is out of sync with individual subsystem configs - a
# specific 4.21/4.22 bug.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";
require "/etc/env2/env2.pl";

my %RESPONSE = (
	"error" => 0
);

sub sendResponse {
	&IOG::CGI::sendJson(\%RESPONSE);
	exit
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
	if ($in{query} eq "check") {
		if (-f $ENV{ENV2_FLAG_CORRUPT}) {
			$RESPONSE{corrupt} = `cat $ENV{ENV2_FLAG_CORRUPT}`;
		}
	}
	elsif ($in{query} eq "set") {
		unlink($ENV{ENV2_FLAG_CORRUPT});
	}
	else {
		&sendError("Unrecognized query");
	}
}
else {
	&sendError("Must specify a query");
}

&sendResponse();

exit 0;
