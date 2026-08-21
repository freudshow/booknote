# IMX6ULL 开发板 SSH/SCP 免密配置说明

本文记录本机与 IMX6ULL 开发板之间配置 SSH 公钥免密登录、传统 SCP 文件传输以及 SFTP 验证的完整步骤。

## 1. 环境信息

### 本机

- 本机用户名：`floyd`
- SSH 客户端：OpenSSH
- 本机 SSH 配置文件：`~/.ssh/config`
- 本机专用私钥：`~/.ssh/id_rsa_imx`
- 本机专用公钥：`~/.ssh/id_rsa_imx.pub`

### IMX6ULL 开发板

- IP：`192.168.0.232`
- SSH 端口：`22`
- 用户名：`root`
- SSH 服务端：Dropbear `v2015.71`
- root 用户 HOME：`/home/root`
- 公钥文件：`/home/root/.ssh/authorized_keys`
- SCP 程序：`/sbin/scp`
- SFTP 服务端：`/usr/libexec/sftp-server`

> 安全提示：密码只用于首次登录或安装公钥。配置完成后应避免把密码写入脚本、Git 仓库或文档。本文不记录实际密码。

---

## 2. 检查本机环境

确认 SSH、SCP 和 `sshpass` 是否存在：

```bash
command -v ssh
command -v scp
command -v sshpass
```

如果需要自动执行首次公钥安装，可以使用 `sshpass`。没有该工具时，也可以手工输入密码完成同样操作。

检查本机 SSH 目录：

```bash
ls -la ~/.ssh
```

如果目录不存在，创建并设置权限：

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

检查开发板 SSH 端口是否可达：

```bash
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/192.168.0.232/22' \
    && echo SSH_PORT_OK \
    || echo SSH_PORT_UNREACHABLE
```

也可以直接尝试登录：

```bash
ssh root@192.168.0.232
```

首次连接时确认主机指纹，并输入开发板 root 密码。

---

## 3. 为开发板生成专用 SSH 密钥

建议为开发板单独生成密钥，不要直接复用其他服务器的密钥。

由于开发板运行的是较老的 Dropbear `v2015.71`，本次使用 RSA 密钥兼容旧服务端：

```bash
ssh-keygen -t rsa -b 2048 -N '' \
    -f ~/.ssh/id_rsa_imx \
    -C 'floyd@imx6ull-legacy'
```

参数说明：

- `-t rsa`：生成 RSA 密钥；
- `-b 2048`：使用 2048 位密钥，兼容旧版 Dropbear；
- `-N ''`：私钥不设置口令，因此可以实现完全免交互登录；
- `-f ~/.ssh/id_rsa_imx`：保存为 IMX 专用密钥；
- `-C`：设置备注信息。

生成后应存在两个文件：

```text
~/.ssh/id_rsa_imx       # 私钥，只能保存在本机
~/.ssh/id_rsa_imx.pub   # 公钥，可复制到开发板
```

设置私钥权限：

```bash
chmod 600 ~/.ssh/id_rsa_imx
chmod 644 ~/.ssh/id_rsa_imx.pub
```

查看公钥内容：

```bash
cat ~/.ssh/id_rsa_imx.pub
```

公钥必须是单行，通常以以下内容开头：

```text
ssh-rsa AAAA...
```

---

## 4. 将公钥安装到开发板

### 方法 A：使用 ssh-copy-id

先确认开发板支持 `ssh-copy-id`：

```bash
command -v ssh-copy-id
```

如果存在，可以执行：

```bash
ssh-copy-id \
    -o StrictHostKeyChecking=no \
    -i ~/.ssh/id_rsa_imx.pub \
    root@192.168.0.232
```

根据提示输入一次 root 密码。

### 方法 B：使用 sshpass 自动安装

如果本机安装了 `sshpass`，可以执行：

```bash
sshpass -p '<开发板root密码>' ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    root@192.168.0.232 \
    'mkdir -p /home/root/.ssh; chmod 700 /home/root/.ssh'
```

然后追加本机公钥：

```bash
PUBKEY="$(cat ~/.ssh/id_rsa_imx.pub)"

sshpass -p '<开发板root密码>' ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    root@192.168.0.232 \
    "printf '%s\\n' '$PUBKEY' >> /home/root/.ssh/authorized_keys"
```

修正开发板端权限：

```bash
sshpass -p '<开发板root密码>' ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    root@192.168.0.232 \
    'chmod 700 /home/root/.ssh; chmod 600 /home/root/.ssh/authorized_keys; chown root:root /home/root/.ssh /home/root/.ssh/authorized_keys 2>/dev/null || true'
```

> 推荐使用 `printf` 或 `ssh-copy-id` 安装公钥，不要使用可能破坏换行的编辑方式。公钥必须完整保持为一行。

### 方法 C：手工复制公钥

在本机执行：

```bash
cat ~/.ssh/id_rsa_imx.pub
```

复制整行内容。

登录开发板：

```bash
ssh root@192.168.0.232
```

在开发板执行：

```sh
mkdir -p /home/root/.ssh
chmod 700 /home/root/.ssh
vi /home/root/.ssh/authorized_keys
```

将公钥粘贴为一整行，然后执行：

```sh
chmod 600 /home/root/.ssh/authorized_keys
chown root:root /home/root/.ssh /home/root/.ssh/authorized_keys 2>/dev/null || true
```

---

## 5. 验证 SSH 公钥免密登录

在本机执行：

```bash
ssh \
    -o BatchMode=yes \
    -o IdentitiesOnly=yes \
    -o HostKeyAlgorithms=+ssh-rsa \
    -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -i ~/.ssh/id_rsa_imx \
    root@192.168.0.232 \
    'echo key-login-ok'
```

成功时应输出：

```text
key-login-ok
```

`BatchMode=yes` 表示禁止密码交互。如果公钥配置不正确，命令会直接失败，便于确认是否真正实现免密登录。

如果失败，使用详细日志检查：

```bash
ssh -vvv \
    -o IdentitiesOnly=yes \
    -o HostKeyAlgorithms=+ssh-rsa \
    -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -i ~/.ssh/id_rsa_imx \
    root@192.168.0.232
```

重点查看以下日志：

```text
Offering public key
Server accepts key
Authenticated
```

如果出现 `no mutual signature algorithm`，通常需要确认：

1. 使用的是 RSA 密钥；
2. SSH 命令中包含 `PubkeyAcceptedAlgorithms=+ssh-rsa`；
3. 开发板 `authorized_keys` 中的公钥与本机私钥匹配。

---

## 6. 配置本机 SSH 别名

编辑本机配置文件：

```bash
vi ~/.ssh/config
```

加入：

```sshconfig
Host imx6ull
    HostName 192.168.0.232
    User root
    Port 22
    IdentityFile ~/.ssh/id_rsa_imx
    IdentitiesOnly yes
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
```

设置权限：

```bash
chmod 600 ~/.ssh/config
```

之后可以使用别名登录：

```bash
ssh imx6ull
```

或者执行远程命令：

```bash
ssh imx6ull 'uname -a'
```

检查最终生效配置：

```bash
ssh -G imx6ull | grep -E \
    'hostname|user|port|identityfile|identitiesonly|pubkeyacceptedalgorithms'
```

---

## 7. Dropbear 与传统 SCP 的兼容性

开发板的 Dropbear 版本为：

```text
Dropbear v2015.71
```

本机 OpenSSH 版本较新时，`scp` 默认可能使用 SFTP 协议，而不是旧版 SCP 协议。开发板虽然提供了自编译的：

```text
/usr/libexec/sftp-server
```

但老版本 Dropbear 对 SFTP 子系统的配置和兼容性可能不完整。因此传统文件复制建议显式使用 `-O`：

```bash
scp -O local_file imx6ull:/tmp/
```

其中：

```text
-O = 使用传统 SCP 协议
```

不要将 `-O` 和 `-o` 混淆：

```text
-O          scp 的传统协议选项
-o option   SSH 配置选项
```

---

## 8. 修正开发板 SCP 程序路径

Dropbear 处理传统 SCP 请求时，通常会在远端执行：

```text
scp
```

当前开发板实际只有：

```text
/sbin/scp
```

而默认 PATH 为：

```text
/usr/bin:/bin
```

因此需要创建软链接：

```bash
ssh imx6ull
```

在开发板执行：

```sh
ln -sf /sbin/scp /usr/bin/scp
ls -l /usr/bin/scp
```

预期结果：

```text
/usr/bin/scp -> /sbin/scp
```

验证远端路径：

```sh
ls -l /sbin/scp /usr/bin/scp
```

如果文件系统是只读的，软链接可能无法永久保存，需要在系统启动脚本、overlay 文件系统或制作根文件系统时加入该链接。

---

## 9. 验证 SCP 上传

在本机创建测试文件：

```bash
printf 'scp-test-%s\n' "$(date +%s)" > /tmp/mqttdb-key-test
```

使用传统 SCP 协议上传：

```bash
scp -O /tmp/mqttdb-key-test \
    imx6ull:/tmp/mqttdb-key-test.remote
```

检查远端内容：

```bash
ssh imx6ull \
    'cat /tmp/mqttdb-key-test.remote; rm -f /tmp/mqttdb-key-test.remote'
```

批量上传本工程 IMX 产物：

```bash
scp -O output/demo_client \
    output/mqttsafe_demo \
    imx6ull:/tmp/mqttdb-test/
```

上传动态库：

```bash
scp -O lib/libjson-c.so \
    imx6ull:/tmp/mqttdb-test/lib/
```

上传配置文件：

```bash
scp -O config/demo_config_example.json \
    imx6ull:/tmp/mqttdb-test/
```

---

## 10. 验证 SFTP

启动 SFTP：

```bash
sftp imx6ull
```

在 SFTP 命令行中执行：

```text
pwd
ls /tmp/mqttdb-test
put output/demo_client /tmp/mqttdb-test/demo_client
bye
```

也可以使用批处理方式：

```bash
printf 'pwd\nls /tmp/mqttdb-test\nbye\n' | sftp -q imx6ull
```

如果提示找不到 SFTP 子系统，需要确认开发板上的 SFTP 服务路径，以及 Dropbear 的编译/启动配置。当前开发板上检测到：

```text
/usr/libexec/sftp-server
```

如果 Dropbear 启动参数或编译配置没有启用 SFTP 子系统，传统 SCP 仍然可以作为文件传输方式。

---

## 11. 推荐命令汇总

### SSH 登录

```bash
ssh imx6ull
```

### 执行远程命令

```bash
ssh imx6ull 'hostname; uname -a'
```

### 上传单个文件

```bash
scp -O ./local_file imx6ull:/tmp/
```

### 上传多个文件

```bash
scp -O file1 file2 imx6ull:/tmp/
```

### 上传目录

```bash
scp -O -r ./output imx6ull:/tmp/
```

### 下载文件

```bash
scp -O imx6ull:/tmp/remote_file ./
```

### SFTP

```bash
sftp imx6ull
```

---

## 12. 部署本工程程序的示例

上传 IMX 版本程序和动态库：

```bash
ssh imx6ull 'mkdir -p /tmp/mqttdb-test/lib'

scp -O output/demo_client \
    output/mqttsafe_demo \
    imx6ull:/tmp/mqttdb-test/

scp -O lib/libjson-c.so \
    imx6ull:/tmp/mqttdb-test/lib/

scp -O config/demo_config_example.json \
    imx6ull:/tmp/mqttdb-test/
```

在开发板上执行：

```bash
ssh imx6ull
```

```sh
cd /tmp/mqttdb-test
chmod +x demo_client mqttsafe_demo
export LD_LIBRARY_PATH=/tmp/mqttdb-test/lib
./demo_client demo_config_example.json
```

如果配置文件中的 Broker 地址可达，程序即可继续进行实际 MQTT 数据中心接口测试。

---

## 13. 常见问题排查

### 13.1 仍然要求输入密码

检查实际使用的私钥：

```bash
ssh -G imx6ull | grep identityfile
```

确认输出包含：

```text
/home/floyd/.ssh/id_rsa_imx
```

检查私钥权限：

```bash
chmod 600 ~/.ssh/id_rsa_imx
```

确认开发板公钥位置：

```bash
sshpass -p '<开发板root密码>' ssh root@192.168.0.232 \
    'ls -l /home/root/.ssh/authorized_keys; wc -l /home/root/.ssh/authorized_keys'
```

### 13.2 出现 `Permission denied (publickey,password)`

使用调试模式：

```bash
ssh -vvv -o IdentitiesOnly=yes -i ~/.ssh/id_rsa_imx imx6ull
```

检查：

- 开发板用户 HOME 是否为 `/home/root`；
- 公钥是否放在 `/home/root/.ssh/authorized_keys`；
- `.ssh` 是否为 `700`；
- `authorized_keys` 是否为 `600`；
- 公钥是否完整且只有一行；
- 本机私钥是否与开发板公钥匹配。

### 13.3 SCP 报 `scp: command not found`

在开发板执行：

```sh
ls -l /sbin/scp /usr/bin/scp
ln -sf /sbin/scp /usr/bin/scp
```

然后重新执行：

```bash
scp -O local_file imx6ull:/tmp/
```

### 13.4 SCP 默认使用 SFTP 失败

强制使用传统 SCP：

```bash
scp -O local_file imx6ull:/tmp/
```

### 13.5 SFTP 登录失败

确认开发板存在：

```sh
ls -l /usr/libexec/sftp-server
```

再使用详细日志：

```bash
sftp -vvv imx6ull
```

如果 SFTP 子系统不可用，优先使用传统 SCP。SFTP 服务端需要由 Dropbear 的配置或启动方式正确调用，单独存在 `/usr/libexec/sftp-server` 并不一定代表 Dropbear 已经配置好 SFTP 子系统。

### 13.6 重启后软链接消失

说明 `/usr/bin` 所在文件系统由启动脚本重新生成，或者根文件系统为临时/只读文件系统。需要将以下命令加入启动脚本或固件制作流程：

```sh
ln -sf /sbin/scp /usr/bin/scp
```

同时建议在固件中直接修正目录布局，确保 `/usr/bin/scp` 在系统启动后始终存在。

---

## 14. 安全建议

1. 配置完成后，可以关闭 Dropbear 的密码登录，仅保留公钥登录；修改前必须确保公钥登录已验证成功，并保留一个已登录的 SSH 会话，避免把自己锁在开发板外。
2. 不要在 Shell 历史记录中保存明文密码。使用 `sshpass -p` 会把密码暴露在 Shell 历史或进程信息中，建议仅在临时初始化时使用。
3. 更安全的初始化方式是手工输入密码，或者使用受保护的密码文件：

   ```bash
   chmod 600 password-file
   sshpass -f password-file ssh root@192.168.0.232
   ```

4. 私钥 `~/.ssh/id_rsa_imx` 不能复制到开发板或提交到代码仓库。
5. 如果给多人使用，应为每个人生成独立公钥，并在开发板 `authorized_keys` 中分别管理。
6. 开发板使用固定 root 密码存在安全风险，建议在受控网络中使用，并在产品化部署时更换密码。
