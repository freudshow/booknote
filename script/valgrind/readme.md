# `imx.6ull`交叉编译`valgrind`

1. 将`configure`文件中的`armv6`改为`armv7ve`
1. 安装恩智浦官方工具链
1. 运行命令`./configure --prefix=/opt/valgrind --host=arm-linux`
1. `make -j4 && make install`

