#!/usr/bin/perl  -I /home/httpd/jbmconfig/bin
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
# FIXME: Accept a "delete_on_download" flag and act on it to 
# remove files once they have been usccessfully downloaded.

use JBM_System;

require "./cgi-lib.pl";

my $SYSTEM = JBM_System->new();
my %in;

ReadParse(\%in);

$ENV{PATH} .= ":/home/httpd/jbmconfig/bin";

if (!exists($in{file}) or $in{file} !~ /^[a-z0-9\-._\/]$/i)
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('Invalid filename provided')\"></body></html>\n";

    exit;
}

$SYSTEM->Syslog("Download $in{file} requested");

my @pieces = split(/\//, $in{file});

my $size = @pieces;

if (3 != $size)
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('Download permission for \\'$in{file}\\' is denied')\"></body></html>\n";

    exit;
}


$SYSTEM->Syslog("Download() $pieces[0]");

if ("tmp" ne $pieces[1])
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('Download permission for \\'$in{file}\\' is denied')\"></body></html>\n";

    exit;
}

my $basename = $pieces[2];

$SYSTEM->Syslog("Allowing download of $in{file}");

if (!open(FILE, $in{file}))
{
    print "Content-type: text/html; charset=utf8\n\n<html><head><title></title></head>\n";
    print "<body onload=\"alert('Unable to open \\'$in{file}\\'')\"></body></html>\n";

    exit;
}


print "Content-type: application/octet-stream\n";
print "Content-Disposition: attachment; filename=$basename\n\n";

foreach my $line (<FILE>)
{
    print $line;
}

$SYSTEM->Syslog("Downloaded $in{file}");

close(FILE);

if ($in{rm})
{
    $SYSTEM->Syslog("Removing $in{file}");
    if (unlink($in{file}))
    {
        $SYSTEM->Syslog("Successfully removed $in{file}");
    }
}

exit;
