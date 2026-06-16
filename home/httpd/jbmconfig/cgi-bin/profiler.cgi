#!/bin/bash

# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

# Registration directory for profile handlers
PROFILES_DIR="/var/run/profile"

# Run for at most this many seconds
TIME_RUN=300
TIME_INIT="$(date +%s)"

# Flag to indicate whether a profile handler is running
PROFILING=

# Cleared by trap to signal script to exit
RUN_FLAG=1

# Exit gracefully for signal
quit() {
	RUN_FLAG=
	#logger -t "profiler[$$]" "Caught signal"
}
trap quit HUP INT TERM

time_diff() {
	local a="$1"
	local b="$2"
	local d="$((b-a))"

	# Using absolute value difference makes us resistant to time change.
	if [ "$d" -lt 0 ]; then
		echo "$((-1*d))"
	else
		echo "$d"
	fi
}

echo -ne "Content-type: text/plain\n\n"

# Send initial state - socket needs a minimal amount of data to start moving bits
[ "$(ls "$PROFILES_DIR")" ] && echo 1 || echo 0

state=
time_now=
wait_code=
while [ "$RUN_FLAG" ]; do
	time_now="$(date +%s)"

	[ "$(ls "$PROFILES_DIR")" ] && state=1 || state=0

	# wait_code == 2 means inotifywait hit timeout instead of seeing event.
	if [ "$state" != "$PROFILING" -o "$wait_code" == 2 ]; then
		echo "$state"
		PROFILING="$state"
	fi

	# This should break if "-lt" errors, too. Just in case.
	if ! [ $(time_diff "$TIME_INIT" "$time_now") -lt "$TIME_RUN" ]; then
		#logger -t "profiler[$$]" "Run-time expired"
		break
	fi

	inotifywait --event create --event delete --timeout 30 "$PROFILES_DIR" &>/dev/null
	wait_code=$?
done
