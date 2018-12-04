# 文件排重命令

```
find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

# 文件排重工具

**fdupes**

```shell
sudo apt-get install fdupes
fdupes -r + directory #递归搜索重复文件
#使用-S选项来查看某个文件夹内找到的重复文件的大小
fdupes -Sr /to_directory/
#删除重复文件, 同时保留一个副本, 你可以使用-d选项
fdupes -d /to_directory/
#使用-f选项来忽略每个匹配集中的首个文件
fdupes -f /to_directory/
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
    # tar cvpjf backup.tar.bz2 –exclude=/proc –exclude=/lost+found –exclude=/backup.tar.bz2 –exclude=/mnt –exclude=/sys /
```

## 恢复系统

- 将backup.tar.bz2放到根目录, 使用下面的命令来恢复系统
```bash
    #tar xvpfj backup.tar.bz2 -C /
```

- 恢复命令结束时, 别忘了重新创建那些在备份时被排除在外的目录：
```bash
    # mkdir proc
    # mkdir lost+found
    # mkdir mnt
    # mkdir sys
```