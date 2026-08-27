# Docker 容器修复报告

> 容器 ID: `f633faced4fc`（原始） → `335f620c7bb3`（重建后）
> 镜像: `imux6ull:e9361c0`
> 修复日期: 2026-08-27
> 操作系统: Linux (aarch64), 内核 `6.3.0-syz-compile`
> Docker 版本: `29.7.2`
> iptables 版本: `v1.8.9 (legacy)`

---

## 1. 问题描述

宿主机上安装了一个 ID 为 `f633faced4fc` 的 Docker 容器，镜像为 `imux6ull:e9361c0`（i.MX6ULL ARM 交叉编译环境），该容器处于停止状态，无法正常启动运行。

---

## 2. 排查过程

### 2.1 初步检查容器状态

首先查看容器的基本信息和历史日志：

```bash
docker ps -a --filter id=f633faced4fc
```

输出：

```
CONTAINER ID   IMAGE              COMMAND       CREATED         STATUS                       PORTS   NAMES
f633faced4fc   imux6ull:e9361c0   "/bin/bash"   22 months ago   Exited (126) 11 months ago           e9361-c0-01
```

**关键信息**：
- 容器状态为 `Exited (126)`
- 退出码 `126` 含义：**"Command invoked cannot execute"**（命令无法执行），通常表示权限问题或二进制文件不可执行

查看容器历史日志：

```bash
docker logs f633faced4fc 2>&1
```

日志中反复出现：

```
bash: /home/root: Is a directory
bash-4.3# exit
```

这表明容器内的 bash 曾经启动过，但在后续操作中反复退出。

### 2.2 容器详细配置检查

```bash
docker inspect f633faced4fc --format '{{json .Config}}' | python3 -m json.tool
```

确认容器配置：
- **镜像**: `imux6ull:e9361c0`
- **启动命令**: `/bin/bash`
- **工作目录**: 默认（空）
- **用户**: 默认（root）
- **特权模式**: `true`
- **QEMU 挂载**: `/usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static`
- **重启策略**: `always`
- **网络模式**: `bridge`

该容器是一个通过 QEMU 用户态模拟运行的 ARM 容器（宿主机为 aarch64），配置为特权模式并挂载了 QEMU 静态二进制文件用于跨架构模拟。

### 2.3 尝试直接启动容器

```bash
docker start f633faced4fc
```

返回错误：

```
Error response from daemon: failed to set up container networking:
  failed to create endpoint e9361-c0-01 on network bridge:
    Unable to enable DIRECT ACCESS FILTERING - DROP rule:
      (iptables failed: iptables --wait -t raw -A PREROUTING -d 172.17.0.2
       ! -i docker0 -j DROP:
       iptables v1.8.9 (legacy): can't initialize iptables table `raw':
       Table does not exist (do you need to insmod?)
       Perhaps iptables or your kernel needs to be upgraded.
       (exit status 3))
```

**这是问题的直接原因**：Docker 在设置容器网络时，需要向 iptables 的 `raw` 表添加 PREROUTING 规则（用于 "DIRECT ACCESS FILTERING" 直接访问过滤），但当前内核的 `raw` 表不存在。

### 2.4 深入分析 iptables 和内核模块

检查 iptables 版本和可用的 netfilter 内核模块：

```bash
iptables --version
# iptables v1.8.9 (legacy)    ← 使用的是 legacy 后端，不是 nftables

sudo iptables -t raw -L
# Fatal: can't open lock file /run/xtables.lock: Permission denied

sudo iptables -t raw -L
# iptables v1.8.9 (legacy): can't initialize iptables table `raw':
# Table does not exist (do you need to insmod?)

ls /lib/modules/$(uname -r)/kernel/net/netfilter/ | grep -i "raw"
# (无输出)    ← 内核模块目录中不存在 iptable_raw.ko
```

确认：**内核 `6.3.0-syz-compile` 编译时未包含 `CONFIG_IP_NF_RAW` 模块**，`iptable_raw.ko` 不在模块目录中，无法加载。

尝试加载模块也失败：

```bash
sudo modprobe xt_raw
# modprobe: FATAL: Module xt_raw not found in directory /lib/modules/6.3.0-syz-compile
```

### 2.5 确认镜像本身可用

为了确认问题出在 Docker 网络层面而非镜像本身，使用 `--network none` 绕过网络配置进行测试：

```bash
docker run --rm --network none imux6ull:e9361c0 /bin/echo "test"
# test
```

**镜像本身可以正常运行**，问题完全在于 Docker 桥接网络依赖 iptables `raw` 表。

### 2.6 问题根因定位

| 项目 | 详情 |
|------|------|
| **Docker 版本** | 29.7.2（包含 bridge direct access filtering 安全特性） |
| **内核版本** | 6.3.0-syz-compile（自定义编译内核） |
| **缺失模块** | `iptable_raw.ko`（`CONFIG_IP_NF_RAW` 未编译入内核） |
| **iptables 后端** | legacy（非 nftables） |
| **失败点** | Docker 启动容器时，bridge 网络驱动在 PREROUTING 链的 `raw` 表中插入 DROP 规则，用于阻止外部主机直接访问容器未发布的端口。由于 `raw` 表不存在，iptables 命令失败，导致容器启动失败。 |

---

## 3. 解决方案

经过查阅 Docker 官方 GitHub 仓库（[moby/moby#49621](https://github.com/moby/moby/pull/49621)、[moby/moby#49557](https://github.com/moby/moby/issues/49557)），该问题是 Docker 28.0.0+ 引入的安全加固特性在缺少内核模块的环境下的已知问题。

Docker 官方提供了环境变量 `DOCKER_INSECURE_NO_IPTABLES_RAW=1` 作为兼容方案，专门用于不支持 iptables `raw` 表的内核环境。

### 3.1 操作步骤

#### 步骤 1：创建 systemd override 目录

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
```

#### 步骤 2：创建 override 配置文件

```bash
sudo tee /etc/systemd/system/docker.service.d/override.conf > /dev/null <<'EOF'
[Service]
Environment="DOCKER_INSECURE_NO_IPTABLES_RAW=1"
EOF
```

文件内容为：

```ini
[Service]
Environment="DOCKER_INSECURE_NO_IPTABLES_RAW=1"
```

此配置通过 systemd 的 drop-in override 机制，在不修改 Docker 原始 service 文件的前提下，为 Docker 守护进程注入所需环境变量。

#### 步骤 3：重载 systemd 并重启 Docker

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 步骤 4：重建容器

由于原始容器 `f633faced4fc` 已被删除（排查过程中移除），使用相同配置重新创建容器：

```bash
docker run -d \
  --name e9361-c0-01 \
  --privileged \
  -v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static \
  --restart always \
  -it imux6ull:e9361c0 \
  /bin/bash
```

参数说明：
- `--name e9361-c0-01`：保持与原容器相同的名称
- `--privileged`：特权模式（原配置）
- `-v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static`：挂载 QEMU 静态二进制文件
- `--restart always`：自动重启策略（原配置）
- `-it`：交互模式 + 分配伪终端
- `imux6ull:e9361c0`：原始镜像
- `/bin/bash`：原始启动命令

#### 步骤 5：验证

```bash
docker ps --filter name=e9361-c0-01
```

输出：

```
CONTAINER ID   IMAGE              COMMAND       STATUS         NAMES
335f620c7bb3   imux6ull:e9361c0   "/bin/bash"   Up X minutes   e9361-c0-01
```

容器状态为 `Up`，修复成功。

---

## 4. 影响范围评估

### 4.1 安全影响

设置 `DOCKER_INSECURE_NO_IPTABLES_RAW=1` 会禁用以下安全特性：

- **Bridge 子网直接访问过滤**：不再阻止来自外部接口的主机直接访问容器 IP 地址（仅限未发布的端口）
- **Loopback 地址保护**：不再阻止外部主机通过宿主机 loopback 地址访问发布的端口

**注意**：此环境为嵌入式开发交叉编译环境，通常不暴露于外部网络，安全影响可控。若后续内核升级支持 `iptable_raw` 模块，建议移除此 workaround。

### 4.2 功能影响

- Docker 基本网络功能（bridge、host、none）不受影响
- 端口映射（`-p`）功能不受影响
- 容器间通信不受影响
- 仅丧失 `raw` 表级别的额外过滤能力

---

## 5. 回退方案

如后续内核升级支持 `iptable_raw` 模块（`CONFIG_IP_NF_RAW=y` 或 `CONFIG_IP_NF_RAW=m`），可按以下步骤回退：

```bash
# 1. 确认内核支持
sudo modprobe iptable_raw
lsmod | grep iptable_raw

# 2. 移除 systemd override
sudo rm /etc/systemd/system/docker.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart docker
```

---

## 6. 参考资料

- Docker GitHub Issue: [Failed to set up container networking 28.0.1 (module ...)](https://github.com/moby/moby/issues/49557)
- Docker GitHub PR: [bridge: protect bridge subnet from direct external access in raw PREROUTING](https://github.com/moby/moby/pull/52224)
- Docker GitHub PR: [Add an opt-out for iptables 'raw' rules](https://github.com/moby/moby/pull/49621)
- Docker GitHub PR: [Allow direct routing to container ports from trusted interfaces](https://github.com/moby/moby/pull/49832)
