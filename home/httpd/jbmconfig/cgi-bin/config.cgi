#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

use IOG::GetFC;

$| = 1;

$LibraryDIR = "/home/httpd/jbmconfig/cgi-bin";
$AuthDIR = "/tmp/JBMBOA";
$ModDIR = "$LibraryDIR/modules";
$RootHTML = "/cgi-bin/";
$ENV{'PATH'} .= ":/sbin";


if ( $ENV{FC_MODELNO} )
{
	$ModelName = $ENV{FC_MODELNO};
	chomp $ModelName;
}
else
{
	$ModelName = "unknown";
}

if ( $ENV{FC_SERIALNO} )
{
        $Serial = $ENV{FC_SERIALNO};
        chomp $Serial;
}
else
{
	$Serial = "unknown";
}


#version looks like this:
#Redlion Version 4.14rc10 098b1741 --  Mon Apr 8 17:41:32 CDT 2013
$embedded_version = "unknown";
if ( -e "/etc/version" )
{
	#give only 1 match, the top one. new file has more info in it
	#but still contains original format at the top commented
	if ( -x "/bin/build_version" )
	{
		$embedded_version = `/bin/build_version`;
		chomp($embedded_version);
	}
	else
	{
		my $tmp = `grep "Version" /etc/version -m 1`;
		if ( $tmp =~ /^.*s*Version\s+(\d+\.\d+.*?\s).*$/i )
		{
			$embedded_version = $1;
		}
	}
}

#build date looks like this:
#cat /etc/build-date
#2013.04.08-17:41:32
my $build_date_file = "/etc/build-date";
if ( -e "$build_date_file" )
{
	$embedded_date = `cat $build_date_file`;
	chomp $embedded_date;
}
else
{
	$embedded_date = "unknown";
}



#include cgi-lib.pl
eval
{
        require "$LibraryDIR/cgi-lib.pl"; # must be first
        require "/etc/jbm/jbm_lib.pl";
        require "$LibraryDIR/shared.cgi";
};

if ($@)
{       #this must be sent with a \n\n at the end
        print "Content-type: text/html; charset=utf8\n\n";
        print "<html><head><title>CGI Error</title></head>
               <body><b>Script Error</b><br><br>
               Couldn't load required libraries.
               <br>\nCheck that they exist, permissions
               are set correctly and that they compile.
               <br><br>Reason: $@</body></html>";
               exit;
}


# Envirment Varibles
$serveraddress=$ENV{'SERVER_ADDR'}; # server IP address
$servername=$ENV{'SERVER_NAME'}; # servername this is running on
$script=$ENV{'SCRIPT_NAME'}; # script webpath/name
$remoteip = $ENV{'REMOTE_ADDR'}; # get the remote IP

$AuthFile = "$AuthDIR/boaAuth.$remoteip";

# When writing files, several options can be set..
# Spool the files to the /tmp directory
$cgi_lib::writefiles = "/tmp";
$cgi_lib::maxdata = 200000;

###
###Global variables
###

$TRUE=1;
$FALSE=0;

$html_table_width = "100%";





#do NOT remove the line below
1;

