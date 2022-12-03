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
