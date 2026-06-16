#!/usr/bin/perl

# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./gau-profile-acl.pl";

my %REQUEST = ();
&IOG::CGI::getRequest(\%REQUEST);

&validateRequest();

&importXml();

&IOG::CGI::sendJson({error => "false"});

sub validateRequest {
	if (! exists $REQUEST{xml} or "" eq $REQUEST{xml}) {
		&IOG::CGI::sendError("Expected valid xml paramter");
		exit 0;
	}

	if (! exists $REQUEST{action}) {
		$REQUEST{action} = "cfgonly"
	}
	elsif ($REQUEST{action} ne "apply" and $REQUEST{action} ne "save" and $REQUEST{action} ne "cfgonly") {
		&IOG::CGI::sendError("Invalid action parameter");
		exit 0;
	}

	if (! exists $REQUEST{table}) {
		$REQUEST{table} = "replace"
	}
	elsif ($REQUEST{table} ne "replace" and $REQUEST{table} ne "append") {
		&IOG::CGI::sendError("Invalid table parameter");
		exit 0;
	}

}

sub importXml {
	my $output;
	chomp(my $tmpfile = `mktemp`);

	while ($REQUEST{xml} =~ /subsystem="(\w+)"/g) {
		if (profileAclAccess($ENV{REMOTE_USER}, $1) ne "write") {
			unlink("$tmpfile");
			&IOG::CGI::sendError("User '$ENV{REMOTE_USER}' not authorized to configure '$1'");
			exit 0;
		}
	}

	if (open OFILE, ">", "$tmpfile") {
		print OFILE $REQUEST{xml};
		close(OFILE);
	}
	else {
		unlink("$tmpfile");
		&IOG::CGI::sendError("Failed to write config");
		exit 0;
	}

	chomp($output = `importxml --$REQUEST{action} --$REQUEST{table} $tmpfile 2>&1`);
	if ( 0 != $?) {
		unlink("$tmpfile");
		&IOG::CGI::sendError($output);
		exit 0;
	}

	unlink("$tmpfile");
}

exit 0;
