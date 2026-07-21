# 使用 Neovim 搭建 C/C++ IDE

本文记录如何把 Neovim 配置成一个接近 VSCode/Eclipse 使用体验的 C/C++ IDE，包括：项目文件树、代码大纲、补全、跳转、诊断、格式化、调试、构建运行，以及 C/C++ 工程符号索引。

本文以 Linux 环境为主，配置脚本文件名为 `setup-nvim-cpp.sh`。

## 目标效果

最终打开一个 C/C++ 工程时，希望 Neovim 呈现类似 IDE 的布局：

- 左侧：项目文件列表
- 中间：当前文件代码编辑区
- 右侧：当前文件代码大纲
- 后台：自动通过 `clangd` 索引工程符号
- 常用能力：补全、跳转定义、查找引用、重命名、诊断、格式化、调试、运行任务

推荐打开方式：

```bash
cd /path/to/your/cpp-project
nvim .
```

或：

```bash
nvim /path/to/your/cpp-project
```

## 需要安装的软件

建议系统中至少安装以下工具：

- `nvim`：Neovim，建议 0.10 或更新版本
- `git`：插件管理和工程操作
- `gcc` / `g++` / `clang`：C/C++ 编译器
- `clangd`：C/C++ 语言服务器，负责补全、跳转、诊断、索引
- `clang-format`：代码格式化
- `cmake` / `make` / `ninja`：常见构建系统
- `gdb`：调试器
- `ripgrep`：全文搜索
- `nodejs` / `npm`：部分 Neovim 插件依赖
- `python3`：部分工具依赖
- `bear`：可选，用于 Makefile 工程生成 `compile_commands.json`

Debian/Ubuntu 示例：

```bash
sudo apt-get update
sudo apt-get install -y \
  git curl wget unzip tar gzip \
  build-essential gcc g++ gdb clang clangd clang-format \
  cmake make ninja-build ripgrep fd-find \
  nodejs npm python3 python3-venv \
  xclip wl-clipboard bear
```

## 配置脚本的作用

`setup-nvim-cpp.sh` 是一个自动配置脚本，主要完成以下事情：

1. 检查或安装 Neovim。
2. 安装系统依赖。
3. 备份已有的 Neovim 配置目录。
4. 写入新的 Neovim 配置文件。
5. 安装和同步插件。
6. 安装 LSP、treesitter parser 等开发组件。

脚本默认会写入如下配置结构：

```text
~/.config/nvim/
├── init.lua
└── lua/
    └── ide/
        ├── options.lua
        ├── keymaps.lua
        └── lazy.lua
```

其中：

- `init.lua`：入口文件，加载 IDE 配置模块
- `options.lua`：通用编辑器选项
- `keymaps.lua`：基础快捷键
- `lazy.lua`：插件列表、LSP 配置、调试配置、构建运行配置

## 运行脚本

完整安装：

```bash
bash ~/setup-nvim-cpp.sh
```

只写配置，不安装依赖和插件：

```bash
bash ~/setup-nvim-cpp.sh --write-only
```

跳过系统依赖安装：

```bash
bash ~/setup-nvim-cpp.sh --no-deps
```

跳过插件安装：

```bash
bash ~/setup-nvim-cpp.sh --no-plugins
```

查看帮助：

```bash
bash ~/setup-nvim-cpp.sh --help
```

## 主要插件说明

该配置使用 `lazy.nvim` 管理插件。

### 文件树

插件：`nvim-neo-tree/neo-tree.nvim`

用途：显示项目文件列表，类似 VSCode 左侧 Explorer。

关键配置：

```lua
{
  "nvim-neo-tree/neo-tree.nvim",
  branch = "v3.x",
  lazy = false,
}
```

设置 `lazy = false` 的原因是希望打开工程目录时自动加载文件树，而不是等快捷键触发后才加载。

常用快捷键：

- `<leader>e`：切换文件树
- `<leader>fe`：聚焦文件树

### 代码大纲

插件：`stevearc/aerial.nvim`

用途：显示当前文件的函数、类、变量等结构，类似 VSCode Outline。

关键配置：

```lua
{
  "stevearc/aerial.nvim",
  lazy = false,
  config = function()
    require("aerial").setup({
      backends = { "lsp", "treesitter", "markdown" },
      layout = { default_direction = "right", min_width = 28, max_width = 42 },
      attach_mode = "global",
      show_guides = true,
    })
  end,
}
```

设置 `lazy = false` 的原因是希望打开 C/C++ 文件时自动出现右侧代码大纲。

常用快捷键：

- `<leader>o`：切换代码大纲
- `<leader>fs`：在当前文件符号中搜索

### 模糊查找

插件：`nvim-telescope/telescope.nvim`

用途：查找文件、全文搜索、查找引用、跳转定义等。

常用快捷键：

- `<leader>ff`：查找文件
- `<leader>fg`：全文搜索
- `<leader>fb`：查找 buffer
- `<leader>fr`：最近文件
- `<leader>fw`：搜索光标下单词
- `<leader>gd`：查找定义
- `<leader>gr`：查找引用
- `<leader>gi`：查找实现
- `<leader>gt`：查找类型定义
- `<leader>ds`：当前 buffer 诊断
- `<leader>dS`：工作区诊断

### LSP

核心插件：

- `neovim/nvim-lspconfig`
- `williamboman/mason.nvim`
- `williamboman/mason-lspconfig.nvim`
- `p00f/clangd_extensions.nvim`
- `hrsh7th/cmp-nvim-lsp`

用途：为 C/C++、CMake、Lua 等语言提供补全、跳转、诊断、重命名等能力。

C/C++ 使用的语言服务器是 `clangd`。

重要参数：

```lua
cmd = {
  "clangd",
  "--background-index",
  "--clang-tidy",
  "--header-insertion=iwyu",
  "--completion-style=detailed",
  "--function-arg-placeholders",
  "--all-scopes-completion",
  "--pch-storage=memory",
}
```

其中最关键的是：

```text
--background-index
```

它让 `clangd` 在后台索引整个工程。

### 补全

插件：`hrsh7th/nvim-cmp`

用途：自动补全 LSP、路径、buffer、snippet。

相关插件：

- `hrsh7th/cmp-nvim-lsp`
- `hrsh7th/cmp-buffer`
- `hrsh7th/cmp-path`
- `L3MON4D3/LuaSnip`
- `saadparwaiz1/cmp_luasnip`
- `rafamadriz/friendly-snippets`

常用按键：

- `<C-Space>`：手动触发补全
- `<Tab>`：选择下一个补全项或跳转 snippet
- `<S-Tab>`：选择上一个补全项或反向跳转 snippet
- `<CR>`：确认补全

### 语法高亮

插件：`nvim-treesitter/nvim-treesitter`

用途：更准确的语法高亮和缩进。

注意：新版 `nvim-treesitter` 主线发生了不兼容重写，旧配置中常见的：

```lua
require("nvim-treesitter.configs").setup(...)
```

在新版分支可能不可用。因此本配置将 `nvim-treesitter` 固定到 `master` 分支：

```lua
{
  "nvim-treesitter/nvim-treesitter",
  branch = "master",
  lazy = false,
  build = ":TSUpdate",
}
```

### 格式化

插件：`stevearc/conform.nvim`

用途：调用 `clang-format` 格式化 C/C++。

常用快捷键：

- `<leader>cf`：格式化当前文件

配置中还启用了 C/C++ 保存时格式化。

### 调试

插件：

- `mfussenegger/nvim-dap`
- `rcarriga/nvim-dap-ui`
- `theHamsta/nvim-dap-virtual-text`

用途：通过 GDB 调试 C/C++ 程序。

常用快捷键：

- `<F5>`：启动或继续调试
- `<F9>`：切换断点
- `<F10>`：单步越过
- `<F11>`：单步进入
- `<F12>`：单步跳出
- `<leader>du`：切换调试 UI
- `<leader>dr`：打开调试 REPL
- `<leader>dt`：结束调试

### 任务运行

插件：`stevearc/overseer.nvim`

用途：运行构建任务、测试任务等。

常用快捷键：

- `<leader>rr`：运行任务
- `<leader>rt`：切换任务面板

配置中还提供了简单的单文件 C/C++ 编译运行快捷键：

- `<leader>cb`：编译当前 C/C++ 文件
- `<leader>cr`：编译并运行当前 C/C++ 文件

## 修复 nvim-lspconfig 弃用报错

如果你使用较新的 Neovim 和 `nvim-lspconfig`，可能遇到如下报错：

```text
The `require('lspconfig')` "framework" is deprecated, use vim.lsp.config
(see :help lspconfig-nvim-0.11) instead.
Feature will be removed in nvim-lspconfig v3.0.0
```

旧写法类似：

```lua
local lspconfig = require("lspconfig")
lspconfig.cmake.setup({ capabilities = capabilities })
lspconfig.lua_ls.setup({ capabilities = capabilities })
```

新写法应优先使用 Neovim 内置 LSP 配置 API：

```lua
local function lsp_setup(server, config)
  if vim.lsp.config and vim.lsp.enable then
    vim.lsp.config(server, config)
    vim.lsp.enable(server)
  else
    require("lspconfig")[server].setup(config)
  end
end

lsp_setup("clangd", {
  capabilities = capabilities,
  cmd = {
    "clangd",
    "--background-index",
    "--clang-tidy",
    "--header-insertion=iwyu",
    "--completion-style=detailed",
    "--function-arg-placeholders",
    "--all-scopes-completion",
    "--pch-storage=memory",
  },
  init_options = {
    usePlaceholders = true,
    completeUnimported = true,
    clangdFileStatus = true,
  },
})

lsp_setup("cmake", { capabilities = capabilities })
lsp_setup("lua_ls", {
  capabilities = capabilities,
  settings = { Lua = { diagnostics = { globals = { "vim" } } } },
})
```

这样可以兼容新版 Neovim，同时保留旧版兼容回退。

## C/C++ 工程索引的关键：compile_commands.json

Neovim 本身并不直接索引 C/C++ 工程。真正负责索引的是 `clangd`。

`clangd` 要准确理解工程，必须知道每个源文件的真实编译参数，例如：

- 头文件搜索路径
- 宏定义
- C/C++ 标准版本
- 编译器参数
- 条件编译开关

这些信息通常来自工程根目录下的：

```text
compile_commands.json
```

如果没有这个文件，`clangd` 仍然可以提供部分补全和跳转，但经常会出现：

- 头文件找不到
- 宏识别不正确
- 跳转定义不完整
- 模板类型推导错误
- 诊断结果和真实编译不一致

### CMake 工程

CMake 工程推荐这样生成 `compile_commands.json`：

```bash
cd /path/to/your/cpp-project
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ln -sf build/compile_commands.json compile_commands.json
nvim .
```

解释：

- `cmake -S . -B build`：源码目录是当前目录，构建目录是 `build`
- `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`：让 CMake 导出编译数据库
- `ln -sf ...`：在工程根目录创建软链接，方便 `clangd` 自动发现

### Makefile 工程

Makefile 工程可以使用 `bear`：

```bash
cd /path/to/your/cpp-project
bear -- make
nvim .
```

`bear` 会监听构建过程，并生成 `compile_commands.json`。

如果系统没有 `bear`，Debian/Ubuntu 可安装：

```bash
sudo apt install bear
```

### 使用 .clangd 指定编译数据库位置

如果不想在工程根目录创建 `compile_commands.json` 软链接，也可以创建 `.clangd` 文件：

```yaml
CompileFlags:
  CompilationDatabase: build
```

这样告诉 `clangd` 编译数据库在 `build` 目录。

## 确认 LSP 是否正常工作

打开 C/C++ 文件后，在 Neovim 中执行：

```vim
:LspInfo
```

如果看到 `clangd` attached 到当前 buffer，说明 LSP 已经工作。

也可以尝试以下功能：

- `gd`：跳转定义
- `gr`：查找引用
- `K`：查看悬浮文档
- `<leader>rn`：重命名符号
- `<leader>ca`：Code Action

第一次打开大工程时，`clangd` 需要后台索引，可能要等待一段时间。

## 推荐工作流

### 新 CMake 工程

```bash
cd my-project
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ln -sf build/compile_commands.json compile_commands.json
nvim .
```

进入 Neovim 后：

1. 左侧文件树选择源文件。
2. 等待 `clangd` attach。
3. 使用 `gd` / `gr` / `<leader>rn` 等 LSP 功能。
4. 使用 `<leader>o` 查看代码大纲。
5. 使用 `<leader>fg` 搜索工程文本。
6. 使用 `<leader>cf` 格式化当前文件。
7. 使用 `<F5>` 或 `<leader>dc` 启动调试。

### 已有 Makefile 工程

```bash
cd legacy-project
bear -- make
nvim .
```

如果构建命令不是 `make`，把 `bear -- make` 替换成真实构建命令，例如：

```bash
bear -- ./build.sh
```

## 常用快捷键总览

基础操作：

| 快捷键 | 功能 |
| --- | --- |
| `<leader>w` | 保存文件 |
| `<leader>q` | 关闭窗口 |
| `<C-h>` | 切到左侧窗口 |
| `<C-j>` | 切到下方窗口 |
| `<C-k>` | 切到上方窗口 |
| `<C-l>` | 切到右侧窗口 |
| `<leader>sv` | 垂直分屏 |
| `<leader>sh` | 水平分屏 |
| `<leader>bn` | 下一个 buffer |
| `<leader>bp` | 上一个 buffer |
| `<leader>bd` | 删除 buffer |

项目导航：

| 快捷键 | 功能 |
| --- | --- |
| `<leader>e` | 切换文件树 |
| `<leader>fe` | 聚焦文件树 |
| `<leader>o` | 切换代码大纲 |
| `<leader>ff` | 查找文件 |
| `<leader>fg` | 全文搜索 |
| `<leader>fb` | 查找 buffer |
| `<leader>fr` | 最近文件 |

LSP：

| 快捷键 | 功能 |
| --- | --- |
| `gd` | 跳转定义 |
| `gD` | 跳转声明 |
| `gi` | 跳转实现 |
| `gr` | 查找引用 |
| `gt` | 跳转类型定义 |
| `K` | 悬浮文档 |
| `<leader>rn` | 重命名符号 |
| `<leader>ca` | Code Action |
| `[d` | 上一个诊断 |
| `]d` | 下一个诊断 |

构建、运行、格式化：

| 快捷键 | 功能 |
| --- | --- |
| `<leader>cf` | 格式化当前文件 |
| `<leader>cb` | 编译当前 C/C++ 文件 |
| `<leader>cr` | 编译并运行当前 C/C++ 文件 |
| `<leader>rr` | 运行任务 |
| `<leader>rt` | 切换任务面板 |

调试：

| 快捷键 | 功能 |
| --- | --- |
| `<F5>` | 启动或继续调试 |
| `<F9>` | 切换断点 |
| `<F10>` | 单步越过 |
| `<F11>` | 单步进入 |
| `<F12>` | 单步跳出 |
| `<leader>du` | 切换调试 UI |
| `<leader>dr` | 打开调试 REPL |
| `<leader>dt` | 结束调试 |

## 常见问题

### 打开工程后没有右侧代码大纲

可能原因：

1. 当前没有打开 C/C++ 文件。
2. `clangd` 尚未 attach。
3. 当前文件没有可识别的 LSP 或 treesitter 符号。
4. 插件还未安装完成。

可尝试：

```vim
:Lazy sync
:TSUpdate
:LspInfo
:AerialToggle right
```

### 跳转定义不准确

优先检查工程根目录是否有 `compile_commands.json`。

CMake 工程重新生成：

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ln -sf build/compile_commands.json compile_commands.json
```

然后在 Neovim 中执行：

```vim
:LspRestart
```

### 头文件找不到

这通常不是 Neovim 的问题，而是 `clangd` 没有拿到正确 include 路径。

解决方法：

1. 生成正确的 `compile_commands.json`。
2. 确认 `compile_commands.json` 在工程根目录，或用 `.clangd` 指定位置。
3. 重启 LSP。

### nvim-lspconfig 报 deprecated

使用 `vim.lsp.config()` 和 `vim.lsp.enable()` 替代旧的 `require("lspconfig")` 框架式 setup。

### treesitter 报 module not found

如果使用旧配置：

```lua
require("nvim-treesitter.configs").setup(...)
```

建议将 `nvim-treesitter` 固定到 `master` 分支，或按照新版 README 重写 treesitter 配置。

本文中的脚本选择固定到 `master`，因为稳定且兼容传统配置。

## 验证配置是否正常

可以用 headless 模式检查 Neovim 启动：

```bash
nvim --headless '+qa'
```

检查 C++ buffer 加载路径：

```bash
nvim --headless '+edit /tmp/nvim_test.cpp' '+set filetype=cpp' '+doautocmd FileType' '+qa'
```

如果命令没有输出错误，说明基本配置加载正常。

## 导出 PDF

本文是 Markdown 文件，可以用 `pandoc` 转成 PDF。

示例：

```bash
pandoc nvim.cpp.md -o nvim.cpp.pdf
```

如果中文 PDF 字体有问题，可以指定 XeLaTeX 和中文字体，例如：

```bash
pandoc nvim.cpp.md -o nvim.cpp.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="Noto Sans CJK SC"
```

如果系统没有该字体，可先安装中文字体包，或替换成系统中已有的中文字体。

## 总结

这套配置的核心思路是：

1. 用 `neo-tree` 提供项目文件树。
2. 用 `aerial` 提供代码大纲。
3. 用 `clangd` 提供 C/C++ LSP 能力。
4. 用 `compile_commands.json` 让 `clangd` 准确理解工程。
5. 用 `nvim-cmp` 提供补全。
6. 用 `treesitter` 提供语法高亮和缩进。
7. 用 `nvim-dap` + `gdb` 提供调试。
8. 用 `telescope` 提供快速搜索和导航。

其中最容易被忽略、但最重要的一点是：C/C++ 工程索引的质量主要取决于 `compile_commands.json` 是否正确，而不是 Neovim 插件数量多少。
