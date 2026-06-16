#!/usr/bin/perl

# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

use strict;
use warnings;
use IOG::CGI;

my %REQUEST = ();
my %RESPONSE = (
	error => 0
);

my $OVPN_CFG = "/etc/openvpn/openvpn_cfg_parse.cfg";

IOG::CGI::request_parse(\%REQUEST, \@ARGV, "file");

if (! exists $REQUEST{query}) {
	IOG::CGI::sendError("Missing query parameter");
	exit 1;
}

if ($REQUEST{query} eq "status") {
	chomp($RESPONSE{ifconfig} = `ifconfig tun0 2>&1`);
	chomp($RESPONSE{routes} = `route -n 2>&1`);
	chomp($RESPONSE{pid} = `pidof openvpn`);
	chomp($RESPONSE{status} = `cat /var/log/openvpn.status 2>&1`);
	$RESPONSE{config} = `cat $OVPN_CFG 2>&1`;
}

# Bootstrap query: installs itself to the Extensions drop-down on-load.
elsif ($REQUEST{query} eq "setup") {
	system("webui_extension_add -p 'SmartVPN' clov");
}

elsif ($REQUEST{query} eq "start") {
	$RESPONSE{message} = &sanitize_service_output(
		`chkconfig openvpn on 2>&1; service openvpn restart 2>&1`
	);
}

elsif ($REQUEST{query} eq "stop") {
	$RESPONSE{message} = &sanitize_service_output(
		`chkconfig openvpn off 2>&1; service openvpn stop 2>&1`
	);
}

elsif ($REQUEST{query} eq "save") {
	if (! exists $REQUEST{config}) {
		IOG::CGI::sendError("Missing config parameter");
		exit 1;
	}
	if (open my $cfh, '>', $OVPN_CFG) {
		print $cfh $REQUEST{config};
		close($cfh);
	}
}

elsif ($REQUEST{query} eq "upload") {
	if (! exists $REQUEST{file}) {
		IOG::CGI::sendError("Missing file parameter");
		exit 1;
	}
	my $code = "/tmp/.clov-parse-code";
	system("mv $REQUEST{file} $OVPN_CFG");
	$RESPONSE{message} = `openvpn_cl_parser.pl --file $OVPN_CFG; echo \$? > $code`;
	if (`cat $code` !~ /^0/) {
		$RESPONSE{error} = 1;
	}
	unlink($code);
}

else {
	IOG::CGI::sendError("Invalid query");
	exit 1;
}

IOG::CGI::sendJson(\%RESPONSE);

exit 0;

# Remove color codes and nonprintable characters from service start/stop strings
sub sanitize_service_output {
	# Each line comes in as an argument because of IFS
	for (@_) {
		chomp;
		s/\e\[\d+(?>(;\d+)*)m//g;
		s/[^[:print:]]//g;
		s/\[60G//g;
	}
	return join("\n", @_);
}
