#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use strict;
use warnings;

require "./cgi-lib.pl";

# Make STDOUT 'hot' so we aren't buffering output
local $| = 1;

my %in = ();
ReadParse(\%in);

print "Content-type: text/html; charset=utf8\n\n";

if (exists($in{num}) && $in{num} =~ /^[0-9]+$/) {
	system("tail -f -n $in{num} /var/log/messages");
}
else {
	system("tail -f /var/log/messages");
}
