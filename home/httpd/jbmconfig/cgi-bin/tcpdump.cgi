#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use strict;
use warnings;

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";

my $TCPDUMP = "/usr/sbin/tcpdump";
my $LASTRUNFILE = "/var/run/tcpdump-cgi.last";
my $CAPFILE  = "/tmp/tcpdump.cap";
my $TCPLOCK = "/var/run/tcpdump-cgi.lck";
my $NUMCAPS = 3;
my $IFIGNORE = "mon.wlan0|.*_cpu";

my %RESPONSE = ( error => 0 );

sub send_response {
	&IOG::CGI::printHeaders();
	print &JSON_Serialize(\%RESPONSE);
	exit
}
sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
}

# Populate $RESPONSE{data}{last}
sub getlastrun {
	$RESPONSE{data}{last} = "";
	if (-r $LASTRUNFILE) {
		if (open(LFILE, $LASTRUNFILE)) {
			local $/ = undef;
			$RESPONSE{data}{last} = <LFILE>;
			close(LFILE);
		}
	}
}

# Populate $RESPONSE{data}{files}
sub getfileslist {
	my @fstat;
	my @unsorted = ();

	# See if there was an interface specified to append to file name
	my $intf = "all";
	&getlastrun();
	if ($RESPONSE{data}{last} =~ /-i ([a-z0-9:]+) /) {
		$intf = $1;
	}

	opendir(DIR, "/tmp") or &send_error("Failed to find tcpdump files");
	while (my $f = readdir(DIR)) {
		if ($f =~ /^tcpdump.cap/) {
			@fstat = stat("/tmp/$f");
			push(@unsorted, {(
				size => $fstat[7],
				time => `date -d \@$fstat[9] -R`, # last modify time
				name => $f
			)});
		}
	}
	closedir(DIR);
	# Sort files by modification time
	@{$RESPONSE{data}{files}} = sort { $b->{time} <=> $a->{time} } @unsorted;
	# Create symlinks to files so the file name increases in order of modification time
	my $linkname;
	for (my $i = 0; $i <= $#unsorted; $i++) {
		$linkname = "tcpdump-$intf-$i.cap";
		unlink("/tmp/$linkname") if (-l "/tmp/$linkname");
		symlink("/tmp/$RESPONSE{data}{files}[$i]{name}", "/tmp/$linkname");
		$RESPONSE{data}{files}[$i]{name} = $linkname;
	}
}

sub isValidInterface {
	return $_[0] =~ /^[a-z0-9:.]+$/;
}

sub isValidSnap {
	return $_[0] =~ /^[0-9]+$/
}

sub getMaxSize {
	my $inSize = shift;
	my $maxSize = 3;
	if (`df` =~ /tmpfstmp\s+([0-9]+)\s.+\/tmp/) {
		$maxSize = int($1 / 6144); # kb / 2 / 3 / 1024
	}
	if ($inSize =~ /^[0-9]+$/) {
		return $inSize <= $maxSize ? $inSize : $maxSize;
	}
	else {
		return 1;
	}
}

sub isValidFilter {
	return $_[0] !~ /'/;
}

my %in = ();
ReadParse(\%in);

if (exists($in{cmd})) {
	if ($in{cmd} eq "status") {
		if (-d $TCPLOCK) {
			$RESPONSE{data}{running} = 1;
		}
		else {
			$RESPONSE{data}{running} = 0;
		}
		&getfileslist();
		&send_response();
	}
	elsif ($in{cmd} eq "list") {
		@{$RESPONSE{data}} = ();
		if (open(IFC, "/sbin/ifconfig |")) {
			while (<IFC>) {
				if ($_ =~ /^([^\s]+)\s/) {
					if ($1 !~ /$IFIGNORE/) {
						push(@{$RESPONSE{data}}, $1);
					}
				}
			}
			close(IFC);
		}
		else {
			&send_error("Failed to query list of interfaces");
		}
		&send_response();
	}
	elsif ($in{cmd} eq "download") {
		if (! exists($in{file}) or ! -r "/tmp/$in{file}") {
			&IOG::CGI::printHeaders();
			print "Invalid file specified.";
			exit;
		}
		&IOG::CGI::printHeaders({
			"Content-type" => "application/x-download",
			"Content-Disposition" => "attachment;filename=$in{file}"
		});
		local $/ = undef;
		open(DLFILE, "/tmp/$in{file}");
		print <DLFILE>;
		close(DLFILE);
		exit;
	}
	elsif ($in{cmd} eq "start") {
		my $filter = "";
		my $command = "$TCPDUMP";
		if (! mkdir($TCPLOCK)) {
			$RESPONSE{data}{running} = 1;
			&send_error("Please stop previous capture before starting a new one.");
		}
		if (exists($in{i}) and &isValidInterface($in{i})) {
			$filter .= " -i $in{i}";
		}
		else {
			&send_error("Please specify a valid interface with 'i'");
		}
		if (exists($in{s}) and &isValidSnap($in{s})) {
			$filter .= " -s $in{s}";
		}
		if (exists($in{C})) {
			$filter .= " -C " . &getMaxSize($in{C});
		}
		else {
			$filter .= " -C 1";
		}
		if (exists($in{filter}) and &isValidFilter($in{filter})) {
			$filter .= " '$in{filter}'";
		}
		if (open(LFILE, '>', $LASTRUNFILE)) {
			print LFILE "$filter";
			close(LFILE);
		}
		$RESPONSE{data}{last} = $filter;
		$command .= " $filter";
		$command .= " -nnn";           # Don't resolve hostnames
		$command .= " -U";             # packet-buffered output (for binary .cap)
		$command .= " -w $CAPFILE";    # Send binary to $CAPFILE
		$command .= " -W $NUMCAPS";    # Rotate through $NUMCAPS log files

		system("rm -rf /tmp/tcpdump*; ($command; rm -rf '$TCPLOCK') &>/dev/null &");
		$RESPONSE{data}{running} = 1;
		# Wait a second to see if tcpdump started successfully
		sleep 1;
		if (! -d $TCPLOCK) {
			$RESPONSE{data}{running} = 0;
			&send_error("tcpdump failed to start. Bad filter?");
		}
		&send_response();
	}
	elsif ($in{cmd} eq "stream") {
		&IOG::CGI::printHeaders();
		my $filter = "";
		my $command = "$TCPDUMP";
		if (exists($in{i}) and &isValidInterface($in{i})) {
			$filter .= " -i $in{i}";
		}
		else {
			print "Please specify a valid interface with 'i'\n";
			exit 1;
		}
		if (exists($in{s}) and &isValidSnap($in{s})) {
			$filter .= " -s $in{s}";
		}
		if (exists($in{filter}) and &isValidFilter($in{filter})) {
			$filter .= " '$in{filter}'";
		}
		$command .= " $filter";
		$command .= " -nnn";           # Don't resolve hostnames
		$command .= " -l";             # line-buffered output for streaming

		# Send any tcpdump errors upstream too
		system("$command 2>&1");
	}
	elsif ($in{cmd} eq "stop") {
		system("killall tcpdump");
		$RESPONSE{data}{running} = 0;
		&getfileslist();
		system("rm -rf '$TCPLOCK'"); # Just in case
		&send_response();
	}
	elsif ($in{cmd} eq "view") {
		if (! exists($in{file}) or ! -r "/tmp/$in{file}") {
			&send_error("Please specify a valid file");
		}
		my $command = "$TCPDUMP";
		$command .= " -nnn";             # Don't resolve hostnames
		$command .= " -l";               # Line-buffered
		$command .= " -r /tmp/$in{file}"; # Read from link to newest cap file
		&IOG::CGI::printHeaders();
		my $dump;
		if (! open($dump, "$command |")) {
			print "Failed to open tcpdump stream";
			exit;
		}
		local $/ = undef;
		print <$dump>;
		close($dump);
	}
	else {
		&send_error("Unknown command");
	}
}
else {
	&send_error("Please specify an action with 'cmd'");
}
