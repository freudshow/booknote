# AI 智能体自动更新系统配置文档

> **创建时间**: 2026-10-24  
> **适用环境**: Linux (systemd 用户服务)  
> **维护者**: floyd  

---

## 1. 概述

本文档记录了为以下 AI 编程智能体配置自动更新系统的完整过程：

| 智能体 | 命令 | 更新方式 |
|--------|------|----------|
| **pi** (含 codex) | `pi` | `pi update --self --approve` |
| **agy** | `agy` | `agy update` |
| **opencode** | `opencode` | `opencode upgrade` |
| **Claude Code** | `claude` | `claude update` |
| **free-claude-code** (fcc-*) | `fcc-*` | `uv tool upgrade free-claude-code` |
| **cursor-agent** | `cursor-agent` | `cursor-agent update` |
| **trae-agent** | `trae-agent` | `trae-agent update` |
| **hermes-agent** | `hermes-agent` | Git pull (如为 git 仓库) |

**自动化目标**: 每 12 小时自动检查并更新，无需人工干预。

---

## 2. 环境准备

### 2.1 确认已安装的智能体

```bash
# 检查所有智能体路径和版本
which pi agy opencode codex claude cursor-agent trae-agent hermes-agent
ls -la ~/.local/bin/ | grep -E 'fcc|agent'
pi --version && agy --version && opencode --version && claude --version
```

### 2.2 确认更新命令

```bash
pi update --help
agy --help | grep update
opencode upgrade --help
claude update --help
uv tool upgrade --help
cursor-agent update --help
trae-agent update --help
```

### 2.3 创建必要目录

```bash
mkdir -p ~/.local/log ~/.local/run ~/.config/systemd/user
```

---

## 3. 核心脚本创建

### 3.1 更新脚本 `update-agents.sh`

**位置**: `/home/floyd/repo/python_compile_json_to_c/update-agents.sh`

**关键设计要点**:

1. **锁机制**: 防止并发执行 (`flock`)
2. **容错处理**: 单个工具失败不影响其他工具 (`|| true` / `continuing...`)
3. **超时控制**: 网络操作设置超时 (`timeout 60`)
4. **版本对比**: 更新前后版本对比，仅记录实际变更
5. **日志记录**: 统一输出到 `~/.local/log/agent-updates.log`

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${HOME}/.local/log/agent-updates.log"
LOCK_FILE="${HOME}/.local/run/agent-updates.lock"

mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$LOCK_FILE")"

exec 200>"$LOCK_FILE"
flock -n 200 || {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Another update process is running, exiting" >> "$LOG_FILE"
    exit 0
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

update_tool() {
    local name="$1" check_cmd="$2" update_cmd="$3"
    local version_before="" version_after=""

    log "Checking $name..."
    eval "$check_cmd" >/dev/null 2>&1 && version_before=$(eval "$check_cmd" 2>/dev/null | head -1)

    if eval "$update_cmd" >> "$LOG_FILE" 2>&1; then
        eval "$check_cmd" >/dev/null 2>&1 && version_after=$(eval "$check_cmd" 2>/dev/null | head -1)
        if [[ -n "$version_before" && -n "$version_after" && "$version_before" != "$version_after" ]]; then
            log "✓ $name updated: $version_before -> $version_after"
        elif [[ -n "$version_after" ]]; then
            log "✓ $name checked (current: $version_after)"
        else
            log "✓ $name update completed"
        fi
    else
        log "✗ $name update failed (exit code: $?), continuing..."
    fi
}

log "=== Starting agent update check ==="

update_tool "pi" "pi --version" "timeout 60 pi update --self --approve || true"
update_tool "agy" "agy --version" "agy update"
update_tool "opencode" "opencode --version" "opencode upgrade"
update_tool "claude" "claude --version" "claude update"
update_tool "free-claude-code (fcc-*)" "uv tool list | grep free-claude-code" "uv tool upgrade free-claude-code"
update_tool "cursor-agent" "cursor-agent --version" "cursor-agent update 2>/dev/null || true"
update_tool "trae-agent" "trae-agent --version 2>/dev/null | head -1" "trae-agent update 2>/dev/null || true"

if [[ -d "$HOME/.local/share/hermes-agent/.git" ]]; then
    update_tool "hermes-agent" "hermes-agent --version 2>/dev/null | head -1" "cd $HOME/.local/share/hermes-agent && git pull --ff-only"
else
    log "hermes-agent: not a git repo, skipping auto-update"
fi

log "=== Agent update check completed ==="
```

### 3.2 赋予执行权限

```bash
chmod +x /home/floyd/repo/python_compile_json_to_c/update-agents.sh
```

---

## 4. Systemd 服务配置

### 4.1 服务单元 `agent-updater.service`

**位置**: `/home/floyd/repo/python_compile_json_to_c/agent-updater.service`

```ini
[Unit]
Description=AI Agent Auto-Updater
Documentation=https://github.com/your-repo/agent-updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/home/floyd/repo/python_compile_json_to_c/update-agents.sh
User=floyd
Group=floyd
Environment=HOME=/home/floyd
Environment=PATH=/home/floyd/.local/bin:/home/floyd/.opencode/bin:/home/floyd/.local/share/pi-node/node-v22.23.1-linux-x64/bin:/usr/local/bin:/usr/bin:/bin
WorkingDirectory=/home/floyd/repo/python_compile_json_to_c
StandardOutput=append:/home/floyd/.local/log/agent-updates.log
StandardError=append:/home/floyd/.local/log/agent-updates.log

# Resource limits
MemoryMax=512M
CPUQuota=50%

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/floyd/.local/log /home/floyd/.local/run /home/floyd/.local/share /home/floyd/.cache /home/floyd/.config /home/floyd/.pi /home/floyd/.npm /home/floyd/.gemini /home/floyd/.local/bin
```

**关键配置说明**:

| 配置项 | 说明 |
|--------|------|
| `Type=oneshot` | 单次执行型服务，适合定时任务 |
| `MemoryMax=512M` | 限制内存，防止内存泄漏 |
| `CPUQuota=50%` | 限制 CPU 使用 |
| `ProtectSystem=strict` | 系统目录只读 |
| `ProtectHome=read-only` | 用户目录只读 |
| `ReadWritePaths` | 明确允许写入的路径（含各工具缓存目录） |

### 4.2 定时器 `agent-updater.timer`

**位置**: `/home/floyd/repo/python_compile_json_to_c/agent-updater.timer`

```ini
[Unit]
Description=Run AI Agent Auto-Updater every 12 hours
Requires=agent-updater.service

[Timer]
OnCalendar=*-*-* 00:00,12:00
Persistent=true
RandomizedDelaySec=30m
AccuracySec=1h

[Install]
WantedBy=timers.target
```

**关键配置说明**:

| 配置项 | 说明 |
|--------|------|
| `OnCalendar=*-*-* 00:00,12:00` | 每天 00:00 和 12:00 触发 |
| `Persistent=true` | 系统休眠/关机期间错过的任务会在唤醒后补跑 |
| `RandomizedDelaySec=30m` | 随机延迟 0-30 分钟，避免同时请求更新服务器 |
| `AccuracySec=1h` | 允许 1 小时内触发，减少系统唤醒 |

---

## 5. 安装部署

### 5.1 安装脚本 `install-updater.sh`

**位置**: `/home/floyd/repo/python_compile_json_to_c/install-updater.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="${SCRIPT_DIR}/agent-updater.service"
TIMER_FILE="${SCRIPT_DIR}/agent-updater.timer"
SCRIPT_FILE="${SCRIPT_DIR}/update-agents.sh"

USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "Installing AI Agent Auto-Updater..."

mkdir -p "${USER_SYSTEMD_DIR}"
cp "${SERVICE_FILE}" "${USER_SYSTEMD_DIR}/"
cp "${TIMER_FILE}" "${USER_SYSTEMD_DIR}/"
chmod +x "${SCRIPT_FILE}"
mkdir -p "${HOME}/.local/log" "${HOME}/.local/run"

systemctl --user daemon-reload
systemctl --user enable agent-updater.timer
systemctl --user start agent-updater.timer

echo "✓ Service installed and timer started"
echo ""
echo "Check status with:"
echo "  systemctl --user status agent-updater.timer"
echo "  systemctl --user status agent-updater.service"
echo ""
echo "View logs with:"
echo "  journalctl --user -u agent-updater.service -f"
echo "  tail -f ~/.local/log/agent-updates.log"
echo ""
echo "Run manually once to test:"
echo "  systemctl --user start agent-updater.service"
```

### 5.2 执行安装

```bash
chmod +x /home/floyd/repo/python_compile_json_to_c/install-updater.sh
/home/floyd/repo/python_compile_json_to_c/install-updater.sh
```

### 5.3 验证安装

```bash
# 查看定时器状态
systemctl --user status agent-updater.timer

# 查看服务文件是否正确加载
systemctl --user cat agent-updater.service
systemctl --user cat agent-updater.timer
```

---

## 6. 测试与验证

### 6.1 手动触发首次运行

```bash
systemctl --user start agent-updater.service
```

### 6.2 监控运行日志

```bash
# 实时查看 systemd 日志
journalctl --user -u agent-updater.service -f

# 或查看脚本日志
tail -f ~/.local/log/agent-updates.log
```

### 6.3 验证更新结果

```bash
# 检查所有智能体版本
pi --version && agy --version && opencode --version && claude --version
cursor-agent --version && trae-agent --version
```

---

## 7. 常见问题与解决

### 7.1 pi 更新失败：EROFS (只读文件系统)

**现象**: `Error: EROFS: read-only file system, mkdir '/home/floyd/.pi/agent/trust.json.lock'`

**原因**: systemd 的 `ProtectHome=read-only` 导致 `~/.pi` 无法写入

**解决**: 在 `ReadWritePaths` 中添加 `/home/floyd/.pi` 和 `/home/floyd/.npm`

```ini
ReadWritePaths=... /home/floyd/.pi /home/floyd/.npm
```

### 7.2 agy 更新失败：目录不可写

**现象**: `Error: directory /home/floyd/.local/bin is not fully accessible`

**解决**: 添加 `/home/floyd/.local/bin` 和 `/home/floyd/.gemini` 到 `ReadWritePaths`

### 7.3 pi 更新超时

**现象**: `Error: Could not determine latest pi version: The operation was aborted due to timeout`

**解决**: 
- 使用 `--self` 仅更新 pi 自身，不更新扩展包
- 添加 `timeout 60` 限制
- 失败时用 `|| true` 继续执行其他工具

### 7.4 claude 更新网络失败

**现象**: `Failed to fetch version from https://downloads.claude.ai/...`

**解决**: 网络问题属于外部依赖，脚本已容错处理，不阻塞其他工具更新

### 7.5 free-claude-code 版本固定

**现象**: `hint: 'free-claude-code' is pinned to '6.16.16'`

**说明**: uv tool 安装时使用了精确版本锁定，如需大版本升级需手动执行：
```bash
uv tool install free-claude-code@latest
```

### 7.6 服务内存超限

**现象**: `Memory: 511.9M (max: 512M)`

**解决**: 调整 `MemoryMax` 到 1G，或优化脚本减少并发进程

---

## 8. 维护操作手册

### 8.1 查看定时任务下次运行时间

```bash
systemctl --user list-timers --all | grep agent
```

### 8.2 手动执行一次更新

```bash
systemctl --user start agent-updater.service
```

### 8.3 查看最近一次运行结果

```bash
journalctl --user -u agent-updater.service -n 50 --no-pager
# 或
cat ~/.local/log/agent-updates.log
```

### 8.4 临时禁用自动更新

```bash
systemctl --user stop agent-updater.timer
systemctl --user disable agent-updater.timer
```

### 8.5 重新启用自动更新

```bash
systemctl --user enable --now agent-updater.timer
```

### 8.6 修改更新频率

编辑 `agent-updater.timer` 中的 `OnCalendar`：

```ini
# 每 6 小时
OnCalendar=*-*-* 00:00,06:00,12:00,18:00

# 每天凌晨 3 点
OnCalendar=*-*-* 03:00

# 每周一凌晨 2 点
OnCalendar=Mon *-*-* 02:00
```

修改后重载：
```bash
systemctl --user daemon-reload
systemctl --user restart agent-updater.timer
```

### 8.7 卸载自动更新系统

```bash
systemctl --user disable --now agent-updater.timer
systemctl --user disable --now agent-updater.service
rm ~/.config/systemd/user/agent-updater.service
rm ~/.config/systemd/user/agent-updater.timer
systemctl --user daemon-reload
```

---

## 9. 文件清单

| 文件路径 | 说明 |
|----------|------|
| `~/repo/python_compile_json_to_c/update-agents.sh` | 核心更新脚本 |
| `~/repo/python_compile_json_to_c/agent-updater.service` | systemd 服务定义 |
| `~/repo/python_compile_json_to_c/agent-updater.timer` | systemd 定时器定义 |
| `~/repo/python_compile_json_to_c/install-updater.sh` | 一键安装脚本 |
| `~/.config/systemd/user/agent-updater.service` | 已安装的服务文件 |
| `~/.config/systemd/user/agent-updater.timer` | 已安装的定时器文件 |
| `~/.local/log/agent-updates.log` | 运行日志 |
| `~/.local/run/agent-updates.lock` | 防并发锁文件 |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-10-24 | 初始版本：创建脚本、服务、定时器，完成安装测试 |
| 1.1 | 2026-10-24 | 修复 pi/agy 权限问题，添加 ReadWritePaths，优化容错逻辑 |

---

## 11. 参考资源

- [systemd.timer 官方文档](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [systemd.service 官方文档](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [systemd.exec 安全选项](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectSystem=)
- [pi 更新文档](https://github.com/earendil-works/pi)
- [agy 更新文档](https://github.com/antigravity-cli/agy)
- [opencode 升级文档](https://opencode.ai/docs/upgrade)
- [Claude Code 更新](https://docs.anthropic.com/claude-code)
- [uv tool 升级](https://docs.astral.sh/uv/reference/cli/uv_tool_upgrade/)

---

*文档结束*