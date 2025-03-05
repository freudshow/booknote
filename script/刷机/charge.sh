#!/bin/bash

USB_PATH="/sys/class/power_supply/qcom-smbchg-usb"
MAX_CAPACITY=95
MIN_CAPACITY=40
CURRENT_CAPACITY=$(cat /sys/class/power_supply/qcom-battery/capacity)
echo 当前电量: $(cat /sys/class/power_supply/qcom-battery/capacity)
if [ $CURRENT_CAPACITY -ge $MAX_CAPACITY ]; then

    echo "当前电量高于 $MAX_CAPACITY%. 停止充电."
    echo 0 > $USB_PATH/input_current_limit 
elif [ $CURRENT_CAPACITY -le $MIN_CAPACITY ]; then
    echo "当前电量低于 $MIN_CAPACITY%. 开始充电."
    echo 300000 > $USB_PATH/input_current_limit
fi
