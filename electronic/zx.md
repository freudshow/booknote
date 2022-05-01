# 智芯`TTU`方便开发修改

## `sudo`不需要输入密码

每次`sudo`输入密码很烦人, 依照下列步骤去掉输入密码

```bash
sudo vi /etc/sudoers # 然后将光标定位到文档的最后一行, 加上一句话
	 sysadm    ALL=(ALL) NOPASSWD: NOPASSWD: ALL # sysadm是当前你想去掉输入密码的用户名, 可以是任意有效的用户名. 保存并关闭这个文档

sudo vi /etc/sudoers.d/sysadm #然后将光标定位到文档的最后一行, 加上一句话
	sysadm    ALL=(ALL) NOPASSWD: NOPASSWD: ALL # 保存并关闭这个文档
	 
```

然后每次使用`sysadm`用户运行`sudo`命令, 就不需要输入密码了



## 开启`root`用户登录

1. `vi /etc/passwd` ,  第一行就是`root`用户的配置: `root:x:0:0:root:/root:/usr/sbin/nologin`, 把这句话改成  `root:x:0:0:root:/root:/bin/bash`. 保存并关闭这个文档
2. `sudo passwd root`, 设置一个复杂的密码. 如果遇到`passwd: Authentication token manipulation error`这样的错误, 运行`sudo chattr -i /etc/shadow`和`sudo chattr -i /etc/passwd`命令去掉修改密码的限制,
3. 使用`xshell`, 用`root`用户登录即可

## 免密码向终端上传文件

### 在虚拟机`Linux`安装`ssh`客户端

如果虚拟机的`Linux`中没有安装`ssh`客户端, 则先安装`ssh`客户端:

```bash
sudo apt-get install -y openssh-client
```

### 在虚拟机`Linux`生成`ssh`密钥对

```bash
ssh-keygen -t rsa
```
一路回车, 使用默认设置即可,  这样会在你的虚拟机`Linux`的当前用户的主目录下的`.ssh`目录下生成一对密钥: `id_rsa`(私钥), `id_rsa.pub`(公钥).

### 智芯终端开启`rsa`公钥验证

为了响应国网的终端安全加固要求, 智芯终端默认关闭了`ssh`的公钥方式验证, 通过以下命令打开:

```bash
sudo vi /etc/ssh/sshd_config : # 找到 RSAAuthentication 这一行, 修改成下面的设置, 如果没有这3句话, 手动加入即可
	RSAAuthentication yes
	PubkeyAuthentication yes
	AuthorizedKeysFile      %h/.ssh/authorized_keys
# 保存并关闭这个文件	
```

这样, 就打开了智芯终端的`rsa`公钥验证方式,  再重启`ssh`服务即可:

```bash
sudo service ssh restart
```

### 将虚拟机`Linux`的公钥复制到智芯终端

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub -p 8888 sysadm@192.168.1.101
# 其中"~/.ssh/id_rsa.pub"是公钥的存放位置, "-p 8888"是智芯终端的"ssh"服务的端口号, "sysadm@192.168.1.101"的意思是, 将公钥存放到"192.168.1.101"这个"ssh"服务器的"sysadm"的主目录下的".ssh/authorized_keys"文件中
# 输入上述命令后, 会让你输入"sysadm"用户的登录密码, 输入即可.
```

经过上述命令, 以后再向终端复制文件, 只要使用以下命令远程上传即可:

```bash
scp -P 8888  yourfile sysadm@192.168.1.101:/home/sysadm/bin/
# 其中"scp"命令是使用"ssh"协议的远程复制/上传命令, 类似于"FTP"的功能; "yourfile"是你想要往终端复制的文件; "sysadm@192.168.1.101"意思是使用用户名"sysadm"登录"192.168.1.101"进行本次复制动作; ":/home/sysadm/bin/"是要将本次的文件放到终端的哪个目录下, 注意这个目录"sysadm"要有写权限

scp -P 8888  -r yourdir sysadm@192.168.1.101:/home/sysadm/
# 上面的命令是上传文件夹的命令, "-r yourdir"的意思是递归上传"yourdir"
```

### 在智芯终端安装`gcc`

> 注意: 智芯终端安装了`gcc`后, `container`命令就用不了了, 因为`container`命令使用的`libc`和`libstdc++`库文件, 与ubuntu源中的版本不一致. 所以如果要使用容器及其相关命令, 就不要进行本次修改了.

1. 找一台闲置的路由器, 将它的公网地址设置成公司的网址和`dns`服务器.
2. 将路由器的`lan`网段设置成`192.168.1*.`
3. 将智芯终端用网线连接路由器的`lan`口, 并将智芯终端的网关设置成路由器的`lan`网关, 并将智芯终端的`dns`服务器设置为正确可用的, 这样智芯终端就可以上网了.
4. `sudo apt install -y build-essential dpkg`将安装包下载到终端.
5. 智芯终端默认删除了`dpkg`, 所以第4步的命令执行完下载任务后, 就会报错: "找不到dpkg",  所以要手动安装`dpkg`.
6. `apt`命令下载的安装包, 默认放在`/var/cache/apt/archives/`目录下,  在这个目录下找到文件`dpkg_1.18.4ubuntu1.6_armhf.deb`, 把它下载下来, 放到虚拟机`Linux`的一个空目录中, 这里假设放在`exdpkg`这个目录中.
7. `cd`到`exdpkg`这个目录中, 执行命令`dpkg -X dpkg_1.18.4ubuntu1.6_armhf.deb xdeb/`, 这样`dpkg`的安装包就解压到`exdpkg/xdeb`目录下了.
8. 将`xdeb`上传到智芯终端: `scp -P 8888  -r xdeb sysadm@192.168.1.101:/home/sysadm/`, 就将`xdeb`上传到`/home/sysadm/`目录下了.
9. 到智芯终端, 将刚才上传的目录复制到根目录: 

```bash
cd /home/sysadm/xdeb
sudo cp ./* / -R
```
这样就将`dpkg`安装到了智芯终端上了.

10. 重新运行`sudo apt install -y build-essential`, 就将`gcc`安装到智芯终端上了. 如果你想安装其他软件, 比如`git`, `sqlite3`等, 也可以用`apt`命令安装了.

### 智芯`libsqlite3`版本号

将智芯终端里的`/usr/lib/libsqlite3.so`复制出来, 作为链接库使用.

```C
	#include <stdio.h>
	#include <sqlite3.h>
	
	int main()
	{
  		printf("%s\n", sqlite3_libversion());
	}
```

然后编译

```bash
	arm-linux-gnueabihf-gcc -o sqlite3 sqlite3.c -I"./" -L"./" -lsqlite3 -lpthread -ldl
```