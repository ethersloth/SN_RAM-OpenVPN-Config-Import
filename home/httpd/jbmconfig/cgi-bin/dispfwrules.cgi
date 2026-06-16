#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: " . gmtime(time()) . " GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";
print "Pragma: no-cache\n";
print "Content-type: text/html; charset=utf8\n\n";


# Get the IP Transparency enable flag from the GAU Master Configuration file config.xml in /home/httpd/jbmconfig/home using the
# xpeval program:

my $ipTransEnable = "";

if (open(
         FILE,
         "/home/httpd/jbmconfig/bin/xpeval -s --in=/home/httpd/jbmconfig/conf/config.xml --xpath=\"/GAUCfg/iptrans/enable/text()\" |"
        )
   )
  {
   while (<FILE>)
        {
         $ipTransEnable = $_;

         chomp($ipTransEnable);
        }

   close(FILE);
  }

if ("y" eq $ipTransEnable)
  {
   print "IP Transparency is enabled, which prevents normal firewall operation.\n";

   exit(0);
  }

my $cmdStr = "/sbin/iptables -L -n -v; echo '-------------------'; /sbin/iptables -L -n -v -t nat";

$cmdStr .= " 2>&1 |";

if (!open(FILE, $cmdStr))
  {
   print "Unable to obtain firewall rules.\n";
  }

while (<FILE>)
     {
      print $_;
     }

close(FILE);

exit(0);

