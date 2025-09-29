sudo ln -s /usr/lib/x86_64-linux-gnu/libncursesw.so.6 /usr/lib/x86_64-linux-gnu/libncursesw.so.5
sudo ln -s /usr/lib/x86_64-linux-gnu/libtinfo.so.6 /usr/lib/x86_64-linux-gnu/libtinfo.so.5
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
wget https://www.python.org/ftp/python/3.6.15/Python-3.6.15.tgz
tar -xf Python-3.6.15.tgz
cd Python-3.6.15
./configure --enable-shared --prefix=/usr/local
make -j$(nproc)
sudo make install
sudo ldconfig /usr/local/lib
libpython3.6m.so.1.0

sudo echo "/usr/local/lib/">/etc/ld.so.conf.d/python36.conf && sudo ldconfig

gdb缺少依赖库的解决

交叉开发时，经常遇到Debian/Ubuntu系统下的arm工具链提供的gdb运行不起来，我的解决过程如下：
1. 提示"libncursesw.so.5"找不到
        libncursesw.so.5 这个库以及很老了, 现在的高版本的Debian/Ubuntu早就不提供这个库了，但是可以建立符号链接：
        sudo ln -s /usr/lib/x86_64-linux-gnu/libncursesw.so.6 /usr/lib/x86_64-linux-gnu/libncursesw.so.5
2. 提示"libtinfo.so.5"找不到
       同上，建立符号链接：
       sudo ln -s /usr/lib/x86_64-linux-gnu/libtinfo.so.6 /usr/lib/x86_64-linux-gnu/libtinfo.so.5
3. 提示"libpython3.6m.so.1.0"找不到
       这个属于 Python3.6 的库文件，但是高版本的Debian/Ubuntu不提供了，所以要从源代码编译安装：
       ① 安装必要的工具
                 sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
       ② 下载Python3.6源代码
                  wget https://www.python.org/ftp/python/3.6.15/Python-3.6.15.tgz
       ③ 解压
                 tar -xf Python-3.6.15.tgz && cd Python-3.6.15
       ④ 编译并安装
                ./configure --enable-shared --prefix=/usr/local
                make -j$(nproc)
                sudo make install
       ⑤ 配置ldconfig
              sudo echo "/usr/local/lib/">/etc/ld.so.conf.d/python36.conf && sudo ldconfig    (如果提示权限不够，则切换到 root 用户执行这个命令)
4. 再次运行工具链的gdb就可以了