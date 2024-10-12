# `dropbear`相关配置

飞凌的开发板使用`dropbear`来作为`ssh`服务端, `dropbear`相比`openssh`来说比较轻便, 但是它没有`sftp`服务器功能

## 启用`sftp-server`

1. 打开[阿里云下载链接](https://mirrors.aliyun.com/pub/OpenBSD/OpenSSH/portable/openssh-9.9p1.tar.gz), 下载`openssh`代码包, 此文成文时的最新版本为`9.9p1`.
1. 将代码包`openssh-9.9p1.tar.gz`放到一个临时目录中, 本文假设为`~/openssh/`, 解压缩:

    ```bash
    tar xzvf openssh-9.9p1.tar.gz
    cd openssh-9.1p1
    ```

1. 如果使用飞凌提供的编译工具链, 假设工具链安装在`/opt`目录下, 运行

    ```bash
    echo ". /opt/fsl-imx-x11/4.1.15-2.0.0/environment-setup-cortexa7hf-neon-poky-linux-gnueabi">>~/.bashrc
    ```

    将其添加到用户的`bash`配置文件中, 不必每次都手动运行上述命令

1. 如果使用`ARM`公司提供的工具链, 将其解压到一个目录里, 将目录里的`bin`目录加入到`PATH`环境变量

	```bash
		sudo echo "export PATH=$PATH:$HOME/path_to_toolchain/bin" >> /etc/profile
	```

	重启或注销后生效

1. 编译`zlib`

	```bash
		export CC=aarch64-none-linux-gnu-gcc
		./configure --prefix==$HOME/soft/openssh/zlib-1.3.1/build
		make && make install
	```

1. 编译`openssh`

    ```bash
	#在 openssh-9.9p1 目录中, 运行
    ./configure --host=aarch64-none-linux-gnu --without-openssl --with-zlib=$HOME/soft/openssh/zlib-1.3.1/build --prefix=$HOME/soft/openssh/openssh-9.9p1/build && make sftp-server
    ```

    即可生成可执行程序`sftp-server`, 将其复制到开发板的`/usr/libexec/`目录下, 重启开发板, 即可使用`sftp`传输文件了
