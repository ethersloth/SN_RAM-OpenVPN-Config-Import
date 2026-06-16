#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

# getstat3 - next-generation replacement for getstatii
#
# In support of modularity, this script actually loses many fields to other cgi.
# E.g. ifconfig and cardstats

use IOG::CGI;
use IOG::SKVS;
require "./jsonlib.pl";
require "/etc/env2/env2.pl";

my $features_file = "/etc/iog/model_features";

my %RESPONSE = (
    error => 0,
    stats => {}
);

sub chomp_file {
    my $filename = shift;
    my $content = "";
    local $/ = undef;
    open (RF, $filename) or return $content;
    $content = <RF>;
    close(RF);
    $content =~ s/\r?\n$//; # chomp
    return $content;
}

sub send_response {
    &IOG::CGI::sendJson(\%RESPONSE);
    exit;
}

sub send_error {
    my $message = shift;
    $RESPONSE{error} = 1;
    $RESPONSE{message} = $message;
    &send_response();
}

# cell_modem
$RESPONSE{stats}{cell_modem} = &chomp_file("/var/log/cell_modem");

# cellmodem_cpin
$RESPONSE{stats}{cellmodem_cpin} = &chomp_file("/etc/jbm/wireless/cellmodem_cpin");

# lightbar_decode
$RESPONSE{stats}{lightbar_decode} = &chomp_file("/var/log/lightbar_decode");

# link_usb0 (state)
$RESPONSE{stats}{link_usb0} = &chomp_file("/sys/class/net/usb0/operstate");

# link_eth0 (state)
$RESPONSE{stats}{link_eth0} = &chomp_file("/sys/class/net/eth0/operstate");

# link_eth1 (state)
$RESPONSE{stats}{link_eth1} = &chomp_file("/sys/class/net/eth1/operstate");

# release
$RESPONSE{stats}{release} = &chomp_file( $ENV{ENV2_FLAG_RELEASE} );

# uptime_seconds
(my $proc_uptime, my $proc_idletime) = split(/\s+/, &chomp_file("/proc/uptime"));
$RESPONSE{stats}{uptime_seconds} = $proc_uptime;

# wireless_uptime
$RESPONSE{stats}{wireless_uptime} = `/bin/pppWirelessUptime.pl 2>/dev/null`;
chomp $RESPONSE{stats}{wireless_uptime};

# wirelessactivation_status
$RESPONSE{stats}{wirelessactivation_status} = &chomp_file("/var/log/wirelessactivation_status");

# wirelessdial
if (-e "/var/log/wirelessdial_dialing") {
    $RESPONSE{stats}{wirelessdial} = "dialing";
}
elsif (-e "/var/log/wirelessdial_notdialing") {
    $RESPONSE{stats}{wirelessdial} = "notdialing";
}
else {
    $RESPONSE{stats}{wirelessdial} = "unavailable";
}

$RESPONSE{stats}{cpu} = IOG::SKVS::get("FC_CPU_NAME");
$RESPONSE{stats}{cpuid} = IOG::SKVS::get("FC_CPU_ID");
$RESPONSE{stats}{model} = IOG::SKVS::get("FC_MODELNO");
$RESPONSE{stats}{numeth} = IOG::SKVS::get("FC_NUM_ETH");
$RESPONSE{stats}{serial} = IOG::SKVS::get("FC_SERIALNO");

# It's cheaper to get these config.xml attributes here than using cfgfetch
if (open my $cfh, "head -5 /home/httpd/jbmconfig/conf/config.xml | grep \"<GAUCfg\" |") {
	my $gaucfg = <$cfh>;
	close($cfh);
	if ($gaucfg =~ /firmware="([^"]+)"/) {
		$RESPONSE{stats}{firmware} = $1;
	}
}

&send_response();
