#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

###############################################################################################################################
#                                                                                                                             #
# getiftfs - Get Interface List                                                                                               #
#                                                                                                                             #
# Obtain a (sorted) list of interfaces in the form of a list of html <option> elements from the system, filtered according to #
# the command line arguments.                                                                                                 #
#                                                                                                                             #
# For the record . .                                                                                                          #
#                                                                                                                             #
# Copyright (c) 2008 by Sixnet.                                                                                               #
#                                                                                                                             #
# All rights reserved.  No part of this program may be reproduced, stored in a retrieval system or transmitted, in any form   #
# or by any means, including but not limited to electronic, mechanical, photocopying, recording, or otherwise, without the    #
# express prior written consent of Sixnet, 4645 LaGuardia, St. Louis, MO 63134.  (314) 426-7781, fx: (314) 426-0007.          #
# Contact support@sixnet.com                                                                                                  #
#                                                                                                                             #
#                                                                                                                             #
# This program was written by Art Surgant.                                                                                    #
#                                                                                                                             #
###############################################################################################################################


require "./cgi-lib.pl";

my %in = ();

ReadParse(\%in);

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: " . gmtime() . " GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";
print "Pragma: no-cache\n";
print "Content-type: text/html; charset=utf8\n\n";


if (!exists($in{'tunnelname'}) or $in{'tunnelname'} !~ /^[a-z0-9]+$/i)
  {
   print "Unable to obtain tunnel status, invalid tunnelname";

   exit(1);
  }


my $tunnelname = $in{"tunnelname"};

my $cmdStr = "/sbin/ipsec auto --status | grep \"$tunnelname\\\"\"";
#print "$cmdStr\n";
my $output = `$cmdStr 2>&1`;

if ( $? )
{
	print "Unable to obtain tunnel status for '" . $tunnelname . "'.";
	exit(1);
}

my @OUTPUT = split/\n/, $output;
print "Tunnel $tunnelname :\n\n";
foreach $line(@OUTPUT)
{
	chomp($line);
	$line =~ s/^0+\s+//g;
	#$line =~ s/^\"$tunnelname\":\s+//g;
	$line =~ s/\"$tunnelname\":\s*//g;
	$line =~ s/\.\.\./...\n   ....\[encrypted\]....\n.../g;
	$line =~ s/;\s+/\n   /g;
	$line =~ s/\stun\./\n   tun\./g;
	$line =~ s/\sesp\./\n   esp\./g;
	$line =~ s/^#/\n#/;
	print "$line\n";

}


#print "$output";
exit(0);

