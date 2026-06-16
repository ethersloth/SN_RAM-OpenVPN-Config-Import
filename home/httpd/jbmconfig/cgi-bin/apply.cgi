#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Script to apply a list of subsystems in the background
#
# This allows a browser to quickly save a series of subsystems before applying
# them all at once. It also allows a browser to prepare to reconnect if a
# configuration change breaks the connection.

require "./cgi-lib.pl";
require "./jsonlib.pl";

my %RESPONSE = (
	"error" => 0
);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%RESPONSE);
	exit
}
sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
}

sub apply_subs {
	my $list = shift;
	my $command = "sleep 1; (cd /home/httpd/jbmconfig/cgi-bin/; ";
	foreach my $subsystem (@{$list}) {
		$command .= "./gau --subsystem=$subsystem --action=Apply; ";
	}
	$command .= ") &>/dev/null &";
	system($command);
}

my %in;
ReadParse(\%in);

if (exists($in{list})) {
	my @list = ();
	foreach my $subsystem (split ',', $in{list}) {
		if ($subsystem =~ /^[a-z0-9]+$/) {
			push(@list, $subsystem);
		}
	}
	&apply_subs(\@list);
}
else {
	&send_error("Must specify a list of subsystems");
}

&send_response();

exit 0;
