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

my $notes = "";

if (exists($in{'notes'}))
  {
   $notes = $in{'notes'};

   if (!open(FILE, ">/tmp/GAU_SpTstNotes.txt"))
     {
      print "Unable to open notes file.\n";

      exit;
     }

   print FILE $notes;

   close(FILE);
  }

my $cmdStr = "(/bin/throughput_test &>/dev/null) &";

system($cmdStr);

exit;




