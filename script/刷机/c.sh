#!/usr/bin/env bash

USB_INPUT_CURRENT_LIMIT_PATH="/sys/class/power_supply/qcom-smbchg-usb/input_current_limit"
MAX_BATTERY_CAPACITY=95
MIN_BATTERY_CAPACITY=40
CURRENT_CAPACITY=$(cat /sys/class/power_supply/qcom-battery/capacity)
BATTERY_STATUS=$(cat /sys/class/power_supply/qcom-battery/status)

CHARGING_LIMIT=300000

PUSH_SCRIPT_PATH=/PATH/TO/FILE

# 不要删注释也不要删下一行
# CURRENT_STATUS=${BATTERY_STATUS}

echo "当前电量: ${CURRENT_CAPACITY}"
echo "电池状态: ${BATTERY_STATUS}"

if [ ${CURRENT_CAPACITY} -ge ${MAX_BATTERY_CAPACITY} ]; then
    echo "当前电量高于 ${MAX_BATTERY_CAPACITY}%. 停止充电."
    echo 0 > ${USB_INPUT_CURRENT_LIMIT_PATH} 
elif [ ${CURRENT_CAPACITY} -le ${MIN_BATTERY_CAPACITY} ]; then
    echo "当前电量低于 ${MIN_BATTERY_CAPACITY}%. 开始充电."
    echo ${CHARGING_LIMIT} > ${USB_INPUT_CURRENT_LIMIT_PATH}
fi

sleep 3
CURRENT_STATUS=$(cat /sys/class/power_supply/qcom-battery/status)

# echo CURRENT_STATUS: ${CURRENT_STATUS}

if [ ! "$BATTERY_STATUS" = "$CURRENT_STATUS" ]; then
    bash ${PUSH_SCRIPT_PATH}
    # echo push
fi

