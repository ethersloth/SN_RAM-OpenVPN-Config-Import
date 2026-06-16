#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

RV=0
PROG=`basename $0`

## gatherconfigs
#GCFGS_FILE="/tmp/$PROG.$$.configs.zip"
#GCFGS_CMD="/bin/gatherconfigs -d -n -p -a -o ${GCFGS_FILE}"
#${GCFGS_CMD}
#if [ 0 -ne $? ]
#then
#    RV=1
#    GCFGS_FILE=""
#fi

## gatherstats
#GSTATS_FILE="/tmp/$PROG.$$.stats.zip"
#GSTATS_CMD="/bin/gatherstats -p -i -l -o ${GSTATS_FILE}"
#${GSTATS_CMD}
#if [ 0 -ne $? ]
#then
#    RV=1
#    GSTATS_FILE=""
#fi

# cfgsync
CFGSYNC_RESULT="success"
CFGSYNC_CMD="/bin/cfgsync.sh -s"
${CFGSYNC_CMD}
if [ 0 -ne $? -a 1 -ne $? ]
then
    RV=1
    CFGSYNC_RESULT="failure"
fi

# print results
#echo "gatherconfigs=${GCFGS_FILE}"
#echo "gatherstats=${GSTATS_FILE}"
echo "cfgsync=${CFGSYNC_RESULT}"

# exit
exit ${RV}
