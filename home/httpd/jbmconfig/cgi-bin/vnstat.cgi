#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";

my $vnstat = "/usr/bin/vnstat";
my $iflist_ignore = "Available|interfaces:|br|can|cpu|dummy|lo|mon|nophy|sit|wwan1|\\(.*|.*\\)";
my %response = (
	error => 0
);
my %in = ();

ReadParse(\%in);

sub send_response {
	&IOG::CGI::sendJson(\%response);
}
sub send_error {
	my $msg = shift;
	$response{error} = 1;
	$response{message} = $msg;
	&send_response();
	exit;
}

sub check_interfaces {
	my @iflist = split(' ', `$vnstat --iflist`);
	@{$response{interfaces}} = ();
	foreach $if (@iflist) {
		if ($if !~ /$iflist_ignore/) {
			push(@{$response{interfaces}}, $if);
		}
	}
}

sub check_chkconfig {
	$response{chkconfig} = "unknown";
	open (CMD, "/sbin/chkconfig --list |");
	while (<CMD>) {
		if ($_ =~ /^vnstat .*3:(on|off)/) {
			$response{chkconfig} = $1;
			return;
		}
	}
}

sub check_status {
	$response{status} = "unknown";
	if (`/sbin/service vnstat status` =~ /is (running|stopped)/) {
		$response{status} = $1;
	}
}

if (exists($in{cmd})) {
	if ($in{cmd} eq "enable") {
		system("/sbin/chkconfig vnstat on &>/dev/null");
		system("/sbin/service vnstat restart &>/dev/null");
		&check_chkconfig();
		&check_status();
		&send_response();
		exit;
	}
	elsif ($in{cmd} eq "force") {
		system("$vnstat -u --force &>/dev/null");
		system("/sbin/service vnstat restart &>/dev/null");
		&check_chkconfig();
		&check_status();
		&send_response();
		exit;
	}
	elsif ($in{cmd} eq "reset") {
		&check_chkconfig();
		&check_status();
		# Disable vnstat to keep it from getting in the way
		chmod(0644, "/etc/cron.5min/check_vnstat");
		if ($response{status} eq "running") {
			system("/sbin/service vnstat stop &>/dev/null");
		}
		system("rm -rf /storage/vnstat/*");
		if ($response{chkconfig} eq "on") {
			system("/sbin/service vnstat start &>/dev/null");
		}
		chmod(0755, "/etc/cron.5min/check_vnstat");
	}
}

if (exists($in{type}))
{
	# Compile options for vnstat
	my $vcmd = $vnstat;
	if ($in{type} eq 's')
	{
		$vcmd = "$vcmd | grep -v 'Not enough'";
	}
	elsif (exists($in{intf}))
	{
		if ($in{type} eq 'h')
		{
			$vcmd = "$vcmd -h";
		}
		elsif ($in{type} eq 'd')
		{
			$vcmd = "$vcmd -d";
		}
		elsif ($in{type} eq 'w')
		{
			$vcmd = "$vcmd -w";
		}
		elsif ($in{type} eq 'm')
		{
			$vcmd = "$vcmd -m";
		}
		else
		{
			&send_error("Unrecognized option: '$in{type}'");
		}
		if (`$vnstat --iflist` =~ m/$in{intf}/)
		{
			$vcmd = "$vcmd -i $in{intf}";
		}
		else
		{
			&send_error("Unrecognized interface: '$in{intf}'");
		}
	}
	# Update databases before read
	if (`$vnstat -u` =~ m/Error/)
	{
		&send_error("Missing databases. Are you sure vnStat is running?");
	}
	else
	{
		# If snapshot, parse out ignored interfaces
		if ($in{type} eq 's')
		{
			my $eraseMode = 0;
			&check_interfaces();
			#print $vcmd;
			open (CMD, "$vcmd |");
			while (<CMD>)
			{
				#print "Line: $_";
				if ($_ =~ /^\s*([A-Za-z0-9_.]+):\s*$/)
				{
					if ($1 =~ /$iflist_ignore/)
					{
						$eraseMode = 1;
					}
					else
					{
						$eraseMode = 0;
					}
				}
				if (! $eraseMode)
				{
					$response{data} .= $_;
				}
			}
			close (CMD);
		}
		else
		{
			$response{data} = `$vcmd`;
		}
	}
}
else
{
	&send_error("Unrecognized options");
}
&check_chkconfig();
&check_status();
&send_response();
exit;
