#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Sample CGI to use for developing per-page logic.
#
# Note: If this is a new cgi, you will need to add it to gau-3.23.000/Makefile
# to ensure it is actually installed on-device

use strict;
use warnings;
use IOG::CGI;

# Include for ReadParse function - loads request from environment
require "./cgi-lib.pl";
# Include for JSON serialization subroutines
require "./jsonlib.pl";

my %REQUEST = ();
my %RESPONSE = (
	"error" => 0
);

# Load request into hash
ReadParse(\%REQUEST);

#
# Primary incoming request validation
#
# To minimize clutter, individual queries should be processed in subroutines
# after all inputs have been validated
#

if (exists($REQUEST{query})) {
        if ($REQUEST{query} eq "test") {
                if (! exists $REQUEST{hostname}){
                        &send_error("Invalid hostname attribute");
                }
                if ($REQUEST{hostname} ne "azure") {
                        if (! exists $REQUEST{host} or ! &validate_ip_address($REQUEST{host}) && ! &validate_domain_name($REQUEST{host})) {
                                &send_error("Invalid Broker attribute");
                        }
                        if (! exists $REQUEST{username} or $REQUEST{username} =~ /(['])/ ){
                                &send_error("Invalid username attribute");
                        }
                        if (! exists $REQUEST{usessl}){
                                &send_error("Invalid usessl attribute");
                        }
                        if (! exists $REQUEST{useauth}){
                                &send_error("Invalid useauth attribute");
                        }
                }

                if (! exists $REQUEST{port} or $REQUEST{port} !~ /(\d{1,5})/ ) {
                        &send_error("Invalid port attribute");
                }
                if (! exists $REQUEST{password} or $REQUEST{username} =~ /(['])/ ){
                        &send_error("Invalid password attribute");
                }
		$RESPONSE{results} =
			&test($REQUEST{host},
				    $REQUEST{port},
				    $REQUEST{username},
				    $REQUEST{password},
				    $REQUEST{usessl},
				    $REQUEST{useauth},
				    $REQUEST{hostname},
				    $REQUEST{devcert},
				    $REQUEST{devkey},
				    $REQUEST{devca},
				    $REQUEST{devname},
				    $REQUEST{authtype},
				    $REQUEST{clientId},
				    $REQUEST{lwtTopic},
				    $REQUEST{deviceConnectionString},
				    $REQUEST{sasTokenTTL});
	}
	elsif ($REQUEST{query} eq "stats") {
		$RESPONSE{results} = `cat /var/log/ramqtt.status`;
		if (0 != $?) {
			&send_error("No RAMQTT Status LOG Detected");
		}
	}
	else {
		&send_error("Unrecognized query");
	}

}
else {
	&send_error("No query specified");
}

&send_response();

#
# Query-handling routines
#

sub test {
	my $host     = shift;
	my $port     = shift;
	my $username = shift;
	my $password = shift;
	my $usessl   = shift;
	my $useauth  = shift;
	my $hostname = shift;
	my $devcert  = shift;
	my $devkey   = shift;
	my $devca    = shift;
	my $devname  = shift;
	my $authtype = shift;
	my $clientId = shift;
	my $lwtTopic = shift;
	my $deviceConnectionString = shift;
	my $sasTokenTTL = shift;

	my $certpath = '/etc/ramqtt/certs/';
	my $devcertpath = $certpath . $devcert;
	my $devkeypath = $certpath . $devkey;
	my $devcapath  = $certpath . $devca;

	my $syscmd = "/usr/iog/bin/ramqtt";
	$syscmd .= " -d 15"; # debug level, will allow the output to print the SUCCESS or FAILURE
	$syscmd .= " -o '$host'";
	$syscmd .= " -r '$port'";
	$syscmd .= " -i '$clientId'";
	$syscmd .= " -u '$username'";
	$syscmd .= " -p '$password'";
	$syscmd .= " -s '$usessl'";
	$syscmd .= " -a '$useauth'";
	$syscmd .= " -n '$hostname'";
	$syscmd .= " -C '$devcertpath'";
	$syscmd .= " -R '$devcapath'";
	$syscmd .= " -K '$devkeypath'";
	$syscmd .= " -D '$devname'";
	$syscmd .= " -A '$authtype'";
	$syscmd .= " --lwttopic='$lwtTopic'";
	$syscmd .= " --deviceConnectionString='$deviceConnectionString'";
	$syscmd .= " --sasTokenTTL='$sasTokenTTL'";
	$syscmd .= " -t"; # test connection only
	chomp( my $result = `$syscmd` );

	if ($result =~ /FAILURE/) {
		return "Could not connect to remote host";
	}
	if ($result =~ /SUCCESS/) {
		return "Device can successfully connect to remote host";
	}

	# else return raw command output
	return $result;
}

#
# Response handling routines
#

sub send_response {
	&IOG::CGI::sendJson(\%RESPONSE);
	exit;
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
}

sub check_ip_address {
	return $_[0] =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ &&
		$1 >= 0 && $1 <= 255 && $1 !~ /^0\d+$/ &&
		$2 >= 0 && $2 <= 255 && $2 !~ /^0\d+$/ &&
		$3 >= 0 && $3 <= 255 && $3 !~ /^0\d+$/ &&
		$4 >= 0 && $4 <= 255 && $4 !~ /^0\d+$/;
}

sub validate_ip_address {
		return check_ip_address($_[0]);
}

sub check_domain_name {
	return $_[0] =~ /^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/i
}

sub validate_domain_name {
	return check_domain_name($_[0]);
}
