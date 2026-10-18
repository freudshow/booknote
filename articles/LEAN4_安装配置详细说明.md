# Debian 13 安装与配置 Lean 4 详细说明

本文记录当前这台 Debian 系统上的 Lean 4 安装结果、elan 工具链管理、Shell 环境配置、验证方法、项目使用方式和常见问题，便于后续复现与维护。

## 1. 当前系统与安装结果

- 操作系统：Debian GNU/Linux 13（trixie）
- 架构：x86_64（64 位）
- Lean 版本：Lean 4.34.1（Release）
- Lean commit：`5045d0056413266e57c625dcd7c365b10e377c52`
- 工具链管理器：elan 4.2.4
- 构建工具：Lake 5.0.0-src+5045d00（随 Lean 工具链提供）
- 安装范围：当前用户 `floyd`，没有使用 root 或 sudo

安装完成后的关键路径：

| 内容 | 路径 |
| --- | --- |
| elan、lean、lake 等命令 | `~/.elan/bin/` |
| elan 配置 | `~/.elan/settings.toml` |
| Lean 工具链发行目录 | `~/.cache/lean4/lean-4.34.1-linux/` |
| 下载的官方发行包 | `~/.cache/lean4/lean-4.34.1-linux.tar.zst` |
| Bash 登录环境 PATH 配置 | `~/.profile` 中的 `~/.elan/bin` 条目 |

**重要：** 当前 elan 注册的 `leanprover/lean4:v4.34.1` 工具链链接到 `~/.cache/lean4/lean-4.34.1-linux/`。不要删除或移动这个已解压目录，否则 elan 将找不到 Lean 的可执行文件和库。下载压缩包是安装归档；删掉它不会删除已解压的工具链，但建议在确认备份/复现需求后再清理。

## 2. 组件说明

- **Lean 4** 是编程语言及定理证明器；`lean` 命令负责检查、编译 Lean 源文件。
- **elan** 是 Lean 工具链管理器，负责选择/切换 Lean 版本。项目目录可以用 `lean-toolchain` 文件固定所需版本。
- **Lake** 是 Lean 的构建与包管理工具；安装 Lean 工具链后可通过 `lake` 命令使用。
- **VS Code Lean 4 扩展**是可选编辑器支持，不是命令行 Lean 的必需条件。

本机采用 elan 管理 Lean。elan 通过官方安装脚本安装，设置 `stable` 为默认工具链。由于该环境下载 GitHub Release 大文件时官方安装器下载速度很慢，实际 Lean 发行包从 Lean 官方 GitHub Release 下载后经 elan 注册；最终将 `leanprover/lean4:v4.34.1` 设为默认工具链。归档下载地址为：<https://github.com/leanprover/lean4/releases/download/v4.34.1/lean-4.34.1-linux.tar.zst>。

## 3. 在 Debian 13 上复现安装

以下步骤适用于本机相同的 Linux x86_64 环境。Lean 官方手动安装页面注明其 Linux 步骤主要针对 Ubuntu；Debian 上应结合本机发行版调整。官方安装方法及发行版本可能随时间更新；如果是复现当前安装，应使用本文记录的 `v4.34.1` 版本。

### 3.1 安装 elan

确认系统能访问 HTTPS，并具备 `curl`。通过 Lean 官方 elan 安装脚本安装当前用户版本：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain stable
```

安装程序会在家目录创建 `~/.elan/`，并将命令放在 `~/.elan/bin/`。本机的 `~/.profile` 已添加如下 PATH 条目：

```bash
export PATH="$HOME/.elan/bin:$PATH"
```

本机登录 Bash 会从 `~/.profile` 加载 `~/.bashrc`，且以上 PATH 设置位于该文件末尾。若在另一台机器上安装后没有 PATH 配置，可将该行加入 Bash 登录环境配置，再重新登录；当前终端可临时执行：

```bash
export PATH="$HOME/.elan/bin:$PATH"
```

检查 elan：

```bash
elan --version
```

本机结果：`elan 4.2.4 (227caca13 2026-08-25)`。

### 3.2 下载并注册 Lean 4.34.1 官方工具链

本机的完整发行包大小约 553 MiB。安装器自动下载曾因网络吞吐过低而耗时较长，因此本机改用支持多连接下载的 `aria2c`；Debian 上如未安装，可先由有权限的管理员安装 `aria2` 包。以下是本机使用的下载和校验流程：

```bash
mkdir -p "$HOME/.cache/lean4"
aria2c --continue=true --allow-overwrite=false \
  --max-tries=10 --retry-wait=5 --timeout=60 --connect-timeout=30 \
  --split=16 --max-connection-per-server=16 --min-split-size=4M \
  --file-allocation=none \
  --dir="$HOME/.cache/lean4" --out=lean-4.34.1-linux.tar.zst \
  'https://github.com/leanprover/lean4/releases/download/v4.34.1/lean-4.34.1-linux.tar.zst'
```

校验归档可读，然后解压到缓存目录：

```bash
zstd -t "$HOME/.cache/lean4/lean-4.34.1-linux.tar.zst"
tar --use-compress-program=unzstd \
  -xf "$HOME/.cache/lean4/lean-4.34.1-linux.tar.zst" \
  -C "$HOME/.cache/lean4"
```

解压后应存在 `~/.cache/lean4/lean-4.34.1-linux/`。通过 elan 把该发行目录注册为版本 `leanprover/lean4:v4.34.1`，并设为默认：

```bash
elan toolchain link 'leanprover/lean4:v4.34.1' \
  "$HOME/.cache/lean4/lean-4.34.1-linux"
elan default 'leanprover/lean4:v4.34.1'
```

在解压或注册前，先确认目标目录不存在；不要覆盖一个已有的工具链目录。使用自定义的本地链接注册后，elan 使用的是该路径下的工具链文件，不会自动重新下载同一版本。

## 4. 验证安装

打开新终端或重新加载登录环境，然后执行：

```bash
command -v elan
command -v lean
command -v lake
elan --version
lean --version
lake --version
elan show
```

本机检查结果：

```text
/home/floyd/.elan/bin/elan
/home/floyd/.elan/bin/lean
/home/floyd/.elan/bin/lake
elan 4.2.4 (227caca13 2026-08-25)
Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)
Lake version 5.0.0-src+5045d00 (Lean version 4.34.1)
leanprover/lean4:v4.34.1 (default)
```

本机还在新登录 Bash 中创建并成功运行了最小 Lean 文件，确认不只是版本信息命令可用：

```bash
printf '#eval 1 + 1\n' > Smoke.lean
lean Smoke.lean
```

预期输出为 `2`。本机该验证已通过。

## 5. 在项目中使用和固定 Lean 版本

### 5.1 检查当前工具链

在项目目录运行：

```bash
elan show
```

如果项目目录或其父目录存在 `lean-toolchain`，elan 会优先按该文件选取工具链；否则使用全局默认版本。

### 5.2 固定项目版本

团队项目通常应在项目根目录提交 `lean-toolchain` 文件，确保成员使用相同 Lean 版本。当前安装已注册以下工具链名，可将文件内容设为：

```text
leanprover/lean4:v4.34.1
```

命令行创建方式：

```bash
printf '%s\n' 'leanprover/lean4:v4.34.1' > lean-toolchain
```

项目中的文件只应在项目确实计划固定此版本时新增或修改。切换项目版本前，应检查项目依赖（尤其是 `lake-manifest.json` 和 mathlib 版本）是否与该版本兼容。

### 5.3 Lake 项目常用检查

在已配置的 Lake 项目目录运行：

```bash
lake --version
lake build
```

`lake build` 会按项目配置构建代码；首次构建可能需要下载项目依赖，因此需要可用的网络连接。若只是验证编译器本身，使用上一节的单文件 `lean Smoke.lean` 即可，不必创建项目或下载依赖。

## 6. 常见问题排查

### 提示 `lean: command not found`

检查 `~/.elan/bin` 是否存在，并确认它已加入当前 Shell 的 PATH：

```bash
ls -l "$HOME/.elan/bin/lean"
printf '%s\n' "$PATH"
```

当前终端临时修复：

```bash
export PATH="$HOME/.elan/bin:$PATH"
```

若临时修复有效，将该配置加入适合当前 Shell 的启动文件并重新登录。VS Code 等桌面程序可能不会继承新加的登录 PATH；PATH 更新后需重启该程序。

### elan 首次调用时长时间下载或报网络错误

Lean 发行包较大。检查是否可访问 `releases.lean-lang.org`、GitHub Release 和重定向后的 `release-assets.githubusercontent.com`。如果网络慢，可使用支持断点续传和并发分段的 `aria2c` 下载官方 Release 文件，并按第 3.2 节校验、解压和注册。不要使用来源不明的二进制包。

若下载中断，可对相同文件再次运行 aria2c 命令以续传。下载完成后 `zstd -t` 应成功；校验失败时不要注册该归档。

### `elan show` 显示的版本与项目要求不一致

检查项目中的 `lean-toolchain` 文件。项目固定版本优先于全局默认值。如版本尚未安装且网络可用，可用 `elan toolchain install <工具链名>` 安装；修改项目固定版本前先确认项目依赖兼容性。

### 找不到 `lean`、但 elan 命令存在

确认当前 shell 调用的是 `~/.elan/bin/lean`，而不是系统中其他 Lean 安装：

```bash
type -a lean
elan which lean
elan show
```

检查 `~/.elan/toolchains/` 中的工具链链接是否仍指向存在的目录。当前安装的本地链接目标是 `~/.cache/lean4/lean-4.34.1-linux/`；若该目录被移动或删除，需要恢复目录，或重新解压并执行 `elan toolchain link`。

### Lake 构建依赖下载失败

这通常是项目依赖仓库的网络问题，不一定表示 Lean 安装损坏。先单独运行 `lean --version` 和单文件 smoke test；若通过，再检查项目网络访问、依赖地址和代理配置。

## 7. 版本更新与卸载注意事项

- 保持当前版本：不需要再执行安装命令；项目可通过 `lean-toolchain` 固定版本。
- 安装官方发布的新版本时，应查看 Lean 官方安装说明和发行页，然后通过 elan 安装、切换工具链；不要直接覆盖当前本地发行目录。
- 当前默认工具链是本地注册的版本，不会随 `stable` 标签自动升级。需要更新时，应注册新的发行目录并明确切换默认版本，项目版本也需单独评估。
- 删除或移动 `~/.cache/lean4/lean-4.34.1-linux/` 会使当前 elan 工具链链接失效。卸载前应先确认没有项目依赖它，并按 elan 的卸载命令说明处理。
- `elan self uninstall` 会移除当前用户的 elan 安装；执行前先查看命令提示，并确认不再需要任何由 elan 管理的 Lean 工具链。

## 8. 官方参考

- Lean 官方安装页面：<https://lean-lang.org/install/>
- Lean 官方手动安装说明：<https://lean-lang.org/install/manual/>
- Lean 4 官方仓库及发行版：<https://github.com/leanprover/lean4>
- elan 官方仓库：<https://github.com/leanprover/elan>
- 当前安装的 Lean 4.34.1 官方发行包：<https://github.com/leanprover/lean4/releases/download/v4.34.1/lean-4.34.1-linux.tar.zst>

---

文档记录日期：2026-10-06。系统与版本信息根据本机实际安装和命令输出记录；再次安装或升级后，应重新运行验证命令并更新版本、commit 和路径信息。

---

## Lean 4 日常使用详细说明

本部分面向已经安装好 Lean 4 和 elan 的使用者，介绍从写第一段代码、检查类型和证明定理，到创建 Lake 项目、组织模块、构建和运行程序的基本流程。命令示例按本机 Debian 13、Lean 4.34.1、Lake 5.0.0 编写。Lean 的语法和标准库会继续演进；项目中应以其 `lean-toolchain` 文件指定的版本为准。

### 9. 先理解日常使用中的几个工具

- **`lean`**：解析 Lean 源文件，并执行 elaboration（名称解析、类型推断等）和检查；可运行文件中的 `#eval`，也可用 `lean --run` 执行 `main`。
- **`lake`**：管理 Lean 项目、模块、依赖与构建。正式项目通常通过 Lake 构建，而不是手工维护一串 Lean 编译参数。
- **`elan`**：根据项目所在目录的 `lean-toolchain` 选择 Lean 版本；项目指定版本优先于全局默认版本。
- **VS Code Lean 4 扩展（可选）**：提供语法高亮、实时错误信息、悬停类型信息和交互式证明信息窗口。终端工作流不依赖 VS Code。

Lean 同时可用于函数式编程和定理证明。普通表达式的运行结果可用 `#eval` 查看；定理声明则必须提供 Lean 能检查的证明项。Lean 内核会检查证明是否符合其逻辑规则，编辑器显示没有错误是开发反馈，保存并通过项目构建是更完整的检查。

### 10. 最快开始：在文件中交互

#### 10.1 检查表达式和类型

在 `QuickStart.lean` 中写入：

```lean
#check 1 + 2
#eval 1 + 2

def double (n : Nat) : Nat := n * 2

#check double
#eval double 21
```

在终端运行：

```bash
lean QuickStart.lean
```

`#check` 显示一个表达式的类型，`#eval` 执行表达式并显示结果；上例的结果包括 `Nat` 类型信息和 `42`。也可以在命令行用 `lean --run` 运行同一个文件；文件里的 `#eval` 仍会执行。

常用交互命令：

| 命令 | 用途 |
| --- | --- |
| `#check expression` | 查询表达式的类型 |
| `#eval expression` | 编译并运行表达式，显示结果 |
| `#reduce expression` | 按 Lean 的定义规约表达式；复杂项可能较慢 |
| `#print name` | 查看已声明的定义或定理 |
| `#synth Add Nat` | 查看 Lean 能否合成自然数加法的类型类实例 |

这些以 `#` 开头的命令适合探索、检查和做轻量测试。持久程序逻辑应写成定义、函数或测试，不要只依赖编辑器临时执行的命令。

#### 10.2 运行一个简单程序

保存为 `Hello.lean`：

```lean
def greet (name : String) : String := s!"你好，{name}！"

def main : IO Unit := do
  IO.println (greet "Lean")
```

执行：

```bash
lean --run Hello.lean
```

程序通过标准输出打印问候语。Lean 程序的 I/O 通常写在 `IO` 中；`do` 块用于按顺序组织 I/O 等单子操作。纯函数则通常直接用表达式定义，不必为了计算而引入 I/O。

### 11. Lean 文件的基础写法

#### 11.1 定义、类型与函数

```lean
def square (n : Nat) : Nat := n * n

def describe (enabled : Bool) : String :=
  if enabled then "enabled" else "disabled"

#check square
#eval square 12
```

`def` 声明定义；参数和返回值可显式写出类型。Lean 也支持类型推断，但初学时建议给重要函数和定理参数写清楚类型。调用普通函数时用空格分隔函数和参数，例如 `square 12`。

常见基础类型包括：

- `Nat`：自然数。
- `Int`：整数。
- `Rat`、`Float`：有理数和浮点数；涉及精度时应明确选择类型。
- `Bool`：可执行计算中的真/假值。
- `String`、`Char`：字符串和字符。
- `List α`、`Array α`：列表和数组；`α` 表示元素类型。
- `Option α`：可选值，表示 `none` 或 `some value`。
- `Prop`：命题的类型；证明是命题的项。

数字字面量的类型通常由上下文推断。若需要消除歧义，可写类型标注，例如 `(3 : Int)`。

#### 11.2 用 `#eval` 探索数据

```lean
#eval [1, 2, 3].map (fun n => n * 2)
#eval (some 7 : Option Nat)
```

`#eval` 适合运行有可显示结果的计算，不适合直接打印函数本身。结果需要 `Repr`、`ToString` 或相关显示实例。自定义结构体可以派生 `Repr`：

```lean
structure Point where
  x : Int
  y : Int
  deriving Repr

def origin : Point := { x := 0, y := 0 }

#eval origin
```

若值不支持显示，Lean 会报无法合成显示实例；可为自定义类型派生或实现合适的实例，或改为打印某个字段。

#### 11.3 结构体、枚举和模式匹配

结构体用于组合有名称的字段：

```lean
structure User where
  name : String
  age : Nat
  deriving Repr

def sampleUser : User := { name := "Lin", age := 30 }
#eval sampleUser.name
```

归纳类型用于定义有限选项或递归数据：

```lean
inductive Color where
  | red
  | green
  | blue
  deriving Repr

def colorName (c : Color) : String :=
  match c with
  | .red => "red"
  | .green => "green"
  | .blue => "blue"
```

Lean 会检查模式是否覆盖所有情况。遇到 `Option`、列表或用户定义的归纳类型时，`match` 通常是清楚且安全的分支处理方式。

#### 11.4 递归函数

Lean 会检查递归定义是否满足终止性要求。下面的阶乘函数递归调用时参数逐步减小：

```lean
def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

#eval factorial 5
```

不要为了绕过终止性检查而随意使用 `partial`。只有确实要表达 Lean 无法自动证明终止的程序，并理解其逻辑限制时，才考虑该机制。

#### 11.5 命名空间

命名空间用于组织名称，避免不同模块定义重名：

```lean
namespace Geometry

def double (n : Nat) : Nat := n * 2

end Geometry

#eval Geometry.double 4
```

在项目中，目录和文件也会参与模块名称；例如 `MyProject/Geometry/Circle.lean` 通常以 `import MyProject.Geometry.Circle` 引入。模块导入名称必须与项目的模块根和实际文件路径一致。

### 12. 写定理与构造证明

#### 12.1 命题和证明

用 `theorem` 声明命题并给出证明：

```lean
theorem twoPlusThree : (2 : Nat) + 3 = 5 := by
  decide

theorem addZeroRight (n : Nat) : n + 0 = n := by
  rfl
```

`rfl` 适用于等式两侧按定义计算后相同的情形。`decide` 可为某些可判定且规模合适的命题执行计算并生成证明。证明超出这些简单情形时，通常需要展开步骤、调用定理或使用 tactic。

#### 12.2 常见 tactic 的作用

- `exact h`：直接用已有证明 `h` 完成当前目标。
- `intro h`：引入蕴含前提或全称量化变量。
- `apply theoremName`：把目标转化为该定理所需的前提。
- `rw [h]`：按等式 `h` 在目标中改写。
- `simp`：使用 simp 引理集化简目标；必要时可给出局部规则，如 `simp [myDefinition]`。
- `constructor`：把合取、结构或其他构造型目标拆成各部分。
- `cases h`：按归纳类型的构造情况分类讨论。
- `induction n`：对自然数、列表等归纳类型进行归纳证明。
- `rfl`：证明定义上相等的目标。

每条 tactic 执行后，Lean 会显示剩余目标（goal）。可以先逐步缩小目标，再把经过验证的 tactic 脚本保留在源文件中。初学时不要把 `sorry` 当作成功证明：它是未完成证明占位符，可能产生警告，并使定理仍未真正证明。

#### 12.3 命题 `Prop` 与布尔值 `Bool`

`Bool` 用于程序中的可计算条件；`Prop` 用于声明逻辑命题。例：

```lean
def isSmall (n : Nat) : Bool := n < 10

theorem smallExample : 3 < 10 := by
  decide
```

布尔表达式可执行；命题需要提供证明。遇到二者之间的转换时，应查看目标显示的类型，不要仅凭外观相似把 `Bool` 当成证明。

### 13. 创建并构建一个 Lake 项目

#### 13.1 创建项目

在希望存放 Lean 代码的位置运行：

```bash
mkdir -p "$HOME/LeanProjects"
cd "$HOME/LeanProjects"
lake new HelloLean
cd HelloLean
```

`lake new` 会生成项目目录、`lean-toolchain`、Lake 配置、入口程序及示例库文件。项目名称应使用适合作为 Lean 包和模块名称的标识符，不要把绝对路径当作包名。`lake new --help` 会列出可用模板，如默认 `std`、仅可执行程序 `exe`、仅库 `lib` 和 Mathlib 模板 `math`。

可用 `lake init` 在当前目录初始化项目，但应先确认目录内容并避免覆盖已有项目文件：

```bash
mkdir MyExistingEmptyProject
cd MyExistingEmptyProject
lake init
```

#### 13.2 检查项目文件

```bash
ls
cat lean-toolchain
cat lakefile.toml
```

Lake 配置也可以使用 `lakefile.lean`；模板通常会选定一种配置格式。默认模板的入口文件一般是 `Main.lean`，库模块位于与项目名相同的目录中。Lake 配置中的 `[[lean_exe]]` 声明可执行文件及其入口模块，`[[lean_lib]]` 声明要构建的库。

项目的 `lean-toolchain` 应与项目及其依赖兼容。项目内执行 `elan show` 可看到实际选中的版本。不要仅因全局默认是 Lean 4.34.1 就覆盖项目原有工具链版本。

#### 13.3 构建、运行和清理

```bash
lake build
lake exe hellolean
lake clean
```

- `lake build` 构建默认目标；第一次构建也会生成或更新 `lake-manifest.json`，并可能下载依赖。
- `lake exe hellolean` 构建并运行示例项目的可执行程序。实际项目中，`lake exe` 后面应填写 `lakefile.toml` 或 `lakefile.lean` 中 `lean_exe` 声明的名称；模板可能会将包名规范化为小写。
- `lake clean` 清理生成的构建输出，通常会让下一次构建重新编译。
- 构建产物放在 `.lake/` 下；通常不需要手动编辑其中的文件。

Lake 命令还包括 `lake test`、`lake lint`、`lake update` 和 `lake env`。测试与 lint 命令只有在项目配置了相应 driver/工作流时才有实际测试或检查可运行；可先用 `lake check-test`、`lake check-lint` 查看配置情况。`lake update` 会更新依赖解析并可能改动 manifest，不应当作每次构建前的例行命令。

#### 13.4 单独运行或检查文件

对于不依赖项目模块的独立文件，可直接运行：

```bash
lean Example.lean
lean --run Example.lean
```

第一条主要用于检查文件并执行其中的 `#eval`；第二条还会运行文件中的 `main`。如果文件依赖当前 Lake 项目的包和模块路径，在项目目录内使用 `lake build`，或在构建环境中运行：

```bash
lake env lean Main.lean
```

### 14. 项目模块与文件组织

假设项目名为 `HelloLean`，可以按功能建立文件：

```text
HelloLean/
├── HelloLean.lean
├── HelloLean/
│   ├── Basic.lean
│   └── Geometry.lean
├── Main.lean
├── lakefile.toml
└── lean-toolchain
```

`HelloLean/Geometry.lean` 可作为 `HelloLean.Geometry` 模块；其他 Lean 文件中使用：

```lean
import HelloLean.Geometry
```

如果库根文件 `HelloLean.lean` 需要把子模块汇总到库中，可写入相应 `import`，例如：

```lean
import HelloLean.Basic
import HelloLean.Geometry
```

加入新模块后运行 `lake build`。若报 `unknown module prefix` 或找不到模块，先检查文件位置、文件名大小写、导入名称和项目根目录，然后从项目根目录构建。

### 15. 使用 VS Code 交互开发（可选）

如果本机已安装 VS Code，可在扩展市场安装由 `leanprover` 发布的官方 **Lean 4** 扩展。使用时建议通过 VS Code 打开项目根目录（包含 `lean-toolchain` 和 Lake 配置），而不只是打开单个 `.lean` 文件。扩展会读取项目工具链并为打开的 Lean 文件提供诊断和交互信息。

常见使用方式：

1. 在编辑器中打开或创建 `.lean` 文件。
2. 在源文件中输入 `#check`、`#eval`，或编写定义与定理。
3. 保存文件并查看 Lean 诊断；证明过程中查看当前目标（goal）和 tactic 执行后的结果。
4. 修改后重新检查，最后在终端项目根目录执行 `lake build`，确认完整项目可构建。

如果扩展没有启动，先在同一项目目录运行 `elan show` 和 `lake build`，确认工具链与项目本身正常，再重启 VS Code。桌面应用可能没有继承刚更新的 PATH；必要时从已配置好环境的终端启动 VS Code。

### 16. 依赖和 Mathlib

Lean 标准库与 Mathlib 是不同层次的依赖。普通 Lean 项目不一定需要 Mathlib；若需要 Mathlib 的数学定理、记号和 tactic，应使用与项目目标兼容的 Mathlib 版本。

Lean 官方安装指南提供 Mathlib 项目模板示例：

```bash
lake +leanprover-community/mathlib4:lean-toolchain new MyMathlibProject math
```

该命令使用 Mathlib 仓库中的 `lean-toolchain` 选择配套 Lean 版本，并创建 Mathlib 项目；它可能下载与本机默认 Lean 4.34.1 不同的 Lean 工具链和 Mathlib 依赖。网络慢时首次下载会花费较长时间。实际项目应遵循当前 Mathlib 项目的官方说明，并提交/保留项目的 `lean-toolchain` 和依赖 manifest，避免自行混用不匹配的版本。

Mathlib 项目构建通常使用：

```bash
lake build
```

Mathlib 仓库本身还提供缓存工具；在 Mathlib 项目支持并按官方说明配置后，可运行：

```bash
lake exe cache get
```

该缓存命令不是所有普通 Lean 项目都具备的命令，不要在没有相应依赖/配置的项目中假设它可用。更改 Mathlib 依赖或更新版本后，应重新构建并解决 API 变化导致的错误。

### 17. 常见开发错误排查

#### 17.1 找不到变量或名称

- 检查拼写和大小写；Lean 标识符区分大小写。
- 检查是否需要 `import` 对应模块。
- 检查名称是否在命名空间中；可写完整名称，或正确打开相应 namespace。
- 检查 VS Code 或 Lake 当前使用的项目根目录是否正确。

#### 17.2 类型不匹配

用 `#check expression`、编辑器悬停或错误中的 expected/actual 类型检查 Lean 推断的类型。数字可能因上下文推断为不同类型；可增加显式标注，例如 `(5 : Int)`。注意 `Bool` 和 `Prop` 的差别。

#### 17.3 证明目标未完成

查看 tactic 后剩下的全部 goal。一个定理可能有多个前提或分支；`cases` 和 `induction` 后通常需要为每种情况分别完成证明。尝试用 `simp?` 获取建议时要确认规则适用于项目版本；最终把实际证明脚本保存并通过 `lake build`。

#### 17.4 `rfl` 无法证明等式

`rfl` 只证明定义规约意义下两侧相同的等式；数学上等价并不必然是定义相等。通常要使用已有引理和 `rw`/`simp`，或按变量归纳。先检查目标完整形式以及参数类型。

#### 17.5 项目版本或依赖与全局版本不一致

在项目根目录运行：

```bash
elan show
cat lean-toolchain
```

如果项目依赖固定版本，优先保持该版本，勿直接删除或覆盖 `lean-toolchain`、`lake-manifest.json`。版本升级应与团队约定及依赖库要求一并处理。

#### 17.6 构建错误和编辑器显示不一致

以项目根目录执行的 `lake build` 作为完整构建检查。错误中注明的文件、行号和列号通常是定位起点；先修复最早出现的错误，再重新构建，因为后续错误可能由第一个错误引起。若编辑器环境没有跟上文件变化，保存并等待诊断更新，必要时重启语言服务器或 VS Code。

### 18. 建议的日常工作循环

1. 进入已有项目根目录，先看 `lean-toolchain` 并运行 `elan show`。
2. 按模块职责新增或修改 `.lean` 文件，保持模块文件路径和 `import` 名称一致。
3. 通过 `#check` 探索 API，通过 `#eval` 验证可执行计算；写定理时逐步完成所有 proof goals。
4. 保存源码，运行 `lake build`；有项目测试工作流时再运行配置好的 `lake test`。
5. 修改依赖前检查工具链和 manifest；仅在确实要更新依赖时运行 `lake update`。
6. 检查最终改动，保留项目需要的 `lean-toolchain`、Lake 配置和 manifest，不提交 `.lake/build` 生成物，除非项目有明确要求。

### 19. Lean 使用参考

- Lean 4 语言参考（定义、类型、证明、模块和 I/O）：<https://lean-lang.org/doc/reference/latest/>
- Lean 官方安装、VS Code 和 Mathlib 入门说明：<https://lean-lang.org/install/manual/>
- Lake 构建工具参考：<https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/>
- Lean 4 官方源码与示例：<https://github.com/leanprover/lean4>
- Mathlib 4 项目：<https://github.com/leanprover-community/mathlib4>

本使用说明的示例已使用本机 Lean 4.34.1 实测：类型查询与求值、定理检查、结构体输出、`lean --run` 执行 `main`，以及用 Lake 模板创建项目、`lake build` 和 `lake exe` 运行生成的程序均通过。Mathlib 部分是项目用法指引，未在本机安装或构建 Mathlib 项目。

官方语言参考的 `latest` 文档可能比本机 Lean 4.34.1 更新；遇到语法或库 API 差异时，以项目 `lean-toolchain` 对应版本、该版本自带的 Lean/Lake 命令帮助和项目依赖说明为准。
