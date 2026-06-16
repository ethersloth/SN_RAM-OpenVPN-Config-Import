#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

print "Content-type: text/html; charset=utf8\n\n";

my $clientsipaddress = $ENV{REMOTE_ADDR};
print $clientsipaddress;

exit 0;
