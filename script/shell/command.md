# 文件排重命令

```bash
    find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

# 文件排重工具

**fdupes**

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

# Linux系统备份与还原

## 备份系统
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

## 恢复系统

- 将backup.tar.bz2放到根目录, 使用下面的命令来恢复系统
```bash
    #tar xvPjf backup.tar.bz2 -C /
```

- 恢复命令结束时, 别忘了重新创建那些在备份时被排除在外的目录：
```bash
    # mkdir proc
    # mkdir lost+found
    # mkdir mnt
    # mkdir sys
```

# debian 安装 nodejs
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