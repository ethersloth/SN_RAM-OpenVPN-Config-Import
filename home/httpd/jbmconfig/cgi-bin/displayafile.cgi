#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";

my $allowfile = "/home/httpd/jbmconfig/txt/allowfile.txt";
my $isallowed = "FALSE";
my $filtermatch = "^[a-zA-Z0-9_.\\-\\s]*\$";

my %in = ();

ReadParse(\%in);

&IOG::CGI::printHeaders();

my $filter   = "";
my $maxLines = 0;
my $filename = "";

if (exists $in{'file'} && $in{'file'} =~ /^[0-9A-Za-z-._\/]+$/)
  {
   $filename = $in{'file'};
  }
else
  {
   print "ERROR: 5 Must specify a file to display.\n";
  }
if (exists $in{'maxlines'} && $in{'maxlines'} =~ /^[1-9][0-9]*$/)
  {
   $maxLines = $in{'maxlines'};
  }
if (exists $in{'filter'})
  {
   if ($in{'filter'} !~ /$filtermatch/)
     {
      print "ERROR: 6 Invalid filter string. Must =~ /$filtermatch/\n";
      exit(1);
     }
   $filter = $in{'filter'};
  }

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
      print "ERROR: 3 Unable to open file\n";

      exit(3);
     }

   my $cmdStr = "";
   if ($maxLines > 0)
     {
      $cmdStr = "tail -n $maxLines $filename";
     }
   else
     {
      $cmdStr = "cat $filename";
     }

   if ("" ne $filter)
     {
      print "Using filter: '" . $filter . "'\n\n";
      $cmdStr .= "| grep " . $filter;
     }

   $cmdStr .= " 2>&1 |";

   if (!open(FILE, $cmdStr))
     {
      print "ERROR: 4 Unable to obtain file\n";

      exit(4);
     }

   while (<FILE>)
        {
         print $_;
        }

   close(FILE);
  }
else
  {
   print "ERROR: 2 Access to file not allowed.\n";

   exit(2);
  }

exit(0);
