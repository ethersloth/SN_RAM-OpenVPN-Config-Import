#!/usr/bin/perl

use strict;
use warnings;

require "./cgi-lib.pl";
require "./uploadlib.pl";
require "./jsonlib.pl";
require "./gau-profile-acl.pl";
require "/etc/env2/env2.pl";
my $sdcard_path = "/media/sdcard/";

my $CONFIG_XML = $ENV{ENV2_FILE_CONFIG_XML};
my $MIGRATECFG = "migratecfg";
my $CFG_TRIM = "system_config_trim";
my $IMPORT_PROGRESS_FILE = "/tmp/updcfg.txt";
my $IMPORT_EOS = "Config operation complete.";
my $xmlimportfile;

my %RESPONSE = (
	"error" => 0
);

my %in = ();
ReadParseUpload(\%in);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%RESPONSE);
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
	exit;
}

sub export {
	my $method = shift;
	my $sublist = shift;
	my $excludes = shift;
	my $filename = "config-" . `printf "\$(serialno)-\$(date +%d%h%y-%H%M)"` . ".xml";
	my $export_file = "/tmp/cfg_export_tmp.xml";
	my $sdcard_file = "$sdcard_path/config/$filename";
	# "vpn" subsystems must be grouped so they can be nested in a <vpn> tag
	my $is_vpn = 0;
	my $vpn_snippet = "";

	if ($sublist) {
		open (TFH, '>', $export_file) or &send_error("Failed to pipe export file");
		print TFH "<GAUCfg version='3.23.091'>\n";
		foreach my $subsystem (split(',', $sublist)) {
			$is_vpn = 0;
			# For <dhcp subsystem="dhcpserver">
			if ($subsystem eq "dhcpserver") {
				$subsystem = "dhcp";
			}
			# For <oobm subsystem="oob">
			elsif ($subsystem eq "oob") {
				$subsystem = "oobm";
			}
			# For <vpn><ipsec subsystem="ipsectunnel"></vpn>
			elsif ($subsystem eq "ipsectunnel") {
				$is_vpn = 1;
				$subsystem = "vpn/ipsec";
			}
			# For <vpn><ipip subsystem="ipiptunnel"></vpn>
			elsif ($subsystem eq "ipiptunnel") {
				$is_vpn = 1;
				$subsystem = "vpn/ipip";
			}
			# For <vpn><gre subsystem="gretunnel"></vpn>
			elsif ($subsystem eq "gretunnel") {
				$is_vpn = 1;
				$subsystem = "vpn/gre";
			}
			if ($subsystem =~ /^[a-z0-9\/?]+$/i) {
				if (! $is_vpn) {
					print TFH `/home/httpd/jbmconfig/bin/xmlpretty --in=$CONFIG_XML --xpath=/GAUCfg/$subsystem --stdout | sed 's/^/    /'`;
				}
				else {
					# Append vpn-nested subsystems to special snippet so they can be grouped together.
					$vpn_snippet .= `/home/httpd/jbmconfig/bin/xmlpretty --in=$CONFIG_XML --xpath=/GAUCfg/$subsystem --stdout | sed 's/^/        /'`;
				}
			}
		}
		if ($vpn_snippet) {
			print TFH "    <vpn>\n";
			print TFH $vpn_snippet;
			print TFH "    </vpn>\n";
		}
		print TFH "</GAUCfg>\n";
		close(TFH);
	}
	else {
		$export_file = $CONFIG_XML;
	}

	if ($method eq "sdcard") {
		system("/bin/mkdir -p $sdcard_path/config; $CFG_TRIM -f $export_file $excludes > $sdcard_file");
		if (-f $sdcard_file) {
			$RESPONSE{file} = $sdcard_file;
		}
		else {
			&send_error("Failed to create $sdcard_file");
		}
	}
	else {
		print "Content-Type:application/x-download\n";
		print "Content-Disposition:attachment;filename=$filename\n\n";
		system("$CFG_TRIM -f $export_file $excludes");
		# Bail out to prevent any further data from being sent as the file
		exit 0;
	}
}

sub import {
	my $filename = shift;
	my $mode = shift;
	my $importMode = shift;

	if (open(SNIPPET, $filename)) {
		foreach my $line (<SNIPPET>) {
			if ($line =~ /subsystem="(\w+)"/g){
				$line =~ s/.+\ssubsystem=\"//;
				$line =~ s/\">\n//;
				if (profileAclAccess($ENV{REMOTE_USER}, $line) ne "write") {
					close(SNIPPET);
					unlink("$filename");
					&send_error("User '$ENV{REMOTE_USER}' not authorized to configure '$line'");
				}
			}
		}
		close(SNIPPET);
	}
	else {
		unlink("$filename");
		&send_error("Failed to open import file");
	}

	my $migrate = "(" .
		"touch /var/run/profile/cfgmgr-import; " .
		"/home/httpd/jbmconfig/bin/$MIGRATECFG " .
			"--tplfile=$CONFIG_XML " .
			"--dftfile=/home/httpd/jbmconfig/conf/cfgtbldflts.xml " .
			"--impfile=$filename " .
			"--outfile=/tmp/config.xml " .
			"--report=detailed " .
			"--dftimpmode=$importMode " .
			"--$mode " .
			"--debug=200 " .
			"&>$IMPORT_PROGRESS_FILE; " .
		"echo 'Synchronizing Config...' >> $IMPORT_PROGRESS_FILE; " .
		"rm -f $filename; " .
		"/home/httpd/jbmconfig/bin/gau_sysinit.sh &>/dev/null; " .
		"echo '$IMPORT_EOS' >> $IMPORT_PROGRESS_FILE; " .
		"rm -f /var/run/profile/cfgmgr-import; " .
		"rm -f $in{cfgfile}; " .
	") &>/dev/null &";
	system($migrate);
	# Tell the browser what string to watch for to confirm end of stream
	$RESPONSE{eos} = "$IMPORT_EOS";
}

sub stream {
	my $complete = 0;
	# Time resolution for checking file for new content
	my $sleepTime = 500;
	# Wait at most 10 seconds after migratecfg dies for more file output (if not complete)
	my $timeout = 10;

	# We actually use this as a counter, ajust for time resolution
	$timeout *= (1000 / $sleepTime);
	# usleep actually uses micro seconds
	$sleepTime *= 1000;

	if (open(my $ipf, $IMPORT_PROGRESS_FILE)) {
		print "Content-type: text/html; charset=utf8\n\n";
		while ( 1 ) {
			while (<$ipf>) {
				print $_;
				# Magic string printed when $MIGRATECFG is done
				if ($_ =~ /$IMPORT_EOS/) {
					$complete = 1;
					last;
				}
			}
			if ($complete) {
				last;
			}
			# If migratecfg dies (and we still haven't seen magic string) exit
			if (`/sbin/pidof $MIGRATECFG` =~ /^\s*$/ and $timeout-- <= 0) {
				last;
			}
			system("/bin/usleep $sleepTime");
			# In case file is still being written, clear EOF flag so we can re-read
			seek($ipf, 0, 1);
		}
		close($ipf);
	}
}

my @FILE_LIST = ();

sub get_file_list {
	my $sdcard_escaped = $sdcard_path;
	$sdcard_escaped =~ s/\//\\\//g;
	if (open my $cmd, "find $sdcard_path -type f |") {
		my $relative_path;
		while (<$cmd>) {
			$relative_path = $_;
			$relative_path =~ s/$sdcard_escaped\/?|\s*$//g;
			push(@FILE_LIST, "sdcard/$relative_path");
		}
		close($cmd);
	}
}

if (exists($in{query})) {
	if ($in{query} eq "export") {
		if (! `mount | grep sdcard` && $in{method} eq "sdcard") {
			&send_error("SD card is not inserted, please insert your SD card");
		}
		&export($in{method}, $in{sublist}, $in{exclude});
	}
	elsif ($in{query} eq "import") {
		if (! exists($in{cfgfile}) || ! -f $in{cfgfile}) {
			&send_error("Missing File");
		}
		if (! exists($in{importmode})) {
			&send_error("Missing Import File Handling");
		}
		elsif ($in{importmode} !~ /^(replace|merge)$/) {
			&send_error("Invalid Import File Handling: '$in{importmode}'");
		}
		if (exists($in{mode})) {
			if ($in{mode} =~ /^(save|apply|applyall)$/) {
				system("xmllint --noout $in{cfgfile} &> /dev/null");
				if ( 0 != $? ) {
					&send_error("The import file $in{cfgfile} is not a valid xml file");
				}
				chomp( $xmlimportfile = `mktemp` );
				open(FILE, ">", "$xmlimportfile");
				if (`head -n 5 $in{cfgfile}` !~ m/GAUCfg/) {
					# File is not wrapped in <GAUCfg> tag
					print FILE `echo "<GAUCfg version='*'>"`;
					print FILE `cat $in{cfgfile}`;
					print FILE `echo "</GAUCfg>"`;
				}
				elsif (`head -n 5 $in{cfgfile}` !~ m/GAUCfg .*version/) {
					# GAUCfg tag is missing "version" attribute
					print FILE `sed -i 's/<GAUCfg/<GAUCfg version=\'*\'/' $in{cfgfile}`;
					print FILE `cat $in{cfgfile}`;
				}
				else {
					print FILE `cat $in{cfgfile}`;
				}
				close(FILE);
				&import($xmlimportfile, $in{mode}, $in{importmode});
			}
			else {
				&send_error("Invalid mode: '$in{mode}'");
			}
		}
		else {
			&import($in{cfgfile}, "save", $in{importmode});
		}
	}
	elsif ($in{query} eq "stream") {
		# Wait a few seconds for migratecfg to start importing:
		my $timeout = 10;
		while (! -f $IMPORT_PROGRESS_FILE && $timeout-- gt 0) {
			sleep 1;
		}
		if (-f $IMPORT_PROGRESS_FILE) {
			&stream();
		}
		else {
			print "Content-type: text/html; charset=utf8\n\n";
			print "Error: Timed out waiting for $MIGRATECFG";
		}
		# Exit to prevent further data being sent in stream
		exit;
	}
	elsif ($in{query} eq "list") {
		if (`mount | grep sdcard`) {
			&get_file_list();
			$RESPONSE{data} = \@FILE_LIST;
		}
		else {
			&send_error("SD card is not inserted, please insert your SD card");
		}
	}
	elsif ($in{query} eq "importsdc") {
		if (! exists($in{content})) {
			&send_error("Missing Import File");
		}
		if (! exists($in{importmode})) {
			&send_error("Missing Import File Handling");
		}
		elsif ($in{importmode} !~ /^(replace|merge)$/) {
			&send_error("Invalid Import File Handling: '$in{importmode}'");
		}
		if ($in{content} !~ /\.\.\/|'|\s|;/) {
			# compensate for adding sdcard/ prefix in get_file_list
			my $media_path = $sdcard_path;
			$media_path =~ s/sdcard\/?//;
			if (-f "$media_path$in{content}") {
				system("xmllint --noout $media_path$in{content} &> /dev/null");
				if ( 0 != $? ) {
					&send_error("The import file $in{content} is not a valid xml file");
				}
				if (exists($in{mode})) {
					if ($in{mode} =~ /^(save|apply|applyall)$/) {
						&import("$media_path$in{content}", $in{mode}, $in{importmode});
					}
					else {
						&send_error("Invalid mode: '$in{mode}'");
					}
				}
				else {
					&import("$media_path$in{content}", "save", $in{importmode});
				}
			}
			else {
				&send_error("Cannot find import file $in{content}");
			}
		}
		else {
			&send_error("The import file $in{content} is not a valid file");
		}
	}
	else {
		&send_error("Unrecognized command: '$in{query}'");
	}
}
else {
	&send_error("Unrecognized options");
}

&send_response();

exit;

