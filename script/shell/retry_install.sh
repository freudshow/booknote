#!/bin/bash

# 初始化尝试次数
attempts=0
# 最大尝试次数，可以根据需求修改
max_attempts=10

while true; do
    # 增加尝试次数
    ((attempts++))
    echo "第 $attempts 次尝试运行命令..."

    # 运行目标命令
    if curl -fsSL https://ollama.com/install.sh | sh; then
        echo "命令运行成功！"
        break
    else
        if [ $attempts -ge $max_attempts ]; then
            echo "已达到最大尝试次数 $max_attempts，退出脚本。"
            break
        else
            echo "命令运行失败，等待 5 秒后进行下一次尝试..."
            sleep 5
        fi
    fi
done    