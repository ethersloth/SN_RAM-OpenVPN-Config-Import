#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require '/etc/jbm/jbm_lib.pl';
my $version = "1.02";

# Global settings
my $conf_file = "/etc/jbm/wifi.conf";
my $hostapd_conf_filename = "/etc/hostapd/hostapd.conf";
my $restart_service = 1;
my $DEBUG_LEVEL = 0;

### ARGUMENT PROCESSING ###
foreach(@ARGV)
{
    chomp;
    $restart_service = 0 if ( $_ =~ /\-no-service/ );
}

### BEGIN MAIN PROGRAM ###
&syslog( "v$version starting" );

if( not $restart_service )
{
    &syslog( "NOTE: not activating changes since we got -no-service option" );
}

my $config_data_ref = &read_jbm_conf_file( $conf_file );
if( not defined $config_data_ref )
{
    print "Couldn't open config file: $conf_file, exiting.\n";
    exit 1;
}

if( &is_option_enabled( $config_data_ref->{'ENABLE'} ) )
{
    # we are enabled
    # TODO: sanity check/required values
    # TODO: write info for bridge intf somewhere?
    #print "ON!\n";
    my $hostapd_conf_text = &generate_hostapd_conf( $config_data_ref );
    if( 0 < $DEBUG_LEVEL )
    {
        print "hostapd.conf contents:\n";
        print $hostapd_conf_text;
    }
    &syslog( "Writing hostapd.conf to $hostapd_conf_filename" );
    my $result  = &write_hostapd_conf( $hostapd_conf_text );
    
    &syslog( "Enabling wifi service to start at boot time" );
    system( "chkconfig wifi on" );
    
    &syslog( "Restarting wifi service to reload settings" ) if( $restart_service );
    system( "service wifi restart" ) if( $restart_service );
}
elsif( &is_option_disabled( $config_data_ref->{'ENABLE'} ) )
{
    # we are disabled
    # TODO: chkconfig wifi off
    # TODO: get rid of bridge
    #print "OFF!\n";
    
    &syslog( "Disabling wifi service to at boot time" );
    system( "chkconfig wifi off" );
    
    &syslog( "Stopping wifi service if running" ) if( $restart_service );
    system( "service wifi stop" ) if( $restart_service );
    
    &syslog( "Cleaning up any remaining wifi network components" );
    system( "ifconfig br0 down &> /dev/null" );
    system( "brctl delif br0 eth1 &> /dev/null" );
}
else
{
    print "ERROR: unrecognized option for ENABLE: $config_data_ref->{'ENABLE'}\n";
    exit 2;
}

if( `ps aux` =~ m/dhcpd/ )
{
    system( "service dhcpd restart" );
}

&syslog( "Configuration update complete!" );
exit;

### BEGIN SUBROUTINES ###

sub read_jbm_conf_file
{
    my ( $config_filename ) = @_;
    if( not defined $config_filename )
    {
        print "ERROR: read_jbm_conf_file called without argument for config file name\n";
        return;
    }

    if( ! -e "$config_filename" )
    {
        print "ERROR: couldn't find config file: $config_filename\n";
        return;
    }

    print "\nReading config from: $config_filename\n\n"
        if( 0 < $DEBUG_LEVEL );

    my %config_data = ();
    $config_data_ref = \%config_data;
    %config_data = &read_config( "$config_filename" );

    if( 0 < $DEBUG_LEVEL )
    {
        for my $key ( keys %{$config_data_ref} )
        {
            print "$key = $config_data_ref->{$key}\n";
        }
    }
    return $config_data_ref if( defined $config_data_ref );
    return;
}

# Returns 1 if a variable is set to yes, y, on, true, or 1
sub is_option_enabled()
{
   my $option = $_[0];
   return 0 if not $option;
   return 1 if ( $option =~ /^yes$/i ||
                 $option =~ /^y$/i  ||
                 $option =~ /^on$/i ||
                 $option =~ /^true$/i ||
                 $option =~ /^enabled?$/i ||
                 1 eq $option );
   return 0;
}

# Returns 1 if a variable is st to no, n, off, false, or 0
sub is_option_disabled()
{
   my $option = $_[0];
   return 0 if not $option;
   return 1 if ( $option =~ /^no$/i ||
                 $option =~ /^n$/i  ||
                 $option =~ /^off$/i ||
                 $option =~ /^false$/i ||
                 $option =~ /^disabled?$/i ||
                 0 eq $option );
   return 0;
}

sub generate_hostapd_conf
{
    my ( $config_hash_ref ) = @_;
    if( not defined $config_hash_ref )
    {
        print "ERROR: generate_hostapd_conf called without argument for config hash\n";
        return;
    }
       
    my $hostapd_conf = "";

    my $ssid = $config_hash_ref->{'SSID'};
    my $presharedkey = $config_hash_ref->{'PRESHAREDKEY'};
    my $encryption_mode = $config_hash_ref->{'ENCRYPTION'};
    my $ssid = $config_hash_ref->{'SSID'};
    
    my $ssid_broadcast_bits;
    if( &is_option_disabled( $config_hash_ref->{'SSIDBROADCAST'}) )
    {
        # 1 is empty SSID field
        # 2 is nulled SSID field (but may be needed by some clients?)
        $ssid_broadcast_bits = 2;
    }
    else
    {
        $ssid_broadcast_bits = 0;
    }

    my $wpa_bits = 0;

    # TODO: Turn on/off wpa/wpa2 as configured
    # 0 = off, 1 = wpa1, 2 = wpa2, 3 = wpa + wpa2
    #if( $encryption_mode ... )
    if( "wpa" eq $encryption_mode ) {
    	$wpa_bits = 1;
    }
    elsif( "wpa2" eq $encryption_mode ) {
    	$wpa_bits = 2;
    }
    elsif( "wpawpa2" eq $encryption_mode ) {
    	$wpa_bits = 3;
    }

    $hostapd_conf .= "# Warning: This file automatically generated by the GAU backend!\n";
    $hostapd_conf .= "interface=ath0\n";
    $hostapd_conf .= "bridge=br0\n";
    $hostapd_conf .= "driver=madwifi\n";
    $hostapd_conf .= "debug=2\n";
    $hostapd_conf .= "ssid=$ssid\n";
    $hostapd_conf .= "ignore_broadcast_ssid=$ssid_broadcast_bits\n";
    $hostapd_conf .= "auth_algs=1\n";
    $hostapd_conf .= "wpa=$wpa_bits\n";
    $hostapd_conf .= "wpa_passphrase=$presharedkey\n";
    $hostapd_conf .= "wpa_key_mgmt=WPA-PSK\n";
    $hostapd_conf .= "wpa_pairwise=TKIP CCMP\n";

    return $hostapd_conf;
}

sub write_hostapd_conf
{
    my ( $hostapd_text ) = @_;

    if( not defined $hostapd_text or $hostapd_text =~ /^\s*$/m )
    {
        print "ERROR: write_hostapd_conf called without valid argument for file contents\n";
        return;
    }

    open my $hostapd_conf_fh, '>', "$hostapd_conf_filename"
        or die "Couldn't open $hostapd_conf_filename for writing";

    print $hostapd_conf_fh $hostapd_text;

    close my $hostap_conf_fh;

    return 1;
}
