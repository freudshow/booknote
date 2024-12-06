#get CSQ
echo -e "AT+CSQ?\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 50
#result
AT+CSQ?


+CSQ: 31,99



OK

#get vendor
echo -e "AT+COPS?\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 50

#result
AT+COPS?


+COPS: 0,0,"CHINA MOBILE",7



OK

#get sim card state
echo -e "AT+CPIN?\r\n" | /usr/bin/microcom -s 9600 /dev/ttyUSB0 -t 50

#result
AT+CPIN?


+CPIN: READY



OK
