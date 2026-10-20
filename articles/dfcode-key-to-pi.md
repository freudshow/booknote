# 把 dfcode 移植到 pi

> **本文三部分**：§1-§7 把 dfcode 企业模型凭证导入 pi；
> §8-§16 把 dfcode 的工作流（spec / plan / review）移植成 pi 的 skill 与扩展；
> §17-§23 溯源：**dfcode 是 opencode 的 fork**，含证据、自研增量与一处已补的门禁。

> 记录于 2026-09-27。本文**不含任何密钥明文**，只记录路径与提取命令。
> 适用环境：Linux + dfcode（企业版，MaaS 私有网关）+ `@earendil-works/pi-coding-agent`。

---

## 0. 结论速览

| 问题 | 答案 |
|---|---|
| dfcode 的凭证在哪 | `~/.local/share/dfcode/enterprise/maas-config.json`（权限 600） |
| 是静态 key 还是 token | **静态** `sk-…`（67 字符），不是会过期的 JWT |
| 能给 pi 用吗 | 能。pi 只需 `baseUrl` + `apiKey` + 模型清单 |
| 为什么 dfcode 要网页登录 | 登录是**设备授权/领凭证**，不是模型认证 |
| 为什么 pi 不用登录 | 网关是哑代理，只校验静态 key；pi 复用了已落盘的凭证 |
| 工作流移植装了哪些东西 | 3 个 skill（`spec-workflow` / `plan-workflow` / `code-review`）+ 3 个扩展（`spec-tool` / `init` / `guard`） |
| dfcode 的 prompt 能直接拷吗 | 不能。需从 `index.js.map` 解出 TS 源码，`.txt` playbook 再从 267MB 二进制 `dd` 出来（§9） |
| pi 能复刻审批门禁吗 | **不能**。dfcode 靠 `plan_exit` 工具程序化卡门，pi 无内置审批，只能写成纪律（§10、§15） |
| dfcode 是自研的吗 | **不是，是 opencode 的 fork**。37/93 个 flag 改名后逐字节相同，sourcemap 里 `createOpencode` 调用 `createDfcodeServer`（§17-§19） |
| pi 能复刻审批门禁吗 | 能，但要走扩展。pi 无内置审批，用 `tool_call` hook 返回 `{block:true}`；已为 `spec new/archive` 补上门禁（§21-§22） |

---

## 1. dfcode 侧的文件布局

数据根目录：`~/.local/share/dfcode/`

| 文件 | 作用 | 关键字段 |
|---|---|---|
| `enterprise/maas-config.json` | **企业模型网关配置（要的就是这个）** | `baseUrl` / `apiKey` / `models[]` / `identity` |
| `auth.json` | 登录会话（**不要用于 pi**，会过期） | `dfcode.token` / `dfcode.refreshToken` / `dfcode.deviceId` |
| `enterprise-device.json` | 设备绑定 | `dev_fbcc6fb7…` / name / platform |
| `enterprise-device-secret.json` | 设备密钥 | `secret` / `protectionLevel: "file-weak"` |
| `kv.json`（在 `~/.local/state/dfcode/`） | 本地偏好 | `enterprise_user_name` 等 |

> `auth.json` 里的 JWT 有效期短，pi 每次请求都要它反而会频繁 401。用 `maas-config.json` 的静态 key。

---

## 2. 登录链路（为什么必须网页登录）

```
/login → 浏览器 OAuth（device code 流程）
       → 轮询控制面 https://api.dfcode.ai
       → 返回 { session: {token, refreshToken, deviceId},
                 maas:    {baseUrl, apiKey, models[]} }
       → writeMaasCache() 落盘到 enterprise/maas-config.json (mode 0600)
       → 之后的模型请求只走 http://<host>:<port>/v1/chat/completions
```

bundle 内可佐证的门禁文案：

- `当前设备需要重新登录后才能使用企业模型。\n\n请先输入 /login，并在浏览器中完成授权。`
- `企业模型已加载到列表`
- `登录后刷新企业模型(免重启)`
- `当前设备校验失败，请重新登录`

**关键点：登录的全部产物就是那个静态 `sk-` key。** 网关不校验
deviceId / secret / JWT——只带 `Authorization: Bearer sk-…` 就能 200。

所以：

- dfcode 强制登录 = 企业管控（谁可用、可用哪些模型、审计、配额、吊销设备）
- pi 无需登录 = pi 不做设备授权，直接复用已落盘的静态凭证
- **换句话说，pi 不是"跳过了登录"，而是"已经拿到了登录的最终产物"**

---

## 3. 查找 API key 的步骤

```bash
# 1) 企业网关配置：baseUrl + apiKey + 27 个模型目录
cat ~/.local/share/dfcode/enterprise/maas-config.json

# 2) 不要用这个（登录 JWT，会过期）
cat ~/.local/share/dfcode/auth.json

# 3) 把 key 放进变量（后续命令复用，避免反复明文出现在命令行历史）
KEY=$(python3 -c "import json;print(json.load(open('$HOME/.local/share/dfcode/enterprise/maas-config.json'))['apiKey'])")
```

### 可选：与服务端核对

`/v1/models` 是最有用的接口，直接返回每个模型的
`protocol` / `endpoint` / `context_window` / `max_output_tokens` /
`input_modalities` / `reasoning_format`——可以照抄生成 pi 配置。

```bash
BASE=$(python3 -c "import json;print(json.load(open('$HOME/.local/share/dfcode/enterprise/maas-config.json'))['baseUrl'])")

curl -s -H "Authorization: Bearer $KEY" "$BASE/v1/models" \
  | python3 -c "
import json,sys
for m in json.load(sys.stdin)['data']:
    print(m['id'],'|',m.get('protocol'),'|',m.get('endpoint'),
          '|',m.get('context_window'),m.get('max_output_tokens'),
          '|',m.get('input_modalities'),'|reasoning:',m.get('reasoning_format'))
"
```

实测可用命令（等价验证）：

```bash
# OpenAI 兼容
curl -s -X POST "$BASE/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"say ok"}],"max_tokens":16}'

# Anthropic 兼容
curl -s -X POST "$BASE/v1/messages" \
  -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-for-coding","messages":[{"role":"user","content":"say ok"}],"max_tokens":16}'
```

---

## 4. 导入 pi

pi 的 provider 配置在 `~/.pi/agent/models.json`（格式见
`@earendil-works/pi-coding-agent/docs/models.md`）。

### 4.1 关键坑：两个 api 类型的 baseUrl 不一样

| `api` | baseUrl | 原因 |
|---|---|---|
| `openai-completions` | `$BASE/v1` | pi 直接拼 `/chat/completions` |
| `anthropic-messages` | `$BASE`（**不带 /v1**） | Anthropic SDK 自己拼 `/v1/messages` |

带错会得到 `404 404 page not found`——我第一次就踩了这个。

### 4.2 手动配置模板

编辑 `~/.pi/agent/models.json`：

```json
{
  "providers": {
    "maas": {
      "name": "DFCode MaAAS (OpenAI-completions)",
      "api": "openai-completions",
      "baseUrl": "<BASE>/v1",
      "apiKey": "<从 maas-config.json 提取>",
      "models": [
        { "id": "gpt-5.6-luna", "contextWindow": 922000, "maxTokens": 128000,
          "input": ["text", "image"], "reasoning": true }
      ]
    },
    "maas-anthropic": {
      "name": "DFCode MaaS (Anthropic-messages)",
      "api": "anthropic-messages",
      "baseUrl": "<BASE>",
      "apiKey": "<同上>",
      "models": [
        { "id": "kimi-for-coding", "contextWindow": 128000, "maxTokens": 32000,
          "input": ["text", "image"], "reasoning": false }
      ]
    }
  }
}
```

### 4.3 自动生成（推荐，读服务端元数据）

从 `/v1/models` 拉目录，按 `protocol` 分流写进 `models.json`：

```bash
python3 - <<'PY'
import json, os, pathlib, urllib.request

src  = pathlib.Path.home()/'.local/share/dfcode/enterprise/maas-config.json'
dst  = pathlib.Path.home()/'.pi/agent/models.json'
cache = pathlib.Path('/tmp/maas_models.json')

cfg = json.loads(src.read_text())
base, key = cfg['baseUrl'], cfg['apiKey']

req = urllib.request.Request(base + '/v1/models',
                             headers={'Authorization': 'Bearer ' + key})
catalog = json.load(urllib.request.urlopen(req, timeout=30))['data']
cache.write_text(json.dumps({'data': catalog}))

def entry(m):
    return {
        'id':   m['id'],
        'name': m.get('display_name') or m['id'],
        # 服务端没给 context_window/max_output_tokens 时的保守值
        'contextWindow': m.get('context_window')  or 128000,
        'maxTokens':     m.get('max_output_tokens') or 32000,
        'input':         m.get('input_modalities') or ['text'],
        'reasoning':     m.get('reasoning_format') == 'openai',
    }

d = json.loads(dst.read_text())
d.setdefault('providers', {})
d['providers']['maas'] = {
    'name': 'DFCode MaaS (OpenAI-completions)',
    'api': 'openai-completions',
    'baseUrl': base + '/v1',
    'apiKey': key,
    'models': [entry(m) for m in catalog if m.get('protocol') == 'openai'],
}
d['providers']['maas-anthropic'] = {
    'name': 'DFCode MaaS (Anthropic-messages)',
    'api': 'anthropic-messages',
    'baseUrl': base,          # 注意：不带 /v1
    'apiKey': key,
    'models': [entry(m) for m in catalog if m.get('protocol') == 'anthropic'],
}
dst.write_text(json.dumps(d, ensure_ascii=False, indent=2))
os.chmod(dst, 0o600)
print('openai:', len(d['providers']['maas']['models']),
      'anthropic:', len(d['providers']['maas-anthropic']['models']))
PY
```

改动前先备份：

```bash
cp ~/.pi/agent/models.json ~/.pi/agent/models.json.bak
```

### 4.4 验证

```bash
pi --list-models maas          # 列出模型（context / max-out / thinking / images）
pi -p --no-session -nt --provider maas           --model gpt-5.6-luna   "回复:pi-ok"
pi -p --no-session -nt --provider maas-anthropic --model kimi-for-coding "回复:ok"
```

会话内 `/model` 也会重载 `models.json`，不必重启 pi。

### 4.5 不想让密钥落盘

用环境变量插值或命令（`models.json` 支持）：

```json
{ "apiKey": "$MAAS_API_KEY" }
{ "apiKey": "!jq -r .apiKey ~/.local/share/dfcode/enterprise/maas-config.json" }
```

注意 `!command` 在**请求时**执行，不缓存。

---

## 5. 日常维护

### 5.1 key 轮换后同步

dfcode 每次 `/login` 会刷新 `maas-config.json`，pi 里的副本是**快照**。
若 pi 突然 401，重跑登录后同步：

```bash
python3 - <<'PY'
import json, pathlib
src = pathlib.Path.home()/'.local/share/dfcode/enterprise/maas-config.json'
dst = pathlib.Path.home()/'.pi/agent/models.json'
cfg = json.loads(src.read_text()); d = json.loads(dst.read_text())
d['providers']['maas'].update(apiKey=cfg['apiKey'], baseUrl=cfg['baseUrl']+'/v1')
d['providers']['maas-anthropic'].update(apiKey=cfg['apiKey'], baseUrl=cfg['baseUrl'])
dst.write_text(json.dumps(d, ensure_ascii=False, indent=2))
print('synced')
PY
```

### 5.2 新增模型

`models.json` 里 `models` 数组**追加**同 ID 即可新增或替换该 provider 下的模型；
只想改内置/扩展模型的元数据（不改 provider 列表）用 `modelOverrides`，
未知 ID 会被忽略。

### 5.3 认证优先级

`--api-key`（运行时） → `auth.json` → `models.json` 的 `apiKey` → provider 环境变量。

---

## 6. 注意事项

1. **合规**：该 key 绑在 `identity`（`b830eb02…`）上，模型列表是企业采购的。
   绕开 `api.dfcode.ai` 意味着绕开了调用审计。若公司对 AI 工具使用有留痕要求，
   先跟管理员确认再用。
2. **可达性**：`baseUrl` 是**公网 IP**（`47.104.0.249:28088`），内网外也能连；
   但依赖公司网络策略，防火墙变更后会失效。
3. **元数据缺口**：`MiMo-*` / `MiniMax-*` / `qwen3.8` 等模型服务端未给
   `context_window` / `max_output_tokens`，脚本里填了保守值
   128K / 32K；`qwen3.8` 给了 262144 上下文。若实际更大，手工调大。
4. **文件权限**：`models.json` 内含明文密钥，保持 `chmod 600`；
   不要提交进任何 git 仓库。
5. **同机另一处**：`~/.config/opencode/opencode.json` 里也有一枚明文
   阿里云 token-plan key（`bailian-token-plan-personal`），性质相同，一并注意。

---

## 7. 参考文档位置

```
~/.local/share/pi-node/node-v22.23.1-linux-x64/lib/node_modules/@earendil-works/pi-coding-agent/docs/
  models.md            # 在 models.json 配置兼容端点
  custom-provider.md   # 需要自定义协议/鉴权流时才写扩展
  providers.md
  security.md
```

pi 端点自查：`pi --help`。
dfcode 端配置 schema 可在 bundle 的 source map 里搜
`MaasConfig` / `MaasAuthConfig` / `maasCachePath`。

---
---

# 第二部分：工作流移植（spec / plan / review）

> 移植日期 2026-09-27。来源：dfcode 0.x 的 sourcemap 与编译产物。

## 8. 装了什么

```
~/.pi/agent/skills/
├── spec-workflow/SKILL.md          四阶段主流程 + 门禁表
│   └── references/
│       ├── explore.md              探索现状（产出理解，不产出产物）
│       ├── propose.md              定义变更（delta 格式的严格定义在这）
│       ├── apply.md                只实现已批准的内容
│       └── archive.md              折回 spec 树
├── plan-workflow/SKILL.md          五阶段只读规划
└── code-review/SKILL.md            只读审查

~/.pi/agent/extensions/
├── spec-tool.ts                    确定性后端 new/status/validate/archive
├── init.ts                         /init —— 采集事实并生成 AGENTS.md
└── guard.ts                        危险操作门禁（bash 规则 + 系统路径写保护）
```

启动 pi 后 `/reload` 生效。

## 9. dfcode 原始定义在哪（可复现）

不用猜，源码都在本机：

| 内容 | 位置 |
|---|---|
| plan 五阶段 | `index.js.map` → sources `src/session/prompt/plan-full.ts` |
| spec 工具（校验/合并逻辑） | `index.js.map` → sources `src/tool/spec.ts` |
| spec 主提示词 | 同上，函数 `PlanPrompt` / 命名空间 `SpecTool` |
| 命令表（`/init` `/review` `/spec` `/unspec`） | `index.js.map` → sources `src/command/index.ts` |
| agent 定义 | `index.js.map` → sources `src/agent/agent.ts` |
| spec-kit 五份 playbook | **不在 sourcemap 里**（`.txt` 未被内联），在 267MB 编译产物中 |

`.txt` 的提取方法：

```bash
BIN=~/.local/share/pi-node/node-v22.23.1-linux-x64/lib/node_modules/dfcode/node_modules/dfcode-linux-x64-baseline/bin/dfcode
grep -aob "src/agent/spec-kit" "$BIN"          # 定位偏移
dd if="$BIN" bs=1 skip=<偏移> count=7000 2>/dev/null | strings -n 8
```

`sourcemap` 本身可以直接解出来用：

```bash
python3 - <<'PY'
import json
m = json.load(open("<...>/bin/index.js.map"))
d = dict(zip(m['sources'], m['sourcesContent']))
open('/tmp/spec-tool.ts','w').write(d['src/tool/spec.ts'])
PY
```

搜命令表的技巧：`rg -o 'description: \\"[^"]{10,90}' index.js.map | sort -u`。

## 10. 核心设计：工具管事实，skill 管纪律

dfcode 的分工必须保留，否则流程会退化成纯提示词：

| | dfcode | pi 移植 |
|---|---|---|
| 阶段 playbook | `spec instructions <phase>` 动态加载 | skill 的 `references/*.md`，模型按阶段自己读 |
| 脚手架 / 校验 / 合并 | `spec` 工具 | 同一个 `spec` 工具（`pi.registerTool`） |
| 审批门禁 | `plan_exit` 工具 | **无对应物** —— pi 无内置审批，只能写成纪律 |

dfcode 的 phase 是"纪律，不是工具强制的门"；它自己在 spec.txt 里也这么说：
`The phases are discipline, not gates the tooling enforce`。

## 11. specs/ 目录结构与 delta 格式

```
specs/current/<capability>/spec.md          活的 spec 树：系统当前"实际做什么"
                                            持久；只有 archive 会合并进来
specs/changes/<slug>/proposal.md            Why / What Changes / Grounding
specs/changes/<slug>/tasks.md               有序清单（打勾 = 进度记录）
specs/changes/<slug>/design.md              可选：HOW（库选型、数据模型）
specs/changes/<slug>/deltas/<cap>/spec.md   只写变化，不是完整未来态
specs/changes/archive/<date>-<slug>/        已归档
```

delta 格式（`validate` 会按此 lint）：

```markdown
## ADDED Requirements          ## MODIFIED Requirements
                              ## REMOVED Requirements
## RENAMED Requirements
```

- 一条需求 = `### Requirement: <名称>` + 一句 **SHALL 或 MUST** 的单一行为陈述
  + 至少一个 `#### Scenario:`（含 **WHEN** / **THEN**）
- MODIFIED 用现有需求的完整标题原文，给完整新需求（不是 diff）
- REMOVED 只列标题 + 一行理由
- RENAMED 写 `- FROM:` / `- TO:`

合并顺序固定：**RENAMED → REMOVED → MODIFIED → ADDED**。

`validate` 会拦的错误：

| code | 含义 |
|---|---|
| `missing-proposal` / `missing-why` / `missing-what-changes` | proposal 缺必需段落（`missing-grounding` 只是 warning） |
| `no-deltas` / `empty-delta` | 没有增量，或增量四个段全空 |
| `requirement-keyword` | 需求里没有 SHALL / MUST |
| `requirement-scenario` | 需求缺 `#### Scenario:` |
| `duplicate-requirement` | 同名需求在多个增量操作里重复 |

## 12. 四阶段与五阶段流程

### spec-workflow（用于真实改动）

```
explore   理解现状，带 file:line 证据；不写代码不写 spec
   ↓ 门禁：发现与候选方案已摆给用户，方向一致
propose   spec new → 填 proposal → 写 deltas → 拆 tasks → validate → 给用户看
   ↓ 门禁：用户明确批准（肯定回复，不是沉默，不是推断）
apply     只实现 deltas 定义的；每完成一个任务同轮打勾；发现提案错了就停下回去改
   ↓ 门禁：任务全勾 + 检查通过（引用真实输出）
archive   沉淀 ## Decisions → validate → archive（合并进 current + 归档目录）
```

三条铁律（原文照搬）：

1. **证据不是叙述** —— 给不出 `file:line` 的断言就是假设，标注它。
   工具失败直说并停下，**绝不编造文件内容或声称"读取最终成功了"**。
2. **行为优先** —— 需求写系统可观测地做什么，HOW 放 design.md / tasks.md。
3. **明确批准才算批准** —— 沉默不算，自己推断更不算。

### plan-workflow（只读规划，用于"先别动"）

Phase 1 初步理解 → 2 设计 → 3 复核与澄清 → 4 最终计划 → 5 交付等确认。

固定结构：`Context` / `Requirements` / `Recommended Approach` /
`Implementation Steps` / `Verification` / `Critical Files for Implementation`。

Phase 3 的提问纪律值得单独记：**只问真正属于用户的决策**（产品行为、范围边界、
架构选型、实质取舍）；仓库约定或低风险默认值能定的实现细节**不要问**；
必须问时给 2-4 个具体选项、推荐项排第一并标注 `(推荐)`。

pi 没有 `plan_exit` 工具，所以 Phase 5 是纯纪律约束——写完停下，别同轮改代码。

## 13. 踩过的坑

### 13.1 `-nt` 会把 skill 和自定义工具一起藏起来

```
$ pi -p -nt "你的系统提示里有哪些 skill？"
1) 可用 skill：系统提示未列出任何 skill。
2) 没有名为 spec 的工具
```

`--no-tools` 不只是关工具，**skill 列表和自定义工具也一起从系统提示里消失**。
验证和实际使用都别加 `-nt`。一度以为移植失败。

### 13.2 移植时抓到的两个真 bug

**(a) `capability()` 路径前缀错位**

dfcode 用 `Bun.Glob("deltas/**/spec.md")`，返回的匹配相对 **changeDir**，即
`deltas/order/spec.md`；于是 `dirname().split(sep).slice(1)` 正好切掉 `deltas`
得到 `order`。

我改用 `fs.readdir` 递归时从 `deltas/` 目录内部开始遍历，`rel` 少了 `deltas/`
这一级 → 顶层 capability 解析成空串 → 后续 `readFile` 抛 ENOENT。

**修法**：遍历时初始 `rel = "deltas"`，让返回值保持与 dfcode glob 一致的形状。

**(b) 归档门禁完全失效（最严重）**

`taskProgress()` 原本只返回 `{ total, done }`，但三处判断都用了
`progress.open`。`undefined > 0` 恒为 `false`，于是：

```
tasks: { total: 8, done: 1, open: 7 }   ← status 显示未完成
$ spec archive
{ "merged": true, ... }                 ← 却直接合并进了 specs/current/
```

人工读 diff 看不出来，只有专门构造"任务没勾完就归档"的测试才能抓到。

**修法**：`taskProgress()` 返回 `{ total, done, open }`。

> 教训：移植校验类逻辑时，**每个布尔判断的取值来源都要单独核一遍**。
> dfcode 原实现里 `tasks()` 也只返回 `{total, done}`，但它没有 `progress.open`
> 这层判断，所以原版没这个 bug —— 缺陷是我在移植时引入的。

### 13.3 扩展里 import `typebox`

`pi.registerTool` 的 `parameters` 要 TypeBox schema，直接
`import { Type } from "typebox"` **在 pi 里可用**，因为 pi 的扩展加载器
（`dist/core/extensions/loader.js:41-76`）专门为扩展做了模块别名。

但**自己用 jiti 单测扩展时会解析失败**。复刻那个 alias 才能测：

```js
const { createRequire } = await import("node:module");
const req = createRequire(PI + "/dist/core/extensions/loader.js");
const jiti = createJiti(import.meta.url, {
  interopDefault: true,
  alias: {
    typebox: req.resolve("typebox"),
    "typebox/compile": req.resolve("typebox/compile"),
    "typebox/value": req.resolve("typebox/value"),
  },
});
```

### 13.4 验证扩展是否真的加载成功

`pi --list-models` **不会**报扩展错误。用 SDK 的 loader 直接查：

```js
import { DefaultResourceLoader, getAgentDir } from "<pi>/dist/index.js";
const rl = new DefaultResourceLoader({ cwd, agentDir: getAgentDir() });
await rl.reload();
console.log(rl.getSkills());                 // { skills, diagnostics }
console.log(rl.getPrompts());                 // { prompts, diagnostics }
console.log(rl.getExtensions().errors);       // 扩展加载错误
```

或者用 pi 自己的 `loadExtensions(paths, cwd)`（记得它会返回 `errors` 数组）。

## 14. 使用与验证

```bash
# 端到端确认模型真的看得到（不要加 -nt）
cd <项目> && pi -p --no-session --provider maas --model gpt-5.6-luna \
  "只依据你的系统提示回答：1) 可用 skill 2) spec 工具的 command 取值 3) spec-workflow 的四个阶段"

# 强制加载某个 skill
/skill:spec-workflow
/skill:spec-workflow 给订单加幂等键
```

预期回答包含：`code-review` / `plan-workflow` / `spec-workflow`，
`spec` 的 command 取值 `new/status/validate/archive`，以及四阶段。

### 日常用法

| 场景 | 入口 |
|---|---|
| 需求 → 方案 → 批准 → 实现 → 归档 | 让模型走 spec 流程（或 `/skill:spec-workflow <需求>`） |
| "先给个方案，别急着写" | `/skill:plan-workflow` |
| "帮我 review 这个改动" | `/skill:code-review`（或直接说 review，描述会触发自动加载） |
| 手上已有 `specs/changes/<slug>/` | `spec {command:"status"}` 查进度，**不要**再开 plan 流程 |
| 危险操作想弹窗确认 | 默认已开；`PI_GUARD=off` 关闭，`PI_GUARD=dry-run` 只提示 |

## 15. 与 dfcode 的差异清单

1. **无 agent 切换** —— dfcode 有 `/spec` `/unspec` 在 plan/build 间切；pi 无 agent
   概念，改用 skill 触发 + 描述里的触发词。
2. **无 `spec instructions`** —— dfcode 靠工具动态吐 playbook；pi 侧放进
   `references/`，模型自己读。
3. **无内置审批，但可由扩展补上** —— dfcode 的 `plan_exit` 与
   `ctx.ask({permission:"spec"})` 都能程序化卡门；pi 没有声明式权限配置，
   但扩展的 `tool_call` hook 能返回 `{block:true}`，效果等价。
   `spec new/archive` 的门禁已在 `guard.ts` 补齐并测试（§21-§22）。
   plan 流程的审批仍是纯纪律。
4. **语言** —— playbook 与工具输出译成中文，但 `SHALL` / `MUST` / `WHEN` /
   `THEN` 保持英文原文，因为 `validate` 的正则按这些关键词匹配。
5. **上游可比对** —— dfcode 本身是 opencode 的 fork，所以这三个 skill 可以直接对着
   本机 opencode（比 dfcode 更新）复核，不必只依赖 dfcode 的版本（§23）。

## 16. 安全提示（与第一部分同源）

绕过 dfcode 管控直接用同一个 MaaS key，意味着绕开了 `api.dfcode.ai` 的调用审计。
本文档与 `spec-tool.ts` 等扩展均不包含密钥明文；密钥只在
`~/.pi/agent/models.json`（权限 600）与
`~/.local/share/dfcode/enterprise/maas-config.json`（权限 600）。
若公司对 AI 工具使用有留痕要求，先与管理员确认。

---

# 第三部分：溯源 —— dfcode 是 opencode 的 fork

> 追加于 2026-09-27。结论基于 dfcode 3.3.21 自带的 `index.js.map`，
> 与本机 opencode 1.18.32 二进制交叉比对。**不是靠印象，是靠证据。**

## 17. 结论

**dfcode 是 SST 的 opencode 的内部 fork（换皮重打包），不是自研。**

同源，本机两个都装着：opencode `1.18.32`（`~/.opencode/bin/opencode`），
dfcode `3.3.21`（MIT，`~/.local/share/pi-node/.../dfcode`）。

## 18. 证据

### 18.1 源码级：sourcemap 里的换皮痕迹

dfcode 附带 `index.js.map`，2262 个 source 条目全部可解。
**没有任何一个属于 opencode 的包**（不存在 `packages/opencode`），
全是 dfcode 自己的 `src/` —— 说明是把源码 fork 进来重新打包，
而不是依赖 opencode 的 npm 包。

最露馅的一处，**外层函数名没改、内层改了**：

```ts
// ../sdk/js/src/index.ts
export async function createOpencode(options?: ServerOptions) {
  const server = await createDfcodeServer({ ...options })   // ← 漏改
  const client = createDfcodeClient({ baseUrl: server.url })
  return { client, server }
}
```

同款文件对照：

| dfcode 文件 | 内容 | opencode 对应 |
|---|---|---|
| `src/flag/flag.ts` | `export namespace Flag` + `DFCODE_GIT_BASH_PATH` | `OPENCODE_*` 逐个改名 |
| `src/id/id.ts` | `Identifier` + `ses/msg/per/que/prt/pty` 前缀 | 原样 |
| `../util/src/slug.ts` | `Slug` namespace + 形容词表 | 原样 |
| `src/tool/tool.ts` | `Tool.Context` / `MessageV2` / `Agent.Info` / `PermissionNext` | 原样 |

### 18.2 作者没擦干净的残留

```
src/session/compaction.ts:107   // freshly rebuilt post-compaction context. Mirrors OpenCode's
src/cli/cmd/models.ts:68        const aIsOpencode = a.startsWith("dfcode")   ← 变量名 Opencode，字符串 dfcode
src/index.ts:78-79              process.env.AGENT = "1"; process.env.OPENCODE = "1"
src/plugin/index.ts:19          BUILTIN = ["opencode-anthropic-auth@0.0.9", ...]
```

`compaction.ts` 那行注释是 fork 作者自己承认抄了 opencode。

### 18.3 定量：直接 diff 本机 opencode 二进制

```
opencode flag 数: 82   dfcode flag 数: 93
改名后完全相同:   37        ← 37/93 逐字节相同

createOpencode            opencode=1  dfcode=0
OPENCODE_GIT_BASH_PATH    opencode=1  dfcode=0
DFCODE_GIT_BASH_PATH      opencode=0  dfcode=4
```

复现：

```bash
O=~/.opencode/bin/opencode
D=~/.local/share/pi-node/node-v22.23.1-linux-x64/lib/node_modules/dfcode/node_modules/dfcode-linux-x64-baseline/bin/dfcode
grep -ao 'OPENCODE_[A-Z_]*' $O | sed 's/^OPENCODE_//' | sort -u > /tmp/o.txt
grep -ao 'DFCODE_[A-Z_]*'  $D | sed 's/^DFCODE_//'  | sort -u > /tmp/d.txt
comm -12 /tmp/o.txt /tmp/d.txt | wc -l    # 37
```

### 18.4 怎么解 dfcode 源码

```bash
python3 - <<'PY'
import json
m = json.load(open("<...>/bin/index.js.map"))
d = dict(zip(m['sources'], m['sourcesContent']))
open('/tmp/spec-tool.ts','w').write(d['src/tool/spec.ts'])
PY
```

## 19. dfcode 在 fork 之上加了什么（自研部分）

| 模块 | 作用 |
|---|---|
| `src/enterprise/` | MaaS 设备授权登录（第一部分那套） |
| `src/workflow/` | 工作流引擎：`gate.ts` / `evidence.ts` / `delivery.ts` / `schema.ts` / `store.ts` |
| `src/auto-mode/` | 含 `classifier.ts` + `circuit-breaker.ts` |
| `src/ultra-mode/` | — |
| `src/knowledge/` | `client` / `github` / `workspace` |
| `src/memory/` | `chunk` / `recall` / `topic` / `project` |
| `src/presentation/deck.ts`、`src/spreadsheet/`、`src/document/`、`src/pdf/`、`src/artifact/` | 文档类能力（opencode 没有） |
| `src/tool/spec.ts`、`src/tool/team-*`、`src/tool/workflow-*`、`src/tool/review-effort.ts` | spec / team / workflow 工具 |
| `src/plugin/{codex,copilot,ppchat,marketplace}.ts` | 插件 |

独有 flag：`AUTO_MODE*`、`MEMORY*`、`TEAM*`、`TASK_WATCHDOG_*`、
`PARENT_WATCHDOG`、`DECK`、`COAUTHOR_*`、`PDF_FONT_*`、`TRUST_ALL`、
`ENTERPRISE_URL`、`BYPASS_ENTERPRISE_LOGIN`。

**opencode 有而 dfcode 没有的 45 个**（`DISABLE_FFF`、
`EXPERIMENTAL_EVENT_SYSTEM`、`EXPERIMENTAL_WORKSPACES`、`ZED_DB`、
`PHOTON_WASM_PATH`、`WEBSEARCH_PROVIDER`…）—— 两边已各自演进，
本机 opencode 1.18.32（9/22）比 dfcode 3.3.21（9/18）还新。

## 20. 两处修正：审批门禁的真相

**(a) `plan_exit` 确实存在**（二进制里 33 处，含 `plan_exit = () => {}` 的
非 plan agent 空实现）。第一部分说的"dfcode 能程序化卡门"成立。

**(b) `src/workflow/gate.ts` 不是审批门**，只有 17 行，是**工具调用时序门**：

```ts
const control = tool === "workflow_start" || tool === "workflow_control"
if (current.control || (control && current.used))
  throw new Error("Workflow control must run in a separate model step, without other tools")
```

防止把 `workflow_start` 和别的工具塞进同一个 model step。跟阶段审批无关。

## 21. 重要发现：spec 工具挂在权限系统后面

`src/tool/spec.ts` 里有两处 `ctx.ask`，**只挡有副作用的两个子命令**：

```ts
// :361  —— 校验 slug、确认变更不存在之后，任何 mkdir 之前
await ctx.ask({ permission: "spec", patterns: [`new:${slug}`], metadata: {}, always: ["*"] })

// :491  —— 未完成任务检查（:485）之后，任何写入之前
await ctx.ask({ permission: "spec", patterns: [`archive:${slug}`], metadata: {}, always: ["*"] })
```

`status` / `validate` 是只读的，**不弹窗**。`always: ["*"]` 意味着
**每次都问，从不记忆授权**。

第 491 行的位置尤其讲究：它在 `:485` 的未完成任务检查**之后**，
所以不会为一个注定失败的归档浪费一次点击。

另外 `:495` 有一句值得学的注释：

```ts
// plan phase: compute every target file content; abort on any conflict before writing anything
```

dfcode 的合并是**先算完所有目标文件内容、确认无冲突，再统一写**。
我的 pi 移植是逐文件边算边写 —— 这一点比 dfcode 弱，属已知差距。

## 22. 已把这个门禁补进 pi

既然 pi 的 `tool_call` hook 支持 `CustomToolCallEvent` + `{ block: true }`，
就能复刻 `permission: "spec"`。已在 `~/.pi/agent/extensions/guard.ts` 补上：

```ts
if (event.toolName === "spec") {
    if (process.env.PI_GUARD_SPEC === "off") return;
    // new / archive → 弹窗；status / validate → 直接放行
    if (await gate(ctx, `确认 spec ${command}`, detail, "spec 流程会改动 specs/ 目录")) {
        return { block: true, reason: `用户未确认（spec ${command}:${slug}）` };
    }
}
```

13 个探针全部通过：

| 场景 | 弹窗 | 结果 |
|---|---|---|
| `new` / `archive`（含 `merge:false`、`force:true`） | 是 | 确认→allow，拒绝→BLOCK |
| `status` / `validate` | 否 | allow |
| 无 UI（`pi -p`）+ `new` | — | **BLOCK**（宁可阻断不静默放行） |
| 无 UI + `status` | — | allow |
| `PI_GUARD_SPEC=off` / `PI_GUARD=off` / `dry-run` | 否 | allow |

无 UI 下默认阻断 `new`/`archive`，是为了脚本化场景需要显式设
`PI_GUARD_SPEC=off` —— 与 dfcode 需要预授权配置是对应的取舍。

## 23. 对移植工作的影响（重要）

**之前做的 spec / plan / review 移植，本质是"从 opencode 抄到 pi"，
不是 dfcode 独有。** 三个 skill 可以直接对着 opencode 上游更新后的源码复核。

推论：

1. 想追最新 → 对着本机 `~/.opencode/bin/opencode`（1.18.32）复核，
   比对着 dfcode 3.3.21 更前沿。
2. 想知道 dfcode 到底改了什么 → 就是 §19 那些新增模块 + §18.3 的 flag 差集。
3. opencode 的 SDK 布局（`hey-api` 生成的 `gen/`）在 dfcode 里原样保留，
   所以按 opencode SDK 写的外部工具理论上仍可复用。
4. dfcode 仍带着 `opencode.ai/zen`、`opencode.ai/zen/go` 的模型目录数据
   （继承自 opencode 的 models 注册表），但自己的 provider id 是 `dfcode`
   （103 处），网关是 `api.dfcode.ai`。
