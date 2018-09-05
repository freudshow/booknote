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


