#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

use strict;
use warnings;

require "./cgi-lib.pl";
require "./jsonlib.pl";

my %in = ();
ReadParse(\%in);

my %RESPONSE = (
	"error" => 0
);

my $g_diag_running = 0;
my $g_logfile_present = 0;
my $g_filterfile_present = 0;
my $embedded_date = "";

my $g_module = "MC5727";
my $sdcard_path = "/media/sdcard/";
my $g_filterfile = "/tmp/filter.sqf";
my $g_logfile = "/tmp/SwiDiagOutput0.ldk";
my $g_alt_logfile = "/media/sdcard/SwiDiagOutput0.ldk";
my $g_dm_log_maxed_file = "/tmp/maxDMlog";
my $g_swidiag_name = "SwiDiagnosticJBM";
my $g_swisdk_name = "swisdk";
my $build_date_file = "/etc/build-date";
my $filename = "";
my $tmpfile = "";

my $g_errors = "";
my $use_new_qmi = 0;
my $g_device = "";
my $output = "";
my $ret = 0;
my $sd_card_logging = 0;

if ( -e "$g_alt_logfile" ) {
	$g_logfile = $g_alt_logfile;
	$sd_card_logging = 1;
}

#
# Response handling routines
#
my %JSON_RESPONSE = (
	"error" => 0
);

sub exit_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%JSON_RESPONSE);
	exit
}

sub exit_error {
	my $msg = shift;
	$JSON_RESPONSE{error} = 1;
	$JSON_RESPONSE{message} = $msg;
	&exit_response();
}

#must be done before anything
&GetModuleInfo();

#
# Request validation
#

if (exists($in{query})) {
	if ($in{query} eq "upload") {
		if (exists $in{file}) {
			&upload($in{file})
		}
		else {
			&exit_error("No filter file specified");
		}
	}
	elsif ($in{query} eq "download") {
		&download()
	}
	elsif ($in{query} eq "start" && exists($in{autoconnect})) {
		&StartDiag()
	}
	elsif ($in{query} eq "stop") {
		&StopDiag()
	}
	elsif ($in{query} eq "status") {
		&GetDiagStatus();
	}
	else {
		&exit_error("Unrecognized query");
	}
}
else {
	&exit_error("No query specified");
}

&exit_response();

exit;


#
# Modem Module-handling routines
#
sub GetModuleInfo() {
	#check for MC7|8xx
	$output = `/bin/grep -i 'Product=MC[7|8]' /proc/bus/usb/devices 2>/dev/null`;
	chomp($output);
	#print "$output\n";
	if ( $output =~ m/Product=(MC\d+)/i  ) {
		$g_module = "$1";
		$use_new_qmi = 1;
		$g_swidiag_name = "rl_dmcapture.sh";

		if ( $output =~ m/^.*Product=MC73.*$/i  ) {
			#MC73xx uses USB0
			$g_device = "/dev/ttyUSB0";
		}
		elsif ( $output =~ m/^.*Product=MC77.*$/i  ) {
			#MC7700 uses USB1
			$g_device = "/dev/ttyUSB1";
		}
		elsif ( $output =~ m/^.*Product=MC87.*$/i  ) {
			#MC87xx use USB1 also?
			$g_device = "/dev/ttyUSB1";
		}
		else {
			&exit_error("Unsupported module");
			exit();
		}
		$JSON_RESPONSE{device} = $g_device;
	}
}

sub GetDiagStatus() {
	if ( -e "$build_date_file" ) {
		$embedded_date = `cat $build_date_file`;
		chomp $embedded_date;
		$JSON_RESPONSE{builddate} = $embedded_date;
	}
	else {
		$embedded_date = "unknown";
		$JSON_RESPONSE{builddate} = $embedded_date;
	}
	if ( -e "$g_dm_log_maxed_file" )
	{
	   $JSON_RESPONSE{logmaxed} = "Diagnostic log size is maxed.  Logging has stopped.";
	}
	if ( -e "$g_filterfile" ) {
		$g_filterfile_present = 1;
	}
	if ( -e "$g_logfile" ) {
		$g_logfile_present = 1;
	}
	system("/bin/ps -aux --cols=120 | /bin/grep -v grep | /bin/grep $g_swidiag_name &> /dev/null");
	if ( 0 == $? ) {
		$g_diag_running = 1;
		$JSON_RESPONSE{runstat} = "DM Log Running";
	}
	else {
		$JSON_RESPONSE{runstat} = "DM Log Not Running";
	}
	if (-e "$g_logfile") {
		my @logstat = stat("$g_logfile");
		$JSON_RESPONSE{logfilesize} = "$logstat[7] bytes";
	}
	else {
		$JSON_RESPONSE{logfilesize} = "Log file doesn't exist";
	}
	if ( -e "$g_dm_log_maxed_file" && -e "$g_logfile")
	{
	   $JSON_RESPONSE{logmaxed} = "Diagnostic log file size is maxed. Logging and process have stopped, you can now download the log file.";
	   &StopDiag();
	}
}

sub download {
	$filename = "SierraDiagLogfile_" . `printf "\$(serialno)_\$(date +%d%h%y-%H%M).ldk"`;
	if ( $g_diag_running ) {
		&exit_error("Diag is running, stop it before downloading the log file");
	}
	if (`mount | grep sdcard` && -e "$g_alt_logfile") {
		$tmpfile = "$g_alt_logfile";
	}
	else {
		$tmpfile = "$g_logfile";
	}
	print "Content-Type:application/x-download\n";
	print "Content-Disposition:attachment;filename=$filename\n\n";
	if (open(my $cfh, $tmpfile)) {
		local $/ = undef;
		print <$cfh>;
		close($cfh);
	}
	exit 0;
}

sub upload {
	my $filter = shift;
	if (! -f $filter) {
		&exit_error("No filter file found");
	}
	system("rm -f /tmp/boa-temp.*");
	system("rm -f /tmp/lighttpd-upload.*");
	unlink("$g_filterfile");
	system("/bin/mv -f \"$filter\" $g_filterfile");
	system("/bin/chmod 0600 $g_filterfile");
	$JSON_RESPONSE{data} = "Filter file $g_filterfile has been installed, you can start the diagnostic now.";
}

sub StartDiag() {
	if ( $g_diag_running ) {
		&exit_error("Diagnostic process already running, stop it first.");
		return;
	}
	if ( ! -e "$g_filterfile" ) {
		&exit_error("Upload a filter file before starting.");
		return;
	}
	#remove log file before starting
	&StopDiag();
	unlink($g_dm_log_maxed_file);
	unlink($g_logfile);
	system("rm -f /tmp/*.ldk");

	$ret = 0;
	my $at_cmd_in = "/tmp/at_cmd_in";
	my $at_cmd_out = "/tmp/at_cmd_out";

	if ( $use_new_qmi ) {
		#stop the connection
		#radio off
		#sleep 3
		#start diag
		#radio on
		#sleep 3
		#start connection
		system("logger -t 'dmdiag' 'Auto Stop/Start Connection is set to $in{autoconnect}'");
		if ($in{autoconnect} eq "auto") {
			system("logger -t 'dmdiag' 'Auto Connect is set for $in{autoconnect}'");
			system("cellmodemconnect.pl nocon &>/dev/null");
			sleep(3);
			unlink($at_cmd_out);
			system("echo 'AT+CFUN=0' > $at_cmd_in");
			sleep(3);
		}

		my $cmd = "/sbin/$g_swidiag_name -f $g_filterfile -d $g_device &> /dev/null &";
		system("$cmd");
		sleep(3);

		if ($in{autoconnect} eq "auto") {
			system("echo 'AT+CFUN=1' > $at_cmd_in");
			sleep(3);
			system("cellmodemconnect.pl clear &>/dev/null");
		}
	}
	else {
		$ret = system("/sbin/$g_swidiag_name -v -p /sbin/$g_swisdk_name -t 5000 -i $g_filterfile &> /dev/null");
	}

	if ( 0 != $ret) {
		if ( 2 == $ret || 512 == $ret) {
			&exit_error("Downloaded filter is an invalid format.");
			$g_diag_running = 0;
			$JSON_RESPONSE{runstat} = "DM Log Not Running";
			return;
		}
		if ( 1 == $ret || 256 == $ret ) {
			&exit_error("Sierra interface error.  Please try starting diag again.");
			$g_diag_running = 0;
			$JSON_RESPONSE{runstat} = "DM Log Not Running";
			return;
		}
		&exit_error("Unknown error.  Return code $ret");
		$g_diag_running = 0;
		$JSON_RESPONSE{runstat} = "DM Log Not Running";
		return;
	}
	$JSON_RESPONSE{runstat} = "DM Log Running";
	sleep(3);
}

sub StopDiag() {
	#just kill the process
	system("/usr/bin/killall $g_swidiag_name &> /dev/null");
	if ( $use_new_qmi ) {
		#uses "cat" to get the raw infrom from dev/ttyUSBn
		system("/usr/bin/killall cat &> /dev/null");
	}
	sleep(5);
	$g_diag_running = 0;
	$JSON_RESPONSE{runstat} = "DM Log Not Running";
}
