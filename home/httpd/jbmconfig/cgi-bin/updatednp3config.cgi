#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";

my %in = ();

ReadParse(\%in);


print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: " . gmtime(time()) . " GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";
print "Pragma: no-cache\n";
print "Content-type: text/html; charset=utf8\n\n";

my $filename = $in{'file'}; 

if ($filename !~ /^[a-z0-9\-._\/]+$/i)
  {
   print "ERROR: 2 Invalid file name\n";

   exit(1);
  }

my $cmdStr = "dos2unix " . $filename . "; mv -f " . $filename . " /etc/stacfg/sxdnpdrv.ini";

$cmdStr .= " 2>&1 |";

if (!open(FILE, $cmdStr))
  {
   print "ERROR: 1 Unable to obtain $filename\n";

   exit(1);
  }

while (<FILE>)
     {
       print $_;
     }
                            
close(FILE);

exit(0);
