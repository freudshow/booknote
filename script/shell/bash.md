# `bash`脚本

## 遍历文件和目录

```bash
#!/bin/bash
 
demofun(){
    for file in `ls $1`
    do
        if test -f $file
        then
            echo "file:  $file"
            dpkg -x $file . #需要执行的命令，这里解包deb文件
        elif test -d $file
        then
            echo "path: $file"
        fi
    done
}
 
path="/home/work/xxx/xxx"
demofun $path
```
