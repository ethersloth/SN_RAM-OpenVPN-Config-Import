#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";

my %in = ();

ReadParse(\%in);

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: " . gmtime() . " GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";
print "Pragma: no-cache\n";
print "Content-type: text/html; charset=utf8\n\n";

if (!exists($in{'host'}))
  {
   print "No Destination IP Address provided.\n"; 

   exit;
  }
if ($in{'host'} !~ /^[a-zA-Z0-9_.\-]+$/)
  {
   print "Invalid host parameter.\n";

   exit;
  }

if (!exists($in{'port'}))
  {
   print "No Destination Port Address provided.\n";
     
   exit;
  }
if ($in{'port'} !~ /^[0-9]+$/)
  {
   print "Invalid port parameter.\n";

   exit;
  }
          
#if ("Unspecified" eq $in{'sintf'}) 
#  {                                            
#   print "No Interface port provided.\n";
#   exit;
#  }                   
                       
#my $cmdStr = "/bin/telnet -b " . $in{'sintf'} . $in{'host'} . " " . $in{'port'};

my $cmdStr = "/bin/telnet " . $in{'host'} . " " . $in{'port'};

$cmdStr .= " 2>&1 |";

#ps aux | grep telnet | grep 1.2.3.5 | awk '{print $2}' | xargs kill
$killwatcher = "(sleep 10; ps aux | grep telnet | grep " . $in{'host'} . " | awk '{print $2}' | xargs kill &> /dev/null) &";
system("$killwatcher");

print "Telnet Results for " . $in{'host'} . " " . $in{'port'} . "\n\n";

if (!open(FILE, $cmdStr))
  {
   print "Unable to open TELENET utility.\n";

   exit;
  }

while (<FILE>)
     {
      print $_;
     }

print "\n\n..Test Complete..\n";

close(FILE);

exit;




