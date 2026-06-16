#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
#Prepflash is to clear out competing processes that could interrupt reflashing operation.
#	Genesis was to protect reflashing process
#	Critical to run on any platform
#	Does not setup a failsafe reboot in the future
#       Either this should setup a failsafe reboot in the future
#	    Or it should ONLY be run in connection with btflash
#	Btflash DOES execute this routine.
#	Btflash DOES setup a failsafe rebooter.

# Required executables:
LOGGER="/usr/bin/logger"
SERVICE="/sbin/service"
KILLALL="/usr/bin/killall"
IFCONFIG="/sbin/ifconfig"
SYNC="/bin/sync"

TO_NULL=" &> /dev/null"

function die {
	(sleep 30; reboot) &
	logger -t $0 " -- FAILURE. Rebooting in 30 seconds..."
	exit 1
}



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
# n. Make sure all of the commands we need are executable
##################################################################

for i in $LOGGER $SERVICE $KILLALL $IFCONFIG $SYNC
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
# n. clear up any space we can...
##################################################################

#$SERVICE ipsec stop &> /dev/null
$KILLALL -9 pluto &> /dev/null
$SERVICE dmp stop &> /dev/null
$KILLALL -9 node &> /dev/null #just in case
$SERVICE openvpn stop &> /dev/null
$SERVICE ripd stop &> /dev/null
$SERVICE ospfd stop &> /dev/null
$SERVICE bgpd stop &> /dev/null
$SERVICE zebra stop &> /dev/null
$SERVICE nemo stop &> /dev/null
$KILLALL -9 dnsmasq &> /dev/null

$SERVICE udev stop &> /dev/null
$KILLALL -9 udevd
echo "/bin/true" > /proc/sys/kernel/hotplug 2> /dev/null
echo 0 > /proc/sys/net/ipv4/ip_forward

$KILLALL -9 generic_watch &> /dev/null
$KILLALL -9 snswmon &> /dev/null
$KILLALL lightbar &> /dev/null
rm -f /var/log/lightbar*
$KILLALL gmu_listener &> /dev/null
$KILLALL jbmcontrol &> /dev/null
$KILLALL -9 dhcpd &> /dev/null
$KILLALL ssh-keygen &> /dev/null
$KILLALL -9 ip_transparency &> /dev/null
$KILLALL -9 jbm_swi_vz &> /dev/null
$KILLALL -9 swisdk &> /dev/null
$KILLALL -9 swi_qmi_watch &> /dev/null
$KILLALL -9 slqssdk &> /dev/null
$KILLALL -9 udhcp &> /dev/null
$KILLALL io_retain &> /dev/null

$SERVICE crond stop &> /dev/null
$SERVICE xinetd stop &> /dev/null
$SERVICE datalogd stop &> /dev/null
$SERVICE eventd stop &> /dev/null
$SERVICE ez-ipupdate stop &> /dev/null
$SERVICE gau stop &> /dev/null
$SERVICE gps stop &> /dev/null
$SERVICE iocontrol stop &> /dev/null
$SERVICE iodb_status stop &> /dev/null
$SERVICE lighttpd stop &> /dev/null
$SERVICE jbmconfig stop &> /dev/null
$SERVICE jbmconfigs stop &> /dev/null
$SERVICE modbus stop &> /dev/null
$SERVICE ping_alive stop &> /dev/null
$SERVICE snmpd stop &> /dev/null
$SERVICE snproxy stop &> /dev/null
$SERVICE sshd stop &> /dev/null
$SERVICE sxdnpdrv stop &> /dev/null
$SERVICE vnstat stop &> /dev/null
$SERVICE wifi stop &> /dev/null

$IFCONFIG eth0 down &> /dev/null
$IFCONFIG eth1 down &> /dev/null

#kill all children and go idle
$KILLALL -USR2 jbminit &> /dev/null
sleep 5

# Just in case it ever gets stuck (again)
$SYNC &>/dev/null & sleep 2
echo 3 > /proc/sys/vm/drop_caches

exit

