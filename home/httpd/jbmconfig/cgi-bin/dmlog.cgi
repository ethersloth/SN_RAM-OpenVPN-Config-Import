#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo
# and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company
# and product names are trademarks of their respective owners.

require "./config.cgi";


my $g_diag_running = 0;
my $g_logfile_present = 0;
my $g_filterfile_present = 0;

my $g_module = "MC5727";

my $g_filterfile = "/tmp/filter.sqf";
my $g_logfile = "/tmp/SwiDiagOutput0.ldk";
my $g_alt_logfile = "/media/sdcard/SwiDiagOutput0.ldk";
my $g_dm_log_maxed_file = "/tmp/maxDMlog";

my $g_swidiag_name = "SwiDiagnosticJBM";
my $g_swisdk_name = "swisdk";

my $g_errors = "";
my $g_atcmd_support = 0;

my $use_new_qmi = 0;
my $g_device = "";

my $ret = 0;

my $sd_card_logging = 0;
if ( -e "$g_alt_logfile" )
{
    $g_logfile = $g_alt_logfile;
    $sd_card_logging = 1;
}

#must be done before anything
&GetModuleInfo();

if (&ReadParse(\%parse, \%cgi_cfn,\%cgi_ct,\%cgi_sfn))
{

   if ($parse{'DownloadLog'})
   {
      &DownloadLog();
   }
   elsif ($parse{'StartDiag'})
   {
      &StartDiag();
   }
   elsif ($parse{'StopDiag'})
   {
      &StopDiag();
   }
   elsif ($parse{'UploadFilter'})
   {
      &UploadFilter();
   }

}


&html_start();
&DisplayDiagTable();
&html_end;
exit();

sub GetModuleInfo()
{
   #check for MC7|8xx
   $output = `/bin/grep -i 'Product=MC[7|8]' /proc/bus/usb/devices 2>/dev/null`;
   chomp($output);
   #print "$output\n";
   if ( $output =~ m/Product=(MC\d+)/i  )
   {
      $g_module = "$1";
      $use_new_qmi = 1;
      $g_swidiag_name = "rl_dmcapture.sh";

      if ( $output =~ m/^.*Product=MC73.*$/i  )
      {
         #MC73xx uses USB0
         $g_device = "/dev/ttyUSB0";
         $g_atcmd_support = 1;
      }
      elsif ( $output =~ m/^.*Product=MC77.*$/i  )
      {
         #MC7700 uses USB1
         $g_device = "/dev/ttyUSB1";
         $g_atcmd_support = 1;
      }
      elsif ( $output =~ m/^.*Product=MC87.*$/i  )
      {
         #MC87xx use USB1 also?
         $g_device = "/dev/ttyUSB1";
         $g_atcmd_support = 1;
      }
      else
      {
         print "Unsupported module\n";
         exit();
      }
   }

}

sub DisplayDiagTable
{

   my $spacing = "&nbsp;&nbsp;&nbsp;";
   my $present = "<font color=green>present</font>$spacing";
   my $notpresent = "<font color=red>not present</font>$spacing";
   my $running = "<font color=green>running</font>$spacing";
   my $notrunning = "<font color=red>not running</font>$spacing";
   my $sdcard_msg = "";

   &GetDiagStatus();

   my $l_html_filter_info          = $notpresent;
   my $l_html_log_info             = $notpresent;
   my $l_html_diag_running_info    = $notrunning;

   my $atcmd_box = "";
   if ( $g_atcmd_support )
   {
       $atcmd_box = "<br /><label><input type=checkbox name=autobox1 id=autobox1 checked> Auto stop/start connection</label>\n";
   }


   if ( -e "$g_dm_log_maxed_file" )
   {
      &html_error("Diag log size is maxed.  Logging has stopped.");
   }

   if ( $g_filterfile_present )
   {
      $l_html_filter_info = $present;
      if ( ! $g_diag_running )
      {
         $l_html_diag_running_info .= "<input name=StartDiag type=submit value=Start>\n";
         $l_html_diag_running_info .= "$atcmd_box";


         $l_html_filter_info .= "<input type=file name=upfile size=20>";
         $l_html_filter_info .= "<input name=UploadFilter type=submit value=Upload>\n";
      }
      else
      {
         $l_html_filter_info .= "(stop diag to upload new filter)";
      }
   }
   else
   {
      $l_html_filter_info .= "<input type=file name=upfile size=20>";
      $l_html_filter_info .= "<input name=UploadFilter type=submit value=Upload>\n";

      if ( ! $g_diag_running )
      {
         $l_html_diag_running_info .= "(upload new filter to allow starting)";
      }
   }


   if ( -e $g_logfile )
   {
      if ( $sd_card_logging )
      {
         $sdcard_msg = "<br /><font color=red>(Logging to SD Card.  Stop before removing)</font>";
      }
      my @logstat = stat("$g_logfile");
      $l_html_log_info = "$present ($logstat[7] bytes)$spacing";
      if ( ! $g_diag_running )
      {
         $l_html_log_info .= "<input name=DownloadLog type=submit value=\"Download Log\">\n";
         if ( $sd_card_logging )
         {
            $sdcard_msg = "<br /><font color=red>(Log saved on SD Card)</font>";
         }
      }
      else
      {
         $l_html_log_info .= "(stop diag to download log file)";
      }
   }

   if ( $g_diag_running )
   {
      $l_html_diag_running_info = $running;
      $l_html_diag_running_info .= "<input name=StopDiag type=submit value=Stop>\n";
   }


print <<DIAGINFO;

<div align="center"><h2>Sierra $g_module Diagnostic Status</h2></div>
   <center>
   <form method='POST' action=><input name=noaction type=submit value="Refresh Page"></form>
   <br><font size=+1>$g_errors</font>
   </center>
   <br>

   <table align="center" width="60%" border="1" cellpadding=2>

      <tr align="center">
         <td>Diagnostic process</td>
         <form method='POST' action=>
         <td align=left>$l_html_diag_running_info</td>
         </form>
      </tr>

      <tr align="center">
         <td>Filter file</td>
         <form method='POST' enctype='multipart/form-data' action=>
         <td align=left>$l_html_filter_info</td>
         </form>
      </tr>

      <tr align="center">
         <td>Diag log file</td>
         <form method='POST' action=>
         <td align=left>$l_html_log_info $sdcard_msg</td>
         </form>
      </tr>
      <tr>
      <td colspan=2>
      <pre>
Notes:

1. Starting the diag proccess will remove the current log file.
2. Uploading a filter will replace the existing filter.
3. The filter must be in the proper format.
4. Starting removes any previous DM log
      </pre>
      </td>
      </tr>
   </table>

DIAGINFO

}

sub StartDiag()
{

   #remove log file before starting

   if ( $g_diag_running )
   {
      &html_error("Diag already running, stop it first.");
      return;
   }

   if ( ! -e "$g_filterfile" )
   {
      &html_error("Upload a filter file before starting.");
      return;
   }

   &StopDiag();
   unlink($g_dm_log_maxed_file);
   unlink($g_logfile);

   my $ret = 0;
   my $at_cmd_in = "/tmp/at_cmd_in";
   my $at_cmd_out = "/tmp/at_cmd_out";

   if ( $use_new_qmi )
   {

      #stop the connection
      #radio off
      #sleep 3
      #start diag
      #radio on
      #sleep 3
      #start connection
      if ($parse{'autobox1'} )
      {
            system("cellmodemconnect.pl nocon &>/dev/null");
            sleep(3);
            unlink($at_cmd_out);
            system("echo 'AT+CFUN=0' > $at_cmd_in");
            sleep(3);
      }

      my $cmd = "/sbin/$g_swidiag_name -f $g_filterfile -d $g_device &> /dev/null &";
      system("$cmd");
      sleep(3);

      if ($parse{'autobox1'} )
      {
            system("echo 'AT+CFUN=1' > $at_cmd_in");
            sleep(3);
            system("cellmodemconnect.pl clear &>/dev/null");
      }

   }
   else
   {
      $ret = system("/sbin/$g_swidiag_name -v -p /sbin/$g_swisdk_name -t 5000 -i $g_filterfile &> /dev/null");
   }

   if ( 0 != $ret)
   {
      if ( 2 == $ret || 512 == $ret)
      {
         &html_error("Download filter is an invalid format.");
         $g_diag_running = 0;
         return;
      }
      if ( 1 == $ret || 256 == $ret )
      {
         &html_error("Sierra interface error.  Please try starting diag again.");
         $g_diag_running = 0;
         return;
      }



      &html_error("Unknown error.  Return code $ret");
      $g_diag_running = 0;
      return;

   }
   sleep(3);

}

sub StopDiag()
{
   #just kill the process
   system("/usr/bin/killall $g_swidiag_name &> /dev/null");
   if ( $use_new_qmi )
   {
      #uses "cat" to get the raw infrom from dev/ttyUSBn
      system("/usr/bin/killall cat &> /dev/null");
   }
   sleep(5);
   $g_diag_running = 0;
}

sub DownloadLog()
{
   my $date .= `/bin/date +%d%h%y-%H%M 2>/dev/null`;
   chomp($date);
   my $file_date = "_$date";
   if ( $g_diag_running )
   {
      &html_error("Diag is running, stop it before downloading the log file.");
      return;
   }

   if ( !open(FILE,"$g_logfile"))
   {
      &html_error("ERROR: Unable to open file for download.");
      return;
   }

   print "Content-type: application/octet-stream\n";
   print "Content-Disposition: attachment; filename=SierraDiagLogfile$file_date\.ldk\n\n";
   $| = 1;
   while (<FILE>)
   {
      print;
   }
   close(FILE);
   exit;
}

sub html_error()
{
   $g_errors .= "<font color=red>$_[0]</font>"
}

sub UploadFilter()
{
   $cgi_lib::maxdata = 1024 * 100; #100k max
   #my $tmpname;
   #($tmpname = $cgi_cfn{'upfile'}) =~ s/^.*\\//g;
   #my $newname = "$cgi_lib'writefiles/$tmpname";
   #print "NAME: $cgi_cfn{'upfile'} $newname";

   #remove any boa-temp.* files in /tmp/
   system("rm -f /tmp/boa-temp.*");
   system("rm -f /tmp/lighttpd-upload.*");

   unlink("$g_filterfile");
   system("/bin/mv -f \"$cgi_sfn{'upfile'}\" $g_filterfile");
   system("/bin/chmod 0600 $g_filterfile");

}

sub GetDiagStatus()
{

   if ( -e "$g_filterfile" )
   {
      $g_filterfile_present = 1;
   }
   if ( -e "$g_logfile" )
   {
      $g_logfile_present = 1;
   }

   system("/bin/ps -aux --cols=120 | /bin/grep -v grep | /bin/grep $g_swidiag_name &> /dev/null");
   if ( 0 == $? )
   {
      $g_diag_running = 1;
   }

}


