#!/bin/sh

while [ 1 ]
do
	count=`ps |grep e9361app |grep -v grep |wc -l`

	if [ $count -lt 1 ]
    then
        echo "********************************************"
		echo "              e9361app stopped, restarting!"
		echo "********************************************"
		/home/sysadm/src/e9361app&
		echo "********************************************"
		echo "              e9361app restarted!"
		echo "********************************************"
		sleep 5
	fi
	sleep 10
done
