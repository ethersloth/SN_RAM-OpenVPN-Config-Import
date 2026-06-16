#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
#
# 10/31/13  Added verzion
#   bet     Added cell_modem (name)
#  v2.00    Changed output string name
#           Added function for appending string output so format stays consistant
#           Added wireless.sierra.custom parsing
#           Fixed a bug reading wireless.cardstats vars (mispelled file name)
#
# 4/8/14	Fixed incorrect nai output
# bet
# v2.01
#
# 7/21/15  Added CELLMODEM_RADIO_IF
# bet
# v2.02

BEGIN {
       push @INC, "/home/httpd/jbmconfig/bin";
      }

use JBM_System;
use IOG::SKVS;

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"             .
      "Last-Modified: " . gmtime(time()) . " GMT\n"          .
      "Cache-Control: no-store, no-cache, must-revalidate\n" .
      "Cache-Control: post-check=0, pre-check=0\n"           .
      "Pragma: no-cache\n"                                   .
      "Content-type: text/html; charset=utf8\n\n";

my $SYSTEM = JBM_System->new();

my $outputString = "";

my $proc_fc_dir = "/proc/feature_codes";
my $mdn_file = "/var/log/wireless.mdn";
my $cardstats_file = "/var/log/wireless.cardstats";
my $sierra_custom_file = "/var/log/wireless.sierra.custom";

# Get the name of the Cell Modem Signal Stength image file to be displayed:

my $cmcs = 'q';

if (open(FILE, "/var/log/lightbar_decode"))
  {
   $cmcs = <FILE>;

   chomp($cmcs);

   close(FILE);
  }

my $imgFName = "/images/signal" . $cmcs . ".gif";

AppendOutput("cmcsImg", $imgFName);

# Get the RSSI value:


my $hasOMA = "no";
my $HighRssi = "";
my $firmwVer = "";
my $manu     = "";
my $mdn      = "";
my $model    = "";
my $nai      = "";
my $esn      = "";
my $imei     = "";
my $ccid     = "";
my $carrier  = "Unknown";
my $sim_carrier = "Unknown";
my $firm_num = "Unknown";
my $firm_carrier = "Unknown";
my $firm_priver = "Unknown";
my $firm_pkgver = "Unknown";
my $netType  = "UNKN";
my $netType0  = "";
my $netType1  = "";
my $netType2  = "";
my $LowRssi  = "";
my $prlVer   = "";
my $roaming  = "";
my $rssi     = "N/A";
my $sysUptime = "UNKN";
my $sysIdleTime = "UNKN";

my $iptrans_running = 0;
my $iptrans_int = "";
my $iptrans_ip = "";
my $ip_trans_status_file = "/tmp/iptrans.info";
if ( -e "$ip_trans_status_file" )
{
   $iptrans_running = 1;
   $iptrans_ip = `grep "IPTRANS_GATEWAY" $ip_trans_status_file | sed 's/^.*=//' 2>&1`;
   $iptrans_int  = `grep "IPTRANS_INTERNAL_INT" $ip_trans_status_file | sed 's/^.*=//' 2>&1`;
   chomp($iptrans_int);
   chomp($iptrans_ip);
}


my $cell_modem_name = "Unknown";
my $cell_name_file = "/var/log/cell_modem";

if ( -e "$cell_name_file" )
{
   $cell_modem_name = `/bin/cat $cell_name_file 2>/dev/null`;
   chomp($cell_modem_name);
}

AppendOutput("cell_modem", $cell_modem_name);

# Get the Network type, rssi values and roaming flag from /var/log/wireless.cardstats:

my $wireless_uptime = "";
if ( -x "/bin/pppWirelessUptime.pl" )
{
   $wireless_uptime = `/bin/pppWirelessUptime.pl 2>/dev/null`;
   chomp($wireless_uptime);
}

my $uptime;
my $idletime;
( $uptime, $idletime ) = get_Uptime();
my @timeparts = gmtime($uptime);
$sysUptime = sprintf ("%dD %dH %dM %dS",@timeparts[7,2,1,0]);
@timeparts = gmtime($idletime);
$sysIdleTime = sprintf ("%dD %dH %dM %dS",@timeparts[7,2,1,0]);

#$rsltStr .= ":::sysUptime=" . $sysUptime
#         . ":::sysIdleTime=" . $sysIdleTime;

AppendOutput("sysUptime", $sysUptime);
AppendOutput("sysIdleTime", $sysIdleTime);

if (open(FILE, "$cardstats_file"))
  {
   my $line = "";

   while (<FILE>)
        {
         $line = $_;

         chomp($line);

         my ($varName, $varVal) = split(/=/, $line);

         if ("CELLMODEM_RADIO_IF" eq $varName)
           {
               $netType0 = $varVal;
               next;
           }

         if ("CELLMODEM_SERVICE_TYPE" eq $varName)
           {
               $netType1 = $varVal;
               next;
           }

         if ("CELLMODEM_SYSTEM_MODE" eq $varName)
           {
               $netType2 = $varVal;
               next;
           }

         if ("CELLMODEM_CURRENT_RSSI" eq $varName)
           {
            $rssi = $varVal;
            next;
           }


         if ("CELLMODEM_LOWSPEED_RSSI" eq $varName)
           {
            $LowRssi = $varVal;

            next;
           }

         if ("CELLMODEM_HIGHSPEED_RSSI" eq $varName)
           {
            $HighRssi = $varVal;

            next;
           }

         if ("CELLMODEM_ROAMING" eq $varName)
           {
            $roaming = $varVal;

            next;
           }

         #CELLMODEM_MANU is no longer sent or displayed
         #if ("CELLMODEM_MANU" eq $varName)
         #  {
         #   $manu = $varVal;
         #   next;
         #  }

         if ("CELLMODEM_MDN" eq $varName)
           {
            $mdn = $varVal;

            next;
           }


         if ("CELLMODEM_MODEL" eq $varName)
           {
            $model = $varVal;

            next;
           }

         if ("CELLMODEM_OMA_SUPPORTED" eq $varName)
          {
            $hasOMA = $varVal;
            next;
          }

         if ("CELLMODEM_FIRMWARE_V" eq $varName)
           {
            $firmwVer = $varVal;

            next;
           }

         if ("CELLMODEM_PRL_VERSION" eq $varName)
           {
            $prlVer = $varVal;

            next;
           }

         if ("CELLMODEM_NAI" eq $varName)
           {
            $nai = $varVal;

            next;
           }


         if ("CELLMODEM_CARRIER" eq $varName)
           {
            $carrier = $varVal;
            next;
           }

	 if ("CELLMODEM_SIM_CARRIER" eq $varName)
	   {
	    $sim_carrier = $varVal;
	    next;
	   }

	 if ("CELLMODEM_FIRMWARE_NUM" eq $varName)
	   {
	    $firm_num = $varVal;
	    next;
	   }

	 if ("CELLMODEM_FIRMWARE_CARRIER" eq $varName)
	   {
	    $firm_carrier = $varVal;
	    next;
	   }

	 if ("CELLMODEM_FIRMWARE_PRIVER" eq $varName)
	   {
	    $firm_priver = $varVal;
	    next;
	   }

	 if ("CELLMODEM_FIRMWARE_PKGVER" eq $varName)
	   {
	    $firm_pkgver = $varVal;
	    next;
	   }

	 if ("CELLMODEM_SIM_ID" eq $varName)
	   {
	    $ccid = $varVal;
	    next;
	   }

         if ("CELLMODEM_ESN" eq $varName)
           {
            $esn = $varVal;
            next;
           }

         if ("CELLMODEM_IMEI" eq $varName)
           {
            $imei = $varVal;
            next;
           }
        }

   close(FILE);
  }



#if its being decoded, then get that value
if ( $rssi !~ /\-*\d+/ )
{
        my $rssi_file = "/var/log/lightbar_rssi_out";
        if ( -e "$rssi_file" )
        {
                my $tmp_rssi;
                open(RSSI_FILE,"<$rssi_file");
                read(RSSI_FILE, $tmp_rssi, 4);
                close(RSSI_FILE);
                chomp($tmp_rssi);
                $tmp_rssi =~ s/\s+//g;
                if ( $tmp_rssi =~ /\d+/ )
                {
                        $rssi = $tmp_rssi;
                }
        }
}

if ( $mdn !~ /^[0-9]+$/)
{
   if ( -e "$mdn_file" )
   {
      open(THISMDNFILE,"<$mdn_file") or my $error = 1;
      if (! $error)
      {
         read(THISMDNFILE, $mdn, 80);
         close(THISMDNFILE);
      }
   }
}


if ( $netType0 !~ /^\s*$/ && $netType0 !~ /unknown/i )
{
	$netType = $netType0;
}
elsif ( $netType1 !~ /^\s*$/ && $netType1 !~ /unknown/i )
{
	$netType = $netType1;
}
elsif ( $netType2 !~ /^\s*$/ && $netType2 !~ /unknown/i )
{
	$netType = $netType2; 
}

AppendOutput("firmwver", $firmwVer);
AppendOutput("manu", $manu);
AppendOutput("mdn", $mdn);
AppendOutput("model", $model);
AppendOutput("nai", $nai);
AppendOutput("prlver", $prlVer);
AppendOutput("rssi", $rssi);
AppendOutput("roaming", $roaming);
AppendOutput("nettype", $netType);
AppendOutput("carrier", $carrier);
AppendOutput("sim_carrier", $sim_carrier);
AppendOutput("firm_num", $firm_num);
AppendOutput("firm_carrier", $firm_carrier);
AppendOutput("firm_priver", $firm_priver);
AppendOutput("firm_pkgver", $firm_pkgver);
AppendOutput("esn", $esn);
AppendOutput("imei", $imei);
AppendOutput("ccid", $ccid);
AppendOutput("hasOMA", $hasOMA);

# Get the Provisioning status:

my $provStat = "Unavailable";

if (-e "/var/log/wirelessactivation_status")
  {
   if (open(FILE, "/var/log/wirelessactivation_status"))
     {
      $provStat = <FILE>;
      chomp($provStat);
      close(FILE);
     }
  }

AppendOutput("provStat", $provStat);

# Get the Cell Connection status:

my $cellConnStat = "Unavailable";

if (-e "/var/log/wirelessdial_dialing")
  {
   $cellConnStat = "Enabled";
  }

if (-e "/var/log/wirelessdial_notdialing")
  {
   $cellConnStat = "Disabled";
  }

AppendOutput("cellConnStat", $cellConnStat);

# Get the Cell IP Address:

my $cellIP = "";
my $cellInt = "ppp0";
$cellIP = $SYSTEM->GetInterfaceAddress("$cellInt");
if ("" eq $cellIP)
{
   $cellInt = "wwan0";
   $cellIP = $SYSTEM->GetInterfaceAddress("$cellInt");
   if ("" eq $cellIP)
   {
      $cellInt = "N/A";
      $cellIP = "N/A";
   }
}

AppendOutput("cellInt", $cellInt);
AppendOutput("cellIP", $cellIP);
AppendOutput("cellUptime", $wireless_uptime);

# Get the usb Connection State:

my $usbConnState = "Disabled";


system("ifconfig usb0 &> /dev/null");
if ( $? != 0)
{
        $usbConnState = "";
}
else
{
        AppendOutput("usbConnName", "usb");

        if (1 == $SYSTEM->IsInterfaceUp("usb0"))
        {
                $usbConnState = "Enabled";
        }

        AppendOutput("usbConnState", $usbConnState);

        # Get the usb0 IP Address:

        my $usbIPAddr = "";

        $usbIPAddr = $SYSTEM->GetInterfaceAddress("usb0");

        if ("" eq $usbIPAddr)
        {
                $usbIPAddr = "N/A";
        }

        AppendOutput("usbIPAddr", $usbIPAddr);


        # Get the usb Link State:

        my $usbLinkState = "N/A";

        if (open(
                FILE,
                "/sbin/ethtool usb0 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF;}' |")
                )
        {
                $usbLinkState = <FILE>;

                chomp($usbLinkState);
                close(FILE);
        }

        AppendOutput("usbLinkState", $usbLinkState);
} #end if usb exists


# Get the eth0 Connection State:

my $eth0ConnState = "Disabled";

#units should always have an eth0
AppendOutput("eth0ConnName", "eth0");

if (1 == $SYSTEM->IsInterfaceUp("eth0"))
  {
   $eth0ConnState = "Enabled";
  }

AppendOutput("eth0ConnState", $eth0ConnState);

# Get the eth0 IP Address:

my $eth0IPAddr = "";
if ( $iptrans_running && $iptrans_int =~ /^eth0$/)
{
   $eth0IPAddr = $iptrans_ip;
}
else
{
   $eth0IPAddr = $SYSTEM->GetInterfaceAddress("eth0");
}

if ("" eq $eth0IPAddr)
  {
   $eth0IPAddr = "N/A";
  }

AppendOutput("eth0IPAddr", $eth0IPAddr);

# Get the eth0 Link State:

my $eth0LinkState = "";

if ( 1 == IOG::SKVS::get("FC_SWMODE_SEP") )
{
   if (open(
           FILE,
           "/bin/snswrpt -e 0 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF; }' |")
           )
     {
      $eth0LinkState = <FILE>;

      chomp($eth0LinkState);

      close(FILE);
     }
    else
        {
         $eth0LinkState = "N/A";
        }
}
else
{
  if (open(
          FILE,
          "/sbin/ethtool eth0 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF; }' |")
          )
    {
     $eth0LinkState = <FILE>;

     chomp($eth0LinkState);

     close(FILE);
    }
    else
       {
        $eth0LinkState = "N/A";
       }
}

AppendOutput("eth0LinkState", $eth0LinkState);


# Get the eth1 Connection State:

my $eth1ConnState = "Disabled";


system("ifconfig eth1 &> /dev/null");
if ( $? != 0 || 0 == &HaveDseriesEthFC(1) )
{
        $eth1ConnState = "";
}
else
{
        AppendOutput("eth1ConnName", "eth1");

        if (1 == $SYSTEM->IsInterfaceUp("eth1"))
        {
                $eth1ConnState = "Enabled";
        }

        AppendOutput("eth1ConnState", $eth1ConnState);

        # Get the eth1 IP Address:

        my $eth1IPAddr = "";

        if ( $iptrans_running && $iptrans_int =~ /^eth1^/)
        {
            $eth1IPAddr = $iptrans_ip;
        }
        else
        {
            $eth1IPAddr = $SYSTEM->GetInterfaceAddress("eth1");
        }

        if ("" eq $eth1IPAddr)
        {
                $eth1IPAddr = "N/A";
        }

        AppendOutput("eth1IPAddr", $eth1IPAddr);


        # Get the eth1 Link State:

        my $eth1LinkState = "N/A";


        if ( 1 == IOG::SKVS::get("FC_SWMODE_SEP") )
        {
           if (open(
                   FILE,
                   "/bin/snswrpt -e 1 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF;}' |")
                   )
           {
              $eth1LinkState = <FILE>;

              chomp($eth1LinkState);
              close(FILE);
           }

        }
        else
        {
          if (open(
                  FILE,
                  "/sbin/ethtool eth1 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF;}' |")
                  )
          {

                $eth1LinkState = <FILE>;

                chomp($eth1LinkState);
                close(FILE);
          }
        }

        AppendOutput("eth1LinkState", $eth1LinkState);
} #end if eth1 exists



# Get the wifi Connection State:

my $wifiConnState = "Disabled";


system("ifconfig br0 &> /dev/null");
if ( $? != 0)
{
        $wifiConnState = "";
}
else
{
        AppendOutput("wifiConnName", "WiFi");

        if (1 == $SYSTEM->IsInterfaceUp("br0"))
        {
                $wifiConnState = "Enabled";
        }

        AppendOutput("wifiConnState", $wifiConnState);

        # Get the wifi IP Address:

        my $wifiIPAddr = "";

        $wifiIPAddr = $SYSTEM->GetInterfaceAddress("br0");

        if ("" eq $wifiIPAddr)
        {
                $wifiIPAddr = "N/A";
        }

        AppendOutput("wifiIPAddr", $wifiIPAddr);


        # Get the usb Link State:

        my $wifiLinkState = "N/A";

        if (open(
                FILE,
                "/sbin/ethtool br0 | grep Link | awk '{ sub(\"yes\", \"Up\", \$NF); sub(\"no\", \"Down\", \$NF); print \$NF;}' |")
                )
        {
                $wifiLinkState = <FILE>;

                chomp($wifiLinkState);
                close(FILE);
        }

        AppendOutput("wifiLinkState", $wifiLinkState);
} #end if wifi exists


# Get a bunch of crap from /var/log/wireless.cardstats:

if (open(FILE, "$cardstats_file"))
{
     my $line = "";
     my ($var, $data);
     while (<FILE>)
     {
           $line = $_;
           chomp($line);
           next if ( $line =~ /^#/ );
           next if ( $line !~ /.*=.*/ );
           ($var, $data) = split/=/, $line;
           AppendOutput($var, $data);
     }
     close(FILE);
}


if (open(FILE, "$sierra_custom_file"))
{
     my $line = "";
     my ($var, $data);
     my $var_start = "SIERRACUSTOM_";
     while (<FILE>)
     {
           $line = $_;
           chomp($line);
           next if ( $line =~ /^#/ );
           next if ( $line !~ /.*=.*/ );
           ($var, $data) = split/=/, $line;
           AppendOutput("$var_start$var", $data);
     }
     close(FILE);
}

print $outputString . "\n";


exit(0);

sub HaveDseriesEthFC()
{
        my $eth_num = shift;

        if ( 0 == $eth_num )
        {
                `ifconfig eth0 &> /dev/null`;
                if ( 0 == $? )
                {
                        return 1;
                }
        }
        else
        {
           #are we on a Dseries?
           `ls $proc_fc_dir/eth0_single_marvel_88e6061 &> /dev/null`;
           if ( 0 == $? )
           {
                   `ls $proc_fc_dir/eth$eth_num* &> /dev/null`;
                   if ( 0 == $? )
                   {
                           return 1;
                   }
           }
           else
           {
                   #we are on some other unit, BT, Cclass, etc, so just check ifconfig
                   `ifconfig eth$eth_num &> /dev/null`;
                   if ( 0 == $? )
                   {
                           return 1;
                   }
           }
        }

        return 0;
}


sub get_Uptime()
{

   #uptime looks like this:
   #19:45:19 up 4 days,  7:12, load average: 0.00, 0.00, 0.00
   #my @output = `$uptime_cmd`;
   #chomp($output[0]);
   #$output[0] =~ /\d+:\d+:\d+\s+up\s+(\d+)\s+days\,\s+(\d+):(\d+)\,.*/;
   #return "$1 day(s), $2 hours, $3 minutes";

   my $uptime_file = "/proc/uptime";
   my $ut = "0";
   my $tmp = "";

   if ( -e $uptime_file )
   {
      #cat /proc/uptime
      #374780.66 374606.41
      open(UPTIME,"$uptime_file") or return $ut;
      $/ = undef;
      $tmp = <UPTIME>;
      $/ = "\n";
      close (UPTIME);

      chomp($tmp);
      @num = split /\s+/,$tmp;
     
   }

   #uptime is in $num[0]
   #total idle time is in $num[1]
   return @num;

}

sub AppendOutput()
{
   my $var_name = $_[0];
   my $var_data = $_[1];
   my $start = ":::";
   if ( ! $outputString)
   {
      #if empty, first entry does not get a $start
      $start = "";
   }

   $outputString .= "$start$var_name=$var_data";
}

