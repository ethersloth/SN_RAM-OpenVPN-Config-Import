#!/usr/bin/perl -w
# C2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are
# registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"
.     "Last-Modified: " . gmtime() . " GMT\n"
.     "Cache-Control: no-store, no-cache, must-revalidate\n"
.     "Cache-Control: post-check=0, pre-check=0\n"
.     "Pragma: no-cache\n"
.     "Content-type: text/html; charset=utf8\n\n";

#Tell cellmodemconnect not to save the config on it's own, it should already be updated
print system("/sbin/cellmodemconnect.pl on --nosave &>/dev/null");

exit(0);
