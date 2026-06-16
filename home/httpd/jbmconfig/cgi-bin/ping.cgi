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

if (!exists($in{'host'}) or $in{'host'} !~ /^[a-z0-9-._]+$/i)
  {
   print "Invalid Host/IP Addr provided.\n";

   exit;
  }

my $cmdStr = "/bin/ping -c 4 " . $in{'host'} . " ";

if (exists($in{sintf}))
  {
   if ("Unspecified" ne $in{'sintf'} and $in{'sintf'} =~ /^[a-z0-9:.]+$/i)
     {
      $cmdStr .= "-I " . $in{'sintf'};
     }
  }

$cmdStr .= " 2>&1";

print "Ping Results for " . $in{'host'} . ":\n\n";

system($cmdStr);

exit;
