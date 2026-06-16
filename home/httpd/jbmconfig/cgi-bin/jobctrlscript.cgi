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
$filename =~ s/\/tmp\///;
if ($filename !~ /^[a-z0-9\-._]+$/i) {
   print "ERROR: 2 invalid file name\n";
}
my $impinterval = $in{'impinterval'};
my $basedir = "/etc/jobcontrol";
my $storagedir = "$basedir/custom";
my $intervaldir = "$basedir/$impinterval";

if (! -d $intervaldir) {
   mkdir $intervaldir;
}

if (! -d $storagedir) {
   mkdir $storagedir;
}

my $cmdStr = "rm -f $basedir/5min/$filename rm -f $basedir/hourly/$filename rm -f $basedir/daily/$filename $basedir/weekly/$filename $basedir/monthly/$filename $basedir/custom/$filename;";
$cmdStr .= "head -n 1 /tmp/$filename | grep -e '^#\!/' &>/dev/null && dos2unix /tmp/$filename; chmod +x /tmp/$filename; cp -f /tmp/$filename $basedir/$impinterval/$filename; mv -f /tmp/$filename $storagedir/$filename";
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
