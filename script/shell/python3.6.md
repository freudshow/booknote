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