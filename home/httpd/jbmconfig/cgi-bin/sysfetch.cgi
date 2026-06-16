#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";

$ENV{PATH} .= ":/home/httpd/jbmconfig/bin:/bin:/sbin:/usr/bin";

my $config = "/home/httpd/jbmconfig/conf/sysfetch.conf";
my $output;
my %in = ();
ReadParse(\%in);

&IOG::CGI::printHeaders();

if (exists($in{command}))
{
    if (open(CONFIG, $config)) 
    {
        foreach my $line (<CONFIG>)
        {
            chomp($line);
            my ($label, $command) = split(/\s*:\s*/, $line);
            if ($label eq $in{command})
            {
                if (open(COMMAND, "$command 2>&1 |"))
                {
                    while (<COMMAND>)
                    {
                        print;
                    }
                    close(COMMAND);
                }
            }
        }
        close(CONFIG);
    }
}
