#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

BEGIN {
       push @INC, "/home/httpd/jbmconfig/bin";
      }

use JBM_System;

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"
.     "Last-Modified: " . gmtime(time()) . " GMT\n"
.     "Cache-Control: no-store, no-cache, must-revalidate\n"
.     "Cache-Control: post-check=0, pre-check=0\n"
.     "Pragma: no-cache\n"
.     "Content-type: text/html; charset=utf8\n\n";

my $SYSTEM = JBM_System->new();

my $ipTransIP      = "";
my $ipTransGateway = "";
my $ipTransNetmask = "";


if (open(FILE, "/tmp/iptrans.info"))
  {
   while (<FILE>)
        {
         my $line = $_;

         chomp($line);

         my ($varName, $varVal) = split(/=/, $line);

         if ("IPTRANS_IP" eq $varName)
           {
            $ipTransIP = $varVal;

            next;
           }

         if ("IPTRANS_NETMASK" eq $varName)
           {
            $ipTransNetmask = $varVal;

            next;
           }

         if ("IPTRANS_GATEWAY" eq $varName)
           {
            $ipTransGateway = $varVal;

            next;
           }
        }

   close(FILE);
  }


my $rsltStr = "ipTransIP=" . $ipTransIP  . "|ipTransNetmask=" . $ipTransNetmask . "|ipTransGateway=" . $ipTransGateway;

print $rsltStr . "\n";


exit(0);

