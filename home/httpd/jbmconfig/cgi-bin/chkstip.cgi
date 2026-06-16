#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"
.     "Last-Modified: " . gmtime() . " GMT\n"
.     "Cache-Control: no-store, no-cache, must-revalidate\n"
.     "Cache-Control: post-check=0, pre-check=0\n"
.     "Pragma: no-cache\n"
.     "Content-type: text/html; charset=utf8\n\n";


if (-e "/tmp/throughput.running")
  {
   print "Y";

   exit;
  }

if (-e "/tmp/throughput.results")
  {
   if (!open(FILE, "/tmp/throughput.results"))
     {
      print "Unable to open results file.\n";

      exit;
     }

   foreach my $line (<FILE>)
          {
           print $line;
          }

   close(FILE);

   exit;
  }

print "Test completed, no results were returned.";
