#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

require "./cgi-lib.pl";
require "./jsonlib.pl";

my $scriptfile = "/bin/crimson-access.pl";
my $crimsonPID = "none";

my %RESPONSE = (
	error => 0
);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%RESPONSE);
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
	exit 0;
}

sub checkRunningScripts {
	open(CMD, "ps -ea | grep crimson-access | awk '{print \$1}' 2>&1 |");
	while(<CMD>) {
		$crimsonPID = $_;
	}
	close(CMD);
}

my %in = ();
ReadParse(\%in);
&checkRunningScripts();

if ("start" eq $in{cmd} && 1 ne &checkIP($in{crip})) {
   &send_error("Invalid crimson IP.");
}
if ("start" eq $in{cmd} && 1 ne &checkPort($in{crport})) {
   &send_error("Invalid crimson port.");
}
if ("start" eq $in{cmd} && 1 ne &checkPort($in{allowport})) {
   &send_error("Invalid allow port.");
}
if ("start" eq $in{cmd} && 1 ne &checkIP($in{srcip})) {
   &send_error("Invalid source IP.");
}

if ( -x "$scriptfile" ) {
   if ( "start" eq $in{cmd} ) {
      if (exists($in{cmd}) && exists($in{crip}) && exists($in{crport}) && exists($in{srcip}) && exists($in{allowport}) && exists($in{accesstime})) {
          my $route = `/sbin/ip route get $in{crip}`;
          my $routeIP;
          my $routeDev;
          if ($route =~ /src ([^\s]+)/) {
             $routeIP = $1;
          }
          else {
             &send_error("Failed to parse route source");
          }
          if ($route =~ /dev ([^\s]+)/) {
             $routeDev = $1;
          }
          else {
             &send_error("Failed to parse route device");
          }
          if ( "none" eq $crimsonPID ) {
               system("logger -t 'crimsoncontrol' 'running allowport=$in{allowport} srcip=$in{srcip} crip=$in{crip} crport=$in{crport} accesstime=$in{accesstime} intfip=$routeIP intfname=$routeDev $scriptfile &>/dev/null.'");
               system("allowport=$in{allowport} srcip=$in{srcip} crip=$in{crip} crport=$in{crport} accesstime=$in{accesstime} intfip=$routeIP intfname=$routeDev $scriptfile &>/dev/null &");      
          }
          else {
             &send_error("Crimson access script running");
          }
      }
      else {
         &send_error("Missing crimson access start options");
      }

   }
   elsif ( "stop" eq $in{cmd} ) {
      if ( "none" ne $crimsonPID ) {
         system("/usr/bin/killall crimson-access.pl &>/dev/null");
      }
   }
   else {
      &send_error("Unrecognized comand");
   }
}
else {
   &send_error("Crimson Access Script doesn't exist");
}

&send_response;
exit 0;


# check if a v4 IP is formatted properly
#returns 1 if the IP is valid
#must be x.x.x.x
#octet must be from 0 to 255
#octet can be only 0, but not start with 0 
sub checkIP
{
      return $_[0] =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/  &&
      $1 >= 0 && $1 <= 255 && $1 !~ /^0\d+$/ &&
      $2 >= 0 && $2 <= 255 && $2 !~ /^0\d+$/ &&
      $3 >= 0 && $3 <= 255 && $3 !~ /^0\d+$/ &&
      $4 >= 0 && $4 <= 255 && $4 !~ /^0\d+$/;
}

#returns 1 if the Port is valid
sub checkPort
{
   return $_[0] =~ /^(\d{1,5})$/ &&
                  $1 >= 0 && $1 <= 65535;
}

