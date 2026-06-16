#!/usr/bin/perl -w
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";
require "/etc/env2/env2.pl";
use IOG::SKVS;

my $scriptfile = "/bin/straton-access.pl";
my $stratonPID = "none";

my $T5RL = "/usr/local/bin/iecengine";
my %RESPONSE = (
	"error" => 0
);

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

sub checkRunningScripts {
	open(CMD, "ps -ea | grep straton-access | awk '{print \$1}' 2>&1 |");
	while(<CMD>) {
		$stratonPID = $_;
	}
	close(CMD);
}

sub get_status {
	chomp( $RESPONSE{data}{version} = `$T5RL --version 2>&1` );

	if (`/sbin/service iecengine status` =~ /running/) {
		$RESPONSE{data}{status} = "Running";
	}
	else {
		$RESPONSE{data}{status} = "Stopped";
	}
	if (`/sbin/chkconfig --list | grep iecengine` =~ /3:on/) {
		$RESPONSE{data}{enable} = "y";
	}
	else {
		$RESPONSE{data}{enable} = "n";
	}
	if (-f "/etc/iecengine/t5.cod") {
		$RESPONSE{data}{loaded} = "y";
	}
	else {
		$RESPONSE{data}{loaded} = "n";
	}
	if ( 1 == IOG::SKVS::get("FC_IECENGINE") ) {
		$RESPONSE{data}{unlock} = 1;
	}
	else {
		$RESPONSE{data}{unlock} = 0;
	}
}

sub apply {
	my $options = shift;
	if (exists ${$options}{enable}){
		if (${$options}{enable} eq "y") {
			system("/sbin/chkconfig iecengine on");
		}
		else {
			system("/sbin/chkconfig iecengine off");
		}
	}
}

sub start_remotelink {
	my $accesstime = shift;
	my $srcip = shift;
	if ( -x "$scriptfile" ) {
		if ( $stratonPID eq "none" ) {
			system("logger -t 'stratoncontrol' 'running accesstime=$accesstime srcip=$srcip $scriptfile &>/dev/null.'");
			system("accesstime=$accesstime srcip=$srcip $scriptfile &>/dev/null &");
		}
		else {
			&send_error("Straton access script is running");
		}
	}
	else {
		&send_error("Staton Access Script doesn't exist");
	}
}

#returns 1 if the time value is valid
sub checkTime
{
   return $_[0] =~ /^(\d{1,3})$/ &&
                  $1 >= 5 && $1 <= 240;
}

#returns 1 if the IP is valid
sub checkIP
{
      return $_[0] =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/  &&
      $1 >= 0 && $1 <= 255 && $1 !~ /^0\d+$/ &&
      $2 >= 0 && $2 <= 255 && $2 !~ /^0\d+$/ &&
      $3 >= 0 && $3 <= 255 && $3 !~ /^0\d+$/ &&
      $4 >= 0 && $4 <= 255 && $4 !~ /^0\d+$/;
}

sub unlock {
	my $code = shift;

	if (`/sbin/unlocker -f  iecengine -u $code 2>&1` =~ "Invalid") {
		&send_error("Invalid unlock code");
	}
}

sub snupdate_straton {
        # Generate snpatch_straton.zip file if an application exists in the device.
        #
        # Include the Straton t5.upl zip file if present. This file contains the
        # source code used to build the current application.

        my $iec_path = "/etc/iecengine";
        my $iec_app_file = "t5.cod";
        my $iec_exclude = "t5.upd t5.hot";
        my $iec_install_script = "/etc/iog/install_iecengine.sh";
        my $iec_zip_file = "snpatch_straton_app.zip";

        if (-e "$iec_path/$iec_app_file") {
                if (-e "/tmp/$iec_zip_file") {
                        system("rm -f /tmp/$iec_zip_file");
                }
                system("cd /; zip -r -y /tmp/$iec_zip_file $iec_path/*" .
                       " -x $iec_exclude");
                system("ln -s /etc/iog/install_iecengine.sh" .
                       " $iec_path/install.sh");
                system("cd $iec_path; zip -r /tmp/$iec_zip_file install.sh");
                system("rm -f $iec_path/install.sh");
                print "Content-Type:application/x-download\n";
                print "Content-Disposition:attachment;" .
                    "filename=$iec_zip_file\n\n";
                system("cat /tmp/$iec_zip_file");
                # Bail out to prevent any further data from being sent
                # as the file
                exit 0;
        }
}

my %in = ();
ReadParse(\%in);
&checkRunningScripts();
if (exists($in{query})) {
	if ($in{query} eq "status") {
		&get_status();
	}
	elsif ($in{query} eq "start") {
		system("/sbin/service iecengine restart 1>/dev/null 2>&1");
		&get_status();
	}
	elsif ($in{query} eq "stop") {
		system("/sbin/service iecengine stop 1>/dev/null 2>&1");
		sleep 1;
                #
                # Clear out the iecengine statistics
                #
                system("Write 21 800 30 0 0");
		&get_status();
	}
	elsif ($in{query} eq "apply") {
		&apply(\%in);
		&get_status();
	}
	elsif ($in{query} eq "clear") {
		# In case of emergency, remove toxic program files
		system("rm -f /etc/iecengine/*");
		system("/sbin/service iecengine restart 1>/dev/null 2>&1");
		&get_status();
	}
	elsif ($in{query} eq "startlink") {
		if (! exists $in{accesstime}) {
			&send_error("No access time specified");
		}
		if (! exists $in{srcip}) {
			&send_error("No source IP specified");
		}
		if ( 1 ne &checkTime($in{accesstime}) ) {
			&send_error("Invalid access time.");
		}

		if (1 ne &checkIP($in{srcip})) {
			&send_error("Invalid source IP.");
		}
		&start_remotelink( $in{accesstime}, $in{srcip} );
	}
	elsif ($in{query} eq "stoplink") {
		if ( $stratonPID ne "none" ) {
			system("/usr/bin/killall straton-access.pl &>/dev/null");
		}
	}
	elsif ($in{query} eq "unlock") {
		if (! exists $in{code}) {
			&send_error("No unlock code specified");
		}
		&unlock($in{code});
		&get_status();
	}
	elsif ($in{query} eq "generate_snupdate") {
		&snupdate_straton();
	}
	else {
		&send_error("Unrecognized query '$in{query}'");
	}
}
else {
	&send_error("Unrecognized options");
}

&send_response();
