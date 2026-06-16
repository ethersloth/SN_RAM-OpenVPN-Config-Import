#!/usr/bin/perl -w
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./jsonlib.pl";

my %RESPONSE = ();

open(FH, "/etc/modprobe.conf");
while (<FH>) {
	if ($_ =~ /ain=([0-9]+)/) {
		$RESPONSE{ain} = $1;
	}
	if ($_ =~ /aout=([0-9]+)/) {
		$RESPONSE{aout} = $1;
	}
	if ($_ =~ /lin=([0-9]+)/) {
		$RESPONSE{lin} = $1;
	}
	if ($_ =~ /lout=([0-9]+)/) {
		$RESPONSE{lout} = $1;
	}
}
close(FH);


if (! exists $RESPONSE{ain} || ! exists $RESPONSE{aout} || ! exists $RESPONSE{lin} || ! exists $RESPONSE{lout}) {
	$RESPONSE{error} = "Parameters not found";
}

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%RESPONSE);
