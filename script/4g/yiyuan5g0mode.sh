#!/bin/sh

/bin/sleep 35
cat /dev/ttyUSB2 &
/bin/sleep 2
/bin/echo "AT+QCFG=\"nat\",1" > /dev/ttyUSB2
/bin/sleep 2
/bin/echo "AT+CFUN=1,1" > /dev/ttyUSB2
/bin/sleep 35
cat /dev/ttyUSB2 &
/bin/sleep 2
/bin/echo "AT+QNETDEVCTL=2,3,1" > /dev/ttyUSB2
/bin/sleep 5
/sbin/udhcpc -fnq -i usb0 &

