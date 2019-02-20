# atmel 生产用服务器设置过程

## 安装的软件

- 虚拟机安装及设置(包括外设的自动接管和手动接管)
  虚拟机在vmware官方网站下载vmplayer, 如果是在ubuntu/debian类系统中安装, 则需要额外安装内核头文件, 编译工具等: 

```bash
    sudo apt-get install -y linux-headers-$(uname -r) dkms git vim cscope ctags build-essential rpcbind nfs-kernel-server nfs-common libgmp-dev libmpfr-dev libmpc-dev binutils pkg-config autoconf automake libtool zlib1g-dev libsdl1.2-dev libtool-bin libglib2.0-dev libz-dev libpixman-1-dev libbsd-dev dirmngr tftpd-hpa tftp 
```

安装好上述软件后, 则根据提示一步步安装即可. 
windows安装按照平时安装其他软件步骤, 不再赘述. 其他Linux或类Unix系统的安装方法没有测试, 请到网上自行搜索安装方法, 或到vmware官方网站查看.
- sam-ba刷机软件
- dhcp-server
  安装命令: 

  ```bash
    apt-get install -y isc-dhcp-server
  ```
  
- setmac服务端
- nfs服务
  要安装的软件已经包含在<虚拟机安装及设置>章节安装好了, 下面是具体配置: 
  - 切换至root用户, 新建`/nfs/linux/jzq_II_2014`目录, 配置`/etc/exports`文件: 
  ```bash
    mkdir -p /nfs/linux/jzq_II_2014 #集中器刷完boot镜像后要挂载的nfs文件系统

    chmod 777 -R
    echo "/nfs/linux/jzq_II_2014    *(rw,sync,no_root_squash)" >> /etc/exports #配置 "/nfs/linux/jzq_II_2014" 这个目录的权限, 不限制来源IP和用户权限


  ```
- tftp服务
  
## 系统设置

- root 用户和管理员(ava)用户密码
  root用户和ava用户都是 "admin123"
- 添加test用户并自动登陆

  ```bash
    adduser test
  ```
  设置用户密码后, 使用默认设置即可. test用户密码是1
- 添加桌面快捷方式
- 软件设置
    - 文件路径
        - 内核文件路径
        - 系统设置文件路径
        - 应用软件路径
    - 376.1/698软件设置区别
- sam-ba软件相关设置

## 刷机过程

- 裸机刷机过程
    1. 先将核心板断电, 再短接9260的3和4引脚, 然后上电
    2. 上电后, 在虚拟机中运行 `lsusb` 命令: 

        ```bash
            root@ubuntu:/home/test/Desktop# lsusb 
            Bus 001 Device 005: ID 10c4:ea60 Cygnal Integrated Products, Inc. CP210x UART Bridge / myAVR mySmartUSB light
            Bus 001 Device 006: ID 03eb:6124 Atmel Corp. at91sam SAMBA bootloader
            Bus 001 Device 004: ID 0e0f:0008 VMware, Inc. 
            Bus 001 Device 003: ID 0e0f:0002 VMware, Inc. Virtual USB Hub
            Bus 001 Device 002: ID 0e0f:0003 VMware, Inc. Virtual Mouse
            Bus 001 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
            root@ubuntu:/home/test/Desktop# lsusb 
            Bus 001 Device 005: ID 10c4:ea60 Cygnal Integrated Products, Inc. CP210x UART Bridge / myAVR mySmartUSB light
            Bus 001 Device 006: ID 03eb:6124 Atmel Corp. at91sam SAMBA bootloader
            Bus 001 Device 004: ID 0e0f:0008 VMware, Inc. 
            Bus 001 Device 003: ID 0e0f:0002 VMware, Inc. Virtual USB Hub
            Bus 001 Device 002: ID 0e0f:0003 VMware, Inc. Virtual Mouse
            Bus 001 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
            root@ubuntu:/home/test/Desktop# 

        ```

        当看到`at91sam SAMBA bootloader`字样后, 表明 9260 芯片处于编程模式, 可以开始刷机了.
  1. 以test用户运行 `/opt/tools/sam-ba_cdc_cdc_linux/write-II-all.sh`, 或者直接点击桌面的 `9260-II` 图标, 即开始刷机
- 已运行操作系统的终端刷机过程
  已运行正常的操作系统的终端, 可以用`telnet`或者`ssh`登陆, 运行`flash_eraseall /dev/mtd0`命令, 将mtd0数据全部擦除, 然后运行`reboot`重启, 即可刷机