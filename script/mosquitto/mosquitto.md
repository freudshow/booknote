# `mosquitto`设置

## 开启外部访问

`mosquitto`默认是本机模式, 外部计算机访问不了. 假设`mosquitto`的配置文件放在`/etc/mosquitto.conf`, 则修改`/etc/mosquitto.conf`, 加上几行配置:

```shell
    allow_anonymous true    #开启匿名登录
    listener 1883           #监听1883端口
    persistence true        #永久有效
    persistence_location /mosquitto/data/
    log_dest file /mosquitto/log/mosquitto.log
```

在开发板的`/etc/rc.local`加上:

```shell
    /sbin/mosquitto -v -c /etc/mosquitto #指定运行时读取的配置文件
```

重启开发板, 就可以从外部计算机访问开发板的`mosquitto`了
