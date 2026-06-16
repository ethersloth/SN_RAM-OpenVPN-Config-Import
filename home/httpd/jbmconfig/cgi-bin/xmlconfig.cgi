#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";

my %RESPONSE = (
	error => 0
);

sub send_response {
	&IOG::CGI::sendJson(\%RESPONSE);
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
	system("rm -f /var/run/profile/xmlconfig");
	exit 0;
}

sub logger {
	my $message = shift;
	system("logger -t 'xmlconfig' '$message'");
}

sub require_action {
	my $action = shift;
	foreach (@_) {
		if ($action eq $_) {
			return
		}
	}
	&send_error("Invalid action requested");
}

sub prfaction {
    my $errorMessage;
    chomp($errorMessage = `$_[0] $_[1] 2>&1`);
    if ($? != 0) {
        &send_error($errorMessage);
    }
    &logger("Success calling $_[0] $_[1]");
}

my %request = ();
ReadParse(\%request);

system("touch /var/run/profile/xmlconfig");
&logger("called by Web UI");

if (exists $request{subsystem} && exists $request{action}) {
	if ($request{subsystem} eq "firewall") {
		&require_action($request{action}, "Apply", "Save", "Applywl", "Savewl");
		if ($request{action} =~ /wl/) {
			$request{action} =~ s/wl//;
			system("/home/httpd/jbmconfig/bin/applywl");
			if ($? != 0) {
				&send_error("Failed to run applywl command to build the firewall whitelist");
			}
			&logger("Success applying the whitelist");
		}
	}
	elsif ($request{subsystem} eq "ramqtt") {
		&require_action($request{action}, "Apply", "Save", "Applycert", "Savecert");
		# "cert" appended as flag to call prfhandler_certmgr script
		if ($request{action} =~ /cert/) {
			$request{action} =~ s/cert//;
			&prfaction("prfhandler_certmgr", $request{action});
		}
	}
	else {
		&require_action($request{action}, "Apply", "Save");
	}
	# Not all subsystems have a same-named prfhandler
	if ($request{subsystem} eq "crimson") {
		&prfaction("prfhandler_gwlnxcfgmgr", $request{action});
		&prfaction("prfhandler_snproxy", $request{action});
		&prfaction("prfhandler_sslclient", $request{action});
		&prfaction("prfhandler_firewall", $request{action});
	}
	elsif ($request{subsystem} eq "ipsectunnel") {
		&prfaction("prfhandler_ipsec", $request{action});
	}
	else {
		&prfaction("prfhandler_$request{subsystem}", $request{action});
	}
	# Save/Apply the dhcpserver settings if the interface is eth0, eth1 or usb0
	if ($request{subsystem} eq "eth0" || $request{subsystem} eq "eth1" || $request{subsystem} eq "usb0") {
		&prfaction("prfhandler_dhcpserver", $request{action});
	}
	elsif ($request{subsystem} eq "sshserver") {
		# Save/Apply the telnetserver settings if the interface is sshserver
		&prfaction("prfhandler_telnetserver", $request{action});
	}
}
&send_response;
system("rm -f /var/run/profile/xmlconfig");
exit;
