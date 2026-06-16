#!/bin/bash
# (C)2016 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

# Target for where files will be on device
TARGET_HTML_DIR="/home/httpd/jbmconfig/html"

if [ ! -z "$1" ]; then
	if [ -d "$1" ]; then
		LOCAL_HTML_DIR=$(cd "$1" && pwd)
	else
		echo "$1 is not a valid directory"
		exit 1
	fi
# Check for/can run on a device
elif [ -d $TARGET_HTML_DIR ]; then
	LOCAL_HTML_DIR="$TARGET_HTML_DIR"
fi

# This is a subdirectory of TARGET_HTML_DIR where md5-named files will be
LINKDIR="md5link"

# Default files (will be copied and left unmodified)
MAINJS="${LOCAL_HTML_DIR}/main.js"
HTML="${LOCAL_HTML_DIR}/index-default.html"

LOCAL_JS="${LOCAL_HTML_DIR}/js"
TARGET_JS="${TARGET_HTML_DIR}/js"
LOCAL_PAGES="${LOCAL_HTML_DIR}/pages"
TARGET_PAGES="${TARGET_HTML_DIR}/pages"
LOCAL_LINKS="${LOCAL_HTML_DIR}/${LINKDIR}"

if [ ! -f "$MAINJS" ] || [ ! -f "$HTML" ]; then
	echo "Missing index files"
	exit 1
fi

CAT="/bin/cat"
CP="/bin/cp"
GREP="/bin/grep"
LN="/bin/ln"
MD5SUM="/usr/bin/md5sum"
MKDIR="/bin/mkdir"
MV="/bin/mv"
RM="/bin/rm"
SED="/bin/sed"

# fix_pages: create a pair of links <name>-<md5>.html/.js for each <name>.html/.js in the pages directory
#     These are added to a string (REQUIRED_PATHS) that will be prepended to main.js
function fix_pages {
	for jsfile in $(ls ${LOCAL_PAGES} | grep ".js$"); do
		name=${jsfile/.js/}
		jsfile="${LOCAL_PAGES}/${jsfile}"
		htfile="${LOCAL_PAGES}/${name}.html"

		if [ -f "$jsfile" -a -f "$htfile" ]; then
			md5=$($CAT "$jsfile" "$htfile" | $MD5SUM | awk '{print $1}')
			md5=${md5:0:7}
			md5name="${name}-${md5}"

			$LN -sf "${TARGET_PAGES}/${name}.js"   "${LOCAL_LINKS}/${md5name}.js"
			$LN -sf "${TARGET_PAGES}/${name}.html" "${LOCAL_LINKS}/${md5name}.html"
			if [ -z "$REQUIRED_PATHS" ]; then
				REQUIRED_PATHS="document.md5link_paths = {"
				REQUIRED_PATHS="${REQUIRED_PATHS}\n'${name}':'${LINKDIR}/${md5name}'"
			else
				REQUIRED_PATHS="${REQUIRED_PATHS},\n'${name}':'${LINKDIR}/${md5name}'"
			fi
		else
			echo "WARNING: no html model found for $jsfile"
		fi
	done
}

function fix_js {
	# Only look for js in the first-level directory. Libs don't need to be linked
	# because they are named by version
	for jsfile in $(ls -p ${LOCAL_JS} | grep ".js$"); do
		name=${jsfile/.js/}
		jsfile="${LOCAL_JS}/${jsfile}"

		md5=$($MD5SUM $jsfile | awk '{print $1}')
		md5=${md5:0:7}
		md5name="${name}-${md5}"
		$LN -sf "${TARGET_JS}/${name}.js" "${LOCAL_LINKS}/${md5name}.js"

		REQUIRED_PATHS="${REQUIRED_PATHS},\n'${name}':'${LINKDIR}/${md5name}'"
	done
	REQUIRED_PATHS="${REQUIRED_PATHS}\n};"
}



# Make sure nothing gets in the way if we re-run script
$RM -rf $LOCAL_LINKS
$MKDIR -p $LOCAL_LINKS

REQUIRED_PATHS=
fix_pages
fix_js

# Assemble new main.js
newmain="${LOCAL_LINKS}/main"
echo -e "$REQUIRED_PATHS" > $newmain
$CAT $MAINJS >> $newmain
newmainmd5=$($MD5SUM $newmain | awk '{print $1}')
newmainmd5=${newmainmd5:0:7}
MAINJS="${newmain}-${newmainmd5}.js"
$MV $newmain $MAINJS

# Create index.html and update to use new main.js
newhtml="${LOCAL_HTML_DIR}/index.html"
eval "$CP -f $HTML $newhtml"
HTML="$newhtml"
$SED -i "s/data-main=\"[^\"]*\"/data-main=\"${LINKDIR}\/$(basename $MAINJS)\"/" $HTML
