#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";

my $allowfile = "/home/httpd/jbmconfig/txt/allowfile.txt";
my $isallowed = "FALSE";

my %in = ();

ReadParse(\%in);


print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: " . gmtime(time()) . " GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";
print "Pragma: no-cache\n";
print "Content-type: text/html; charset=utf8\n\n";

my $filename = "";

$filename = $in{'file'};

if (!open(FILE, $allowfile))
  {
   print "ERROR: 1 Missing file access list.\n";

   exit(1);
  }

$/ = undef;
my $filelist = <FILE>;
$/ = "\n";
close(FILE);

my @fileentries = split "\n", $filelist;
 
foreach my $afileentry (@fileentries)
       {
          if ($afileentry eq $filename)
            {
              $isallowed = "TRUE";
            }
       }


if ($isallowed eq "TRUE" ) 
  {
   if (!open(FILE, $filename))
     {
      print "ERROR: 2 Unable to open file\n";

      exit(2);
     }

   my $cmdStr = "cat " . $filename;

   $cmdStr .= " 2>&1 |";

   if (!open(FILE, $cmdStr))
     {
      print "ERROR: 3 Unable to obtain file\n";

      exit(3);
     }

   while (<FILE>)
        {
         print $_;
        }

   close(FILE);
  }
else
  {
   print "ERROR: 4 Access to file not allowed.\n";

   exit(1);
  }

exit(0);
