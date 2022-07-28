# 交叉编译`Paho MQTT C`库

## 交叉编译`OpenSSL`

`paho.mqtt.c`库需要用到`OpenSSL`库，所以要先编译`OpenSSL`

1. 下载`OpenSSL`[源代码](https://www.openssl.org/source/openssl-1.1.1q.tar.gz)
2. 解压后，使用`./config no-asm shared --prefix=$PWD/install --cross-compile-prefix=arm-linux-gnueabihf-`配置编译环境
3. 修改`Makefile`，去掉`-m64`，`-m32`选项
4. 运行`make`和`make install`，就将库文件安装到当前目录的`install`下了

## 交叉编译`paho.mqtt.c`

1. 下载[`paho.mqtt.c`](https://github.com/eclipse/paho.mqtt.c/releases), 选择`Source code (tar.gz)`
2. 解压`tar xzvf paho.mqtt.c-1.3.10.tar.gz && cd paho.mqtt.c-1.3.10`
3. 修改`Makefile`，在`CC ?= gcc`(大约在126行)后面加上`CFLAGS += -I../openssl-1.1.1q/install/include`和`LDFLAGS += -L../openssl-1.1.1q/install/lib`两行
4. 运行`make CC=arm-linux-gnueabihf-gcc`，等待编译结束，库文件就放在`paho.mqtt.c-1.3.10/build/output`中了
