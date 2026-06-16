#!/usr/bin/perl

# (C)2016 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

use strict;
use warnings;

# Include for ReadParse function - loads request from environment
use IOG::CGI;

my $LICENSE_PATH = "/etc/license";
my %REQUEST = ();
my %RESPONSE = (
	"error" => 0
);

if (exists $ENV{HTTP_HOST}) {
	# Load request into hash
	&IOG::CGI::getRequest(\%REQUEST);
}
else {
	# No return host, probably called via CLI. Get request from ARGV
	&parseCliArgs();
}

#
# Primary incoming request validation
#

if (exists $REQUEST{query}) {
	if ($REQUEST{query} eq "list") {
		&list();
	}
	elsif ($REQUEST{query} eq "get") {
		if (exists $REQUEST{name}) {
			&get($REQUEST{name});
		}
		else {
			&exit_error("Please specify a license name");
		}
	}
	else {
		&exit_error("Unrecognized query");
	}
}
else {
	&exit_error("No query specified");
}
&exit_response();



#
# Query-handling routines
#

sub parseCliArgs {
	foreach (@ARGV) {
		if ($_ =~ /^-?-?([^=]+)=(.+)$/) {
			$REQUEST{ $1 } = $2;
		}
	}
}

sub list {
	opendir(my $ldh, $LICENSE_PATH) || &exit_error("Failed to open license folder");

	$RESPONSE{list} = [];
	while (my $_ = readdir $ldh) {
		if ( $_ !~ /^\.+$/ ) {
			push(@{$RESPONSE{list}}, $_);
		}
	}

	closedir ($ldh);
}

sub get {
	my $name = shift;

	if ($name !~ /^[0-9a-z\-._]+$/i or ! -f "$LICENSE_PATH/$name") {
		&exit_error("Invalid license name");
	}

	open (my $lfh, "$LICENSE_PATH/$name") or &exit_error("Failed to read license");

	local $/ = undef;
	$RESPONSE{text} = <$lfh>;

	close($lfh);
}

#
# Response handling routines
#

sub exit_response {
	&IOG::CGI::sendJson(\%RESPONSE);
	exit;
}

sub exit_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&exit_response();
}
