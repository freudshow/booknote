#!/bin/sh

vID=1782

moduleStart(){
/bin/echo "moduleStart"
#/bin/sleep 10
  #/bin/echo 1 > /sys/class/leds/4G_RST1/brightness
  /bin/echo 0 > /sys/class/leds/4G_RST1/brightness
#/bin/sleep 2
  /bin/echo 0 > /sys/class/leds/4G_ONOFF1/brightness
  /bin/sleep 2
  /bin/echo 1 > /sys/class/leds/4G_ONOFF1/brightness
  /bin/usleep 2500000
  /bin/echo 0 > /sys/class/leds/4G_ONOFF1/brightness
  /bin/sleep 10
}
moduleReset(){
/bin/echo "moduleReset"
/bin/echo 1 > /sys/class/leds/4G_RST1/brightness
/bin/sleep 1
/bin/echo 0 > /sys/class/leds/4G_RST1/brightness
/bin/sleep 10
}

/usr/bin/killall udhcpc

no=$(/usr/bin/lsusb | /bin/grep "$vID" | /usr/bin/wc -l | /usr/bin/cut -b 1)
echo "no=$no"
if [ "$no" = "0" ]; then
  moduleStart
else
  moduleReset
fi

isSIM=$(/bin/echo -e "AT+CPIN?\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 500  | /bin/grep "READY" | /usr/bin/wc -l | /usr/bin/cut -b 1)

if [ "$isSIM" = "0" ]; then
   /bin/echo "no sim card!!!"
   exit 0
fi

/bin/echo -e "AT+GTUSBMODE=32\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 500

/bin/echo -e "AT+GTRNDIS=1,1\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 500
/bin/sleep 2

/sbin/udhcpc -q -i usb0 &
