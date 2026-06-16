#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

# carriershim.cgi - GUI Front-end to carriershim.sh
# Expected incoming arguments:
#    command: status|delete|reflash
#    manifest: name of manifest, if command is delete or reflash

require "./cgi-lib.pl";
require "./jsonlib.pl";
require "/etc/env2/env2.pl";

my $manifest_dir = "/images/cell/manifest";
my $carriershim = "/bin/carriershim.sh";
my %response = (
	error => 0
);
my %in = ();

ReadParse(\%in);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%response);
}
sub send_error {
	my $msg = shift;
	$response{error} = 1;
	$response{message} = $msg;
	&send_response();
	exit;
}

# manifest_status Fill response{data} with status
sub manifest_status {
	%{$response{data}} = ();
	%{$response{data}{manifests}} = ();
	foreach my $manifest (split("\n", `$carriershim list`)) {
		if ($manifest ne '' and open(my $m_file, "$manifest_dir/$manifest")) {
			%{$response{data}{manifests}{$manifest}} = ();
			while (my $line = readline($m_file)) {
				if ($line =~ /^([^=]+)="(.*)"$/) {
					$response{data}{manifests}{$manifest}{$1} = $2;
				}
			}
			close($m_file);
		}
	}

	$response{data}{state} = `$carriershim state`;
	chomp($response{data}{state});

	# "active" manifest
	$response{data}{active} = `$carriershim active`;
	chomp($response{data}{active});
}

# carriershim queries that operate on a specific manifest (delete/reflash)
sub manifest_query {
	my $query = shift;
	chomp($response{message} = `$carriershim $query 2>&1`);
	$response{error} = $? >> 8;
}

# stream_reflash_status - stream output from status file to browser
sub stream_reflash_status {
	my @parsed = ();
	my $status_file;

	# Make STDOUT 'hot' so we aren't buffering output
	local $| = 1;

	print "Content-type: text/html; charset=utf8\n\n";
	my $watching = 1;
	while ($watching) {
		# We want to do one last read after the flag is gone to make sure we got everything
		if (! -e $ENV{ENV2_FLAG_MODEM_UPDATE}) {
			$watching = 0;
		}
		if (open(FILE, $ENV{ENV2_FILE_MODEM_UPDATE_STATUS})) {
			while (<FILE>) {
				# Print any lines we haven't previously printed
				if (!($_ ~~ @parsed)) {
					print $_;
					push(@parsed, $_);
				}
			}
			close(FILE);
		}
		sleep 1;
	}

	print "Waiting for module to reset\n";
	while (-e $ENV{ENV2_FILE_PCMCIA_PID}) {
		sleep 1;
	}
	while (! -e $ENV{ENV2_FILE_WIRELESS_CARDSTATS}) {
		sleep 1;
	}
	sleep 5; # Wait for cardstats to finish being written to?
	print "Process Complete\n";
}

if (exists($in{command})) {
	if ($in{command} eq "status") {
		&manifest_status();
	}
	elsif ($in{command} eq "delete") {
		if (exists($in{manifest}) && $in{manifest} =~ /^[0-9A-Za-z-._]+\.mni$/) {
			&manifest_query("delete $in{manifest}");
		}
		else {
			&send_error("Must provide valid manifest");
		}
	}
	elsif ($in{command} eq "reflash") {
		if (exists($in{manifest}) && $in{manifest} =~ /^[0-9A-Za-z-._]+\.mni$/) {
			&manifest_query("reflash $in{manifest}");
		}
		else {
			&send_error("Must provide valid manifest");
		}
	}
	elsif ($in{command} eq "stream") {
		# Wait for ENV{ENV2_FLAG_MODEM_UPDATE_START} to disappear (backend script has started its thing)
		while (-e $ENV{ENV2_FLAG_MODEM_UPDATE_START}) {
			sleep 1;
		}
		&stream_reflash_status();
		# exit since we streamed a response instead of sending a json object
		exit 0;
	}
	else {
		&send_error("Unrecognized command");
	}
}
else
{
	&send_error("Must specify a command");
}
&send_response();
exit;
