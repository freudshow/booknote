# 常用系统配置及命令

## 文件排重命令

```bash
    find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

## 文件排重工具

`fdupes`:

```bash
    $sudo apt-get install fdupes
    $fdupes -r + directory #递归搜索重复文件
    #使用-S选项来查看某个文件夹内找到的重复文件的大小
    $fdupes -Sr /to_directory/
    #删除重复文件, 同时保留一个副本, 你可以使用-d选项
    $fdupes -d /to_directory/
    #使用-f选项来忽略每个匹配集中的首个文件
    $fdupes -f /to_directory/
```

## Linux系统备份与还原

### 备份系统

- 首先成为root用户：

```bash
    $sudo su
```

- 然后进入文件系统的根目录

```bash
    # cd /
```

- 备份系统

```bash
    # tar cvPjf backup.tar.bz2 --exclude=/proc --exclude=/lost+found --exclude=/backup.tar.bz2 --exclude=/mnt --exclude=/media --exclude=/boot --exclude=/etc/fstab --exclude=/var --exclude=/dev --exclude=/tmp --exclude=/sys /
```

### 恢复系统

- 将backup.tar.bz2放到根目录, 使用下面的命令来恢复系统

```bash
    #tar xvPjf backup.tar.bz2 -C /
```

- 恢复命令结束时, 别忘了重新创建那些在备份时被排除在外的目录:

```bash
    # mkdir proc
    # mkdir lost+found
    # mkdir mnt
    # mkdir sys
```

## sqlite3 导出数据到csv

```bash
#每次导出50行, limit后是行偏移量
sqlite3 -header -csv linyi.db "select * from ly order by '序号' limit 50 offset 4300;">4301.csv
```

## debian 安装 nodejs

参考[Debian9安装最新版Nodejs和NPM](https://www.5yun.org/15395.html)

- 添加Node.js PPA  

最新版安装命令:

```bash
    curl -sL https://deb.nodesource.com/setup_9.x | sudo bash -
```

  安装LTS长期维护版:

```bash
    curl -sL https://deb.nodesource.com/setup_8.x |  sudo bash -
```

- 安装Node.js和NPM

```bash
    apt-get install nodejs
```

- To install the Yarn package manager, run:

``` bash
     curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
     echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
     sudo apt-get update && sudo apt-get install yarn
```

## debian/Ubuntu系统安装后要做的事情

### 配置软件源为中科大软件源

用root账号在/etc/apt/sources.list中把软件源修改为：

    deb https://mirrors.ustc.edu.cn/debian/ stretch main contrib non-free
    deb-src https://mirrors.ustc.edu.cn/debian/ stretch main contrib non-free
    
    deb https://mirrors.ustc.edu.cn/debian/ stretch-updates main contrib non-free
    deb-src https://mirrors.ustc.edu.cn/debian/ stretch-updates main contrib non-free
    
    deb https://mirrors.ustc.edu.cn/debian/ stretch-backports main contrib non-free
    deb-src https://mirrors.ustc.edu.cn/debian/ stretch-backports main contrib non-free
    
    deb https://mirrors.ustc.edu.cn/debian-security/ stretch/updates main contrib non-free
    deb-src https://mirrors.ustc.edu.cn/debian-security/ stretch/updates main contrib non-free

    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch main contrib non-free
    deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch main contrib non-free

    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-updates main contrib non-free
    deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-updates main contrib non-free

    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-backports main contrib non-free
    deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-backports main contrib non-free

    deb https://mirrors.tuna.tsinghua.edu.cn/debian-security stretch/updates main contrib non-free
    deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security stretch/updates main contrib non-free

### 让apt-get支持https开头的软件源

sudo apt-get install -y apt-transport-https

### 普通用户使用sudo命令, 不再需要输入密码

把下面的配置写入到 /etc/sudoers, yourname替换为自己的用户名, 下同

```bash
    yourname    ALL=(ALL) NOPASSWD: NOPASSWD: ALL
```

### 查看debian的版本号

cat /etc/debian_version

### 安装常用软件

```bash
    sudo apt-get install -y linux-headers-$(uname -r) dkms caja-open-terminal git vim cscope ctags build-essential rpcbind nfs-kernel-server nfs-common libgmp-dev libmpfr-dev libmpc-dev binutils pkg-config autoconf automake libtool zlib1g-dev libsdl1.2-dev libtool-bin libglib2.0-dev libz-dev libpixman-1-dev libbsd-dev dirmngr tftpd-hpa tftp graphviz emacs common-lisp-controller slime curl curlftpfs pppoe pppoeconf
```

### Ubuntu安装Mate desktop

```bash
    sudo apt install -y ubuntu-mate-core
    sudo apt install -y ubuntu-mate-desktop
    sudo apt install -y ubuntu-mate*
```

### git 常用设置

```bash
    git config --global user.name "s_baoshan"
    git config --global user.email "s_baoshan@163.com"
    git config --global alias.co checkout
    git config --global alias.br branch
    git config --global alias.ci commit
    git config --global alias.st status
    git config --global core.filemode false
    git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
    #git clone 时显示Filename too long的解决办法
    git config --global core.longpaths true
```

### NFS服务器设置

```bash
    echo "/nfsroot    *(rw,sync,no_root_squash)" >> /etc/exports
    mkdir -p /nfsroot
    chmod 777 -R /nfsroot
    /etc/init.d/rpcbind restart
    /etc/init.d/nfs-kernel-server restart
    mount -t nfs -o nolock localhost:/nfsroot /mnt
```

### add i386 support

```bash
    sudo apt install -y firmware-realtek
    sudo dpkg --print-architecture
    sudo dpkg --add-architecture i386
    sudo apt install  -y lib32z1 lib32ncurses5 gcc-multilib
```

### 安装6.828开发环境

```bash
    git clone http://web.mit.edu/ccutler/www/qemu.git
    ./configure --disable-kvm --prefix=/opt/qemu --target-list="i386-softmmu x86_64-softmmu"
    make
    sudo make install
```

### Linux字体渲染

```bash
    sudo apt install -y dirmngr gnome-tweaks
    echo "deb http://ppa.launchpad.net/no1wantdthisname/ppa/ubuntu bionic main" | sudo tee /etc/apt/sources.list.d/infinality.list
    echo "deb-src http://ppa.launchpad.net/no1wantdthisname/ppa/ubuntu bionic main" | sudo tee -a /etc/apt/sources.list.d/infinality.list
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E985B27B

    # 或者直接在Ubuntu系统中运行
    sudo add-apt-repository ppa:no1wantdthisname/ppa
```

执行以下命令来升级你的系统并安装 Infinality 包：

```bash
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install -y fontconfig-infinality
    sudo apt install -y libfreetype6 libfreetype6-dev freetype2-demos
```

### 以太网和wifi同时上网

```bash
    echo "#!/bin/bash">/etc/NetworkManager/dispatcher.d/02myroutes
    echo "sudo route del -net default netmask 0.0.0.0 dev enp7s0">>/etc/NetworkManager/dispatcher.d/02myroutes
    echo "sudo route add -net 192.168.0.0 netmask 255.255.0.0 gw 192.168.0.1 dev enp7s0">>/etc/NetworkManager/dispatcher.d/02myroutes
```

### ttyUSB0 permission or Unable to open serial port /dev/ttyUSB0

```bash
    sudo chmod 666 /dev/ttyUSB0
    sudo gpasswd --add floyd dialout
    sudo echo "KERNEL==\"ttyUSB[0-9]*\", GROUP=\"dialout\", MODE=\"0666\"">/etc/udev/rules.d/50-usb-serial.rules
    sudo echo "KERNEL==\"ttyACM[0-9]*\", GROUP=\"dialout\", MODE=\"0666\"">/etc/udev/rules.d/40-atmel-samba.rules
    sudo /etc/init.d/udev restart # or reboot system
```

### delete by inode

```bash
    ls -il
    find ./ -inum
    find ./ -inum 277191 -exec rm -i {} \;
```

### tftp Sever

```bash
    just use Sample configuration
    service tftpd-hpa status
    service tftpd-hpa stop
    service tftpd-hpa start
    service tftpd-hpa restart
    service tftpd-hpa force-reload
    mkdir -p /srv/tftp
    sudo chmod 777 /srv/tftp -R
```

### get tftp files in arm board

```bash
    tftp tftp-server-ip -g -r remotefile
```

### install LaTex

```bash
    sudo apt-get -y install texlive-full texmaker texstudio
```

### install Typora

```bash
    wget -qO - https://typora.io/linux/public-key.asc | sudo apt-key add -
    # add Typora's repository
    sudo add-apt-repository 'deb https://typora.io/linux ./'
    sudo apt-get update
    # install typora
    sudo apt-get install typora
```

### install notepadqq

```bash
    # trusty 14.04
    # xenial 16.04
    # bionic 18.04
    sudo echo "deb http://ppa.launchpad.net/notepadqq-team/notepadqq/ubuntu trusty main">>/etc/apt/sources.list
    sudo echo "deb-src http://ppa.launchpad.net/notepadqq-team/notepadqq/ubuntu trusty main">>/etc/apt/sources.list
    sudo apt-key adv --recv-key --keyserver keyserver.ubuntu.com 63DE9CD4
    sudo apt-get update
    sudo apt-get install notepadqq
```

### test tex

```LaTeX
    \documentclass{article}
    \begin{document}
        Hello, world!
    \end{document}
```

### graphviz command

```bash
    dot -version  #查看graphviz版本
    dot -Tpng sample.dot -o sample.png  #编译成png图
    dot -Tsvg sample.dot -o sample.png  #编译成png图
```

### install CGAL for Debian or Linux Mint

```bash
    sudo apt-get install  -y libcgal-dev  -y# install the CGAL library
    sudo apt-get install  -y libcgal-demo  -y# install the CGAL demos
```

### install chrome

```bash
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```

### Ubuntu下配置Common Lisp开发环境

```bash
#修改 Emacs 配置文件, 以支持 Common Lisp
    emacs -nw ~/.emacs.d/user.el

    (setq inferior-lisp-program "/usr/bin/sbcl")
        (add-to-list 'load-path "/usr/local/bin/slime/")
        (require 'slime)
        (slime-setup)
    (slime-setup '(slime-fancy))'
```

### mount ftpfs

```bash
    mkdir -p ~/ftpfs
    curlftpfs ftp://root:1@192.168.0.4 /home/floyd/ftpfs/
```

### pppoe server

```bash
    sudo echo "\"user\" * \"123\" *">/etc/pap-secrets
    sudo echo "\"user\" * \"123\" *">/etc/chap-secrets
    sudo echo "login">/etc/ppp/pppoe-server-options
    sudo echo "lcp-echo-interval 30">>/etc/ppp/pppoe-server-options
    sudo echo "lcp-echo-failure 4">>/etc/ppp/pppoe-server-options
    sudo echo "ms-dns  202.118.224.101">>/etc/ppp/pppoe-server-options
    modprobe pppoe
    sudo pppoe-server -I enp9s0 -L 192.168.13.1 -R 192.168.13.100 -N 333
    sudo pppoe-server -I eno1 -L 192.168.13.1 -R 192.168.13.100 -N 333

```

### Linux中error while loading shared libraries错误解决办法

默认情况下, 编译器只会使用/lib和/usr/lib这两个目录下的库文件, 通常通过源码包进行安装时, 如果不指定--prefix, 会将库安装在/usr/local/lib目录下; 当运行程序需要链接动态库时, 提示找不到相关的.so库, 会报错. 也就是说, /usr/local/lib目录不在系统默认的库搜索目录中, 需要将目录加进去.

1. 首先打开/etc/ld.so.conf文件
2. 加入动态库文件所在的目录：执行vi /etc/ld.so.conf, 在"include ld.so.conf.d/*.conf"下方增加"/usr/local/lib".
3. 保存后, 在命令行终端执行：/sbin/ldconfig -v; 其作用是将文件/etc/ld.so.conf列出的路径下的库文件缓存到/etc/ld.so.cache以供使用, 因此当安装完一些库文件, 或者修改/etc/ld.so.conf增加了库的新搜索路径, 需要运行一下ldconfig, 使所有的库文件都被缓存到文件/etc/ld.so.cache中, 如果没做, 可能会找不到刚安装的库.

### Linux 中安装虚拟机, 并在虚拟机中识别USB设备的方法

- 如果安装的是Virtual Box, 需要到vbox的[官网](https://www.virtualbox.org/wiki/Linux_Downloads)下载vbox的扩展包, [VirtualBox 6.0.4 Oracle VM VirtualBox Extension Pack](https://www.virtualbox.org/wiki/Downloads), 下载后, 在`管理`->`全局设定`->`扩展`->`+`浏览到刚才下载的扩展包, 等待自动安装好. 然后运行命令`sudo usermod -a -G vboxusers $(whoami)`, `cat /etc/group | grep vbox`, 看一下已经把当前用户添加进vboxusers了, 然后重启. 重启后, 在对应的虚拟机设置里找到USB设置, 点击`启用USB控制器`, 然后再打开这个虚拟机即可在`设备`->`USB`中找到你想运行在虚拟机中的USB设备了.

### understand 5 修改快捷键

`Tools->Options->Key Bindings` 打开快捷键设置窗口
- 查看符号的定义及声明: `Edit Source`, 改成 `F3`
- 定位到下一个编辑器视图: `Edit History Next`, 改成 `Alt+Right`
- 定位到上一个编辑器视图: `Edit History Previous`, 改成 `Alt+Left`

### vmplayer

vmplayer默认的安装位置是`/usr/lib/vmware`, 下载的`vmware tools`位置是`/usr/lib/vmware/isoimages`

### 修改 `fstab` 自动挂载 `windows` 分区

```bash
    # /etc/fstab: static file system information.
    #
    # Use 'blkid' to print the universally unique identifier for a
    # device; this may be used with UUID= as a more robust way to name devices
    # that works even if disks are added and removed. See fstab(5).
    #
    # <file system> <mount point>   <type>  <options>       <dump>  <pass>
    # / was on /dev/sda2 during installation
    UUID=080c3642-0f86-461b-95bc-4686b79e5629 /               ext4    errors=remount-ro 0       	1
    # /home was on /dev/sda3 during installation
    UUID=0cb479d2-87eb-4619-8079-e3aee1e93f60 /home           ext4    defaults        0       	2
    /dev/sda1			/win/c			  ntfs    defaults,user,rw	0	0
    /swapfile			none			  swap	  sw		  0		0
```

### 创建 `swapfile` 作为交换分区

```bash
    # count=1024*1024*4, 4G, 可根据需要调整大小
    sudo dd if=/dev/zero of=/opt/swapfile bs=1024 count=4121440
    mkswap /opt/swapfile
    swapon /opt/swapfile #挂载swap分区
    free -m #验证是否正确挂载
    swapon -s #查看交换分区的使用情况
    swapoff /opt/swapfile #停用swap分区
```

### github 速度慢

    经常要clone github中的一些项目，无奈如果不爬梯子的话速度实在是龟速，经常1k/s，于是搜了下解决方法，改HOSTS大法。
Windows下在C:/Windows/system32/drivers/etc/hosts
Ubuntu等linux系一般在/etc/hosts
在hosts中添加如下内容：

``` Hosts
    151.101.44.249 github.global.ssl.fastly.net
    192.30.253.113 github.com
    103.245.222.133 assets-cdn.github.com
    23.235.47.133 assets-cdn.github.com
    203.208.39.104 assets-cdn.github.com
    204.232.175.78 documentcloud.github.com
    204.232.175.94 gist.github.com
    107.21.116.220 help.github.com
    207.97.227.252 nodeload.github.com
    199.27.76.130 raw.github.com
    107.22.3.110 status.github.com
    204.232.175.78 training.github.com
    207.97.227.243 www.github.com
    185.31.16.184 github.global.ssl.fastly.net
    185.31.18.133 avatars0.githubusercontent.com
    185.31.19.133 avatars1.githubusercontent.com
```
改完之后立刻刷新，
Windows：ipconfig /flushdns
Ubuntu：sudo systemctl restart nscd


### 虚拟Linux挂在VMware共享文件夹

1. 可以用命令 `vmhgfs-fuse -h` 查看挂载方法
2. 也可以用命令 `sudo mount  -t  vmhgfs  .host:/     /mnt/hgfs`挂载
3. 在 `/etc/fstab` 文件中添加 `./host:/　　/mnt/hgfs　　vmhgfs　　default　　0　　0` 即可自动挂载