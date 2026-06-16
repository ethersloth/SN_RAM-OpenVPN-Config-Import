#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# bet		Added ssl.cipher options, sed inline file editing
# 1/21/2015

FILE="/etc/lighttpd/gau/lighttpd-gau.conf"
TMP_FILE="/tmp/lighttpd-gau.conf.tmp"

if [ ! -e "$FILE" ]; then
	echo "Config file $FILE missing"
	exit 1
fi

cp -f $FILE $FILE.bak

COMMAND="disable"
if [ "$1" = "enable" ]; then
	COMMAND="enable"
elif [ "$1" = "disable" ]; then
	COMMAND="disable"
else
	echo "Command must be 'enable' or disable'"
	exit 1
fi

MATCH="^ssl.engine.*$"
REPLACE="ssl.engine = \"$COMMAND\""

sed -i "s/$MATCH/$REPLACE/g" $FILE

if [ "$?" != "0" ]; then
	echo "Change failed!"
	exit 1
fi

if [ "$COMMAND" = "disable" ]; then
#no need to add good cypher list
	exit 0
fi

#Cannot have duplicate lines or it breaks the config, so add all or none
#so remove any entries we already are going to add in

sed -i -e "s/^ssl.use-sslv3.*$//g" \
	-e "s/^ssl.disable-client-renegotiation.*$//g" \
	-e "s/^ssl.honor-cipher-order.*$//g" \
	-e "s/^ssl.cipher-list.*$//g" $FILE

#Now add in (append) the lines we want
echo '
ssl.use-sslv3 = "disable"
ssl.disable-client-renegotiation = "enable"
ssl.honor-cipher-order = "enable"
ssl.cipher-list = "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:!TLSv1"
' >> $FILE

exit 0

