#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

BEGIN {
    push @INC, "/home/httpd/jbmconfig/bin";
}

use JBM_System;

print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n"             .
"Last-Modified: " . gmtime(time()) . " GMT\n"          .
"Cache-Control: no-store, no-cache, must-revalidate\n" .
"Cache-Control: post-check=0, pre-check=0\n"           .
"Pragma: no-cache\n"                                   .
"Content-type: text/html; charset=utf8\n\n";

my $SYSTEM = JBM_System->new();

my $errmsg = "";

#
# This CGI script will simply act as a wrapper to the syscfgrecovery.sh in ../bin
#
# The main function will be to:
# 1. Gather the current configurations (gatherconfigs)
# 2. Gather all useful debugging info (gatherstats)
# 3. Attempt to recover to the last known good config.xml (cfgsync.sh)
#
my $script_cmd = "/home/httpd/jbmconfig/bin/cfgsync.sh -s -n";

#
# The expected return value (on success) of cfgsync.sh is 0 or 1
#
my $got_cfgsync       = 0;
my $cfgsync_result = undef;

my $retval = system($script_cmd);

$retval /= 256;

$SYSTEM->Syslog("cfgsync ($script_cmd) returned $retval");

if (0 != $retval && 1 != $retval)
{
    $SYSTEM->Syslog("Failure detected in cfgsync from $script_cmd (returned $retval)");
    PrintPage("Unable to recover system configuration file");
    exit(-1);
}

#
# If we got here, we had success with the script. Print a result page:
#
PrintPage("Recovery was successful. You will now be redirected.");

exit(0);

sub PrintPage()
{
    my $errmsg = shift;

    $errmsg =~ s/\:/\./g;

    print "$errmsg";

    return(0);
}


