# i.MX6ULL Docker 开发环境搭建指南

## 1. 项目概述

### 1.1 背景

i.MX6ULL 开发板原始系统基于 Yocto 构建（Freescale i.MX Release Distro 4.1.15-2.0.0），使用 busybox + SysVinit，无包管理器（无 apt/dpkg/opkg），缺少编译器、调试器和常用开发工具。为方便在开发板上进行交叉调试、CAN/RS485/I2C/GPIO/SPI 等外设开发，构建了一个基于 `debian:bullseye` 的 ARM 32 位 Docker 镜像，集成完整的开发工具链和外设调试工具。

### 1.2 技术方案

由于开发板是 ARM 32 位（ARMv7），而构建主机是 x86_64，无法直接使用 Dockerfile 中的 `RUN` 指令运行 ARM 二进制。因此采用 **多阶段构建** 方案：

1. **第一阶段**（`pkg-downloader`）：在 x86_64 Debian 容器中，通过 `apt-get download -o APT::Architecture=armhf` 原生下载所有 armhf 架构的 `.deb` 包
2. **第二阶段**（最终镜像）：基于 `debian:bullseye`（`--platform linux/arm/v7`），使用 QEMU 用户态模拟执行 ARM 二进制，将下载的 `.deb` 包离线安装

### 1.3 镜像信息

| 项目 | 值 |
|------|-----|
| 镜像名 | `imx6ull-dev:latest` |
| 基础镜像 | `debian:bullseye` (ARM v7) |
| 镜像大小 | ~1.06 GB |
| 构建主机 | x86_64 Linux |
| 目标平台 | ARM 32-bit (ARMv7) |
| 编译器 | gcc/g++ 10.2.1 |
| 调试器 | gdb 10.1 + gdbserver |
| Python | 3.9.2 |

---

## 2. 环境准备

### 2.1 安装 Docker

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
# 重新登录或执行 newgrp docker 生效
```

### 2.2 注册 QEMU 用户态模拟（关键步骤）

在 x86_64 主机上构建 ARM 镜像，必须注册 QEMU binfmt_misc，使内核能透明执行 ARM 二进制：

```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

**注意：**
- 每次重启主机或 Docker 服务后，需要重新执行此命令
- `--reset -p yes` 会重置所有 binfmt_misc 注册并自动注册 QEMU 模拟器
- 如果构建时报 `exec format error`，说明 QEMU 未正确注册

验证注册是否成功：

```bash
# 检查 binfmt_misc 是否注册
ls /proc/sys/fs/binfmt_misc/ | grep qemu-arm
# 应该看到 qemu-arm-static 条目
cat /proc/sys/fs/binfmt_misc/qemu-arm-static
# 应该输出 enabled
```

### 2.3 DaoCloud 镜像加速（国内环境可选）

如果网络访问 Docker Hub 或 Debian 官方源较慢，可配置 DaoCloud 加速器：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://docker.m.daocloud.io"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**已知限制：** DaoCloud 镜像加速器屏蔽了 `arm32v7/*` 系列官方镜像（如 `arm32v7/debian:bullseye` 会返回 403），但多架构标签 `debian:bullseye`（带 `--platform linux/arm/v7`）可以正常拉取。因此 Dockerfile 中使用 `debian:bullseye` 而非 `arm32v7/debian:bullseye`。

---

## 3. 文件结构

```
docker-imx6ull/
├── Dockerfile           # 多阶段构建文件（核心）
├── build.sh             # 一键构建脚本（含 QEMU 注册）
├── build-base.sh        # 从原始 rootfs 构建基础镜像（备选方案）
├── run.sh               # 一键运行脚本（含设备挂载）
├── docker-compose.yml   # Docker Compose 配置
├── imx6ull-env.sh       # 容器内辅助命令脚本
├── prepare.sh           # 将开发板文件提取到 workspace
└── README.md            # 本文档
```

辅助文件（SD 卡提取）：

```
自制文件系统/target/
├── rootfs-console.tar.bz2      # 原始 Yocto rootfs（59MB）
├── modules.tar.bz2             # 内核模块（4.1.15，123 个文件）
├── okmx6ull-s-nand.dtb         # 设备树二进制
├── zImage                      # 内核镜像
└── rootfs-console/             # 解压后的 rootfs 目录
```

---

## 4. 构建镜像

### 4.1 一键构建（推荐）

```bash
cd /home/floyd/soft/tf_iso/docker-imx6ull/
chmod +x build.sh run.sh prepare.sh imx6ull-env.sh
./build.sh
```

`build.sh` 会自动执行：
1. 检查 Docker 服务是否运行
2. 注册 QEMU 用户态模拟（`docker run --rm --privileged multiarch/qemu-user-static --reset -p yes`）
3. 执行 `docker build --platform linux/arm/v7 -t imx6ull-dev:latest .`

### 4.2 手动构建

如果 `build.sh` 失败，可以分步手动执行：

```bash
# 步骤 1：注册 QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# 步骤 2：构建镜像
cd /home/floyd/soft/tf_iso/docker-imx6ull/
docker build --platform linux/arm/v7 -t imx6ull-dev:latest .
```

### 4.3 使用 Docker Compose 构建

```bash
docker compose build
```

### 4.4 Dockerfile 详解

Dockerfile 采用两阶段构建，核心逻辑如下：

**第一阶段：`pkg-downloader`（x86_64 原生）**

```dockerfile
FROM --platform=linux/amd64 debian:bullseye AS pkg-downloader
```

- 在 x86_64 上运行，不使用 QEMU，速度快
- 添加 armhf 架构支持：`dpkg --add-architecture armhf`
- 配置 Debian Bullseye 的 armhf 和 amd64 软件源
- 通过 `apt-get download -o APT::Architecture=armhf` 下载所有 armhf `.deb` 包
- 分两批下载：第一批是主要工具和依赖，第二批是编译器和调试器的运行时库

**第二阶段：最终镜像（ARM v7）**

```dockerfile
FROM --platform=linux/arm/v7 debian:bullseye
```

- 基于 `debian:bullseye`，通过 `--platform` 强制拉取 ARM v7 变体
- 通过 QEMU 用户态模拟执行 `RUN` 中的命令
- 将第一阶段下载的 `.deb` 包 `COPY` 到容器中
- 使用 `dpkg -i --force-depends` 离线安装所有包（跳过依赖检查，因为所有依赖都已包含）
- 修复 python3.9 二进制：由于 `dpkg -i --force-depends` 可能跳过 postinst 脚本，手动用 `dpkg-deb -x` 提取 `/usr/bin/python3.9`
- 创建符号链接：`gcc` → `gcc-10`，`g++` → `g++-10`，`python` → `python3.9`
- 配置动态链接器路径：`ldconfig` 加载 `/usr/lib/arm-linux-gnueabihf`
- 生成 UTF-8 locale
- 复制 `imx6ull-env.sh` 到容器中

### 4.5 构建时包含的工具清单

**编译器：**
- gcc 10.2.1、g++ 10.2.1、make 4.3、cmake 3.18.4
- binutils、pkg-config、automake、autoconf、libtool

**调试器：**
- gdb 10.1、gdbserver、strace 5.10、valgrind 3.16.1

**语言环境：**
- python3 3.9.2、python3-pip
- git 2.30.2、perl 5.32

**外设工具：**
- I2C：i2c-tools（i2cdetect/i2cget/i2cset/i2cdump）
- CAN：can-utils（candump/cansend/cangen/canplayer）
- GPIO：libgpiod（gpiodetect/gpioinfo/gpioset/gpioget）
- 串口：minicom 2.8、picocom
- USB：usbutils（lsusb）
- 网络：iproute2（ip）、tcpdump 4.99、nmap、ethtool 5.9
- 无线：wireless-tools、wpasupplicant、hostapd、iw

**终端复用：**
- tmux 3.1c、screen 4.08

**开发库：**
- libssl-dev、libcurl4-openssl-dev、libncurses5-dev
- libreadline-dev、libsqlite3-dev、zlib1g-dev
- libi2c-dev、libudev-dev、libusb-1.0-0-dev
- libbluetooth-dev、libgpiod-dev

---

## 5. 运行容器

### 5.1 一键运行（推荐）

```bash
./run.sh          # 交互式进入容器
./run.sh -it      # 同上
./run.sh -d       # 后台运行
```

`run.sh` 自动执行以下配置：
- `--privileged`：赋予容器完整设备访问权限（操作 GPIO/CAN/I2C 等必须）
- `--network host`：共享主机网络栈
- `-v /dev:/dev`：挂载主机设备目录（串口、I2C、SPI 等）
- `-v /proc:/proc`：挂载主机 proc 文件系统
- `-v /sys:/sys`：挂载主机 sysfs（GPIO/设备信息）
- `-v ./workspace:/workspace`：挂载工作目录（代码编辑、文件交换）
- 自动加载 `imx6ull-env.sh` 辅助命令

### 5.2 手动运行

```bash
# 基本交互式运行
docker run --rm -it \
    --platform linux/arm/v7 \
    --privileged \
    --network host \
    -v /dev:/dev \
    -v /proc:/proc \
    -v /sys:/sys \
    -v $(pwd)/workspace:/workspace \
    imx6ull-dev:latest

# 挂载特定设备（如串口）
docker run --rm -it \
    --platform linux/arm/v7 \
    --privileged \
    --device /dev/ttyUSB0:/dev/ttyUSB0 \
    -v $(pwd)/workspace:/workspace \
    imx6ull-dev:latest
```

### 5.3 使用 Docker Compose 运行

```bash
# 交互式
docker compose run --rm imx6ull-dev

# 后台
docker compose up -d

# 停止
docker compose down
```

### 5.4 运行时参数说明

| 参数 | 作用 | 是否必须 |
|------|------|----------|
| `--privileged` | 允许访问所有设备和系统调用 | 操作硬件时必须 |
| `--platform linux/arm/v7` | 指定 ARM v7 架构 | 必须 |
| `-v /dev:/dev` | 访问串口/I2C/SPI/GPIO 设备节点 | 操作硬件时必须 |
| `-v /proc:/proc` | 查看进程和系统信息 | 推荐 |
| `-v /sys:/sys` | 访问 sysfs 设备属性 | 推荐 |
| `--network host` | 使用主机网络（ping/ifconfig） | 推荐 |
| `-v ./workspace:/workspace` | 代码和文件交换 | 推荐 |

---

## 6. 容器内使用

### 6.1 加载辅助命令

进入容器后，执行以下命令加载外设调试辅助函数：

```bash
source /usr/local/bin/imx6ull-env.sh
```

加载后可用的命令：

| 命令 | 说明 |
|------|------|
| `rs485-list` | 列出所有串口设备 |
| `rs485-monitor [port] [baud]` | 打开串口监控（默认 /dev/ttymxc1 9600） |
| `i2c-scan [bus]` | 扫描 I2C 总线上的设备 |
| `i2c-read [bus] [addr] [reg]` | 读取 I2C 设备寄存器 |
| `i2c-write [bus] [addr] [reg] [val]` | 写入 I2C 设备寄存器 |
| `spi-list` | 列出 SPI 设备 |
| `spi-test [dev] [speed]` | SPI 回环测试 |
| `can-setup [iface] [bitrate]` | 配置 CAN 接口（默认 can0 500kbps） |
| `can-monitor [iface]` | 监听 CAN 帧 |
| `can-send [iface] [msg]` | 发送 CAN 帧 |
| `can-test [iface] [count]` | CAN 发送测试 |
| `gpio-list` | 列出 GPIO 芯片 |
| `gpio-info [chip]` | 查看 GPIO 芯片引脚信息 |
| `gpio-set [chip] [line] [val]` | 设置 GPIO 电平 |
| `gpio-get [chip] [line]` | 读取 GPIO 电平 |
| `net-status` | 显示网络接口状态 |
| `net-eth0 [ip] [gw]` | 快速配置 eth0 |
| `hw-detect` | 一键检测所有已识别硬件 |

### 6.2 常用场景

**RS485/串口调试：**

```bash
source /usr/local/bin/imx6ull-env.sh
rs485-list                          # 查看可用串口
rs485-monitor /dev/ttymxc1 115200   # 打开串口监控
```

**I2C 设备调试：**

```bash
source /usr/local/bin/imx6ull-env.sh
i2c-scan 1                           # 扫描 I2C-1 总线
i2c-read 1 0x50 0x00                 # 读取 AT24C EEPROM
i2c-write 1 0x50 0x00 0xAA          # 写入数据
```

**CAN 总线调试：**

```bash
source /usr/local/bin/imx6ull-env.sh
can-setup can0 500000                # 配置 CAN0 500kbps
can-monitor can0                     # 监听 CAN 帧
can-send can0 123#DEADBEEF           # 发送一帧
can-test can0 100                    # 发送 100 帧测试
```

**GPIO 调试：**

```bash
source /usr/local/bin/imx6ull-env.sh
gpio-list                            # 查看 GPIO 芯片
gpio-info 0                          # 查看 GPIO-0 引脚信息
gpio-set 0 5 1                       # 将 GPIO0 的第 5 引脚拉高
gpio-get 0 5                         # 读取 GPIO0 的第 5 引脚
```

**编译和调试：**

```bash
# 编译
gcc -g -o hello hello.c
make

# 远程调试
gdbserver :2345 ./hello
# 在另一个终端
arm-linux-gnueabihf-gdb hello
(gdb) target remote <board-ip>:2345
(gdb) break main
(gdb) continue
```

### 6.3 文件交换

容器挂载了 `./workspace` 目录到容器内 `/workspace`，可直接在宿主机编辑文件：

```bash
# 宿主机上放置源码
cp my_project.c docker-imx6ull/workspace/

# 容器内编译
cd /workspace
gcc -g -o my_project my_project.c
```

---

## 7. 准备开发板文件

如果需要将原始开发板的内核模块、设备树等文件提取到 workspace：

```bash
cd /home/floyd/soft/tf_iso/docker-imx6ull/
./prepare.sh
```

这会将以下文件从 SD 卡镜像复制到 `workspace/`：

```
workspace/
├── board-modules/lib/modules/    # 内核模块（4.1.15）
├── board-dtb/okmx6ull-s-nand.dtb # 设备树二进制
├── board-rootfs-libs/             # 开发板特有库文件
└── board-udev/                    # udev 规则
```

---

## 8. 从原始 rootfs 构建基础镜像（备选方案）

如果需要直接使用从开发板导出的 rootfs（而非 `debian:bullseye`），可使用 `build-base.sh`：

```bash
cd /home/floyd/soft/tf_iso/docker-imx6ull/
./build-base.sh
```

此脚本执行 `docker import rootfs-console.tar.bz2 imx6ull-base:latest`，将 Yocto rootfs 导入为 Docker 基础镜像。

**注意：** 该基础镜像是精简的 Yocto 系统（无包管理器、无编译器），需要额外的定制才能用于开发。当前主要方案是使用 `debian:bullseye` 基础镜像 + 离线安装 armhf 包。

---

## 9. 镜像导出与传输

### 9.1 导出镜像为 tar 文件

```bash
# 导出镜像
docker save imx6ull-dev:latest > imx6ull-dev.tar

# 压缩
gzip -9 imx6ull-dev.tar
```

### 9.2 在其他主机导入

```bash
# 导入
docker load < imx6ull-dev.tar.gz
# 或
gunzip -c imx6ull-dev.tar.gz | docker load
```

### 9.3 传输到开发板（通过 scp）

```bash
# 从构建主机传输到开发板
scp imx6ull-dev.tar.gz root@<board-ip>:/tmp/

# 在开发板上导入
docker load < /tmp/imx6ull-dev.tar.gz
```

---

## 10. 故障排除

### 10.1 QEMU binfmt_misc 未注册

**现象：** 构建时报 `exec format error`

**解决：**

```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

### 10.2 DaoCloud 镜像加速器 403

**现象：** `arm32v7/debian:bullseye` 拉取失败，返回 403

**解决：** Dockerfile 中使用 `debian:bullseye`（多架构标签）替代 `arm32v7/debian:bullseye`，并指定 `--platform linux/arm/v7`

### 10.3 python3 命令找不到

**原因：** `dpkg -i --force-depends` 跳过了包的 postinst 脚本，`/usr/bin/python3.9` 未正确安装

**解决：** Dockerfile 中通过 `dpkg-deb -x` 手动提取 `python3.9-minimal` 包中的 `/usr/bin/python3.9` 二进制文件

### 10.4 共享库缺失

**现象：** 运行程序时报 `error while loading shared libraries: libXXX.so: cannot open shared object file`

**解决：** 在 Dockerfile 的 `apt-get download` 中添加对应的库包，并确保 `ldconfig` 已运行

已知已解决的缺失库：
- `libi2c0`（i2c-tools 依赖）
- `libdbus-1-3`（蓝牙/无线工具依赖）
- `libmnl0`（网络工具依赖）
- `libtinfo6`（终端信息库）
- `libusb-1.0-0`（lsusb 依赖）
- `libbpf0`（ip 命令依赖）
- `libbsd0`（ip 命令依赖）
- `libmd0`（libbsd 依赖）
- `libutempter0`（tmux 依赖）
- `libcap2`（ip 命令依赖）
- `libevent-2.1-7`（tmux 依赖）

### 10.5 cmake "Could not find CMAKE_ROOT"

**现象：** `cmake --version` 正常但运行 cmake 构建时报错

**原因：** `cmake-data` 包中的模块目录未正确安装

**解决：** 已在 Dockerfile 中添加 `cmake-data` 包下载。如仍报错，在容器内检查：

```bash
ls /usr/share/cmake-3.18/Modules/
# 如缺失，重新安装：
apt-get install -y cmake-data
```

### 10.6 docker compose 报 platform 错误

**现象：** `FromPlatformFlagConstDisallowed` 警告

**解决：** 这是警告而非错误，镜像正常构建。如需消除，可在 compose 文件中将 `platform` 移到 `docker compose run --platform linux/arm/v7` 命令行参数中。

---

## 11. 注意事项

1. **QEMU 模拟性能**：容器内的 ARM 二进制通过 QEMU 用户态模拟执行，编译速度比原生慢约 5-10 倍。大规模编译建议考虑交叉编译方案。

2. **`--privileged` 安全风险**：该参数赋予容器几乎等同于宿主机的权限，仅在可信环境中使用。

3. **设备访问**：操作硬件时，容器需要能够访问宿主机的设备节点。`--privileged` + `-v /dev:/dev` 可满足大部分需求。对于特定设备，也可使用 `--device /dev/xxx` 精确挂载。

4. **内核模块**：如果需要在容器内加载/卸载内核模块（`insmod`/`rmmod`），需要在宿主机上操作，容器内无法直接操作宿主机内核。

5. **网络配置**：`--network host` 使容器直接使用宿主机网络栈，适合嵌入式开发中的网络调试场景。

6. **locale 警告**：容器启动时可能显示 `setlocale: LC_ALL: cannot change locale (en_US.UTF-8)`，这是因为 locale 数据未完全生成，不影响功能使用。如需消除，可在 Dockerfile 中安装 `locales` 包并取消注释 `en_US.UTF-8`。

7. **镜像大小**：最终镜像约 1.06GB。如需减小体积，可移除不需要的工具包（如 nmap、bluez、wireless-tools 等），或使用多阶段构建只保留运行时库。
