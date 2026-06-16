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

&IOG::CGI::request_parse(\%REQUEST, \@ARGV, "file");

#
# Primary incoming request validation
#

if (exists($REQUEST{query})) {
	if ($REQUEST{query} eq "upload") {
		if (exists $REQUEST{file} and exists $REQUEST{name} and exists $REQUEST{type}) {
			&upload($REQUEST{file}, $REQUEST{name}, $REQUEST{type})
		}
		else {
			&exit_error("No file specified");
		}
	}
	elsif ($REQUEST{query} eq "fingerprint") {
		if (exists $REQUEST{cert} and -f "/etc/redlion/certificates/$REQUEST{cert}") {
			chomp($RESPONSE{fingerprint} = `openssl x509 -in "/etc/redlion/certificates/$REQUEST{cert}" -noout -sha1 -fingerprint 2>&1`);
			$RESPONSE{fingerprint} =~ s/SHA1 Fingerprint=(.*)$/$1/;
			$RESPONSE{fingerprint} =~ s/://g;
		}
		else {
			&exit_error("Missing certificate");
		}
	}
	elsif ($REQUEST{query} eq "drop") {
		if (exists $REQUEST{file} and -f $REQUEST{file}) {
			system("mv", "-f", $REQUEST{file}, "/etc/redlion/certificates");
		}
		else {
			&exit_error("No file specified");
		}
	}
	elsif ($REQUEST{query} eq "details") {
		if (exists $REQUEST{cert} and -f "/etc/jbm/certificates/$REQUEST{cert}") {
			$RESPONSE{message} = `/usr/bin/openssl x509 -in /etc/jbm/certificates/$REQUEST{cert} -text 2>&1`;
		}
		else {
			&exit_error("Invalid Cert");
		}
	}
	else {
		$RESPONSE{request} = \%REQUEST;
		$RESPONSE{ENV} = \%ENV;
		&exit_error("Unrecognized query");
	}
}
else {
	&exit_error("No query specified");
}

&exit_response();

exit;



#
# Query-handling routines
#

sub upload {
	my $cert = shift;
	my $name = shift;
	my $type = shift;
	my $output;

	if (! -f $cert) {
		&exit_error("No certificate file found");
	}

	chomp($output = `/usr/iog/bin/install_cert -n $name -t $type -c $cert -a add 2>&1`);
	unlink $cert;

	if ($output !~ /Success/) {
		$RESPONSE{error} = 1;
		$RESPONSE{message} = $output;
	}
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
