#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and
# Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and
# product names are trademarks of their respective owners.

use warnings;
use strict;
require "./jsonlib.pl";
my %RESPONSE = (
	error => "false"
);
%{$RESPONSE{data}} = ();

open(CMD, "ps -eo args |");
while (<CMD>) {
	if ($_ =~ /^\/bin\/svmclient(.*)$/) {
		my $rawargs = $1;
		$RESPONSE{data}{clientstatus} = "ENABLED";
		if ($rawargs =~ /sleeping for (.*)$/) {
			$RESPONSE{data}{checkin} = $1;
		}
		else {
			$RESPONSE{data}{checkin} = "Currently Running";
		}
	}
}
close(CMD);
if (! exists $RESPONSE{data}{clientstatus}) {
	$RESPONSE{data}{clientstatus} = "DISABLED";
	$RESPONSE{data}{checkin} = "N/A";
}

open(FH, "/etc/jbm/svmclient.conf");
while (<FH>) {
	if ($_ =~ /JBM_SERVER_IP = (.*)$/) {
		$RESPONSE{data}{report} = $1;
	}
	if ($_ =~ /JBM_SERVER2_IP = (.*)$/) {
		$RESPONSE{data}{report2} = $1;
	}
}
close(FH);

my $lastchkfile = "/tmp/gmu_last_status";
if (-e $lastchkfile) {
	$RESPONSE{data}{lastchk1} = `head -n 1 $lastchkfile`;
	if ($RESPONSE{data}{lastchk1} =~ /^\s*$/) {
		$RESPONSE{data}{lastchk1} = "N/A";
		$RESPONSE{data}{lastchk2} = "";
	}
	else {
	}
		$RESPONSE{data}{lastchk2} = `tail -n 1 $lastchkfile`;
		if ($RESPONSE{data}{lastchk1} eq $RESPONSE{data}{lastchk2}) {
			$RESPONSE{data}{lastchk2} = "";
		}
}

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%RESPONSE);
