#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";

my %RESPONSE = (
	error => 0
);

$ENV{PATH} = "/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin";
my $PROG = "/usr/local/bin/msmtp";
my $CONF_FILE = "/etc/email.conf";

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

my %in = ();
ReadParse(\%in);

if (exists($in{content}) && exists($in{recipient})) {
	my $debugfile = "/tmp/email_debug_log";
	my $emailfile = "/tmp/email_test";
	my $recipient = $in{recipient};
	my $content = $in{content};
	open(FILE, ">", "$emailfile");
	print FILE $content;
	close(FILE);
	system("$PROG -C $CONF_FILE -t -d --timeout=10 < $emailfile &> $debugfile");
	if ( $? == 0 ) {
		$RESPONSE{data} = "***** SUCCESS: Email Settings are valid and configured properly.\n";
		$RESPONSE{data} .= "***** An email has been sent to $recipient.\n";
		$RESPONSE{data} .= "***** Please check to verify your server settings.\n\n";
		$RESPONSE{data} .= &readFile($debugfile);
	}
	else {
		$RESPONSE{data} = "***** ERROR: Email Settings are not valid\n\n";
		$RESPONSE{data} .= &readFile($debugfile);
	}
	system("/bin/rm -f $emailfile $debugfile");
}
else {
	&send_error("Missing email content or recipient");
}

&send_response;

exit;
