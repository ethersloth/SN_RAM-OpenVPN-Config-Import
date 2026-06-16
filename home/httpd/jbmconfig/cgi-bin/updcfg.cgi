#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

###############################################################################################################################
#                                                                                                                             #
# updcfg.cgi - Update configuration.                                                                                          #
#                                                                                                                             #
# Obtain a (sorted) list of interfaces in the form of a list of html <option> elements from the system, filtered according to #
# the command line arguments.                                                                                                 #
#                                                                                                                             #
# For the record . . .                                                                                                        #
#                                                                                                                             #
# Copyright (c) 2008, 09 by jbm Electronics, 2010 by SixNet LLC.                                                              #
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


# Global variables:

my $CGILIB_FILE = '/home/httpd/jbmconfig/cgi-bin/cgi-lib.pl';
$DEBUG       = 0,
$DEBUG_LEVEL = 0,
$JBMLIB_FILE = '/etc/jbm/jbm_lib.pl',
$VERSION     = '1.2';

require($JBMLIB_FILE);
require($CGILIB_FILE);

my %in = ();

ReadParse(\%in);

print 'Expires: Mon, 26 Jul 1997 05:00:00 GMT',             "\n",
      'Last-Modified: ', gmtime(time()), ' GMT',            "\n",
      'Cache-Control: no-store, no-cache, must-revalidate', "\n",
      'Cache-Control: post-check=0, pre-check=0',           "\n",
      'Pragma: no-cache',                                   "\n",
      'Content-type: text/html; charset=utf8',                            "\n\n";


if (!exists($in{'import'}))
{
    print 'ERROR', "\n",
	  'Unable to update configuration, no import file.';

    exit(1);
}
if ($in{'import'} !~ /^[a-zA-Z0-9_.\-]+$/)
{
    print 'ERROR', "\n",
	  'Invalid import file name.';

    exit(1);
}

unlink("/tmp/udpcfg.txt");
unlink("/tmp/updcfg.err");


my $importFName = $in{'import'};
my $cmdStr;
my $mode = 'apply';
my $importMode = 'replace';

if (exists($in{'dftimpmode'}))
{
    $importMode = $in{'dftimpmode'};
}
if ($in{'dftimpmode'} !~ /^(replace|merge)$/i)
{
    print 'ERROR', "\n",
	  'Invalid import file handling.';

    exit(1);
}

if (exists($in{'mode'}))
{
    $mode = $in{'mode'};
}
if ($in{'mode'} !~ /^(save|apply|applyall)$/i)
{
    print 'ERROR', "\n",
	  'Invalid mode.';

    exit(1);
}


delete $ENV{'REQUEST_METHOD'};


#This must run detached so it doesn't get a broken pipe " ( foo ) &
$cmdStr = '( /home/httpd/jbmconfig/bin/migratecfg --tplfile=/home/httpd/jbmconfig/conf/config.xml '
. '--impfile=/tmp/' . $importFName . ' --outfile=/tmp/config.xml --report=detailed '
. '--dftimpmode=' . $importMode . ' --' . $mode . ' --debug=200 &>/tmp/updcfg.txt; /home/httpd/jbmconfig/bin/gau_sysinit.sh &> /dev/null ) &';

syslog('updcfg: Calling "' . $cmdStr . '"' . "\n");

if (0 != system($cmdStr))
{
    syslog('migrate failed');

    print 'ERROR' ,                                     "\n",
	  'Configuration update process failed:<br />', "\n";

    if (!open(FILE, "</tmp/updcfg.err"))
    {
        print 'See syslog for details.', "\n";
    }
    else
    {
        while (<FILE>)
        {
            print $_;
        }

        close(FILE);
    }

    exit(0);
}

# Added to ensure the newly imported configuration file is populated with the correct unit-specific info:
# Note:  This is not called above at the end of the system call
#system("/home/httpd/jbmconfig/bin/gau_sysinit.sh &> /dev/null");


print 'SUCCESS',                                                                                  "\n",
      'Configuration update is in progress.<br />',                                               "\n",
      'The process can take several minutes to complete.<br />',                                  "\n",
      '<font color="#FF0000">Do not disconnect power during the process.</b></font>',             "\n",
      '<b>Do not exit this page.</b><br />',                                                      "\n",
      'You will be notified here when the process is complete, please standby . . .<br /><br />', "\n";

exit(0);

