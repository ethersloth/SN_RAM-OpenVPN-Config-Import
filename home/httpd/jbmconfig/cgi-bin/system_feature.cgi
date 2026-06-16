#!/usr/bin/perl

# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

use strict;
use warnings;

use IOG::CGI;

my %REQUEST = ();
my %RESPONSE = (
	"error" => 0
);

&IOG::CGI::request_parse(\%REQUEST, \@ARGV);

if (exists($REQUEST{query}))
{
	if ($REQUEST{query} eq "check")
	{
		if (! exists $REQUEST{feature} or ! &isValidFeatureCode($REQUEST{feature}))
		{
			&fail("Invalid feature");
		}
		chomp($RESPONSE{message} = `system_feature check $REQUEST{feature}`);
	}
	elsif ($REQUEST{query} eq "list")
	{
		chomp($RESPONSE{message} = `system_feature list`);
	}
	elsif ($REQUEST{query} eq "unlock")
	{
		if (! exists $REQUEST{feature} or ! &isValidFeatureCode($REQUEST{feature}))
		{
			&fail("Invalid feature");
		}
		if (! exists $REQUEST{feature} or ! &isValidFeatureCode($REQUEST{code}))
		{
			&fail("Invalid unlock code");
		}
		system("system_feature unlock $REQUEST{feature} $REQUEST{code}");
		$RESPONSE{error} = $? >> 8;

		if ($RESPONSE{error})
		{
			&fail("Failed to unlock feature");
			exit 1;
		}
	}
	else
	{
		&fail("Unrecognized query");
	}
}
else
{
	&fail("No query specified");
}

&IOG::CGI::sendJson(\%RESPONSE);
exit;



sub isValidFeatureCode {
	# return 1/0 for true/false
	if ($_[0] =~ /^[a-z0-9]+$/i) {return 1};
	return 0;
}

sub fail {
	&IOG::CGI::sendError($_[0]);
	exit 1;
}
