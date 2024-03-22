# 常用系统配置及命令

## 文件排重命令

```bash
    find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

## 文件排重工具

`fdupes`:

```bash
    $sudo apt install fdupes
    $fdupes -r + directory #递归搜索重复文件
    #使用-S选项来查看某个文件夹内找到的重复文件的大小
    $fdupes -Sr /to_directory/
    #删除重复文件, 同时保留一个副本, 你可以使用-d选项
    $fdupes -d /to_directory/
    #使用-f选项来忽略每个匹配集中的首个文件
    $fdupes -f /to_directory/
```

## Linux下制作ext4文件系统镜像

```bash
    #生成一个空的2GiB文件
    dd if=/dev/zero of=rootfs.ext4 bs=1024 count=20480000

    #对生成的文件进行格式化
    mkfs.ext4 rootfs.ext4

    #挂载此空镜像
    sudo mount -o loop rootfs.ext4 /mnt

```

## 给每个语句加上前缀, 后缀

```bash
sed '/./{s/^/"&/;s/$/&"/}' 698-645-map.sql > char.c
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

## `sqlite3` 导出数据到 `csv`

```bash
#每次导出50行, limit后是行偏移量
sqlite3 -header -csv linyi.db "select * from ly order by '序号' limit 50 offset 4300;">4301.csv
```

## `Qt` 静态编译

```bash
    ./configure -static -prefix ../qt.5.14.1.static

    qt.qpa.plugin: Could not find the Qt platform plugin "xcb" in ""
```

## `debian` 安装 `nodejs`

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
    apt install nodejs
```

- To install the Yarn package manager, run:

``` bash
     curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
     echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
     sudo apt update && sudo apt install yarn
```

### `Linux`一次性复制同一目录下的多个文件

```bash
cp /home/usr/dir/{file1,file2,file3,file4}       /home/usr/destination/#注意文件之间的‘,’不要有空格
#具有共同前缀
cp /home/usr/dir/file{1..4} ./ # 其实同一目录也可以看做是文件名的同一前缀
```

## `debian/Ubuntu`系统安装后要做的事情

### 配置软件源为中科大软件源

用root账号在/etc/apt/sources.list中把软件源修改为：

- `debian 12`:

```bash
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware

deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware

deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware

# deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware
# # deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware

deb https://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
# deb-src https://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
```

- `ubuntu 20.04`

```bash
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse
```

- `ubuntu 22.04`

```bash
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
```

### 让`apt`支持`https`开头的软件源

```bash
sudo apt install -y apt-transport-https
```

### 普通用户使用`sudo`命令, 不再需要输入密码

把下面的配置写入到 `/etc/sudoers`, yourname替换为自己的用户名, 下同

```bash
    floyd    ALL=(ALL) NOPASSWD: NOPASSWD: ALL
```

### 查看`debian`的版本号

cat /etc/debian_version

### 安装常用软件

```bash
    sudo apt install -y linux-headers-$(uname -r) dkms caja-open-terminal git vim cscope universal-ctags build-essential rpcbind nfs-kernel-server nfs-common libgmp-dev libmpfr-dev libmpc-dev binutils pkg-config autoconf automake libtool zlib1g-dev libsdl1.2-dev libtool-bin libglib2.0-dev libz-dev libpixman-1-dev libbsd-dev dirmngr tftpd-hpa tftp graphviz emacs slime curl curlftpfs pppoe pppoeconf  vim-addon-mw-utils flex bison default-jdk openssh-server net-tools qbittorrent vlc aria2 libssl-dev libelf-dev man-db manpages-posix manpages-dev manpages-posix-dev
    sudo apt autoremove --purge snapd #卸载ubuntu自带的包管理软件, 否则它总是在后台运行, 不断读取磁盘
```

### Install VMware tools on Ubuntu 22.04 Jammy Jellyfish Linux

```bash
    sudo apt install open-vm-tools-desktop open-vm-tools
```

### `Ubuntu`/`Debian`系统时间相差8小时解决方法

```bash
    sudo timedatectl set-local-rtc 1
```

### `Ubuntu`安装`Mate desktop`

```bash
    sudo apt install -y ubuntu-mate-core
    sudo apt install -y ubuntu-mate-desktop
    sudo apt install -y ubuntu-mate*
```

### `git` 常用设置

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

### `NFS`服务器设置

```bash
    echo "/nfsroot    *(rw,sync,no_root_squash)" >> /etc/exports
    mkdir -p /nfsroot
    chmod 777 -R /nfsroot
    /etc/init.d/rpcbind restart
    /etc/init.d/nfs-kernel-server restart
    mount -t nfs -o nolock localhost:/nfsroot /mnt
```

### `ssh`服务器设置

```bash
sudo apt install -y openssh-server
ps -e |grep ssh
sudo /etc/init.d/ssh restart
sudo /etc/init.d/ssh start
netstat -tlp
sudo service ssh status
sudo service ssh stop
sudo service ssh restart

#ssh免密码登录
sudo vi /etc/ssh/sshd_config : #把加入或修改成下面的设置
RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile      %h/.ssh/authorized_keys
ssh-copy-id -i ~/.ssh/id_rsa.pub -p 8888 sysadm@192.168.1.101(端口不是22的情况)
#测试复制文件
scp -P 8888  1376.2App sysadm@192.168.1.101:/home/sysadm/bin/

#挂载sshfs
sudo apt install -y sshfs
mkdir -p ~/sshfs
sshfs -p 8888 sysadm@192.168.1.101:/home/sysadm /home/floyd/sshfs
sshfs -p 8888 sysadm@192.168.1.101:/data/app /home/floyd/sshdata

#卸载sshfs文件系统
umount /home/floyd/sshfs
#或者
fusermount -u /home/floyd/sshfs

#在 /etc/ssh/sshd_config 文件的末尾添加如下2个参数
ClientAliveInterval 60
ClientAliveCountMax 5

#设置超时时间, 防止shell无操作自动断开
echo $TMOUT #查看当前设置的超时时间, 单位秒(s)
sudo vi /etc/profile
export TMOUT=60000 #修改为60000秒, 约为16.67小时
```

### `add i386 support`

```bash
sudo apt install -y firmware-realtek
sudo dpkg --print-architecture
sudo dpkg --add-architecture i386
sudo apt install  -y lib32z1 lib32ncurses6 gcc-multilib libncurses5:i386 libncurses5-dev libncurses5 libncursesw5
```

### 安装6.828开发环境

```bash
    sudo apt install -y git build-essential gdb-multiarch qemu-system-misc gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu
    git clone https://github.com/mit-pdos/xv6-riscv.git
    ./configure --disable-kvm --prefix=/opt/qemu --target-list="i386-softmmu x86_64-softmmu"
    make
    sudo make install

    git clone git://github.com/mit-pdos/xv6-riscv-book.git
    退出qemu: Ctrl - A X 按下Ctrl 键和A键, 然后释放这两个键,再按X
```

### `Windows+Ubuntu`双系统如何设置`Windows`为第一启动项

1.打开终端，输入 cd /etc/default/
1.接着输入sudo sudo nano grub，会提示输入密码，输入密码按回车即可
1.现在进入了grub文件，找到GRUB_DEFAULT = 0，因为Ubuntu的顺序是从0开始的，并且windows对应第5个选项，所以将0改为4，
1.按Ctrl+X，会有一个询问是否保存，输入Y保存修改后的grub文件，会有再次询问时，按回车确认退出
1.输入 sudo update-grub更新grub文件

### 安装新立德软件包管理器

```bash
    sudo apt install -y synaptic
```

### `Linux`字体渲染

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
    sudo apt update
    sudo apt upgrade
    sudo apt install -y fontconfig-infinality
    sudo apt install -y libfreetype6 libfreetype6-dev freetype2-demos
```

### `debian`设置默认语言

```bash
sudo apt install -y locales
sudo dpkg-reconfigure locales #根据提示, 安装相应的语言包, 最后设置默认语言集
```

### ubuntu主目录下的文件夹改回英文

编辑配置文件`~/.config/user-dirs.dirs`, 把文件夹指向改掉，例如：

```Shell
mkdir -p $HOME/Desktop
mkdir -p $HOME/Download
mkdir -p $HOME/Templates
mkdir -p $HOME/Public
mkdir -p $HOME/Documents
mkdir -p $HOME/Music
mkdir -p $HOME/Pictures
mkdir -p $HOME/Videos

XDG_DESKTOP_DIR="$HOME/Desktop"
XDG_DOWNLOAD_DIR="$HOME/Download"
XDG_TEMPLATES_DIR="$HOME/Templates"
XDG_PUBLICSHARE_DIR="$HOME/Public"
XDG_DOCUMENTS_DIR="$HOME/Documents"
XDG_MUSIC_DIR="$HOME/Music"
XDG_PICTURES_DIR="$HOME/Pictures"
XDG_VIDEOS_DIR="$HOME/Videos"

```

使用`xdg-user-dirs-gtk-update`点击了`不再问我`这个问题后，再次执行这个命令就会没有反应, 解决方法:

执行一下命令`echo zh_CN > ~/.config/user-dirs.locale`，然后就可以再次执行`xdg-user-dirs-gtk-update`或者`xdg-user-dirs-update`了。

### 以太网和`wifi`同时上网

```bash
    echo "#!/bin/bash">/etc/NetworkManager/dispatcher.d/02myroutes
    echo "sudo route del -net default netmask 0.0.0.0 dev enp7s0">>/etc/NetworkManager/dispatcher.d/02myroutes
    echo "sudo route add -net 192.168.0.0 netmask 255.255.0.0 gw 192.168.0.1 dev enp7s0">>/etc/NetworkManager/dispatcher.d/02myroutes
```

### `ttyUSB0 permission or Unable to open serial port /dev/ttyUSB0`

```bash
    sudo chmod 666 /dev/ttyUSB0
    sudo gpasswd --add floyd dialout
    sudo echo "KERNEL==\"ttyUSB[0-9]*\", GROUP=\"dialout\", MODE=\"0666\"">/etc/udev/rules.d/50-usb-serial.rules
    sudo echo "KERNEL==\"ttyACM[0-9]*\", GROUP=\"dialout\", MODE=\"0666\"">/etc/udev/rules.d/40-atmel-samba.rules
    sudo /etc/init.d/udev restart # or reboot system
```

### `delete by inode`

```bash
    ls -il
    find ./ -inum
    find ./ -inum 277191 -exec rm -i {} \;
```

### `tftp Sever`

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

### `get tftp files in arm board`

```bash
    tftp tftp-server-ip -g -r remotefile
```

### `install LaTex`

```bash
    sudo apt -y install texlive-full texmaker texstudio
```

### `install Typora`

```bash
    wget -qO - https://typora.io/linux/public-key.asc | sudo apt-key add -
    # add Typora's repository
    sudo add-apt-repository 'deb https://typora.io/linux ./'
    sudo apt update
    # install typora
    sudo apt install typora
```

### `install cloudflare warp`

to install warp, go to https://1.1.1.1/, hit Linux, then follow the script below:

```bash
    curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg


	# Add this repo to your apt repositories
	echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list


	# Install
	sudo apt-get update && sudo apt-get install cloudflare-warp
```


### `install notepadqq`

```bash
    # trusty 14.04
    # xenial 16.04
    # bionic 18.04
    sudo echo "deb http://ppa.launchpad.net/notepadqq-team/notepadqq/ubuntu trusty main">>/etc/apt/sources.list
    sudo echo "deb-src http://ppa.launchpad.net/notepadqq-team/notepadqq/ubuntu trusty main">>/etc/apt/sources.list
    sudo apt-key adv --recv-key --keyserver keyserver.ubuntu.com 63DE9CD4
    sudo apt update
    sudo apt install notepadqq
    
    sudo add-apt-repository ppa:notepadqq-team/notepadqq
    sudo apt update
    sudo apt install -y notepadqq
```

### `test tex`

```LaTeX
    \documentclass{article}
    \begin{document}
        Hello, world!
    \end{document}
```

### `graphviz command`

```bash
    dot -version  #查看graphviz版本
    dot -Tpng sample.dot -o sample.png  #编译成png图
    dot -Tsvg sample.dot -o sample.png  #编译成png图
```

### `install CGAL for Debian or Linux Mint`

```bash
    sudo apt install  -y libcgal-dev  -y# install the CGAL library
    sudo apt install  -y libcgal-demo  -y# install the CGAL demos
```

### `install chrome`

```bash
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```

### `Linux` 下转换文件编码

```bash
    # convert file name encoding
    sudo apt install convmv
    convmv -f GBK -t UTF-8 -r --nosmart --notest <target directory>

    -f from
    -t to
    --nosmart ignore utf-8 encoded name
    -r recursive
    --notest force converting

    # convert file encoding
    iconv -f gbk -t utf-8 source-file -o target-file
```

### `Ubuntu` 下配置 `Common Lisp` 开发环境

```bash
#修改 Emacs 配置文件, 以支持 Common Lisp
    emacs -nw ~/.emacs.d/user.el

    (setq inferior-lisp-program "/usr/bin/sbcl")
        (add-to-list 'load-path "/usr/local/bin/slime/")
        (require 'slime)
        (slime-setup)
    (slime-setup '(slime-fancy))'
```

### `mount ftpfs`

```bash
    mkdir -p ~/ftpfs
    curlftpfs ftp://root:1@192.168.0.4 /home/floyd/ftpfs/
```

### `pppoe server`

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

### `Linux` 中 `error while loading shared libraries` 错误解决办法

默认情况下, 编译器只会使用/lib和/usr/lib这两个目录下的库文件, 通常通过源码包进行安装时, 如果不指定--prefix, 会将库安装在/usr/local/lib目录下; 当运行程序需要链接动态库时, 提示找不到相关的.so库, 会报错. 也就是说, /usr/local/lib目录不在系统默认的库搜索目录中, 需要将目录加进去.

1. 首先打开/etc/ld.so.conf文件
2. 加入动态库文件所在的目录：执行vi /etc/ld.so.conf, 在"include ld.so.conf.d/*.conf"下方增加"/usr/local/lib".
3. 保存后, 在命令行终端执行：/sbin/ldconfig -v; 其作用是将文件/etc/ld.so.conf列出的路径下的库文件缓存到/etc/ld.so.cache以供使用, 因此当安装完一些库文件, 或者修改/etc/ld.so.conf增加了库的新搜索路径, 需要运行一下ldconfig, 使所有的库文件都被缓存到文件/etc/ld.so.cache中, 如果没做, 可能会找不到刚安装的库.

### `Linux` 中安装虚拟机, 并在虚拟机中识别USB设备的方法

- 如果安装的是Virtual Box, 需要到vbox的[官网](https://www.virtualbox.org/wiki/Linux_Downloads)下载vbox的扩展包, [VirtualBox 6.0.4 Oracle VM VirtualBox Extension Pack](https://www.virtualbox.org/wiki/Downloads), 下载后, 在`管理`->`全局设定`->`扩展`->`+`浏览到刚才下载的扩展包, 等待自动安装好. 然后运行命令`sudo usermod -a -G vboxusers $(whoami)`, `cat /etc/group | grep vbox`, 看一下已经把当前用户添加进vboxusers了, 然后重启. 重启后, 在对应的虚拟机设置里找到USB设置, 点击`启用USB控制器`, 然后再打开这个虚拟机即可在`设备`->`USB`中找到你想运行在虚拟机中的USB设备了.

### `understand` 5 修改快捷键

`Tools->Options->Key Bindings` 打开快捷键设置窗口

- 查看符号的定义及声明: `Edit Source`, 改成 `F3`
- 定位到下一个编辑器视图: `Edit History Next`, 改成 `Alt+Right`
- 定位到上一个编辑器视图: `Edit History Previous`, 改成 `Alt+Left`

### `vmplayer`

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
    UUID=080c3642-0f86-461b-95bc-4686b79e5629 /               ext4    errors=remount-ro 0    1
    # /home was on /dev/sda3 during installation
    UUID=0cb479d2-87eb-4619-8079-e3aee1e93f60 /home           ext4    defaults        0    2
    /dev/sda1    /win/c    ntfs    defaults,user,rw 0 0
    /swapfile    none    swap    sw    0 0
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

### `github` 速度慢

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

    140.82.113.3 github.com
    199.232.69.194 github.global.ssl.fastly.net
```

改完之后立刻刷新，
Windows：`ipconfig /flushdns`
Ubuntu：`sudo systemctl restart nscd`, 或者 `sudo /etc/init.d/networking restart`

### 虚拟`Linux`挂载`VMware`共享文件夹

1. 可以用命令 `vmhgfs-fuse -h` 查看挂载方法
2. 也可以用命令 `sudo mount  -t  vmhgfs  .host:/     /mnt/hgfs`挂载
3. 在 `/etc/fstab` 文件中添加 `./host:/　　/mnt/hgfs　　vmhgfs　　default　　0　　0` 即可自动挂载

### `vbox` 的共享文件夹没有权限

```bash
    sudo usermod -aG vboxsf $(whoami)
    sudo reboot
```

### 在 `ubuntu` 中搭建 `samba` 文件共享服务

```bash
# 1. 安装 samba
sudo apt update
sudo apt install -y samba samba-common smbclient cifs-utils
# 2. 创建需要共享的目录
sudo mkdir /home/share
sudo chmod 777 /home/share
# 3. 修改基础配置
sudo gedit /etc/samba/smb.conf
# 在 'max log size = 1000' 下面增加
security = user
# 在文末增加
[testshare]
    path = /home/floyd/samba
    browseable = yes
    writable = yes
# 4. 新建访问共享资源的用户和设置密码
 sudo useradd smbuser # 新建用户
 sudo smbpasswd -a smbuser # 设置密码
 sudo service smbd restart # 重启 samba 服务
# 5. 访问windows共享
sudo apt install -y smbclient cifs
# 安装完成后，执行一下命令:
sudo mount -t cifs //192.168.1.121/dpan ~/wind -o username=floyd,password=a,gid=1000,uid=1000
```

至此 `samba` 服务搭建完毕,  可以在 `Windows` 中测试

> 参考 [Android ubuntu-samba 文件共享](https://blog.csdn.net/chenxiaoping1993/article/details/82422990)

### `Ubuntu` 安装 `Nvidia` 驱动

```bash
    # 禁用nouveau
    sudo vim /etc/modprobe.d/blacklist-nouveau.conf
        blacklist nouveau
        options nouveau modeset=0

    # 执行以下命令使禁用生效并且重启
    sudo update-initramfs -u
    sudo reboot

    # 重启后可以验证是否生效：
    lsmod | grep nouveau # 若没有输出，则禁用生效。
    # 禁用X-Window服务
    sudo service lightdm stop # 这会关闭图形界面
    sudo service lightdm start # 然后按Ctrl-Alt+F7即可恢复到图形界面

    # 如果以前是通过ppa源安装的，可以通过下面命令卸载：
    sudo apt remove --purge nvidia*
    # 如果以前是通过runfile安装的，可以通过下面命令卸载：
    sudo ./NVIDIA-Linux-x86_64-384.59.run --uninstall

    # 安装Nvidia驱动
    sudo add-apt-repository ppa:graphics-drivers/ppa
    sudo apt update
    sudo apt install nvidia-driver-430 # 根据具体情况而定, 安装最新版
    sudo apt install mesa-common-dev
    sudo reboot
    # 终端验证是否安装成功：
     nvidia-smi
    # 最好安装 apt-fast 加速下载速度, 不然下载时间很长
    sudo add-apt-repository ppa:apt-fast/stable
    sudo apt install apt-fast
    #安装后就跟apt用法一样了
    sudo apt-fast update
    sudo apt-fast upgrade -y
```

### `Ubuntu` 安装 `rclone` 并挂载为本地硬盘

```bash
# 安装rclone
curl https://rclone.org/install.sh | sudo bash

# 初始化配置
rclone config # 根据提示进行相应的配置

# 手动挂载网络硬盘
rclone mount repo:/ /mnt/onedrive/repo --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000
fusermount -qzu /mnt/onedrive/repo

# 将启动脚本注册为系统服务, 每次重启系统即自动挂载网络硬盘
wget https://www.moerats.com/usr/shell/rcloned && nano rcloned
    # 修改内容：
        NAME=""  #rclone name名，及配置时输入的Name
        REMOTE=''  #远程文件夹，OneDrive网盘里的挂载的一个文件夹
        LOCAL=''  #挂载地址，VPS本地挂载目录

cp rcloned /etc/init.d/rcloned
chmod +x /etc/init.d/rcloned
update-rc.d -f rcloned defaults
bash /etc/init.d/rcloned start
```

### `Ubuntu`息屏后无法唤醒

- 检查是否安装了grep laptop-mode-tools 工具包

    ```shell
     dpkg -l | grep laptop-mode-tools
    ```

- 安装laptop-mode

    ```shell
    sudo apt-get install laptop-mode-tools
    ```

- 判断Laptop是否启用了laptop_mode模式

    ```shell
    cat /proc/sys/vm/laptop_mode
    ```

    如果结果为0, 则表示未启动, 如果为非0, 则表示启动了

- 启动`laptop_mode`, 修改配置文件`/etc/default/acpi-support`, 更改 `ENABLE_LAPTOP_MODE=true`, 直接在终端中输入 `sudo laptop_mode start` 启动了`laptop_mode`之后，在`ubuntu`挂起后, 基本上就不会遇到无法唤醒的情况了. 如果在`acpi-support`中并未找到 `ENABLE_LAPTOP_MODE=true` 被注释的项. 在/etc/laptop-mode/laptop-mode.conf 中进行配置,查找 ENABLE_LAPTOP_MODE_ON_BATTERY, ENABLE_LAPTOP_MODE_ON_AC, ENABLE_LAPTOP_MODE_WHEN_LID_CLOSED, 全部设置为1即可.

- 启动`laptop_mode`

    ```shell
    sudo laptop_mode start
    ```

### `Debian`禁用休眠

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### 为`Bash shell`定义`Home, Del, Insert`热键

```bash
# vi /etc/profile

增加一行：
export INPUTRC=/usr/local/etc/inputrc

# vi /usr/local/etc/inputrc
set meta-flag on
set input-meta on
set convert-meta off
set output-meta on

"\e[1~": beginning-of-line
"\e[4~": end-of-line
"\e[5~": beginning-of-history
"\e[6~": end-of-history
"\e[3~": delete-char
"\e[2~": quoted-insert
"\e[5C": forward-word
"\e[5D": backward-word

logout、login一下再试试
```

### SecureCRT 不让标签页显示当前目录名

用 SecureCRT 连接 Linux主机后, 标签页标题会随着当前目录的变更而改变, 当进入目录层级较深时, 看着非常头大. 下面的方法禁用这个功能:

'Options -> Edit default session -> Terminal -> Emulation -> Advanced -> Other -> Ignore window title change request' 把这一项勾选即可.

### #VirtualBox 中 `debian` 使用物理硬盘(`windows`)

1. 运行`cmd`, `cd`进入你的`VirtualBox`目录

2. 运行`VBoxManage.exe`, 如：`VBoxManage internalcommands createrawvmdk -filename  d:\localdisk.vmdk -rawdisk \\.\PhysicalDrive1`

   **\\.\PhysicalDrive1**  表示第二块硬盘，\\.\PhysicalDrive0 是第一块，\\.\PhysicalDrive2 是第三块, 以此类推。

3. 在`virtualbox`中找到`d:\localdisk.vmdk`, 添加到虚拟机中即可

### `Windows` 10 自动登录

运行 `netplwiz` , 去掉"要使用本计算机, 用户必须输入用户名和密码"的对号, 接下来会让你输入登录密码, 输入完成即可.

### `Windows` 将 `cmder` 添加到右键

1. 将 `cmder` 的运行目录添加到 `path` 环境变量
2. 在任意命令行终端运行 `cmder.exe /REGISTER ALL` 即可在右键添加`cmder`的启动菜单

也可以参考[Adding Cmder to the Windows Explorer Context Menu](https://www.awmoore.com/2015/10/02/adding-cmder-to-the-windows-explorer-context-menu/)

### `Windows` 挂载 `NFS`

1. 打开 `Windows 10` 的 "程序和功能", 打开 "启用或关闭 `Windows` 功能", 找到 `NFS`, 打开 `NFS` 客户端, 等待安装完毕并重启.
2. 假设 `Linux` 端, `NFS` 的共享目录是 `192.168.0.2:/nfs/share`, 且打开了读写权限, 那么在 `Windows` 端打开 `cmd`, 运行命令 `mount -o anon nolock \\192.168.0.2\nfs\share Z:`, 这句命令以匿名身份挂载 `NFS` 到 `Y` 盘下, 但是没有读写权限, 中文也乱码
3. 解决中文乱码. 大多数 `Linux` 端的中文都以 `UTF-8` 编码, 而 `Windows` 则以 `GB-2312` 编码, 两套编码系统不兼容, 所以中文会出现乱码. 在 `Windows 10` 中, 打开 `Windows 设置`, 选择 "时间和语言", 再打开"语言", 在右上角找到"管理语言设置", 再选择第2个页签中的"更改系统区域设置", 勾选"Beta版: 使用 `Unicode UTF-8` 提供全区语言支持", 然后重启 `Windows`, 再次挂载 `NFS` 后, 中文就可以正常显示了.
4. 添加可写权限给匿名用户. 打开注册表编辑器 `regedit`, 定位到 `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default`, 在右侧窗口中新建 `DWORD (32位)` 项 `AnonymousUid`, 把它的值设置为 `Linux` 中有对 `NFS` 目录有读写权限的用户的用户 `id` 值, 再新建 `DWORD (32位)` 项  `AnonymousGid`, 把它的值设置为 `Linux` 中有对 `NFS` 目录有读写权限的用户的组 `id` 值, 重启 `Windows`, 就可以读写所挂载的目录了.
   >注: 也可以在 `Windows Power Shell` 中运行命令 `New-ItemProperty HKLM:\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default -Name AnonymousUID -Value 1000 -PropertyType "DWord"
   New-ItemProperty HKLM:\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default -Name AnonymousGID -Value 1000  -PropertyType "DWord"` 来添加注册表项.
   运行命令 `mount` 后, 显示如下:

   ```bash
    Local    Remote                                 Properties
    -------------------------------------------------------------------------------
    Y:       \\192.168.0.2\home\floyd               UID=1000, GID=1000
    rsize=1048576, wsize=1048576
    mount=soft, timeout=0.8
    retry=1, locking=no
    fileaccess=755, lang=GB2312-80
    casesensitive=no
    sec=sys
   ```

5. 自动挂载 `NFS`. 每次输入挂载命令很麻烦, 在 `Windows` 资源管理器中点击"此电脑"->"计算机"->"映射网络驱动器", 输入 `NFS` 共享的网络和主机路径, 并分配一个盘符, 则下次开机后, `Windows` 就自动挂载 `NFS` 共享目录了.

## `FreeBSD` 安装后设置

### 设置域名解析服务器

``` bash
    ee  /etc/rc.conf   #编辑
    ifconfig_em0="inet 192.168.21.173  netmask 255.255.255.0"  #设置IP地址，子网掩码
    defaultrouter="192.168.21.2"   #设置网关
    hostname="FreeBSD"   #设置主机名字

    ee /etc/resolv.conf  #编辑
    nameserver 192.168.31.1
    reboot #重启系统使之生效

```

### `sysinstall`

`sysinstall`换成了`bsdinstall`

## ARM 64位系统下编译32位程序

```bash
dpkg --add-architecture armhf
apt update
apt install -y libc6:armhf libstdc++6:armhf libc6-dev:armhf gcc-multilib-arm-linux-gnueabihf binutils-arm-linux-gnueabihf g++-multilib-arm-linux-gnueabihf doxygen:armhf transfig:armhf transfig imagemagick:armhf gdb:armhf

```

### TWRP线刷rom

重启手机到TWRP, 点击`adb sideload`, 然后连接数据线到手机上, 运行命令`adb sideload 刷机包.zip`, 等待完成即可. 注意adb版本要在1.0.32及以上

### Termux更新清华源

```bash

deb http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial main multiverse restricted universe
deb http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-backports main multiverse restricted universe
deb http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-proposed main multiverse restricted universe
deb http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-security main multiverse restricted universe
deb http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-updates main multiverse restricted universe
deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial main multiverse restricted universe
deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-backports main multiverse restricted universe
deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-proposed main multiverse restricted universe
deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-security main multiverse restricted universe
deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/ xenial-updates main multiverse restricted universe
```

## CSDN 保存网页自动跳转到首页

```html
<--右键用文本编辑器打开离线保存的网页，搜索关键词onerror，找到下面这段：-->
<img src=""
onerror='setTimeout(function(){if(!/(csdn.net|iteye.com|baiducontent.com|googleusercontent.com|360webcache.com|sogoucdn.com|bingj.com|baidu.com)$/.test(window.location.hostname)){window.location.href="\x68\x74\x74\x70\x73\x3a\x2f\x2f\x77\x77\x77\x2e\x63\x73\x64\x6e\x2e\x6e\x65\x74"}},3000);'>
<--不要心慈手软，直接删除后保存即可。-->
```

## 新建`eclipse`启动图标

在目录`~/.local/share/applications`中新建文件`eclipse.desktop`, 文件内容如下:

```
[Desktop Entry]
Name=eclipse
Comment=Run eclipse embedded C/C++
Exec=/home/floyd/soft/eclipse/eclipse
Terminal=false
Type=Application
Icon=/home/floyd/soft/eclipse/icon.xpm
StartupNotify=true
MimeType=application/x-ipynb+json;
Categories=Development;Education;
Keywords=eclipse;
```

## `sudo update-grub`找不到`windows`

在/etc/default/grub文件中添加
```bash
GRUB_DISABLE_OS_PROBER=false
#之后更新grub的配置：
sudo os-prober
sudo update-grub
```

## `debian`运行`arm-none-linux-gnueabihf-gdb`的错误

1. 找不到`libncursesw.so.5`

```shell
    sudo apt install libncursesw5 libncursesw5-dev
```

2. 安装对应的`python`环境

```shell
    curl https://pyenv.run | bash
    pyenv install 3.8.18
    sudo mkdir -p /usr/local/bld-tools
    sudo ln -s $PYENV_ROOT/versions/3.8.18 /usr/local/bld-tools/bld-tools-virtual-env
    
    #再次检查版本号即可
    /home/floyd/soft/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gdb --version
    GNU gdb (Arm GNU Toolchain 13.2.rel1 (Build arm-13.7)) 13.2.90.20231008-git
    Copyright (C) 2023 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
```


