#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

print 'Expires: Mon, 26 Jul 1997 05:00:00 GMT',             "\n",
      'Last-Modified: ', gmtime(), ' GMT',                  "\n",
      'Cache-Control: no-store, no-cache, must-revalidate', "\n",
      'Cache-Control: post-check=0, pre-check=0',           "\n",
      'Pragma: no-cache',                                   "\n",
      'Content-type: text/html; charset=utf8',                            "\n\n";


if (0 != system('touch /etc/jbm/wireless/FORCE_PRL'))
  {
   print 'FAILED';

   exit(1);
  }

print 'SUCCESS';

exit(0);
