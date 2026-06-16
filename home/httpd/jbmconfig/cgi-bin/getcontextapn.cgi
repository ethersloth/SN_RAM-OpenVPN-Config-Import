#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

#bet     - file created
#v1.0
#
#bet	 - changed default apn from "unknown" to empty
#v1.01

require "./cgi-lib.pl";

my %in = ();
ReadParse(\%in);
my $context = 0

if (exists $in{'context'} && $in{'context'} =~ /^[0-9]+$/) {
	$context = $in{'context'};
}

my $apn = "";
my $cardstats_file = "/var/log/wireless.cardstats";
my $search_string = "CELLMODEM_SIM_CONT_APN";

if ( int($context) < 1 || int($context)> 9)
{
   &print_apn();
}

if ( -e "$cardstats_file")
{
   my @output = `cat $cardstats_file  | grep $search_string | grep "=$context:" 2>&1`;
   if ( 1 == @output )
   {
      my @element = split /:/, $output[0];
      ($apn = $element[1]) =~ s/\s+//g;
   }
}

&print_apn();

sub print_apn()
{

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"               .
	"Last-Modified: " . gmtime(time()) . " GMT\n"          .
	"Cache-Control: no-store, no-cache, must-revalidate\n" .
	"Cache-Control: post-check=0, pre-check=0\n"           .
	"Pragma: no-cache\n"                                   .
	"Content-type: text/html; charset=utf8\n\n";

   print "$apn";
   exit;
}

