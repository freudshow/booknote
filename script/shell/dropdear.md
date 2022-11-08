# `dropbear`相关配置

飞凌的开发板使用`dropbear`来作为`ssh`服务端, `dropbear`相比`openssh`来说比较轻便, 但是它没有`sftp`服务器功能

## 启用`sftp-server`

1. 打开[阿里云下载链接](https://mirrors.aliyun.com/pub/OpenBSD/OpenSSH/portable/openssh-9.1p1.tar.gz), 下载`openssh`代码包, 此文成文时的最新版本为`9.1p1`.
1. 将代码包`openssh-9.1p1.tar.gz`放到一个临时目录中, 本文假设为`~/openssh/`, 解压缩:

    ```bash
    tar xzvf openssh-9.1p1.tar.gz
    cd openssh-9.1p1
    ```

1. 配置编译环境, 下载飞凌提供的编译工具链, 假设工具链安装在`/opt`目录下, 运行

    ```bash
    echo ". /opt/fsl-imx-x11/4.1.15-2.0.0/environment-setup-cortexa7hf-neon-poky-linux-gnueabi">>~/.bashrc
    ```

    将其添加到用户的`bash`配置文件中, 不必每次都手动运行上述命令

1. 在`openssh-9.1p1`目录中, 运行

    ```bash
    ./configure --host=arm-poky-linux-gnueabi  --without-openssl && make sftp-server
    ```

    即可生成可执行程序`sftp-server`, 将其复制到开发板的`/usr/libexec/`目录下, 重启开发板, 即可使用`sftp`传输文件了
