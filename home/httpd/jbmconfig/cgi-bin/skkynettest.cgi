#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";

my $etkscriptPID = "none";
my %RESPONSE = (
	error => 0
);
my $LSPDEFAULT = "/etc/skkynet/rldefault.lsp";
my $LSPFILE = "/etc/skkynet/rlcustom.lsp";
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

sub printStatus {
        if ( "none" eq $etkscriptPID ) {
		$RESPONSE{data} = "Stopped";
	}
	else {
		$RESPONSE{data} = "Running";
	}
	if (-f $LSPFILE) {
		$RESPONSE{points} = &readFile($LSPFILE);
	}
	else {
		$RESPONSE{points} = &readFile($LSPDEFAULT);
	}
}

sub checkRunningSkkynet {
	open(CMD, "ps -ea | grep etkscript | awk '{print \$1}' 2>&1 |");
	while(<CMD>) {                                                       
	      $etkscriptPID = $_;                                            
	}                        
	close(CMD);              
}

my %in = ();
ReadParse(\%in);

&checkRunningSkkynet();

if (exists($in{type}) && exists($in{name})) {
	my $inputfile = $in{name};
	if ($in{type} eq 'load') {
                my $file = &readFile($inputfile);
                   $RESPONSE{data} = $file;
	}
        elsif ($in{type} eq 'save') {
                my $outputfile = "/tmp/file_output";
                my $content = $in{content};
                open(OFILE, ">", "$outputfile");
                print OFILE $content;
                close(OFILE);
                system("mv -f $outputfile $inputfile");
		$RESPONSE{data} = &readFile($inputfile);

	}
	else {
		&send_error("Unrecognized type");
	}
}
elsif ($in{type} eq 'points' and exists $in{points}) {
	if (open (LFILE, '>', $LSPFILE)) {
		print LFILE $in{points};
		close(LFILE);
		# Send the file we just wrote back to the GUI for confirmation
		&printStatus();
	}
	else {
		&send_error("Failed to write points to file");
	}
}
elsif (exists($in{type}) && "status" eq $in{type}) {
	&printStatus();
}
else {
	&send_error("Unrecognized type");
}

&send_response;

exit;
