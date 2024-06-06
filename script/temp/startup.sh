#!/bin/bash

# process name
PROCESS_NAME="e9361app"

# check if exists this process
check_process() {
    # using pgrep to check if exists this process
    if pgrep -x "$PROCESS_NAME" > 0
    then
        echo "$PROCESS_NAME is running"
        return 1
    else
		echo "$PROCESS_NAME is Not running"
        echo "starting $PROCESS_NAME..."
		/home/sysadm/src/$PROCESS_NAME&
		echo "$PROCESS_NAME started."
        return 0
    fi
}

while true
do
    check_process
    # wait a seconds
    sleep 5
done