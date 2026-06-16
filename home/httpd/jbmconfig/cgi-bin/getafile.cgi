#!/usr/bin/perl  -I /home/httpd/jbmconfig/bin
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
require "./cgi-lib.pl";

my $allowfile = "/home/httpd/jbmconfig/txt/allowfile.txt";
my $isallowed = "FALSE";

my %in = ();
my $filename = "";

ReadParse(\%in);

$filename = $in{'file'};
$file = $filename;
$file =~ s/^[\.\/].*\///g;

if (!open(FILE, $allowfile))
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('1 Access denied to download $file file');\"></body></html>\n";

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
        print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
        print "<body onload=\"alert('3 Unable to download $file file');\"></body></html>\n";

        exit(3);
    }


    print "Content-type: application/octet-stream\n";
    print "Content-Disposition: attachment; filename=$file.txt\n\n";

    foreach my $line (<FILE>)
    {
        print $line;
    }


    close(FILE);
}
else
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('2 Access denied to download $file file');\"></body></html>\n";

    exit(2);
}

exit(0);
