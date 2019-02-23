# atmel 生产用服务器设置过程

## Version 0.01

## 虚拟机安装

在windows或Linux中首先安装虚拟机软件.  
虚拟机在[vmware官方网站](https://www.vmware.com/cn/products/workstation-player.html)下载`vmplayer`, 如果是在ubuntu/debian类系统中安装, 则需要额外安装内核头文件, 编译工具等: 

> 注意: 请下载使用 `VMware Workstation Player`, 而不是 `VMware Workstation`. 因为`vmplayer`是针对个人用户免费使用的, 而`workstation`无论是个人使用还是商用, 都需要购买许可. 实际上`vmplayer`商用的话, 也需要付费. 
>> 为何不用`oracle virtual box`? 因为`vbox`安装好后, 需要额外安装一些扩展驱动, 才能使用宿主系统中的硬件设备(比如USB设备), 设置起来比较麻烦. 如果您喜欢折腾, 使用`vbox`也是可以的.

在ubuntu/debian系统中安装`vmplayer`时, `vmplayer`需要将自己的驱动编译安装, 所以还需要先安装一些软件: 

```bash
  sudo apt-get install -y linux-headers-$(uname -r) dkms build-essential libusb-dev libusb-1.0-0-dev
```

安装好上述软件后, 则根据提示一步步安装即可. windows安装按照平时安装其他软件的安装方法, 不再赘述. 其他Linux或类Unix系统的安装方法没有测试, 请到网上自行搜索安装方法, 或到vmware官方网站查看.

## 虚拟机中的设置

- 虚拟机中需要安装的软件: 

```bash
    sudo apt-get install -y rpcbind nfs-kernel-server nfs-common tftpd-hpa tftp isc-dhcp-server cutecom minicom
```

- sam-ba刷机软件 
    - sam-ba支持9260-ek  

    - II型集中器脚本
        - shell脚本  
        ```shell
          ./sam-ba /dev/ttyACM0 9260-ii 9260_all.tcl
        ```
    
        - 9260_all.tcl:  

        ```tcl
          NANDFLASH::Init
          NANDFLASH::EraseAll
          send_file {NandFlash} "/nfs/linux/boot.bin" 0x0 0
          send_file {NandFlash} "/nfs/linux/image_sam_II.bin" 0x20000 0
        ```

    - I型集中器脚本
        - shell脚本  

        ```shell
          ./sam-ba /dev/ttyACM0 9260-ek 9260_I.tcl
        ```

        - 9260_I.tcl:  

        ```tcl
            NORFLASH::Init
            send_file {NorFlash} "/nfs/linux/image_sam_I.bin" 0 0
        ```

- dhcp-server  
  安装好`dhcp`服务端软件后, 需要进行一些设置:  
  - 配置`/etc/default/isc-dhcp-server`, 在最后加上虚拟机中的网卡名: `INTERFACES="ens33"`. 
    > 注意: 虚拟机的网络模式必须选择桥接模式(`Briged`), 否则外部设备无法通过交换机发现虚拟机的`dhcp`服务.
  - 配置`/etc/dhcp/dhcpd.conf`:  

    ```dhcpd.conf
      ddns-update-style none;

      option domain-name "example.org";
      option domain-name-servers 192.168.0.6;

      default-lease-time 600;
      max-lease-time 7200;

      log-facility local7;

      #配置子网网段, 并配置dhcp自动分配的网址范围
      subnet 192.168.0.0 netmask 255.255.255.224 {
        range 192.168.0.10 192.168.0.20;#地址池
        option routers 192.168.0.1;#分发默认网关
        default-lease-time 60;#默认租期时间(秒)
        max-lease-time 720;#最大租期时间(秒)
      }

    ```
  - 启动DHCP服务  

    ```bash
      sudo service isc-dhcp-server restart
      sudo netstat -uap#查看DHCP服务是否正常启动
    ```

- setmac服务端 
  用管理员用户执行: 
  ```bash
    echo "/nfs/linux/setmac &" >>/etc/rc.local
    chmod +x /etc/rc.local
  ```
  即可在系统启动时自动启动mac地址分配的服务端, 以供终端使用.

- nfs服务  
  要安装的软件已经包含在`虚拟机安装及设置`章节安装好了, 下面是具体配置: 
    - 切换至root用户, 新建`/nfs/linux/jzq_II_2014`目录, 配置`/etc/exports`文件: 
  ```bash
    mkdir -p /nfs/linux/jzq_II_2014 #集中器刷完boot镜像后要挂载的nfs文件系统

    chmod 777 -R
    echo "/nfs/linux/jzq_II_2014    *(rw,sync,no_root_squash)" >> /etc/exports #II型集中器的nfs根文件. 配置 "/nfs/linux/jzq_II_2014" 这个目录的权限, 不限制来源IP和用户权限
    echo "/nfs/linux/gw_jzq_2013    *(ro,sync,no_root_squash)" >> /etc/exports #I型集中器的nfs根文件.

  ```

- tftp服务  

- cutecom  
  cutecom安装好后, 在`device`里写上用于监控核心板的串口名, 一般是`/dev/ttyUSB0`, 选择波特率9600, 数据位8, 停止位1, 无校验.
> 注: 普通用户可能没有打开串口`/dev/ttyUSB0`的权限, 这时用管理员用户执行下面的命令, 并重启系统即可:  
    ```bash
        sudo echo "KERNEL==\"ttyUSB[0-9]*\", MODE=\"0666\"">/etc/udev/rules.d/70-ttyusb.rules
    ```

## 系统设置

- root 用户和管理员(ava)用户密码  
  root用户和ava用户都是 "admin123"
- 添加test用户并自动登陆

  ```bash
    adduser test
  ```
  设置用户密码后, 使用默认设置即可. test用户密码是1
- 添加桌面快捷方式  
  [Desktop Entry 语法标准](https://specifications.freedesktop.org/desktop-entry-spec/latest/)  
    以下是虚拟机中快捷方式的设置: 
 
    ```Desktop Entry
      [Desktop Entry]
      Version=1.0
      Type=Application
      Terminal=false
      StartupNotify=true
      Exec=gnome-terminal -x sh -c "cd /opt/tools/sam-ba_cdc_cdc_linux;./write-II-all.sh;echo \"write finished!!!\"; sleep 2"
      Name=9260-II
      Icon=/usr/share/icons/hicolor/48x48/status/application-running.png

    ```

## 各种内核, 软件, 脚本等存放位置

- II型集中器的相关文件  
    II型集中器没有Nor flash, sam-ba刷机阶段要先写一个qboot, 再刷一个内核
    - qboot程序存放在 `/nfs/linux/boot.bin`, sam-ba刷机第1个文件, 用于引导下一步的小内核.
    - 小内核放在`/nfs/linux/image_sam_II.bin`, sam-ba刷机第2个文件, 用于启动网络, 挂载服务器的nfs根文件, 初始化nand flash等.
    - 内核+根文件存放在 `/nfs/linux/jzq_II_2014/image/image_sam.bin`, sam-ba刷机重启后要复制的内核+根文件系统.
    - rcS启动文件  
        在`/nfs/linux/jzq_II_2014/etc/init.d/`目录中的`rcS`脚本, 是终端刷入小内核后的启动脚本, 应用程序的复制放在这里:  

        ```bash
          #!/bin/sh
          /bin/mount -t proc none /proc
          /bin/mount tmpfs /dev/shm -t tmpfs -o size=4m
          echo "format /dev/mtd1"
          /usr/sbin/flash_eraseall -q /dev/mtd1
          echo "format /dev/mtd2"
          /usr/sbin/flash_eraseall -q /dev/mtd2
          echo "format /dev/mtd3"
          /usr/sbin/flash_eraseall -j -q /dev/mtd3
          /bin/mount -t jffs2 /dev/mtdblock3  /nor
          echo "format /dev/mtd4"
          /usr/sbin/flash_eraseall -j -q /dev/mtd4
          /bin/mount -t jffs2 /dev/mtdblock4  /nand
          mkdir /nor/rc.d
          mkdir /nor/ppp
          mkdir /nor/ppp/peers
          mkdir /nor/ppp/chat
          mkdir /nor/config
          mkdir /nor/lib
          mkdir /nor/dev
          mkdir /nor/bin
          mkdir /nor/dhcp
          mkdir /nand/bin
          #376.1 app file
          #echo "write 376.1 to /nand/ "
          #cp /sbin/lib/*		/nor/lib/
          #cp /sbin/config/*	/nor/config/
          #cp /sbin/app/*		/nand/bin/
          #698 app file
          echo "write 698 to /nand/"
          mkdir /nor/init/
          cp /sbin/698/lib/*		/nor/lib/
          cp /sbin/698/config/*		/nor/config/
          cp /sbin/698/init/*		/nor/init/
          cp /sbin/698/app/*		/nand/bin/

          cp /sbin/tcpdump 	/nand/bin/
          cp /sbin/mux.sh 	/nor/bin/
          cp /sbin/gsmMuxd 	/nor/bin/
          cp /sbin/dhcp.conf	/nor/dhcp/

          cp /sbin/ppp/chap-secrets		/nor/ppp
          cp /sbin/ppp/gprs-connect-chat		/nor/ppp
          cp /sbin/ppp/gprs-disconnect-chat	/nor/ppp
          cp /sbin/ppp/pap-secrets		/nor/ppp
          cp /sbin/ppp/peers/disgprs		/nor/ppp/peers
          cp /sbin/ppp/peers/gprs			/nor/ppp/peers
          /bin/getmac
          chmod +x /nor/rc.d/mac.sh
          cp /etc/ip.sh /nor/rc.d/ip.sh
          #cp /etc/runapp.sh /nor/rc.d/runapp.sh

          #echo "write 376.1 rc.local to /dev/mtd1"
          #cp /etc/rc.local.3761 /nor/rc.d/rc.local

          echo "write 698 rc.local to /dev/mtd1"
          cp /etc/rc.local.698 /nor/rc.d/rc.local

          echo "write image_sam.bin to /dev/mtd1"
          nandwrite -p /dev/mtd1 /image/image_sam.bin 
          echo "write image_sam.bin to /dev/mtd2"
          nandwrite -p /dev/mtd2 /image/image_sam.bin
          hostname arm9
          sleep 3
          reboot

        ```
        > 从上面的脚本内容可以看出, 这是关于698终端相关程序和文件的复制, 如果要复制376.1相关程序和文件, 则将698相关语句注释后, 将376.1的相关语句去掉注释即可. 实际上在此脚本的目录里, 已有文件`rcS_698`和`rcS_3761`, 实际使用时, 只需用其中的一个文件覆盖`rcS`即可.
    - 应用程序文件  
      通过上述对`rcS`脚本的分析, 即可分别找到698相关文件和376.1相关文件的存放目录
- I型集中器的相关文件
    I型集中器有Nor flash, 不需要像II型集中器那样麻烦
    - 小内核放在`/nfs/linux/image_sam_I.bin`
    - 内核+根文件存放在`/nfs/linux/gw_jzq_2013/image/9260.cramfs_2013.bin`
    - `rcS`文件和应用程序文件的存放目录可用与II型集中器的同样的分析方法得到, 不再赘述.

## 终端的启动过程

1. boot阶段, 启动小内核, 通过`dhcp`请求一个IP地址, 获取IP地址后请求一个`MAC`地址.
1. 挂载服务器的对应`nfs`目录为根文件, 初始化Nand, 复制服务器根文件的内核镜像到nand.
1. 复制服务器的应用程序相关文件到nand和nor
1. 重启正常运行

## 终端的刷机过程

- 裸机刷机过程
    1. 先将核心板断电, 再短接`SDRAM`的3和4引脚, 然后上电. 短接3和4引脚的具体原因请参照 Atmel 9260 的数据手册, 里面的第11章讲解了芯片的启动过程, 至于为何短接的是`SDRAM`端引脚, 我猜想是因为9260的封装方式是`LFBGA`, 芯片焊接好以后, 只能在其引出到`SDRAM`线路上进行短接, 这个猜想有待查阅原理图进行验证.
    1. 上电后, 在虚拟机中运行 `lsusb` 命令: 

        ```bash
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