#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
#Purpose:
#Prepfs to clear enough room in ram and rom for images to fit.
#	Genesis was 32meg CPU9.
#	Plenty of room on G25
#	Doesn’t stop networking functions (so that images can be transferred next)
#	Does setup a reboot to happen in the future (dangerous now, but required for 32meg units)
#	RECOMMENDED NOT TO USE GOING FORWARD

# Version 1.01

# Required executables:
RM="/bin/rm"
PS="/bin/ps"
GREP="/bin/grep"
LOGGER="/usr/bin/logger"
SLEEP="/bin/sleep"
SERVICE="/sbin/service"
KILLALL="/usr/bin/killall"
SYNC="/bin/sync"
SLEEP="/bin/sleep"
REBOOT="/sbin/reboot"

TO_NULL=" &> /dev/null"

function die {
	(sleep 30; reboot &> /dev/null) &
	logger -t $0 " -- FAILURE. Rebooting in 30 seconds..."
	exit 1
}

##################################################################
# n. Make sure all of the commands we need are executable
##################################################################

for i in $RM $PS $GREP $LOGGER $SLEEP $SERVICE $KILLALL $SYNC $SLEEP $REBOOT
do
	if [ ! -x $i ]
	then
		# try our best:
		logger -t $0 "Required command ($i) is missing or NOT executable!"
		die
	fi
done

LOGGER="$LOGGER -t $0"


##################################################################
# n. If a Modem module firmware update is in progress, abort
##################################################################

#if cell modem firmware update is in progress, abort
CELL_FIRM_UPD_FILE="/var/log/cellmodem.firmware.upd.flag"
ABORT_DELAY=600
if [ -e "$CELL_FIRM_UPD_FILE" ]; then
	EPOCH_NOW=$(date "+%s")
	EPOCH_FILE=$(stat $CELL_FIRM_UPD_FILE -c %Y 2>/dev/null)
	EPOCH_DIFF=$(expr $EPOCH_NOW - $EPOCH_FILE)
	if [ "$EPOCH_DIFF" -le "$ABORT_DELAY" ]; then
		MESG="Modem module firmware update is in progress, aborting"
		echo "$MESG"
		logger -t $0 "$MESG"
		exit 1
	fi
fi

##################################################################
# n. clear up any space we can...
##################################################################

if [ "$1" != "GAU" ]
then
	$RM -rf /tmp/*
else
    $RM -f /tmp/boa-temp*
fi
if [ `$PS -ax | $GREP -c plutorun` -gt 0 ]
then 
    $SERVICE syslog stop 
fi
touch /tmp/noreboot
$SERVICE dmp stop
$SERVICE udev stop
$SERVICE snmpd stop
$SERVICE sshd stop
$SERVICE ping_alive stop
$SERVICE dhcpd stop
$SERVICE modbus stop
$SERVICE sxdnpdrv stop
$KILLALL -9 node
#-9 generic_watch so it does not showdown wwan0
$KILLALL -9 generic_watch
$KILLALL -9 jbm_swi_vz
$KILLALL -9 swisdk
$KILLALL crond
$KILLALL lightbar
$KILLALL gmu_listener
$KILLALL jbmcontrol
$KILLALL dhcpd
$KILLALL ssh-keygen
$KILLALL udevd
$RM -f /var/log/lightbar*
echo "/bin/true" > /proc/sys/kernel/hotplug 2> /dev/null

$SYNC
echo 3 > /proc/sys/vm/drop_caches

#In 45 minutes, the box should reboot.  The reflashing better be done by now.
($SLEEP 2700; $REBOOT &> /dev/null) &

exit 0
