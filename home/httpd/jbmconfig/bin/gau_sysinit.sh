#!/bin/bash
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.
#
# Populate config.xml with the following:
# <GAUCfg version="" family="" model="" serial="" firmware="" platform="" romsize="" ramsize="" isram="" numeth="">
#

FC_MODEL_FILE="/etc/iog/model_features"
. $FC_MODEL_FILE &>/dev/null

MODEL=$FC_MODELNO
SERIAL=$FC_SERIALNO
ISRAM=$FC_RAM
CPU=$FC_CPU_NAME
NUMETH=$FC_NUM_ETH
VERSION=`/home/httpd/jbmconfig/cgi-bin/gau -v`
FAMILY=`/home/httpd/jbmconfig/bin/format_modemno.pl`


if [ -x "/bin/build_firmware" ]; then
	FIRMWARE=$(/bin/build_firmware)
else
	#always split on Version, which takes care of company name being 1 word or more, only 1 match
	FIRMWARE_END=$(grep "Version" /etc/version -m 1 | awk 'BEGIN { FS = "Version" } ; { print $2 }')
	FIRMWARE=$(echo -n 'SN '; echo "$FIRMWARE_END" | awk '{print "version", $1}')
fi

PLATFORM="BT"
if [ "2" = "$FC_CPU_ID" ]; then
	PLATFORM="S5T"
fi

if [ "$PLATFORM" = "BT" ]
then
	STORAGE=`cat /proc/mtd | grep -i '\"storage\"' | awk '{print $2}'`
	KERNEL=`cat /proc/mtd | grep -i '\"kernel\"' | awk '{print $2}'`
	ROOTFS=`cat /proc/mtd | grep -i '"rootfs"' | awk '{print $2}'`
else
	KERNEL=0
	ROOTFS=`cat /proc/mtd | grep -i '\"root1\"' | awk '{print $2}'`
	STORAGE=`cat /proc/mtd | grep -i '\"data\"' | awk '{print $2}'`
fi
STORAGE=`printf "%d" "0x$STORAGE"`
[ -z "$KERNEL" ] && KERNEL=0
[ -z "$ROOTFS" ] && ROOTFS=0
KERNEL=`printf "%d" "0x$KERNEL"`
ROOTFS=`printf "%d" "0x$ROOTFS"`
ROMSIZE=`expr $STORAGE + $KERNEL + $ROOTFS`

RAMSIZE=`free -b|grep '^Mem'|awk '{print $2}'`

CFGXML="/home/httpd/jbmconfig/conf/config.xml"

# Effectively replaces xpeval after scraping the GAUCfg line into a separate
# file below
xpeval_attr() {
	local attribute="$1"
	local value="$2"
	local xmlcfg="$3"
	if echo "$gaucfg" | grep --quiet "$attribute="; then
		sed -i "s/\(<GAUCfg.*\) $attribute=\"[^\"]*\"/\1 $attribute=\"$value\"/" "$xmlcfg"
	else
		sed -i "s/<GAUCfg/<GAUCfg $attribute=\"$value\"/" "$xmlcfg"
	fi
}

# Occasionally there is an additional tag or two ahead of GAUCfg
gaucfg="$(head -5 "$CFGXML" | grep "<GAUCfg")"
if [ "$gaucfg" ]; then
	# Scraping just the GAUCFG open tag lets us create a unique few-line file we
	# can quickly and safely operate on.
	tmpxml="$(mktemp)"
	# Clean copy of config.xml pre-operation
	romxml="$(mktemp "$CFGXML.XXXXXX")"
	cp "$CFGXML" "$romxml"
	head -5 "$romxml" > "$tmpxml"
	xpeval_attr "version" "$VERSION" "$tmpxml"
	xpeval_attr "family" "$FAMILY" "$tmpxml"
	xpeval_attr "model" "$MODEL" "$tmpxml"
	xpeval_attr "serial" "$SERIAL" "$tmpxml"
	xpeval_attr "firmware" "$FIRMWARE" "$tmpxml"
	xpeval_attr "platform" "$PLATFORM" "$tmpxml"
	xpeval_attr "romsize" "$ROMSIZE" "$tmpxml"
	xpeval_attr "ramsize" "$RAMSIZE" "$tmpxml"
	xpeval_attr "isram" "$ISRAM" "$tmpxml"
	xpeval_attr "cpu" "$CPU" "$tmpxml"
	xpeval_attr "numeth" "$NUMETH" "$tmpxml"
	tail -n +6 "$romxml" >> "$tmpxml"
	mv -f "$tmpxml" "$romxml"
	mv -f "$romxml" "$CFGXML"
fi

# This typically accompanies configuration updates. Make sure ini configs are updated
/usr/iog/bin/system_config_syncd

exit 0
