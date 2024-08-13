# `docker`学习笔记

## 常用命令

```bash

### 在修改已运行的容器, 使其重启自动运行
docker update --restart=always <CONTAINER ID>

### 将已经运行的镜像导出
docker export -o name.tar <CONTAINER ID>


### run docker
docker run -it -v /home/floyd/dockermap:/map -p 5901:5901 --restart=always my/ubuntu16.04armhf
docker run -it -v /home/floyd/dockermap:/map -p 5901:5901 --restart=always hello-world
```

## Linux 下修改Docker默认存储路径

修改配置文件 `/etc/docker/daemon.json`

```javascript
{
    ...
    "data-root": "/data/docker/",
    ...
    
}
```

重启`docker`服务

```shell
sudo systemctl daemon-reload && sudo systemctl restart docker
```

查看`docker`信息

```shell
docker info
...
OSType: linux
Architecture: x86_64
CPUs: 8
Total Memory: 15.42GiB
Name: VM-125-197-centos
ID: OLLW:ZRBS:Z2XV:34ER:NKGJ:NNH4:LKOX:YX3U:BSDO:SL2I:F7S7:CMSM
Docker Root Dir: /data/docker
Debug Mode (client): false
Debug Mode (server): false
Registry: https://index.docker.io/v1/
...
```

## 在`x86`系统运行`arm`架构的`docker`镜像

```shell
#安装qemu的arm模拟器
sudo apt install binfmt-support qemu-user-static
#将文件系统 rootfs-console.tar.bz2 导入为docker镜像
docker import rootfs-console.tar.bz2 imux6ull:e9361c0
#创建容器, --name 后是容器的名字; imux6ull:e9361c0 是镜像名; --restart=always, 指定了容器在主机重启后，自动启动
docker run -itd --name e9361-c0-01 --restart=always --privileged -v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static imux6ull:e9361c0 /bin/bash
#进入容器
docker exec -it e9361-c0-01 /bin/bash
```

