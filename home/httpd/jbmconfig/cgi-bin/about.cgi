#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./jsonlib.pl";

my $VERSION_FILE = "/etc/version";

my %RESPONSE = ();

open(FH, $VERSION_FILE);
while (<FH>) {
	if ($_ =~ /BUILD_VERSION="([0-9.]+)"/) {
		$RESPONSE{BUILD_VERSION} = $1;
		last;
	}
}
close(FH);

if (! exists $RESPONSE{BUILD_VERSION}) {
	$RESPONSE{error} = "Parameters not found";
}

# Not really text/html, but the js expects to do json parsing itself.
&IOG::CGI::printHeaders({"Content-type" => "text/html"});
print &JSON_Serialize(\%RESPONSE);
