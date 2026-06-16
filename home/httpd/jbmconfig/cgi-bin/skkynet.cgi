#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";

my $etkscriptPID = "none";
my %RESPONSE = (
	error => 0
);
my $CONFDIR = "/etc/skkynet";
my $LSPDEFAULT = "$CONFDIR/rldefault.lsp";
my $LSPMODBUSFILE = "$CONFDIR/modbus_connections.lsp";
my $LSPDATAHUBFILE = "$CONFDIR/datahub_connections.lsp";
my $LSPLOCALFILE = "$CONFDIR/modbus_slave_1.lsp";
my $LSPREMOTEFILE = "$CONFDIR/modbus_slave_2.lsp";
$ENV{PATH} = "/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin";

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%RESPONSE);
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
	exit 0;
}

sub readFile
{
	my $file = shift;
	open(FILE,"$file") or return "";
	$/ = undef;
	$tmp = <FILE>;
	$/ = "\n";
	close (FILE);
	return $tmp;
}

sub writeFile
{
	(my $file, my $contents) = @_;
	open(FILE, '>', "$file") or return;
	print FILE $contents;
	close(FILE);
}

sub checkChkConfig {
	my $status = `/sbin/chkconfig --list | grep etkscript | awk '{print \$5}'`;
	if ($status =~ /3:(on|off)/) {
		return ucfirst($1);
	}
	return "Unavailable";
}

sub checkIsRunning {
	my $status = `ps -ea | grep etkscript | awk '{print \$1}'`;
	if ($status !~ /^\s*$/) {
		return "Running";
	}
	return "Stopped";
}

sub setResponseStatus {
	$RESPONSE{running} = &checkIsRunning();
	$RESPONSE{chkconfig} = &checkChkConfig();
}

sub setResponseFiles {
	$RESPONSE{datahub} = &readFile($LSPDATAHUBFILE);
	$RESPONSE{modbus} = &readFile($LSPMODBUSFILE);
	# Files setting up actual transfer points have a default
	if (-f $LSPLOCALFILE) {
		$RESPONSE{local} = &readFile($LSPLOCALFILE);
	}
	else {
		$RESPONSE{local} = &readFile($LSPDEFAULT);
	}
	if (-f $LSPREMOTEFILE) {
		$RESPONSE{remote} = &readFile($LSPREMOTEFILE);
	}
	else {
		$RESPONSE{remote} = &readFile($LSPDEFAULT);
	}
}

my %in = ();
ReadParse(\%in);

if (exists($in{type})) {
	if ("pageload" eq $in{type}) {
		&setResponseStatus();
		&setResponseFiles();
	}
	elsif ("status" eq $in{type}) {
		&setResponseStatus();
	}
	elsif ("write" eq $in{type}) {
		if (exists $in{local}) {
			&writeFile($LSPLOCALFILE, $in{local});
		}
		if (exists $in{remote}) {
			&writeFile($LSPREMOTEFILE, $in{remote});
		}
		if (exists $in{datahub}) {
			&writeFile($LSPDATAHUBFILE, $in{datahub});
		}
		if (exists $in{modbus}) {
			&writeFile($LSPMODBUSFILE, $in{modbus});
		}
		# Read back files as confirmation of what we wrote
		&setResponseFiles();
	}
	elsif ("start" eq $in{type}) {
		system("/sbin/service etkscript restart &>/dev/null");
		sleep 1;
		&setResponseStatus();
	}
	elsif ("stop" eq $in{type}) {
		system("/sbin/service etkscript stop &>/dev/null");
		sleep 1;
		&setResponseStatus();
	}
	elsif ("enable" eq $in{type}) {
		system("/sbin/chkconfig etkscript on &>/dev/null");
		sleep 1;
		&setResponseStatus();
	}
	elsif ("disable" eq $in{type}) {
		system("/sbin/chkconfig etkscript off &>/dev/null");
		sleep 1;
		&setResponseStatus();
	}
	else {
		&send_error("Unrecognized type");
	}
}
else {
	&send_error("Must specify type of query");
}

&send_response;

exit;
