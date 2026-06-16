#!/bin/bash
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

###### CHANGE LOG ###### ###### CHANGE LOG ###### ###### CHANGE LOG ###### ###### CHANGE LOG ######
#
# 6/14/2011 - DBK - Version 0.3: Added new argument (-n) to tell the Copy function to NOT run sync
#                   when it finishes its cp -af. There is a weird side effect of the sync command.
# 6/15/2011 - DBK - Version 0.4: Removed new argument (-n). No more sync at all.

# If firstboot hasn't completed and we are not given the -f option,
# then exit immediately with return code 0. Can't be handled easily 
# later with getopts because -f may not be the first argument we are given
[ -e '/etc/.firstboot' ] && ( echo "$@" | grep -qv -- '-\w*f' ) && exit 0

DEBUG=0

PROGRAM="${0}"
VERSION="0.5"
DEFAULT_CONFIG="/etc/jbm/recovery/firstboot/gauv3/gauv3.template.config.xml"
BACKUP_CONFIG="/home/httpd/jbmconfig/conf/config.xml.bak"
CURRENT_CONFIG="/home/httpd/jbmconfig/conf/config.xml"
ERROR_LOG_FILE="/etc/jbm/cfgsync.log"
MAX_ERROR_LOG="102400"
DATE_TIME=$(date +%y%m%d-%H%m%S)
PID_FILE_NAME="/var/lock/cfgsync.LCK"
STORAGE_CFG="/storage/config-invalid.$DATE_TIME.xml"

XPEVAL="/home/httpd/jbmconfig/bin/xpeval"
CP="/bin/cp"
CAT="/bin/cat"
SYSLOG="/usr/bin/logger"
LS="/bin/ls"
MV="/bin/mv"
PS="/bin/ps"
RM="/bin/rm"
AWK="/bin/awk"
GREP="/bin/grep"
BASENAME="/usr/bin/basename"
DATE="/bin/date"
PERL="/usr/bin/perl"


for i in ${XPEVAL} ${CP} ${CAT} ${SYSLOG} ${LS} ${PS} ${RM} ${AWK} ${GREP} ${BASENAME} ${DATE} ${MV}
do
    if [ ! -x ${i} ]
    then
        echo "Unable to use required command (${i}): Missing or NOT executable!"
        exit 255
    fi
done

PROGRAM=`${BASENAME} ${0}`
SYSLOG="${SYSLOG} -t ${PROGRAM}[$$]"

function Usage {
${CAT} <<EOF

Usage: ${PROGRAM} <options>

Options:
-h      Display this usage information and exit.
-f      Force ${PROGRAM} to run even if called during first boot.
-b      Force a back-up of the last known good configuration.
-s      Synchronize the current and last known good configurations,
        using the latest valid file as the master.
-v      Validate the current configuration file.
-x      Validate the last known good configuration file.

Returns:
0       Success
1       Success, but changes were made. This can happen when the
        current configuration is found to be invalid during a 
        synchronization, but is subsequently overwritten (and thus
        repaired) by the last known good configuration.
2-255   Failure

Note: 
On a validation failure, check ${ERROR_LOG_FILE}.

EOF
}

function WritePIDFile {
RV=0
if [ -e "${PID_FILE_NAME}" ]
then
    FILE_PID=`${CAT} ${PID_FILE_NAME}`
    MY_PID=${$}
    if [ ${FILE_PID} -ne ${MY_PID} ]
    then
        echo "FILE_PID is ${FILE_PID}. MY_PID is ${MY_PID}."
        if [ `${PS} -ax | ${AWK} '{print \$1}' | ${GREP} -c ${FILE_PID}` -gt 0 ]
        then
            echo "An instance of ${1} is still running!"
            RV=1
        else
            ${RM} -f "${PID_FILE_NAME}"
        fi
    fi
else
    echo ${$} > "${PID_FILE_NAME}"
fi
return ${RV}
}
function Copy {
RV=255
if [ "x${1}" != "x" -a "y${2}" != "y" -a -e "${1}" ]
then
    ${CP} -af "${1}" "${2}" &> /dev/null
    RV=$?
fi

return ${RV}
}


function Validate {
RV=255
if [ "x${1}" != "x" ]
then
    if ${XPEVAL} --in="${1}" --xpath="/GAUCfg" 2>&1 | grep -q "FALSE\|Error"
    then
        ${SYSLOG} "${1} is not valid."
        DumpErrorLog "${1}"
    else
        RV=0
    fi
fi

return ${RV}
}

function Backup {
RV=0
# Create temp on same fs as destination for atomic overwrite operations
TMP_CONFIG="${CURRENT_CONFIG}.cfgsync"
Copy "${CURRENT_CONFIG}" "${TMP_CONFIG}"
# Make sure the current configuration is valid:
Validate "${TMP_CONFIG}"
if [ $? -eq 0 ]
then
    ${MV} -f "${TMP_CONFIG}" "${BACKUP_CONFIG}"
    RV=$?
else
    ${RM} -f "${TMP_CONFIG}"
    RV=255
fi

return ${RV}
}


function Synchronize {
RV=0
CURRENT_VALID=0
BACKUP_VALID=0
DEFAULT_VALID=0
# Create temp on same fs as destination for atomic overwrite operations
TMP_CURRENT="${CURRENT_CONFIG}.cfgsync"
TMP_BACKUP="${BACKUP_CONFIG}.cfgsync"

Copy "${CURRENT_CONFIG}" "${TMP_CURRENT}"

# Validate the current config
Validate "${TMP_CURRENT}"

if [ $? -eq 0 ]
then
    CURRENT_VALID=1
else
    # Maybe something was writing it...
    usleep 500000
    Copy "${CURRENT_CONFIG}" "${TMP_CURRENT}"
    Validate "${TMP_CURRENT}"
    if [ $? -eq 0 ]
    then
        CURRENT_VALID=1
    fi
fi

if [ ${CURRENT_VALID} -eq 1 ]
then
    # This strips off anything after the closing GAUCfg tag, a specifc form of corruption
    # See Jira issue MS-1314
    ${PERL} -0777 -pi -e 's/^<\/GAUCfg>(\n*.*)*/<\/GAUCfg>\n/gm' ${TMP_CURRENT}
else
    ${SYSLOG} "Invalid configuration detected. Saving to ${STORAGE_CFG}"
    Copy "${TMP_CURRENT}" "${STORAGE_CFG}"

    Copy "${BACKUP_CONFIG}" "${TMP_BACKUP}"
    Validate "${TMP_BACKUP}"

    if [ $? -eq 0 ]
    then
        BACKUP_VALID=1
    else

        Validate "${DEFAULT_CONFIG}"

        if [ $? -eq 0 ]
        then
            DEFAULT_VALID=1
        fi
    fi
fi

if [ ${CURRENT_VALID} -eq 1 ]
then
    # Current is valid. Copy over back-up.
    ${SYSLOG} "Synchronizing valid current configuration."
    Copy "${TMP_CURRENT}" "${TMP_BACKUP}"
    ${MV} -f "${TMP_CURRENT}" "${CURRENT_CONFIG}"
    ${MV} -f "${TMP_BACKUP}" "${BACKUP_CONFIG}"
    RV=$?
elif [ ${BACKUP_VALID} -eq 1 ]
then
    # Backup is valid. Copy over current.
    ${SYSLOG} "Synchronizing valid backup configuration."
    Copy "${TMP_BACKUP}" "${TMP_CURRENT}"
    ${MV} -f "${TMP_CURRENT}" "${CURRENT_CONFIG}"
    if [ $? -eq 0 ]
    then
        RV=1
    else
        RV=$?
    fi
    # Run gau_sysinit just in case:
    if [ -x "/home/httpd/jbmconfig/bin/gau_sysinit.sh" ]
    then
        /home/httpd/jbmconfig/bin/gau_sysinit.sh &
    fi
elif [ ${DEFAULT_VALID} -eq 1 ]
then
    # Default is valid. Copy over current AND backup.
    ${SYSLOG} "Synchronizing valid default configuration."
    Copy "${DEFAULT_CONFIG}" "${TMP_CURRENT}"
    Copy "${DEFAULT_CONFIG}" "${TMP_BACKUP}"
    ${MV} -f "${TMP_CURRENT}" "${CURRENT_CONFIG}"
    ${MV} -f "${TMP_BACKUP}" "${BACKUP_CONFIG}"
    if [ $? -eq 0 ]
    then
        RV=1
    else
        RV=$?
    fi
    # Run gau_sysinit just in case:
    if [ -x "/home/httpd/jbmconfig/bin/gau_sysinit.sh" ]
    then
        /home/httpd/jbmconfig/bin/gau_sysinit.sh
    fi
else
    # We have no valid configs! Panic and tell the logs all about it!
    ${SYSLOG} "NO VALID CONFIGURATIONS!!!"
    RV=255
fi

${RM} -f "${TMP_BACKUP}" "${TMP_CURRENT}"

return ${RV}
}

function DumpErrorLog {
if [ -w "${ERROR_LOG_FILE}" ]
then
    FILESIZE=$(stat -c%s "${ERROR_LOG_FILE}")

    if [ ${FILESIZE} -gt ${MAX_ERROR_LOG} ]
    then
        echo "" > ${ERROR_LOG_FILE}
    fi
fi

if [ "x${1}" != "x" ]
then
    echo -n "vvvvvvvvvv " >> ${ERROR_LOG_FILE}
    ${DATE} >> ${ERROR_LOG_FILE}
    echo "${1} is not valid." >> ${ERROR_LOG_FILE}
    ${LS} -al ${1} >> ${ERROR_LOG_FILE}
    ${CAT} ${1}  >> ${ERROR_LOG_FILE}
    echo "^^^^^^^^^^ " >> ${ERROR_LOG_FILE}
fi
}

${SYSLOG} "Version ${VERSION} Started."

WritePIDFile ${PROGRAM}

if [ $? -ne 0 ]
then
    ${SYSLOG} "Another copy of ${PROGRAM} is already running. Exiting."
    exit 255
fi

EXIT_CODE=0


while getopts "bfhsvxn" flag
do
    case "${flag}" in
        'b')
        ${SYSLOG} "Backup"
        Backup
        EXIT_CODE=$?
        ;;

        'f')
        ${SYSLOG} "Got force option, ignoring /etc/.firstboot if present"
        #EXIT_CODE=$?
        ;;

        'h')
        ${SYSLOG} "Usage"
        Usage
        EXIT_CODE=0
        ;;
        
        's')
        ${SYSLOG} "Synchronize"
        if [ "$DEBUG" -eq "1" ]; then
           Copy ${CURRENT_CONFIG} /tmp/config.cfgsync.$$.before.xml
        fi
        Synchronize
        if [ "$DEBUG" -eq "1" ]; then
           Copy ${CURRENT_CONFIG} /tmp/config.cfgsync.$$.after.xml
        fi
        EXIT_CODE=$?
        ;;
        
        'v')
        ${SYSLOG} "Validate Current"
        Validate "${CURRENT_CONFIG}"
        EXIT_CODE=$?
        ;;
        
        'x')
        ${SYSLOG} "Validate Backup"
        Validate "${BACKUP_CONFIG}"
        EXIT_CODE=$?
        ;;

        'n')
        ${SYSLOG} "NOT SYNCING"
        ;;

        *)
        ${SYSLOG} "Unknown option ($@)"
        echo "Unrecognized option (${flag})!"
        Usage
        EXIT_CODE=255
        ;;
    esac
done

if [ "x${1}" = "x" ]
then
    Usage
fi

${RM} -f ${PID_FILE_NAME}


exit ${EXIT_CODE}
