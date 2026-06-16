#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";
require "/etc/env2/env2.pl";

my $MAX_POLL_TIME = 120;

my %RESPONSE = ( error => 0 );

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

sub isValidCmdSet {
	return 1;
}

sub slurp_file {
	my $file = shift;
	my $content = "";
	if (open(my $fh, $file)) {
		local $/ = undef;
		$content = <$fh>;
		close($fh);
	}
	return $content;
}

# Write out $ENV{ENV2_FILE_AT_CMD_IN} with command list in a text block
sub write_cmd_in {
	unlink $ENV{ENV2_FILE_AT_CMD_OUT_RAW}, $ENV{ENV2_FILE_AT_CMD_OUT};
	if (open(my $in_fh, '>', $ENV{ENV2_FILE_AT_CMD_IN})) {
		print $in_fh $_[0];
		close($in_fh);
	}
}

# Populate $RESPONSE{data} and $RESPONSE{raw} with contents of $ENV{ENV2_FILE_AT_CMD_OUT}(_RAW)
sub read_cmd_out {
	my $start_time = time;
	while ((time - $start_time) < $MAX_POLL_TIME and ! -e $ENV{ENV2_FILE_AT_CMD_OUT_RAW}) {
		sleep 1;
	}
	sleep 1;
	$RESPONSE{raw} = &slurp_file($ENV{ENV2_FILE_AT_CMD_OUT_RAW});
	if ($RESPONSE{raw} eq "") {
		$RESPONSE{raw} = "No response from module";
	}
	$RESPONSE{data} = &slurp_file($ENV{ENV2_FILE_AT_CMD_OUT});
	if ($RESPONSE{data} eq "") {
		$RESPONSE{data} = "No response from module to parse";
	}
}

my %in = ();
ReadParse(\%in);

if (exists($in{at_cmd_in}) and &isValidCmdSet($in{at_cmd_in})) {
	&write_cmd_in($in{at_cmd_in});
	# Wait for processor to pick up the file
	sleep 1;
	&read_cmd_out();
}
else {
	&send_error("Please specify an action with 'at_cmd_in'");
}
&send_response();
