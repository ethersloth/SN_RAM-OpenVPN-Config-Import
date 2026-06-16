#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

GATHERCONFIGS="/bin/gatherconfigs"
GREP="/bin/grep"
ZIP="/bin/zip"
UNZIP="/bin/unzip"
OUTFILE="/storage/configs-backup.zip"

for i in ${GATHERCONFIGS} ${ZIP} ${UNZIP}
do
    if [ ! -x ${i} ]
    then
        echo "Unable to locate ${i}: does not exist or is not executable!"
        exit 1
    fi
done

if [ "x$1" != "x" ]
then
    OUTFILE=$1
fi

rm -f "${OUTFILE}"

CMD="${GATHERCONFIGS} -d -n -p -a -o ${OUTFILE}"

${CMD}

if [ $? -ne 0 ]
then
    echo "${CMD} failed: $!"
    exit 1
fi

# If gatherconfigs didn't grab /etc/jbm/wireless/cellmodem_provision_data.conf, add it to the archive now:
${UNZIP} -l ${OUTFILE} | ${GREP} -q cellmodem_provision_data.conf 
if [ $? -ne 0 ]
then
    ${ZIP} ${OUTFILE} /etc/jbm/wireless/cellmodem_provision_data.conf
fi

exit 0

