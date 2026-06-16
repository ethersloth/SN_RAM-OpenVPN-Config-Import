#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.
#
# Written by Brian Tuchten
# 1/21/08
#
#  No part of this program may be reproduced, stored in a retrieval system or transmitted, in any form
#  or by any means, including but not limited to electronic, mechanical, photocopying, recording, or otherwise, without the
#  express prior written consent of Red Lion Controls.
#
# 3/10/08   bet   added a check to make sure the CSQ command wasn't blank
# v1.03
#
# 3/11/08  bet    re-enabled the updating of the modem/carrier to the XML config
# v1.04
#
# 1/9/09   bet    Restores jbminit.conf from the backup zip if it is less than 10 lines (normally over 40 lines)
# v1.09           No longer overwrites jbminit.conf when it has an error reading the contents
#                 Adds PPP holdoff fields to jbminit.conf if missing or commented, used to just replace
#
# 1/15/09  bet   Added speedpref variable witten to hookfile
# v1.10
#
# 3/31/09  bet   Verizon holdoff fix.  Added better logic to detect a Verizon carrier
# v1.11
# v1.12
# v1.13
# v1.14 - Added option "saveonly" which will update stub files, but not dial
# v1.15 - get default card information again incase card reports real carrier
# v1.16 - Don't use carrier default APN anymore, unless "usedefault" is set from the GAU config file
# v1.17 - Always update speed pref even if  save_only is set
# v1.18 - if wireless.cardstats carrier is =~ unknown, then set carrier to generic_cdma or generic_gsm
# v1.19 - Don't change XML carrier if "custom"
# v1.20 - Added detectedcarrer writing into config.xml
# v1.21 - Added reading MIP mode from config.xml, add ppp option receive-all if set to sip
# v1.21 - Fixed logic when checking for carrier "custom" from !~ to =~
# v1.23 - rxidle defaults to 0 instead of 150
# v1.24 - run setisp again if there was an error returned from it
# v1.25 - set prl region supported list and write to chat file
# v1.26 - rxidle defaults back to 150 instead of 0
# v1.27 - If G_GAU_CONFIG_FILE{CM_CARRIER} matches exactly "verizon, then holdoff, so we can not force verizongloballte
# v1.28 - Added a check for carrier bellmobility, and append _cdma or _gsm to the end for the GAU
# v1.29 - Added a check for carrier "generic cdma"
# v1.30 - Added a check for other carriers to get shoved into "detected carrier" (like Cellcom)
# v1.31 - Added in setting DEFAULT_APN and DEFAULT_CONTEXT for gsm modems if PPP config file modem
#         is none, carrier is none, APN is 1, and context is empty.
# v1.32 - Upped TIMEOUT 5 to TIMEOUT 20 for AT command errors.
# v1.33 - Don't write PPP files or run setisp if DCARD_NOPPP=yes
# v1.34 - Only Verizon uses holdoff, no longer try to lock to a detected card
# v1.35 - No longer set holdoff in jbminit.conf.  This is now handled by the backend
# v1.36 - 8/22/14 - Don't write/set ppp if wwan option is on and available
# v1.37 - 9/25/14 - missed commits
#         Pay attention to temporary dial/nodial override files
#         Bug fixes, missing xpeval path, no longer set detectedcarrier which is no longer
#         set by the gau cellular.prf
# v1.38 - 9/26/14 - Don't write/setup jbminit.conf if g_use_ppp_dialer=0
# v1.39 - rxidle defaults to 0 instead of 150
# v1.40 - use xfglib.pl instead of infinity gau system calls
# v1.41 - Bug fix whitespace CM_USE_WWAN_INT, allowing MC8705 to use wwan0
# v1.42 - Enable cellmodem 'no' or 'off' option

#program version
my $prog_version = "1.42";

#
# Exit codes :
#
# 8: unsupported card
#
#

my $jbm_lib = "/etc/jbm/jbm_lib.pl";
if ( ! -e "$jbm_lib" )
{
   print "Missing JBM Perl library, cannot run";
   exit(1);
}
else
{
   require "$jbm_lib";
}

my $jbm_xmllib = "/etc/jbm/xfglib.pl";
if ( -e "$jbm_xmllib" )
{
        require "$jbm_xmllib";
}
else
{
        print "ERROR: Missing $jbm_xmllib\n";
}

require "/etc/env2/env2.pl" || die "$@";



my $prog_name = &RealName;
&syslog("$prog_name v$prog_version starting");

#write our pid file so we don't run twice
&write_pid();


#where default card config files are located.  Also this becomes
#a list of supported cards.
my $g_card_configs_dir = "/etc/jbm/wireless/defaults";
my $g_card_gau_config_file = "/etc/jbm/wireless/cellmodem_ppp.conf";
my $g_cellmodem_speedpref_file = "/etc/jbm/wireless/cellmodem_speedpref";
my $g_cardstats_file    = "/var/log/wireless.cardstats";
my $g_esn_file          = "/var/log/wireless.serialno";
my $g_mdn_file          = "/var/log/wireless.mdn";
my $g_jbminit_conf_file = "/etc/jbm/jbminit.conf";
my $g_cell_modem_file   = "/var/log/cell_modem";
my $ppp_peers_dir       = "/etc/ppp/peers";

my $wwan_interface = "wwan0";

#default on
my $g_use_ppp_dialer = 1;

my $wireless_name = "wireless";

#for updating the new GAU v3 config.xml file
my $program_xpeval    = "/home/httpd/jbmconfig/bin/xpeval";
my $program_getcfgsec = "/home/httpd/jbmconfig/bin/getcfgsec";
my $xml_config_file   = "/home/httpd/jbmconfig/conf/config.xml";

my $g_cell_modem = "";
my @GSM_REGION_SUPPORTED_LIST = ("sierraMC8790", "sierraMC8795");
my %g_region_hash =
    (
        0 => 'Default mode',
        1 => 'Europe',
        2 => 'North America',
        3 => 'Australia',
        4 => 'Japan'
    );

my $save_only = 0;
my $debug_level = 0;
chomp @ARGV;
foreach(@ARGV)
{
   chomp;
   if ( $_ =~ /\-[d|D]$/)
   {
      $debug_level++;
   }
   if ( $_ =~ /saveonly/)
   {
      $save_only = 1;
      &syslog("saveonly option set");
   }
}

my $g_enable_dial_holdoff = 0;
my $g_default_baud_rate = 115200;
my $g_default_rxidle = 0;
my $g_default_dod_timeout = 600;
my $g_default_mdn = "1234567890";
my $g_current_mdn = $g_default_mdn;
my $default_cdma_dialstring = "ATD#777";
my $default_gsm_dialstring = "ATD*99***1#";
my $g_dialstring2use = "";
my $g_ppp_username ="test";
my $g_ppp_password ="test";
my $g_ppp_apn = "";


my %xml_settings = ();

#hash to hold defaults for the inserted card
my %G_THISCARD_DEFAULTS = {};

#hash to hold the config values from the main config file
my %G_GAU_CONFIG_FILE = {};
my $p_gau_config_file = \%G_GAU_CONFIG_FILE; #pointer to the data

#global cardstats hash
my %G_CARDSTATS_FILE = {};

#global carrier default config hash
my %G_CARRIER_DEFAULTS = {};


#########################
### Begin Main ##########
#########################

#Read the inserted card default config file
&ReadDefaultCardFile();

#Check if we have a supported GSM module to set a region for later
my $g_can_set_modem_region = &CheckSupportedGsmRegionSupport();

#Read the GAU config file if it is there
&ReadGauConfigFile();

#Read the wireless.cardstats file
&GetCardstatsInfo();


#get the default carrier, username, passwd, apn
&GetCarrierDefaults()

#Try to determin the real Network Provider, which will
#overwrite any network provider in the GAU config hash
#Also the MDN, and ESN/IMEI if available.
#must be called after GetCarrierDefaults()
&DetermineCardInformation();

#get carrier info again in case the  card can report the REAL carrier
&GetCarrierDefaults()

#Get information out of the carrier config file
&DetermineDialstring();

#get the username/passwd
&DetermineUsernamePasswordAPN()

#Enable dial holdoff if needed
&DetermineDialHoldoff();

#create the PPP wireless and wireless.chat
&CreatePPPFiles();


#write the speedpref file if it changed
#used to be in if ! save_only below, but taken out 5/11/10
#so it happens all the time
&WriteSpeedprefFile();



#write the xml in one shot
if ( %xml_settings )
{
   &syslog("Applying xml configuration");
   &xfg_set_multi_attribute("cellular", \%xml_settings);
   $ret = &xfg_commit("cfgonly");
   if ( 0 != $ret)
   {
      &syslog("ERROR: xfg_apply() gave error $ret");
   }
}

#no need to update these if save_only is used.
#only needed to update the GAU files
if ( ! $save_only )
{
   #write values to jbminit
   &UpdateJBMinit();

   #run setisp wireless
   &RunSetisp();
}

&syslog("done");

unlink("/var/run/$prog_name.pid");
exit(0);

#########################
### End Main ############
#########################

sub RunSetisp()
{

   if ( 0 == $g_use_ppp_dialer ) 
   {
      &syslog("This modem doesn't use PPP to dial.  Not running setisp");
      return;
   }

   my $g_cell_dial_on_override_file = "/tmp/force_cell_con";
   my $g_cell_dial_off_override_file = "/tmp/force_cell_nocon";
   my $l_start_dialing = 1;

   #'no' or 'off'
   if ( $G_GAU_CONFIG_FILE{CM_ENABLE_INTERFACE} =~ /^[n|o]/i || -e $ENV2_FLAG_MODEM_TEMPOFF )
   {
      $l_start_dialing = 0;
   }
   #override
   if ( -e "$g_cell_dial_on_override_file" )
   {
      $l_start_dialing = 1;
   }
   elsif ( -e "$g_cell_dial_off_override_file" )
   {
      $l_start_dialing = 0;
   }


   if ( 0 == $l_start_dialing )
   {
      &syslog("Interface disabled in config file, running unsetisp $wireless_name");
      system("unsetisp $wireless_name &> /dev/null");
   }
   else
   {
      if ( ! $save_only )
      {
         system("setisp $wireless_name &> /dev/null");
         my $ret = $?;
         if ( $ret != 0 )
         {
            &syslog("setisp exited with code $ret, running again");
            #run it again
            system("setisp $wireless_name &> /dev/null");
         }
      }
      else
      {
         &syslog("saveonly option set, not runing setisp...");
      }
   }
}


sub UpdateJBMinit()
{

   &debug_msg("Function: UpdateJBMinit()");

   if ( 0 == $g_use_ppp_dialer )
   {
      &syslog("This modem doesn't use PPP to dial.  Leaving jbminit.conf");
      return;
   }

   &syslog("reading $g_jbminit_conf_file");
   my $jbminit_contents = &read_file($g_jbminit_conf_file);
   my $holdoff_line_option;
   my $holdoff_line_timeout;
   my $new_contents;

 #ppp_holdoff_enable=no
 #ppp_holdoff_timeout=4

   &syslog("PPP holdoff is disabled in jbminit");
   $holdoff_line_option = "ppp_holdoff_enable=no";

   $holdoff_line_timeout = "ppp_holdoff_timeout=$g_enable_dial_holdoff";

   #count the lines, in case jbminit.conf is empty.  Less than 5 lines
   if ( -1 != $jbminit_contents )
   {
      my @tmp_contents = split /\n/, $jbminit_contents;
      if ( 10 > @tmp_contents )
      {
         &syslog("WARNING: jbminit.conf less than 10 lines");
         my $orig_config_zip = "/etc/jbm/recovery/firstboot/original_configs.zip";
         if ( -e $orig_config_zip )
         {
            #something is wrong, restore the original jbminit.conf
            #this format is correct, the files are stored with no leading / (fwd slash)
            &syslog("WARNING: restoring original jbminit.conf");
            unlink("$g_jbminit_conf_file");
            my $cmd = "unzip -o $orig_config_zip etc/jbm/jbminit.conf -d /";
            system("$cmd &> /dev/null");

            if ( 0 == $? )
            {
               &syslog("WARNING: original jbminit.conf restored");
               #now read the file again, if we can't read it, it's ok
               &syslog("Re-reading $g_jbminit_conf_file");
               $jbminit_contents = &read_file($g_jbminit_conf_file);
            }
            else
            {
               &syslog("ERROR: unable to restore original jbminit.conf");
            }
         }
         else
         {
            &syslog("ERROR: unable to restore original jbminit.conf, original config zip file missing");
         }
      }
   }


   if ( -1 != $jbminit_contents )
   {
      #we got file content
      my @orig_contents = split /\n/, $jbminit_contents;

      my $found_holdoff_enable_line = 0;
      my $found_holdoff_timeout_line = 0;

      foreach (@orig_contents)
      {
         chomp;
         if ( $_ =~ /^ppp_holdoff_enable/ )
         {
            $new_contents .= "$holdoff_line_option\n";
            $found_holdoff_enable_line = 1;
            next;
         }
         if ( $_ =~ /^ppp_holdoff_timeout/ )
         {
            $new_contents .= "$holdoff_line_timeout\n";
            $found_holdoff_timeout_line = 1;
            next;
         }

         $new_contents .= "$_\n";

      }

      if ( ! $found_holdoff_timeout_line)
      {
         $new_contents = "$holdoff_line_timeout\n$new_contents"
      }
      if ( ! $found_holdoff_enable_line)
      {
         $new_contents = "$holdoff_line_option\n$new_contents"
      }


      &syslog("writing $g_jbminit_conf_file");
      open(FH,">$g_jbminit_conf_file");
      print FH $new_contents;
      close(FH);
   }
   else
   {
      #jbminit.conf was missing?
      &syslog("WARNING: Cannot Open $g_jbminit_conf_file for reading");
   }


}

sub CreatePPPFiles()
{

   if ( 0 == $g_use_ppp_dialer ) 
   {
      &syslog("This modem doesn't use PPP to dial.  Not setting up PPP files");
      return;
   }

   &debug_msg("Function: CreatePPPFiles()");

   $ppp_peers_file =  "#file automatically generated\n";
   $ppp_peers_file .= "#do not modify\n";
   $ppp_peers_file .= "nodetach\n";

   if ( &option_on($G_GAU_CONFIG_FILE{CM_USE_DOD}) )
   {
      $ppp_peers_file .= "demand\n";
      $ppp_peers_file .= "nopersist\n"; #must be after demand
      $ppp_peers_file .= "idle $G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}\n";
   }


   #default route by default
   if ( ! &is_empty($G_GAU_CONFIG_FILE{CM_DEFAULTROUTE}) )
   {
      if ( &option_on($G_GAU_CONFIG_FILE{CM_DEFAULTROUTE}))
      {
         $ppp_peers_file .= "defaultroute\n";
      }
      else
      {
         $ppp_peers_file .= "nodefaultroute\n";
      }
   }
   else
   {
      $ppp_peers_file .= "defaultroute\n";
   }


   #default to on
   if ( ! &is_empty($G_GAU_CONFIG_FILE{CM_USE_DNS}) )
   {
      if ( &option_on($G_GAU_CONFIG_FILE{CM_USE_DNS}) )
      {
         $ppp_peers_file .= "usepeerdns\n";
      }
   }
   else
   {
      $ppp_peers_file .= "usepeerdns\n";
   }


   $ppp_peers_file .= "lock\n";
   $ppp_peers_file .= "novj\n";
   $ppp_peers_file .= "debug\n";
   $ppp_peers_file .= "linkname $wireless_name\n";
   #wireless PPP is ALWAYS ppp0 (unit 0)
   $ppp_peers_file .= "unit 0\n";

   #verizon mandates we refuse pap
   if ( $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /verizon/i )
   {
      $ppp_peers_file .= "refuse-pap\n";
   }

   $ppp_peers_file .= "rxidle $G_GAU_CONFIG_FILE{CM_RXIDLE}\n";
   $ppp_peers_file .= "$G_THISCARD_DEFAULTS{DCARD_BAUDRATE}\n";
   $ppp_peers_file .= "$G_THISCARD_DEFAULTS{DCARD_DEVHANDLE}\n";
   $ppp_peers_file .= "user \"$g_ppp_username\"\n";
   $ppp_peers_file .= "hide-password\n";
   $ppp_peers_file .= "password \"$g_ppp_password\"\n";

   foreach (@{$p_gau_config_file->{CM_CUSTOM_PPP}})
   {
      chomp;
      next if ( &is_empty($_));
      next if ( $_ =~ /detach/ );
      $ppp_peers_file .= "$_\n";

   }

   my $mip_mode = &GetCfgMipMode();
   chomp($mip_mode);
   if ( $mip_mode eq "sip" )
   {
      &syslog("Wireless modem is set to use SIP (MIP off).  Added PPP option \"receive-all\"");
      $ppp_peers_file .= "receive-all\n";
   }

   $ppp_peers_file .= "connect '/bin/chat -v -t3 -f /etc/ppp/peers/$wireless_name.chat'\n";

   #$ppp_peers_file .= "disconnect '/bin/chat -v -t3 -f /etc/ppp/peers/$wireless_name.chat-disconnect'\n";
   #my $ppp_chatdisconnect_file = "#file automatically generated\n";
   #$ppp_chatdisconnect_file .= "#do not modify\n";
   #$ppp_chatdisconnect_file .= "'' AT\n";
   #$ppp_chatdisconnect_file .= "OK \\d+++\\d\\c\n";
   #$ppp_chatdisconnect_file .= "OK ATH0\n";


   #chat stuff

   my $ppp_chat_file =  "#file automatically generated\n";
   $ppp_chat_file .= "#do not modify\n";

   #timeout 5
   $ppp_chat_file .= "TIMEOUT 20\n";

   #wait for '' send AT
   $ppp_chat_file .= "'' AT\nOK ";

   #wait for OK, send the CSQ command if we have one
   #It might be left out of the default config files eventually
   # and become depricated due to back channel sig support
   if ( ! &is_empty($G_THISCARD_DEFAULTS{DCARD_CSQ}) )
   {
      $ppp_chat_file .= "$G_THISCARD_DEFAULTS{DCARD_CSQ}\nOK ";
   }

   #if we can set the GSM modem region, and we are told to, then do it
   if ( $g_can_set_modem_region )
   {
      my $region_number = int($G_GAU_CONFIG_FILE{CM_RF_RADIO_REGION});
      if ( $region_number >= 0 && $region_number <=4 )
      {
         $ppp_chat_file .= "AT!ENTERCND=\"A710\"\nOK ";
         $ppp_chat_file .= "AT!CUSTOM=\"PRLREGION\",$region_number\nOK ";
         &syslog("Setting PRLREGION to $region_number ($g_region_hash{$region_number})");
      }
      else
      {
         &syslog("PRLREGION number \"$region_number\" is invalid, ignoring.");
      }
   }


   #wait for OK, send the APN setting if needed
   #if the APN was "usedefault" then g_ppp_apn should be empty
   if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "gsm" )
   {

      #add the registration line
      if ( $G_THISCARD_DEFAULTS{DCARD_CGREG} =~ /^[0-2]$/)
      {
         $ppp_chat_file .= "AT+CGREG=$G_THISCARD_DEFAULTS{DCARD_CGREG}\nOK ";
      }

      if ( ! &is_empty($g_ppp_apn) )
      {
         $ppp_chat_file .= "AT+CGDCONT=$G_GAU_CONFIG_FILE{CM_CONTEXT},\"IP\",\"$g_ppp_apn\"\nOK ";
      }
   }

   #now grab customer AT commands
   foreach (@{$p_gau_config_file->{CM_CUSTOM_AT}})
   {
      chomp;
      my ($cmd, $expect) = split /::/, $_;
      $ppp_chat_file .= "$cmd\n$expect ";
   }

   $ppp_chat_file .= "$g_dialstring2use\n";
   $ppp_chat_file .= "TIMEOUT 60\n";
   $ppp_chat_file .= "CONNECT ''\n";


   #file contents complete.

   #TODO: Now check to see if they should be rereitten (if they are different)

   open(FH,">$ppp_peers_dir/$wireless_name");
   print FH $ppp_peers_file;
   close(FH);
   open(FH,">$ppp_peers_dir/$wireless_name.chat");
   print FH $ppp_chat_file;
   close(FH);

   #open(FH,">$ppp_peers_dir/$wireless_name.chat-disconnect");
   #print FH $ppp_chatdisconnect_file;
   #close(FH);

}

sub ReadGauConfigFile()
{
   &debug_msg("Function: ReadGauConfigFile()");

   #load defaults from file into %G_GAU_CONFIG_FILE
   if ( ! &check_file("$g_card_gau_config_file") )
   {
      #nothing to read
      return;
   }
   else
   {
      &debug_msg("reading GAU config file $g_card_gau_config_file");
      %G_GAU_CONFIG_FILE = &read_config("$g_card_gau_config_file");

      $G_GAU_CONFIG_FILE{CM_CARDNAME}             =~ s/\s/_/g; #replace spaces with _
      $G_GAU_CONFIG_FILE{CM_ENABLE_INTERFACE}     =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_CARRIER}              =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_DIALSTRING}           =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_USERNAME}             =~ s/[\s|\"]//g; #remove whitepsace and quotes
      $G_GAU_CONFIG_FILE{CM_PASSWORD}             =~ s/[\s|\"]//g; #remove whitepsace and quotes
      $G_GAU_CONFIG_FILE{CM_DEFAULTROUTE}         =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_USE_DOD}              =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}          =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_RXIDLE}               =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_DATA_SPEED}           =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_CONTEXT}              =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_APN}                  =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_USE_DNS}              =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_RF_RADIO_REGION}      =~ s/\s//g;
      $G_GAU_CONFIG_FILE{CM_USE_WWAN_INT}         =~ s/\s//g;

      #arrays will be accessed like this, checked below if needed
      #@{$p_gau_config_file->{CM_CUSTOM_AT}}
      #@{$p_gau_config_file->{CM_CUSTOM_PPP}}

   }

   #################
   #Sanity checking
   #################

   #also check if the wwan option is turned on AND the wwan0 interface is available
   if ( $G_GAU_CONFIG_FILE{CM_USE_WWAN_INT} =~ /y/i )
   {
      system("ifconfig $wwan_interface &>/dev/null");
      if ( 0 == $? )
      {
         syslog("Use WWAN virtual interface is on and available, not setting up PPP");
         $g_use_ppp_dialer = 0;
      }
   }

   #If it looks like the config is in it's defaqult state, and we have a default card APN and Context, use that instead.
   if ( $G_GAU_CONFIG_FILE{CM_CARDNAME} =~ /none/ && $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /none/ )
   {
      if ( ! is_empty($G_THISCARD_DEFAULTS{DCARD_DEFAULT_APN}) && ! is_empty($G_THISCARD_DEFAULTS{DCARD_DEFAULT_CONTEXT}))
      {
         my $l_group = "$G_THISCARD_DEFAULTS{DCARD_DEFAULT_CONTEXT}/$G_THISCARD_DEFAULTS{DCARD_DEFAULT_APN}";
         syslog("CM_CARDNAME and CM_CARRIER are 'none', using default Context/APN $l_group");
         $G_GAU_CONFIG_FILE{CM_CONTEXT} = $G_THISCARD_DEFAULTS{DCARD_DEFAULT_CONTEXT};
         $G_GAU_CONFIG_FILE{CM_APN} = $G_THISCARD_DEFAULTS{DCARD_DEFAULT_APN};
      }
   }


   #default context to 1 if invalid, won't matter for CDMA
   if ( int($G_GAU_CONFIG_FILE{CM_CONTEXT}) > 5 || int($G_GAU_CONFIG_FILE{CM_CONTEXT}) < 1 )
   {
      $G_GAU_CONFIG_FILE{CM_CONTEXT} = "1";
   }

   if ( &is_empty($G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}) )
   {
      $G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT} = $g_default_dod_timeout;
   }

   if ( int($G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}) < 30 && 0 != int($G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}))
   {
      $G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT} = 600;
   }

   if ( &is_empty($G_GAU_CONFIG_FILE{CM_RXIDLE}) )
   {
      $G_GAU_CONFIG_FILE{CM_RXIDLE} = $g_default_rxidle;
   }
   else
   {
      $G_GAU_CONFIG_FILE{CM_RXIDLE} = int($G_GAU_CONFIG_FILE{CM_RXIDLE});
   }

   if ($debug_level)
   {
      &debug_msg("CM_CARDNAME=$G_GAU_CONFIG_FILE{CM_CARDNAME}");
      &debug_msg("CM_ENABLE_INTERFACE=$G_GAU_CONFIG_FILE{CM_ENABLE_INTERFACE}");
      &debug_msg("CM_CARRIER=$G_GAU_CONFIG_FILE{CM_CARRIER}");
      &debug_msg("CM_DIALSTRING=$G_GAU_CONFIG_FILE{CM_DIALSTRING}");
      &debug_msg("CM_USERNAME=$G_GAU_CONFIG_FILE{CM_USERNAME}");
      &debug_msg("CM_PASSWORD=$G_GAU_CONFIG_FILE{CM_PASSWORD}");
      &debug_msg("CM_USE_DOD=$G_GAU_CONFIG_FILE{CM_USE_DOD}");
      &debug_msg("CM_DOD_TIMEOUT=$G_GAU_CONFIG_FILE{CM_DOD_TIMEOUT}");
      &debug_msg("CM_DEFAULTROUTE=$G_GAU_CONFIG_FILE{CM_DEFAULTROUTE}");
      &debug_msg("CM_RXIDLE=$G_GAU_CONFIG_FILE{CM_RXIDLE}");
      &debug_msg("CM_DATA_SPEED=$G_GAU_CONFIG_FILE{CM_DATA_SPEED}");
      &debug_msg("CM_CONTEXT=$G_GAU_CONFIG_FILE{CM_CONTEXT}");
      &debug_msg("CM_APN=$G_GAU_CONFIG_FILE{CM_APN}");
      &debug_msg("CM_USE_DNS=$G_GAU_CONFIG_FILE{CM_USE_DNS}");
      &debug_msg("CM_USE_WWAN_INT=$G_GAU_CONFIG_FILE{CM_USE_WWAN_INT}");

   }


   #try to verify custom AT commands COMMNAD::EXPECT format
   my @custom_at_commands = ();
   foreach (@{$p_gau_config_file->{CM_CUSTOM_AT}})
   {
      chomp $_;
      my ($at_command, $at_expect) = split /::/, $_;
      $at_command =~ s/\s//g;
      $at_expect =~ s/\s//g;
      if ( &is_empty($at_command) )
      {
         &debug_msg("AT Command is empty, skipping");
         next;
      }
      if ( &is_empty($at_expect) )
      {
         &debug_msg("AT Command is \"$at_command\", but EXPECT string is empty, skipping");
         next;
      }

      &debug_msg("Using AT::EXPECT value $at_command\:\:$at_expect");
      push(@custom_at_commands,"$at_command\:\:$at_expect");
   }
   @{$p_gau_config_file->{CM_CUSTOM_AT}} = @custom_at_commands;


}


sub CheckSupportedGsmRegionSupport()
{
   foreach my $modem(@GSM_REGION_SUPPORTED_LIST)
   {
      chomp($modem);
      if ( $g_cell_modem eq $modem )
      {
         return 1;
      }
   }

   return 0;
}

sub ReadDefaultCardFile()
{
   &debug_msg("Function: ReadDefaultCardFile()");

   my $cell_modem;

   if (  &check_file("$g_cell_modem_file") )
   {
      open(FH,"<$g_cell_modem_file");
      read(FH,$cell_modem,50);
      close(FH);
      chomp($cell_modem);

      if ( &is_empty($cell_modem) )
      {
         #this is the only place that should exit with an 8, which is needed
         #for the calling script ok2dial to reset PCMCIA or whatever
         #if there is no card inserted, and the GAU calls this script, then we will just exit
         #with no harm done
         &syslog("$g_cell_modem_file is empty, cannot determine inserted card");
         exit(8);
      }

      #convert white space to nothing since some cards will be called "GC82 PC CARD"
      #and the config file would be GC82PCCARD.conf
      $cell_modem =~ s/\s//g;
      $cell_modem =~ s/[^A-Za-z0-9_]//g;

      &syslog("Inserted card is \"$cell_modem\"");
   }
   else
   {
      &syslog("$g_cell_modem_file missing, cannot determine inserted card");
      exit(8);
   }

   #load defaults from file into %G_THISCARD_DEFAULTS
   if ( !&check_file("$g_card_configs_dir/$cell_modem.conf") )
   {
      &syslog("cannot locate support file for card \"$cell_modem\", unsupported card?");
      exit(1);
   }
   else
   {
      #we have a local supported card, so update the GAU config.xml file
      &xmlUpdateCellModem($cell_modem);

      &debug_msg("reading $g_card_configs_dir/$cell_modem.conf");
      %G_THISCARD_DEFAULTS = &read_config("$g_card_configs_dir/$cell_modem.conf");
      $G_THISCARD_DEFAULTS{DCARD_CARRIER}         =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE}     =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_DEVHANDLE}       =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_DIALSTRING}      =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_CSQ}             =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_BAUDRATE}        =  int($G_THISCARD_DEFAULTS{DCARD_BAUDRATE});
      $G_THISCARD_DEFAULTS{DCARD_CGREG}           =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_DEFAULT_CONTEXT} =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_DEFAULT_APN}     =~ s/\s//g;
      $G_THISCARD_DEFAULTS{DCARD_NOPPP}           =~ s/\s//g;

      if ( &option_on($G_THISCARD_DEFAULTS{DCARD_NOPPP}) ) 
      {
         $g_use_ppp_dialer = 0;
      }

      #we are setting this value for later
      $G_THISCARD_DEFAULTS{DCARD_CARDNAME} = $cell_modem;

      if ( 0 == $G_THISCARD_DEFAULTS{DCARD_BAUDRATE} )
      {
         &syslog("DCARD_BAUDRATE missing from $cell_modem.conf, defaulting to $g_default_baud_rate");
         $G_THISCARD_DEFAULTS{DCARD_BAUDRATE} = $g_default_baud_rate;
      }

      if ( $debug_level)
      {
         &debug_msg("DCARD_CARRIER=$G_THISCARD_DEFAULTS{DCARD_CARRIER}");
         &debug_msg("DCARD_NETWORKTYPE=$G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE}");
         &debug_msg("DCARD_DEVHANDLE=$G_THISCARD_DEFAULTS{DCARD_DEVHANDLE}");
         &debug_msg("DCARD_DIALSTRING=$G_THISCARD_DEFAULTS{DCARD_DIALSTRING}");
         &debug_msg("DCARD_CSQ=$G_THISCARD_DEFAULTS{DCARD_CSQ}");
         &debug_msg("DCARD_BAUDRATE=$G_THISCARD_DEFAULTS{DCARD_BAUDRATE}");
         &debug_msg("DCARD_CGREG=$G_THISCARD_DEFAULTS{DCARD_CGREG}");
         &debug_msg("DCARD_DEFAULT_CONTEXT=$G_THISCARD_DEFAULTS{DCARD_DEFAULT_CONTEXT}");
         &debug_msg("DCARD_DEFAULT_APN=$G_THISCARD_DEFAULTS{DCARD_DEFAULT_APN}");
      }

   }

   $g_cell_modem = $cell_modem;

   #TODO: Add in some sanity checking

}

sub GetCfgMipMode()
{
   if ( -x "$program_getcfgsec" )
   {
        #check to see if it is already set
        #/home/httpd/jbmconfig/bin/getcfgsec --infile=/home/httpd/jbmconfig/conf/config.xml  --xpath=/GAUCfg/cellular/carrier
        my $cmd = "$program_getcfgsec --infile=$xml_config_file --xpath=/GAUCfg/provisioning/common/mipmode";
        &debug_msg("running command \"$cmd\"");
        my $output = `$cmd 2>&1`;
        chomp($output);
        &debug_msg("MIP mode value from config.xml is \"$output\"");
        #this will return something like <mipmode>pref</mipmode>
        return "pref" if ( $output =~ /\>pref\</i);
        return "only" if ( $output =~ /\>only\</i);
        return "sip" if ( $output =~ /\>sip\</i);
        return "";
   }
}

sub xmlUpdateCellCarrier()
{
   my $carrier = $_[0];
   chomp($carrier);
   #we have a local supported card, so update the GAU config.xml file
   # is the program to update the GAU config.xml file available?
    # is the config.xml file available?
   if ( -f "$xml_config_file" )
   {
      my $update_file = 1;

      if ( -x "$program_xpeval" )
      {
           #check to see if it is already set
           my $cmd = "$program_xpeval -s --in=$xml_config_file --xpath='/GAUCfg/cellular/carrier/text()'";
           &debug_msg("running command \"$cmd\"");
           my @output = `$cmd 2>&1`;
           foreach my $line(@output)
           {
                chomp($line);
                if ( $line =~ m/$carrier/ )
                {
                   $update_file = 0;
                   last;
                }
           }
      }

      if ( $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /custom/i )
      {
         &syslog("Carrier name is \"Custom\", no update needed");
      }
      elsif ( 1 == $update_file )
      {
         $xml_settings{"carrier"} = "$carrier"; 
         &syslog("Current carrier is not \"$carrier\", will update XML config file to carrier \"$carrier\"");
      }
      else
      {
         &syslog("Carrier name \"$carrier\" already matches config.xml, no update needed");
      }

   }
   else
   {
      &syslog("Warning: $xml_config_file is missing, cannot update XML config file");
   }

}

sub xmlUpdateCellModem()
{
   my $cell_modem = $_[0];
   chomp($cell_modem);
   if ( -f "$xml_config_file" )
   {
     my $update_file = 1;
     if ( -x "$program_xpeval" )
     {
          #check to see if it is already set
          my $cmd = "$program_xpeval -s --in=$xml_config_file --xpath=/GAUCfg/cellular/modem";
          &debug_msg("running command \"$cmd\"");
          my @output = `$cmd 2>&1`;
          foreach my $line(@output)
          {
               chomp($line);
               if ( $line =~ m/$cell_modem/ )
               {
                  $update_file = 0;
                  last;
               }
          }
     }

     if (1 == $update_file )
     {
        &syslog("Will update  XML config with Modem name $cell_modem");
        $xml_settings{"modem"} = "$cell_modem";
     }
     else
     {
        &syslog("Modem name $cell_modem already matches config.xml, no update needed");
     }
   }
   else
   {
      &syslog("Warning: $xml_config_file is missing, cannot update XML config file");
   }
}

sub GetCarrierDefaults()
{
   &debug_msg("Function: GetCarrierDefaults()");

   my $file = "";


   #by now, the $G_GAU_CONFIG_FILE{CM_CARRIER} has already been modified if needed

   #check to see if a GSM carrier has been selected, but a CDMA card is inserted, so we don't use
   #the default username/password from the wrong carrier
   my $tmp_carrier_file = "$g_card_configs_dir/carrier_$G_GAU_CONFIG_FILE{CM_CARRIER}.conf";

   &debug_msg("tmp_carrier_file = $tmp_carrier_file");

   if ( &check_file("$tmp_carrier_file") )
   {
      my %TMP_CARRIER_INFO = &read_config("$tmp_carrier_file");

      $TMP_CARRIER_INFO{DCARRIER_NETWORKTYPE} =~ s/\s//g;

      if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} ne $TMP_CARRIER_INFO{DCARRIER_NETWORKTYPE} )
      {
         &syslog("Notice: Defined carrier $G_GAU_CONFIG_FILE{CM_CARRIER} is type $TMP_CARRIER_INFO{DCARRIER_NETWORKTYPE}, but card type is $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE}");
         &syslog("Notice: Setting carrier to card default carrier \"$G_THISCARD_DEFAULTS{DCARD_CARRIER}\"");
         $G_GAU_CONFIG_FILE{CM_CARRIER} = $G_THISCARD_DEFAULTS{DCARD_CARRIER};

         #we have a local supported card, so update the GAU config.xml file
         if ( -f "$xml_config_file" )
         {
            my $update_file = 1;
            if ( -x "$program_xpeval" )
            {
                 #check to see if it is already set
                 my $cmd = "$program_xpeval -s --in=$xml_config_file --xpath='/GAUCfg/cellular/carrier/text()'";
                 &debug_msg("running command \"$cmd\"");
                 my @output = `$cmd 2>&1`;
                 my $tmp_carrier = $G_GAU_CONFIG_FILE{CM_CARRIER};
                 foreach my $line(@output)
                 {
                      chomp($line);
                      if ( $line =~ m/$tmp_carrier/ )
                      {
                         $update_file = 0;
                         last;
                      }
                 }
            }

            if ( 1 == $update_file )
            {

               &syslog("Will update XML config with Modem Default Carrier $G_GAU_CONFIG_FILE{CM_CARRIER}");
               $xml_settings{"carrier"} = "$G_GAU_CONFIG_FILE{CM_CARRIER}";
            }
            else
            {
               &syslog("Carrier name \"$G_GAU_CONFIG_FILE{CM_CARRIER}\" already matches config.xml, no update needed");
            }

         }
         else
         {
            &syslog("Warning: $xml_config_file is missing, cannot update XML config file");
         }
      }
   }


   if ( &check_file("$g_card_configs_dir/carrier_$G_GAU_CONFIG_FILE{CM_CARRIER}.conf") )
   {
      $file = "$g_card_configs_dir/carrier_$G_GAU_CONFIG_FILE{CM_CARRIER}.conf";
   }
   elsif ( ! &is_empty($G_THISCARD_DEFAULTS{DCARD_CARRIER}) )
   {
      if ( &check_file("$g_card_configs_dir/carrier_$G_THISCARD_DEFAULTS{DCARD_CARRIER}.conf") )
      {
         $file = "$g_card_configs_dir/carrier_$G_THISCARD_DEFAULTS{DCARD_CARRIER}.conf";
      }
   }
   else
   {
      &syslog("Error: No carrier is set and inserted card config has no default carrier, exiting.");
      exit(7);
   }

   &debug_msg("reading $file");
   %G_CARRIER_DEFAULTS = &read_config("$file");
   $G_CARRIER_DEFAULTS{DCARRIER_PROVIDER}    =~ s/\s//g;
   $G_CARRIER_DEFAULTS{DCARRIER_NETWORKTYPE} =~ s/\s//g;
   $G_CARRIER_DEFAULTS{DCARRIER_USERNAME}    =~ s/\s//g;
   $G_CARRIER_DEFAULTS{DCARRIER_PASSWORD}    =~ s/\s//g;
   $G_CARRIER_DEFAULTS{DCARRIER_APN}         =~ s/\s//g;

   if ( $debug_level)
   {
      &debug_msg("DCARRIER_PROVIDER=$G_CARRIER_DEFAULTS{DCARRIER_PROVIDER}");
      &debug_msg("DCARRIER_NETWORKTYPE=$G_CARRIER_DEFAULTS{DCARRIER_NETWORKTYPE}");
      &debug_msg("DCARRIER_USERNAME=$G_CARRIER_DEFAULTS{DCARRIER_USERNAME}");
      &debug_msg("DCARRIER_PASSWORD=$G_CARRIER_DEFAULTS{DCARRIER_PASSWORD}");
      &debug_msg("DCARRIER_APN=$G_CARRIER_DEFAULTS{DCARRIER_APN}");
   }


   if ( ! &is_empty($G_CARDSTATS_FILE{CELLMODEM_CARRIER}) )
   {
      #if we get a real carrier from the back channel file, then force it into the GAU.
      #but only if the GAU isn't get to "custom"
      if ( $G_GAU_CONFIG_FILE{CM_CARRIER} !~ /custom/i )
      {
         $G_GAU_CONFIG_FILE{CM_CARRIER} = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
         &syslog("Cardstats file says carrier is \"$G_GAU_CONFIG_FILE{CM_CARRIER}\", setting it in config.xml");
         #we have a local supported ca.rd, so update the GAU config.xml file
         &xmlUpdateCellCarrier($G_GAU_CONFIG_FILE{CM_CARRIER});
      }
   }

   #this will only be set to "none" if the GAU write the config file and no carrier was selected
   if ( $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /^none$/i )
   {
      $G_GAU_CONFIG_FILE{CM_CARRIER} = $G_CARRIER_DEFAULTS{DCARRIER_PROVIDER};
      &syslog("Carrier currently set to \"none\", reverting to card default carrier \"$G_CARRIER_DEFAULTS{DCARRIER_PROVIDER}\"");
      #we have a local supported card, so update the GAU config.xml file
      &xmlUpdateCellCarrier($G_GAU_CONFIG_FILE{CM_CARRIER});
   }

}

sub GetCardstatsInfo()
{
      &debug_msg("Function: GetCardstatsInfo()");

     #read in the file info
     %G_CARDSTATS_FILE = &read_config("$g_cardstats_file");

     #at this point, we only care about the CARRIER in cardstats

     #Fix up the CARDSTATS_CARRIER, get rid of all non letters
     $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ s/[^a-zA-Z]//g;
     #make it lowercase
     $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = lc($G_CARDSTATS_FILE{CELLMODEM_CARRIER});

     if ( &is_empty($G_CARDSTATS_FILE{CELLMODEM_CARRIER}))
     {
        &syslog("No Carrier read from CARDSTATS");
        return;
     }

     #used to write detected carrer into config.xml with supported provisioning carriers
     my $l_real_carrier = "";

     #now massage the entry so we match what the GAU expects, and what the default carrier config files are named
     if ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /verizon/i )
     {

        #special case
        if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "gsm" ) 
        {
           $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "verizongloballte";
        }
        else
        {
           $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "verizon";
        }

        #incase it is named "verizonwireless"
        $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};

     }
     elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /sprint/i )
     {
        $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "sprint";
        $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
     }
     elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /us/i &&  $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /cellular/i )
     {
        $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "uscellular";
        $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
     }
     elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /bellmobility/i )
     {
        #bell movility can be cdma or gsm
        if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "cdma" )
        {
           &syslog("Modem is CDMA, adding _cdma to end of carrier name");
           $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "bellmobility_cdma";
           $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
        }
        elsif ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "gsm" )
        {
           &syslog("Modem is GMS, adding _gsm to end of carrier name");
           $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "bellmobility_gsm";
           $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
        }
        else
        {
           #this shouldn't ever hit
           $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "bellmobility";
           $l_real_carrier = $G_CARDSTATS_FILE{CELLMODEM_CARRIER};
        }
     }
     elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /generic/i && $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /cdma/i )
     {
        $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = "generic_cdma";
        $l_real_carrier = "generic_cdma";
     }
     elsif ( ! &is_empty($G_CARDSTATS_FILE{CELLMODEM_CARRIER}) )
     {
        $l_real_carrier = lc($G_CARDSTATS_FILE{CELLMODEM_CARRIER});
     }
     else
     {
        #clear real carrier
        $l_real_carrier = "none";
     }

     &syslog("Carrier read from CARDSTATS is \"$G_CARDSTATS_FILE{CELLMODEM_CARRIER}\"");

     if ( $l_real_carrier )
     {
        &syslog("Will update XML config with detected carrier \"$l_real_carrier\"");
        $xml_settings{"detectedcarrier"} = "$l_real_carrier";
     }

}

sub DetermineUsernamePasswordAPN()
{

   &debug_msg("Function: DetermineUsernamePasswordAPN()");

   #get the username
   if ( ! &is_empty($G_GAU_CONFIG_FILE{CM_USERNAME}))
   {
      $g_ppp_username = $G_GAU_CONFIG_FILE{CM_USERNAME};
   }
   elsif ( ! &is_empty($G_CARRIER_DEFAULTS{DCARRIER_USERNAME}) )
   {
      $g_ppp_username = $G_CARRIER_DEFAULTS{DCARRIER_USERNAME};
   }

   #replace xMDNx with the actual MDN if needed
   if ( $g_ppp_username =~ /xMDNx/ )
   {
      $g_ppp_username =~ s/xMDNx/$g_current_mdn/m;

   }

   #get the password
   if ( ! &is_empty($G_GAU_CONFIG_FILE{CM_PASSWORD}))
   {
      $g_ppp_password = $G_GAU_CONFIG_FILE{CM_PASSWORD};
   }
   elsif ( ! &is_empty($G_CARRIER_DEFAULTS{DCARRIER_PASSWORD}) )
   {
      $g_ppp_password = $G_CARRIER_DEFAULTS{DCARRIER_PASSWORD};
   }

   if ( $g_ppp_password =~ /xMDNx/ )
   {
      $g_ppp_password =~ s/xMDNx/$g_current_mdn/m;

   }


   #get the APN if the card type is GSM
   if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "gsm" )
   {
      if ( ! &is_empty($G_GAU_CONFIG_FILE{CM_APN}))
      {
         if ( $G_GAU_CONFIG_FILE{CM_APN} =~ /usedefault/i )
         {
            $g_ppp_apn = $G_CARRIER_DEFAULTS{DCARRIER_APN};
         }
         else
         {
            $g_ppp_apn = $G_GAU_CONFIG_FILE{CM_APN};
         }
      }
      #No longer use the default APN.
      #elsif ( ! &is_empty($G_CARRIER_DEFAULTS{DCARRIER_APN}) )
      #{
      #   $g_ppp_apn = $G_CARRIER_DEFAULTS{DCARRIER_APN};
      #}
   }


}



sub DetermineDialstring()
{

   &debug_msg("Function: DetermineDialstring()");

   if ( &is_empty($G_GAU_CONFIG_FILE{CM_DIALSTRING}) )
   {
      if ( &is_empty($G_THISCARD_DEFAULTS{DCARD_DIALSTRING}) )
      {
         &syslog("Warning: card $G_THISCARD_DEFAULTS{DCARD_CARDNAME} has no default carrier, and no dial string is configured");
         if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "gsm" )
         {
            $g_dialstring2use = $default_gsm_dialstring;
            &syslog("using default GSM dialstring $default_gsm_dialstring");
         }
         elsif ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "cdma" )
         {
            $g_dialstring2use = $default_cdma_dialstring;
            &syslog("using default CDMA dialstring $default_cdma_dialstring");
         }
         else
         {
            &syslog("Error: Cannot determine DCARD_NETWORKTYPE for $G_THISCARD_DEFAULTS{DCARD_CARDNAME}, exiting");
            exit(4);
         }
      }
      else
      {

         $g_dialstring2use = $G_THISCARD_DEFAULTS{DCARD_DIALSTRING};
         $g_dialstring2use =~ s/xCONTEXTx/$G_GAU_CONFIG_FILE{CM_CONTEXT}/m;

      }
   }
   else
   {
      $g_dialstring2use = $G_GAU_CONFIG_FILE{CM_DIALSTRING};
   }

   &debug_msg("Dialstring2use=$g_dialstring2use");


}

sub DetermineCardInformation()
{
   &debug_msg("Function: DetermineCardInformation()");

   &debug_msg("G_CARDSTATS_FILE{CELLMODEM_CARRIER}=$G_CARDSTATS_FILE{CELLMODEM_CARRIER}");

   if ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /verizon/i )
   {
      &syslog("** Cardstats reports carrer \"$G_CARDSTATS_FILE{CELLMODEM_CARRIER}\", enabling holdoff");
      $G_GAU_CONFIG_FILE{CM_CARRIER} = "verizon";
      #$g_enable_dial_holdoff = 15;
   }
   elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /sprint/i )
   {
      &syslog("** Cardstats reports carrer \"$G_CARDSTATS_FILE{CELLMODEM_CARRIER}\"");
      $G_GAU_CONFIG_FILE{CM_CARRIER} = "sprint";
   }
   elsif ( $G_CARDSTATS_FILE{CELLMODEM_CARRIER} =~ /unknown/i )
   {
      #$G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE}
      if ( $G_THISCARD_DEFAULTS{DCARD_NETWORKTYPE} eq "cdma" )
      {
         $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = $G_GAU_CONFIG_FILE{CM_CARRIER} = "generic_cdma";
      }
      else
      {
         #its GSM
         $G_CARDSTATS_FILE{CELLMODEM_CARRIER} = $G_GAU_CONFIG_FILE{CM_CARRIER} = "generic_gsm";
      }

   }
   else
   {
      #but ignore verizonglobal and verizongloballte
      if ( $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /^verizon$/i )
      {
         &syslog("** GAU config cell carrier (or card default) is set to \"$G_GAU_CONFIG_FILE{CM_CARRIER}\", enabling holdoff");
         $G_GAU_CONFIG_FILE{CM_CARRIER} = "verizon";
         #$g_enable_dial_holdoff = 15;
      }
      else
      {
         if ( $G_GAU_CONFIG_FILE{CM_CARRIER} =~ /none/i && $G_CARRIER_DEFAULTS{DCARRIER_PROVIDER} =~ /verizon/i )
         {
            &syslog("** Unconfigured carrier, card's default carrier is Verizon, enabling holdoff.");
            $G_GAU_CONFIG_FILE{CM_CARRIER} = "verizon";
            #$g_enable_dial_holdoff = 15;
         }
      }
   }


   if ( $G_CARDSTATS_FILE{CELLMODEM_MDN} =~ /^[0-9]+$/ )
   {
      $g_current_mdn = $G_CARDSTATS_FILE{CELLMODEM_MDN};
   }
   elsif ( &check_file($g_mdn_file) )
   {
      my $tmp_mdn;
      open(THIS_MDN, "<$g_mdn_file");
      my $chars_read = read(THIS_MDN,$tmp_mdn,20);
      close(THIS_MDN);
      chomp($tmp_mdn);
      $tmp_mdn =~ s/[^0-9]//g;
      &debug_msg("read \"$tmp_mdn\" from $g_mdn_file");
      if ( $tmp_mdn =~ /^([0-9]+)$/ )
      {
         $g_current_mdn = $1;
      }
   }
}

sub WriteSpeedprefFile()
{
   #TODO: reset the modulecard if it changed?
   open(FH,">$g_cellmodem_speedpref_file");
   print FH "$G_GAU_CONFIG_FILE{CM_DATA_SPEED}";
   close(FH);
}

#Holdoff now controlled by backend programs
sub DetermineDialHoldoff()
{
   &debug_msg("Function: DetermineDialHoldoff()");
   $g_enable_dial_holdoff = 0;
}


sub debug_msg()
{
   return if ($debug_level < 1);
   my $msg = $_[0];
   chomp($msg);
   &syslog("DEBUG$debug_level: $_[0]");
}

#returns 1 if a variable is set to yes, on, or 1
sub option_on()
{
   my $option = $_[0];
   $option =~ s/\s//g;
   return 1 if ( $option =~ /^yes$/i ||
                 $option =~ /^y$/i ||
                 $option =~ /^on$/i ||
                 $option =~ /^true$/i ||
                 1 == $option );
   return 0;
}


