#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";

my %in = ();                                                                                                                   
ReadParse(\%in);                                                                                                               
                                                                                                                               
print 'Expires: Mon, 26 Jul 1997 05:00:00 GMT',             "\n",                                                              
      'Last-Modified: ', gmtime(time()), ' GMT',            "\n",                                                              
      'Cache-Control: no-store, no-cache, must-revalidate', "\n",                                                              
      'Cache-Control: post-check=0, pre-check=0',           "\n",
      'Pragma: no-cache',                                   "\n",
      'Content-type: text/html; charset=utf8',                            "\n\n";

if (!exists($in{'file'}) or ! -f "/tmp/$in{'file'}")
{                                                                                                                              
    exit(1);                                                                                                                   
}                                                                                                                              

my $cmdStr = 'openssl x509 -in /tmp/' . $in{'file'} .  ' -text -noout &>/dev/null';                                           
my $result = system $cmdStr;

if ( 0 != $result )                                                              
{                                                                  
    print "INVALID\n";                                                              
}
else
{
    print "VALID\n";                                                              
}
exit(0);
