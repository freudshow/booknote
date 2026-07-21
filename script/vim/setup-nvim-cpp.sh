#!/usr/bin/env bash
set -euo pipefail

NVIM_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"
NVIM_DATA="${XDG_DATA_HOME:-$HOME/.local/share}/nvim"
NVIM_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/nvim"
NVIM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/nvim"
DO_DEPS=1
DO_PLUGINS=1

info() { printf '\033[32m[INFO]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[WARN]\033[0m %s\n' "$*"; }
err()  { printf '\033[31m[ERR]\033[0m %s\n' "$*" >&2; }
run()  { printf '\033[36m[RUN]\033[0m %s\n' "$*"; "$@"; }

have() { command -v "$1" >/dev/null 2>&1; }

pkg_manager() {
  if have apt-get; then echo apt
  elif have dnf; then echo dnf
  elif have pacman; then echo pacman
  elif have zypper; then echo zypper
  elif have apk; then echo apk
  else echo unknown
  fi
}

install_packages() {
  local pm; pm="$(pkg_manager)"
  case "$pm" in
    apt)
      run sudo apt-get update
      run sudo apt-get install -y git curl wget unzip tar gzip build-essential gcc g++ gdb clang clangd clang-format cmake make ninja-build ripgrep fd-find nodejs npm python3 python3-venv xclip wl-clipboard
      ;;
    dnf)
      run sudo dnf install -y git curl wget unzip tar gzip gcc gcc-c++ gdb clang clang-tools-extra clang-tools-extra-devel cmake make ninja-build ripgrep fd-find nodejs npm python3 xclip wl-clipboard
      ;;
    pacman)
      run sudo pacman -S --needed --noconfirm git curl wget unzip tar gzip base-devel gcc gdb clang cmake make ninja ripgrep fd nodejs npm python xclip wl-clipboard
      ;;
    zypper)
      run sudo zypper install -y git curl wget unzip tar gzip gcc gcc-c++ gdb clang clang-tools cmake make ninja ripgrep fd nodejs npm python3 xclip wl-clipboard
      ;;
    apk)
      run sudo apk add git curl wget unzip tar gzip build-base gcc g++ gdb clang clang-extra-tools cmake make ninja ripgrep fd nodejs npm python3 xclip wl-clipboard
      ;;
    *)
      warn "Unknown package manager. Please install manually: git curl unzip gcc g++ gdb clangd clang-format cmake make ninja ripgrep fd node npm python3"
      ;;
  esac
}

install_neovim_if_missing() {
  if have nvim; then
    info "Found $(nvim --version | sed -n '1p')"
    return
  fi

  local pm; pm="$(pkg_manager)"
  case "$pm" in
    apt) run sudo apt-get install -y neovim ;;
    dnf) run sudo dnf install -y neovim ;;
    pacman) run sudo pacman -S --needed --noconfirm neovim ;;
    zypper) run sudo zypper install -y neovim ;;
    apk) run sudo apk add neovim ;;
    *) err "Please install Neovim >= 0.10 first: https://github.com/neovim/neovim/releases"; exit 1 ;;
  esac
}

check_neovim_version() {
  local major minor
  major="$(nvim --version | sed -n '1s/^NVIM v\([0-9]*\)\.\([0-9]*\).*/\1/p')"
  minor="$(nvim --version | sed -n '1s/^NVIM v\([0-9]*\)\.\([0-9]*\).*/\2/p')"
  if [[ -z "$major" || -z "$minor" ]]; then
    warn "Could not parse Neovim version; continuing. Neovim >= 0.10 is recommended."
  elif (( major == 0 && minor < 10 )); then
    err "Neovim >= 0.10 is required. Current: $(nvim --version | sed -n '1p')"
    exit 1
  fi
}

backup_existing() {
  local stamp; stamp="$(date +%Y%m%d%H%M%S)"
  if [[ -e "$NVIM_CONFIG" ]]; then
    warn "Backing up existing config: $NVIM_CONFIG -> ${NVIM_CONFIG}.bak.${stamp}"
    run mv "$NVIM_CONFIG" "${NVIM_CONFIG}.bak.${stamp}"
  fi
  for d in "$NVIM_DATA" "$NVIM_STATE" "$NVIM_CACHE"; do
    if [[ -e "$d" ]]; then
      warn "Backing up existing runtime dir: $d -> ${d}.bak.${stamp}"
      run mv "$d" "${d}.bak.${stamp}"
    fi
  done
}

write_config() {
  info "Writing self-contained C/C++ IDE configuration to $NVIM_CONFIG"
  run mkdir -p "$NVIM_CONFIG/lua/ide"

  cat > "$NVIM_CONFIG/init.lua" <<'EOF_INIT'
require("ide.options")
require("ide.keymaps")
require("ide.lazy")
EOF_INIT

  cat > "$NVIM_CONFIG/lua/ide/options.lua" <<'EOF_OPTIONS'
local opt = vim.opt

vim.g.mapleader = " "
vim.g.maplocalleader = " "

opt.number = true
opt.relativenumber = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.termguicolors = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.splitright = true
opt.splitbelow = true
opt.wrap = false
opt.scrolloff = 8
opt.sidescrolloff = 8
opt.ignorecase = true
opt.smartcase = true
opt.incsearch = true
opt.hlsearch = true
opt.expandtab = true
opt.tabstop = 4
opt.shiftwidth = 4
opt.softtabstop = 4
opt.smartindent = true
opt.breakindent = true
opt.undofile = true
opt.updatetime = 250
opt.timeoutlen = 400
opt.completeopt = "menu,menuone,noselect"
opt.pumheight = 12
opt.laststatus = 3
opt.showmode = false
opt.list = true
opt.listchars = { tab = "  ", trail = ".", nbsp = "+" }
opt.fillchars = { eob = " " }

vim.diagnostic.config({
  virtual_text = { spacing = 2, prefix = ">" },
  signs = true,
  underline = true,
  update_in_insert = false,
  severity_sort = true,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = { "c", "cpp", "cc", "cxx", "h", "hpp", "hxx" },
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
    vim.opt_local.expandtab = true
  end,
})
EOF_OPTIONS

  cat > "$NVIM_CONFIG/lua/ide/keymaps.lua" <<'EOF_KEYMAPS'
local map = vim.keymap.set

map("n", "<Esc>", "<cmd>nohlsearch<CR>", { desc = "Clear search highlight" })
map("n", "<leader>w", "<cmd>write<CR>", { desc = "Save file" })
map("n", "<leader>q", "<cmd>quit<CR>", { desc = "Quit window" })
map("n", "<C-h>", "<C-w>h", { desc = "Move left" })
map("n", "<C-j>", "<C-w>j", { desc = "Move down" })
map("n", "<C-k>", "<C-w>k", { desc = "Move up" })
map("n", "<C-l>", "<C-w>l", { desc = "Move right" })
map("n", "<leader>sv", "<C-w>v", { desc = "Split vertical" })
map("n", "<leader>sh", "<C-w>s", { desc = "Split horizontal" })
map("n", "<leader>bn", "<cmd>bnext<CR>", { desc = "Next buffer" })
map("n", "<leader>bp", "<cmd>bprevious<CR>", { desc = "Previous buffer" })
map("n", "<leader>bd", "<cmd>bdelete<CR>", { desc = "Delete buffer" })
EOF_KEYMAPS

  cat > "$NVIM_CONFIG/lua/ide/lazy.lua" <<'EOF_LAZY'
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  { "nvim-lua/plenary.nvim", lazy = true },
  { "nvim-tree/nvim-web-devicons", lazy = true },

  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    config = function()
      require("catppuccin").setup({ flavour = "mocha", transparent_background = false })
      vim.cmd.colorscheme("catppuccin")
    end,
  },

  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    config = function()
      require("which-key").setup({ preset = "modern" })
    end,
  },

  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = { theme = "catppuccin", globalstatus = true, component_separators = "|", section_separators = "" },
      })
    end,
  },

  {
    "akinsho/bufferline.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    version = "*",
    config = function()
      require("bufferline").setup({ options = { diagnostics = "nvim_lsp", separator_style = "thin" } })
    end,
  },

  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = { "nvim-lua/plenary.nvim", "nvim-tree/nvim-web-devicons", "MunifTanjim/nui.nvim" },
    lazy = false,
    keys = {
      { "<leader>e", "<cmd>Neotree toggle reveal left<CR>", desc = "Toggle file explorer" },
      { "<leader>fe", "<cmd>Neotree focus<CR>", desc = "Focus file explorer" },
    },
    config = function()
      require("neo-tree").setup({
        close_if_last_window = false,
        enable_git_status = true,
        enable_diagnostics = true,
        filesystem = { filtered_items = { visible = true, hide_dotfiles = false, hide_gitignored = false } },
        window = { width = 32, mappings = { ["<space>"] = "none" } },
      })
      vim.api.nvim_create_autocmd("VimEnter", {
        callback = function(data)
          if vim.fn.argc() == 0 or vim.fn.isdirectory(data.file) == 1 then
            vim.cmd("Neotree show left")
          end
        end,
      })
    end,
  },

  {
    "stevearc/aerial.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    lazy = false,
    keys = {
      { "<leader>o", "<cmd>AerialToggle right<CR>", desc = "Toggle code outline" },
      { "<leader>fs", "<cmd>Telescope aerial<CR>", desc = "Find symbols in file" },
    },
    config = function()
      require("aerial").setup({
        backends = { "lsp", "treesitter", "markdown" },
        layout = { default_direction = "right", min_width = 28, max_width = 42 },
        attach_mode = "global",
        show_guides = true,
      })
      vim.api.nvim_create_autocmd("LspAttach", {
        callback = function(args)
          local ft = vim.bo[args.buf].filetype
          if ft == "c" or ft == "cpp" or ft == "objc" or ft == "objcpp" then
            vim.defer_fn(function()
              pcall(vim.cmd, "AerialOpen right")
            end, 300)
          end
        end,
      })
    end,
  },

  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim", "nvim-telescope/telescope-ui-select.nvim" },
    keys = {
      { "<leader>ff", "<cmd>Telescope find_files<CR>", desc = "Find files" },
      { "<leader>fg", "<cmd>Telescope live_grep<CR>", desc = "Search text" },
      { "<leader>fb", "<cmd>Telescope buffers<CR>", desc = "Find buffers" },
      { "<leader>fr", "<cmd>Telescope oldfiles<CR>", desc = "Recent files" },
      { "<leader>fw", "<cmd>Telescope grep_string<CR>", desc = "Search word under cursor" },
      { "<leader>gr", "<cmd>Telescope lsp_references<CR>", desc = "References" },
      { "<leader>gi", "<cmd>Telescope lsp_implementations<CR>", desc = "Implementations" },
      { "<leader>gd", "<cmd>Telescope lsp_definitions<CR>", desc = "Definitions" },
      { "<leader>gt", "<cmd>Telescope lsp_type_definitions<CR>", desc = "Type definitions" },
      { "<leader>ds", "<cmd>Telescope diagnostics bufnr=0<CR>", desc = "Buffer diagnostics" },
      { "<leader>dS", "<cmd>Telescope diagnostics<CR>", desc = "Workspace diagnostics" },
    },
    config = function()
      local telescope = require("telescope")
      telescope.setup({
        defaults = { sorting_strategy = "ascending", layout_config = { prompt_position = "top" } },
        extensions = { ["ui-select"] = { require("telescope.themes").get_dropdown({}) } },
      })
      telescope.load_extension("ui-select")
    end,
  },

  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      require("gitsigns").setup({ current_line_blame = true })
    end,
  },

  {
    "folke/trouble.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    keys = {
      { "<leader>xx", "<cmd>Trouble diagnostics toggle<CR>", desc = "Diagnostics panel" },
      { "<leader>xq", "<cmd>Trouble quickfix toggle<CR>", desc = "Quickfix panel" },
      { "<leader>xl", "<cmd>Trouble loclist toggle<CR>", desc = "Location list panel" },
    },
    config = function()
      require("trouble").setup({})
    end,
  },

  {
    "nvim-treesitter/nvim-treesitter",
    branch = "master",
    lazy = false,
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = { "c", "cpp", "cmake", "make", "lua", "vim", "vimdoc", "bash", "json", "markdown" },
        highlight = { enable = true },
        indent = { enable = true },
      })
    end,
  },

  {
    "windwp/nvim-autopairs",
    event = "InsertEnter",
    config = function()
      require("nvim-autopairs").setup({})
    end,
  },

  {
    "numToStr/Comment.nvim",
    keys = { "gcc", "gc", "gbc", "gb" },
    config = function()
      require("Comment").setup({})
    end,
  },

  {
    "williamboman/mason.nvim",
    build = ":MasonUpdate",
    config = function()
      require("mason").setup({ ui = { border = "rounded" } })
    end,
  },
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason-lspconfig.nvim",
      "p00f/clangd_extensions.nvim",
      "hrsh7th/cmp-nvim-lsp",
    },
    config = function()
      local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
      local capabilities = ok_cmp and cmp_lsp.default_capabilities() or vim.lsp.protocol.make_client_capabilities()

      local function lsp_setup(server, config)
        if vim.lsp.config and vim.lsp.enable then
          vim.lsp.config(server, config)
          vim.lsp.enable(server)
        else
          require("lspconfig")[server].setup(config)
        end
      end

      require("mason-lspconfig").setup({
        ensure_installed = { "clangd", "lua_ls", "cmake" },
        automatic_installation = false,
      })

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
    end,
  },

  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
      "hrsh7th/cmp-cmdline",
      "L3MON4D3/LuaSnip",
      "saadparwaiz1/cmp_luasnip",
      "rafamadriz/friendly-snippets",
    },
    event = "InsertEnter",
    config = function()
      local cmp = require("cmp")
      local luasnip = require("luasnip")
      require("luasnip.loaders.from_vscode").lazy_load()

      cmp.setup({
        snippet = { expand = function(args) luasnip.lsp_expand(args.body) end },
        mapping = cmp.mapping.preset.insert({
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<CR>"] = cmp.mapping.confirm({ select = true }),
          ["<Tab>"] = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then luasnip.expand_or_jump()
            else fallback() end
          end, { "i", "s" }),
          ["<S-Tab>"] = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_prev_item()
            elseif luasnip.jumpable(-1) then luasnip.jump(-1)
            else fallback() end
          end, { "i", "s" }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "luasnip" },
          { name = "path" },
        }, {
          { name = "buffer" },
        }),
      })
    end,
  },

  {
    "stevearc/conform.nvim",
    keys = {
      { "<leader>cf", function() require("conform").format({ async = true, lsp_fallback = true }) end, desc = "Format file" },
    },
    config = function()
      require("conform").setup({
        formatters_by_ft = { c = { "clang_format" }, cpp = { "clang_format" }, cuda = { "clang_format" } },
        format_on_save = function(bufnr)
          local ft = vim.bo[bufnr].filetype
          if ft == "c" or ft == "cpp" then return { timeout_ms = 1000, lsp_fallback = true } end
        end,
      })
    end,
  },

  {
    "stevearc/overseer.nvim",
    keys = {
      { "<leader>rr", "<cmd>OverseerRun<CR>", desc = "Run task" },
      { "<leader>rt", "<cmd>OverseerToggle<CR>", desc = "Task panel" },
    },
    config = function()
      require("overseer").setup({ templates = { "builtin" } })
    end,
  },

  {
    "mfussenegger/nvim-dap",
    dependencies = {
      "rcarriga/nvim-dap-ui",
      "nvim-neotest/nvim-nio",
      "theHamsta/nvim-dap-virtual-text",
    },
    keys = {
      { "<F5>", function() require("dap").continue() end, desc = "Debug continue/start" },
      { "<F9>", function() require("dap").toggle_breakpoint() end, desc = "Toggle breakpoint" },
      { "<F10>", function() require("dap").step_over() end, desc = "Step over" },
      { "<F11>", function() require("dap").step_into() end, desc = "Step into" },
      { "<F12>", function() require("dap").step_out() end, desc = "Step out" },
      { "<leader>db", function() require("dap").toggle_breakpoint() end, desc = "Toggle breakpoint" },
      { "<leader>dB", function() require("dap").set_breakpoint(vim.fn.input("Breakpoint condition: ")) end, desc = "Conditional breakpoint" },
      { "<leader>dc", function() require("dap").continue() end, desc = "Debug continue/start" },
      { "<leader>di", function() require("dap").step_into() end, desc = "Step into" },
      { "<leader>do", function() require("dap").step_over() end, desc = "Step over" },
      { "<leader>dO", function() require("dap").step_out() end, desc = "Step out" },
      { "<leader>dr", function() require("dap").repl.open() end, desc = "Debug REPL" },
      { "<leader>dt", function() require("dap").terminate() end, desc = "Terminate debug" },
      { "<leader>du", function() require("dapui").toggle() end, desc = "Toggle debug UI" },
    },
    config = function()
      local dap = require("dap")
      local dapui = require("dapui")

      require("nvim-dap-virtual-text").setup({})
      dapui.setup({})

      dap.adapters.gdb = {
        type = "executable",
        command = "gdb",
        args = { "--interpreter=dap", "--eval-command", "set print pretty on" },
      }

      local function executable()
        return vim.fn.input("Path to executable: ", vim.fn.getcwd() .. "/", "file")
      end

      dap.configurations.c = {
        { name = "Launch executable (GDB)", type = "gdb", request = "launch", program = executable, cwd = "${workspaceFolder}", stopAtBeginningOfMainSubprogram = false },
        { name = "Attach to process (GDB)", type = "gdb", request = "attach", processId = require("dap.utils").pick_process, cwd = "${workspaceFolder}" },
      }
      dap.configurations.cpp = dap.configurations.c

      dap.listeners.after.event_initialized["dapui_config"] = function() dapui.open() end
      dap.listeners.before.event_terminated["dapui_config"] = function() dapui.close() end
      dap.listeners.before.event_exited["dapui_config"] = function() dapui.close() end
    end,
  },

  {
    "folke/lazydev.nvim",
    ft = "lua",
    opts = { library = { { path = "luvit-meta/library", words = { "vim%.uv" } } } },
  },
  { "Bilal2453/luvit-meta", lazy = true },

  {
    "folke/todo-comments.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    event = { "BufReadPost", "BufNewFile" },
    config = function()
      require("todo-comments").setup({})
    end,
  },
}, {
  install = { colorscheme = { "catppuccin" } },
  checker = { enabled = true, notify = false },
  change_detection = { notify = false },
})

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(event)
    local map = function(mode, lhs, rhs, desc)
      vim.keymap.set(mode, lhs, rhs, { buffer = event.buf, desc = desc })
    end
    map("n", "gd", vim.lsp.buf.definition, "Go to definition")
    map("n", "gD", vim.lsp.buf.declaration, "Go to declaration")
    map("n", "gi", vim.lsp.buf.implementation, "Go to implementation")
    map("n", "gr", vim.lsp.buf.references, "Find references")
    map("n", "gt", vim.lsp.buf.type_definition, "Go to type definition")
    map("n", "K", vim.lsp.buf.hover, "Hover documentation")
    map("n", "<leader>rn", vim.lsp.buf.rename, "Rename symbol")
    map({ "n", "v" }, "<leader>ca", vim.lsp.buf.code_action, "Code action")
    map("n", "[d", vim.diagnostic.goto_prev, "Previous diagnostic")
    map("n", "]d", vim.diagnostic.goto_next, "Next diagnostic")
  end,
})

local function compile_current(run_after)
  local file = vim.fn.expand("%:p")
  local ext = vim.fn.expand("%:e")
  local out = vim.fn.expand("%:p:r")
  if file == "" then return end

  local compiler
  local std
  if ext == "c" then
    compiler = "gcc"
    std = "-std=c11"
  elseif ext == "cpp" or ext == "cc" or ext == "cxx" then
    compiler = "g++"
    std = "-std=c++17"
  else
    vim.notify("Current file is not C/C++", vim.log.levels.WARN)
    return
  end

  vim.cmd("write")
  local cmd = string.format('%s -Wall -Wextra -g %s -o %q %q', compiler, std, out, file)
  if run_after then cmd = cmd .. " && " .. vim.fn.shellescape(out) end
  vim.cmd("botright 12split | terminal " .. cmd)
end

vim.keymap.set("n", "<leader>cb", function() compile_current(false) end, { desc = "Build current C/C++ file" })
vim.keymap.set("n", "<leader>cr", function() compile_current(true) end, { desc = "Build and run current C/C++ file" })
EOF_LAZY

  cat > "$NVIM_CONFIG/README-cpp-ide.md" <<'EOF_README'
# Neovim C/C++ IDE

This configuration is generated by `setup-nvim-cpp.sh`.

## Main features

- File explorer opens on the left: Neo-tree
- Code outline opens on the right for C/C++ buffers: Aerial
- C/C++ language intelligence: clangd
- Completion/snippets: nvim-cmp + LuaSnip
- Symbol/reference navigation: native LSP + Telescope
- Diagnostics panel: Trouble
- Git signs and inline blame: gitsigns
- Build/run tasks: Overseer and simple single-file build mappings
- Debugging: nvim-dap + GDB DAP

## Useful keys

- `<leader>e`: toggle file explorer
- `<leader>o`: toggle code outline
- `<leader>ff`: find files
- `<leader>fg`: search text in project
- `gd`: go to definition
- `gr`: references
- `K`: hover documentation
- `<leader>rn`: rename symbol
- `<leader>ca`: code action
- `<leader>cf`: format file
- `<leader>cb`: build current C/C++ file with debug info
- `<leader>cr`: build and run current C/C++ file
- `<F5>` or `<leader>dc`: start/continue debug
- `<F9>` or `<leader>db`: toggle breakpoint
- `<F10>`: step over
- `<F11>`: step into
- `<F12>`: step out
- `<leader>du`: toggle debug UI
- `<leader>rr`: run a task
- `<leader>rt`: task panel

## Project notes

For best clangd results, generate `compile_commands.json`:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ln -sf build/compile_commands.json compile_commands.json
```
EOF_README
}

install_plugins() {
  info "Installing plugins with lazy.nvim. This can take several minutes on first run."
  nvim --headless "+Lazy! sync" +qa
  info "Installing Mason LSP packages where possible. System clangd/gdb are also supported."
  nvim --headless "+MasonInstall clangd lua-language-server cmake-language-server" +qa || true
  info "Installing Treesitter parsers."
  nvim --headless "+TSInstallSync c cpp cmake make lua vim vimdoc bash json markdown" +qa || true
}

print_summary() {
  cat <<'EOF_SUMMARY'

Neovim C/C++ IDE setup complete.

Open Neovim:
  nvim

Layout:
  - Left: project file explorer
  - Center: editor with line numbers, completion, diagnostics
  - Right: code outline for C/C++ files
  - Bottom: terminal/tasks/debug panels when needed

Core keys:
  <leader>e   file explorer
  <leader>o   code outline
  <leader>ff  find files
  <leader>fg  search project text
  gd / gr      definition / references
  <leader>cb  build current C/C++ file
  <leader>cr  build and run current C/C++ file
  F5/F9/F10/F11/F12 debug controls

Full notes:
  ~/.config/nvim/README-cpp-ide.md

To deploy on another machine, copy and run:
  bash ~/setup-nvim-cpp.sh

EOF_SUMMARY
}

main() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --no-deps) DO_DEPS=0 ;;
      --no-plugins) DO_PLUGINS=0 ;;
      --write-only) DO_DEPS=0; DO_PLUGINS=0 ;;
      -h|--help)
        cat <<'EOF_HELP'
Usage: setup-nvim-cpp.sh [--no-deps] [--no-plugins] [--write-only]

Options:
  --no-deps      Do not install system packages.
  --no-plugins   Do not run lazy.nvim, Mason, or Treesitter installers.
  --write-only   Only back up old config and write the new Neovim config.
EOF_HELP
        exit 0
        ;;
      *) err "Unknown option: $1"; exit 1 ;;
    esac
    shift
  done

  info "Starting Neovim C/C++ IDE setup"
  install_neovim_if_missing
  check_neovim_version
  if (( DO_DEPS )); then
    install_packages
  else
    warn "Skipping system package installation"
  fi
  backup_existing
  write_config
  if (( DO_PLUGINS )); then
    install_plugins
  else
    warn "Skipping plugin installation. Open nvim or run the script without --no-plugins to install plugins."
  fi
  print_summary
}

main "$@"

# -----------------------------------------------------------------------------
# 2026-07-21 修复记录和使用说明
# -----------------------------------------------------------------------------
#
# 本节记录本次对 setup-nvim-cpp.sh 及其生成的 Neovim 配置所做的修复，
# 便于以后重新运行脚本、迁移到新机器或排查 C/C++ 工程索引问题。
#
# 一、本次修复内容
#
# 1. 修复 Neovim 启动时的 nvim-lspconfig 弃用报错
#
#    报错内容类似：
#
#      The `require('lspconfig')` "framework" is deprecated, use vim.lsp.config
#      (see :help lspconfig-nvim-0.11) instead.
#      Feature will be removed in nvim-lspconfig v3.0.0
#
#    根因：当前 Neovim 是 NVIM v0.12.4，新版 nvim-lspconfig 已经弃用：
#
#      require("lspconfig").clangd.setup(...)
#      require("lspconfig").cmake.setup(...)
#      require("lspconfig").lua_ls.setup(...)
#
#    现在脚本生成的 ~/.config/nvim/lua/ide/lazy.lua 会优先使用新版 API：
#
#      vim.lsp.config(server, config)
#      vim.lsp.enable(server)
#
#    并保留旧版 Neovim 兼容回退：
#
#      require("lspconfig")[server].setup(config)
#
#    因此在 Neovim 0.11/0.12 及后续版本上不会再因为 lspconfig 旧 API
#    触发启动报错。
#
# 2. 修复打开工程时不像 IDE 的布局问题
#
#    原配置中 neo-tree 和 aerial 主要依赖 lazy-load，某些打开方式下不会
#    在启动阶段加载，所以没有稳定出现：
#
#      左侧：项目文件树
#      中间：当前代码文件
#      右侧：当前文件代码大纲
#
#    现在脚本将以下插件设置为 lazy = false：
#
#      nvim-neo-tree/neo-tree.nvim
#      stevearc/aerial.nvim
#
#    效果：使用 `nvim .` 或 `nvim /path/to/project` 打开目录时，左侧
#    文件树会自动出现；打开 C/C++ 文件且 clangd attach 后，右侧大纲会自动
#    打开。也可以用快捷键手动控制。
#
# 3. 修复 nvim-treesitter 最新分支和旧配置不兼容的问题
#
#    nvim-treesitter 新版主线发生了不兼容重写，原来的：
#
#      require("nvim-treesitter.configs").setup(...)
#
#    在新版分支会找不到 nvim-treesitter.configs。为了让本脚本保持稳定，
#    现在将 nvim-treesitter pin 到 master 分支，并继续使用成熟配置：
#
#      branch = "master"
#      ensure_installed = { "c", "cpp", "cmake", "make", "lua", "vim", ... }
#      highlight.enable = true
#      indent.enable = true
#
#    已验证可安装 C/C++ 等 parser。
#
# 4. 同步修复当前配置和脚本模板
#
#    本次修改同时应用到了：
#
#      ~/.config/nvim/lua/ide/lazy.lua
#      ~/setup-nvim-cpp.sh
#
#    因此以后重新运行本脚本，不会把已修复的配置覆盖回旧错误版本。
#
# 二、验证过的命令
#
# 本次修复后执行过以下验证：
#
#   nvim --headless '+qa'
#
# 结果：Neovim 无启动报错。
#
# 还执行过 C++ buffer 加载路径检查：
#
#   nvim --headless '+edit /tmp/dfcode_nvim_test.cpp' '+set filetype=cpp' \
#     '+doautocmd FileType' '+qa'
#
# 结果：C++ 文件类型加载路径无报错。
#
# 三、像 VSCode/Eclipse 那样打开 C/C++ 工程
#
# 推荐方式：进入工程目录后打开当前目录。
#
#   cd /path/to/your/cpp-project
#   nvim .
#
# 或直接打开工程目录：
#
#   nvim /path/to/your/cpp-project
#
# 预期布局：
#
#   左侧：neo-tree 项目文件树
#   中间：编辑区
#   右侧：aerial 当前文件代码大纲
#
# 注意：右侧代码大纲依赖当前 buffer 的 LSP 或 treesitter 符号。打开一个
# .c/.cpp/.h/.hpp 文件，并等待 clangd attach 后，代码大纲会更完整。
#
# 常用快捷键：
#
#   <leader>e   切换左侧文件树
#   <leader>o   切换右侧代码大纲
#   gd          跳转定义
#   gD          跳转声明
#   gi          跳转实现
#   gr          查找引用
#   gt          跳转类型定义
#   K           查看悬浮文档
#   <leader>rn  重命名符号
#   <leader>ca  Code Action
#   <leader>ff  查找文件
#   <leader>fg  全文搜索
#   <leader>dS  工作区诊断
#   <leader>ds  当前 buffer 诊断
#
# 四、如何让 clangd 自动索引当前 C/C++ 工程符号
#
# Neovim 本身不负责 C/C++ 工程级索引，真正负责索引的是 clangd。
# 本脚本生成的配置已经启用了 clangd 后台索引：
#
#   clangd --background-index
#
# 但 clangd 要想准确理解整个工程，必须知道每个源文件的真实编译参数，
# 包括 include 路径、宏定义、C/C++ 标准、编译选项等。最重要的是在工程
# 根目录生成 compile_commands.json。
#
# 1. CMake 工程推荐方式
#
#   cd /path/to/your/cpp-project
#   cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
#   ln -sf build/compile_commands.json compile_commands.json
#   nvim .
#
# 2. Makefile 或普通构建系统
#
#   cd /path/to/your/cpp-project
#   bear -- make
#   nvim .
#
# 如果系统没有 bear，可安装：
#
#   sudo apt install bear
#
# 其他发行版可用对应包管理器安装 bear。
#
# 3. 使用 .clangd 指定编译数据库目录
#
# 如果 compile_commands.json 放在 build 目录，不想创建软链接，也可以在
# 工程根目录创建 .clangd：
#
#   CompileFlags:
#     CompilationDatabase: build
#
# 4. 确认 clangd 是否已连接当前文件
#
# 在 Neovim 中执行：
#
#   :LspInfo
#
# 如果看到 clangd attached 到当前 C/C++ buffer，说明 LSP 正在工作。
# 第一次打开大工程时，后台索引可能需要等待一段时间。
#
# 五、常见注意事项
#
# 1. 没有 compile_commands.json 时，clangd 仍可能提供部分补全和跳转，
#    但跨文件跳转、宏、include 路径、模板诊断可能不准确。
#
# 2. 如果打开头文件时符号不完整，通常也是因为缺少或不正确的
#    compile_commands.json。
#
# 3. 如果修改了 CMake 配置或编译选项，请重新生成 compile_commands.json，
#    然后重启 Neovim 或执行 :LspRestart。
#
# 4. 首次运行本脚本后，插件和 treesitter parser 可能需要下载。若网络失败，
#    可稍后在 Neovim 中执行：
#
#      :Lazy sync
#      :TSUpdate
#      :Mason
#
# 5. 本脚本会备份旧配置和 runtime 目录，再写入新的自包含 C/C++ IDE 配置。
#    如只想重写配置、不安装依赖和插件，可执行：
#
#      bash ~/setup-nvim-cpp.sh --write-only
#
# -----------------------------------------------------------------------------
