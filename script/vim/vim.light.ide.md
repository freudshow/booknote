# <center>**under ubuntu 18.04**</center>

## **install git**

```shell
    sudo apt install -y git curl wget
```

## **download plugins**

```shell
    mkdir ~/vim_plugins
    cd ~/vim_plugins
    git clone https://github.com/tpope/vim-pathogen.git #manages plugins
    git clone https://github.com/vim-syntastic/syntastic.git #check grammer errors
    git clone https://github.com/jiangmiao/auto-pairs.git #auto complete braces
    git clone https://github.com/scrooloose/nerdcommenter.git #comment helper
    git clone https://github.com/garbas/vim-snipmate.git
    git clone https://github.com/scrooloose/nerdtree.git
    git clone https://github.com/ervandew/supertab.git
```

### **nerdcommenter 用法(摘自互联网)**
- \cc 注释当前行和选中行
- \cn 貌似和 \cc一样。。
- \c<空格> 如果被选区域有部分被注释，则对被选区域执行取消注释操作其- 它情况执行反转注释操作
- \cm 对被选区域用一对注释符进行注释，前面的注释对每一行都会添加释
- \ci 执行反转注释操作，选中区域注释部分取消注释，非注释部分添加释
- \cs 添加性感的注释，代码开头介绍部分通常使用该注释
- \cy 添加注释，并复制被添加注释的部分
- \c$ 注释当前光标到改行结尾的内容
- \cA 跳转到该行结尾添加注释，并进入编辑模式
- \ca 转换注释的方式，比如： //和//
- \cl \cb 左对齐和左右对其，左右对其主要针对//
- \cu 取消注释

### **NERDTree用法(摘自互联网)**
#### 文件相关操作
- o : 在光标所在的上一个窗口打开文件，并将光标置于新打开的窗口
- go : 预览文件，光标停留在NERDTree窗口中
- t : 在新标签中打开文件并激活
- gt : 在新标签打开文件，光标留在NERDTree窗口中
- i : 水平分割打开文件
- gi : 水平分割预览
- s : 垂直分割打开文件
- gs : 垂直分割预览
#### 目录树相关操作
- o : 展开/关闭目录
- O : 递归展开目录。慎用，如果目录层级多，打开会很慢
- x : 关闭父目录
- C : 切换光标所在目录为根目录
- u : 切换目录树的根目录为上层目录
- U : 切换目录树的根目录为上层目录，并保持旧的目录树的状态
- r : 刷新当前目录
- R : 刷新当前根目录(这个在新加入文件后会用到）
- cd : 切换vim工作目录为光标所在目录(命令模式下:pwd可查看当前工目- 录）
#### 快捷键
- ctrl + w + w 光标自动在左右窗口切换
- ctrl + w + l 光标 移动到右侧窗口
- ctrl + w + h 光标移动到左侧窗口
- ctrl + w + r 切换NERDTree窗口位置(左或右）
- 或
- ctrl+w+(↑ 、↓ 、← 、→)

## **install taglist**

```shell
    wget https://www.vim.org/scripts/download_script.php?src_id=19574 -O taglist.zip
    unzip -d taglist taglist.zip
```

### **install details**
1. Download the taglist.zip file and unzip the files to the HOME/.vim or the 
    `$HOME/vimfiles` or the `$VIM/vimfiles` directory. After his step, you should 
    have the following two files (the directory structure hould be preserved):  
plugin/taglist.vim - main taglist plugin file
doc/taglist.txt    - documentation (help) file 
   Refer to the |add-plugin|, |add-global-plugin| and |untimepath| Vim 
   help pages for more details about installing Vim lugins. 
1. Change to the $HOME/.vim/doc or $HOME/vimfiles/doc or VIM/vimfiles/doc 
    directory, start Vim and run the ":helptags ." command o process the 
    taglist help file. Without this step, you cannot jump o the taglist help 
    topics. 
1. If the exuberant ctags utility is not present in your ATH, then set the 
    Tlist_Ctags_Cmd variable to point to the location of he exuberant ctags 
    utility (not to the directory) in the .vimrc file. 
1. If you are running a terminal/console version of Vim and he terminal 
    doesn't support changing the window width then set the 
    'Tlist_Inc_Winwidth' variable to 0 in the .vimrc file. 
1. Restart Vim. 
1. You can now use the ":TlistToggle" command to open/close he taglist 
    window. You can use the ":help taglist" command to get ore information 
    about using the taglist plugin.

## **install omnicppcomplete**

```shell
wget https://www.vim.org/scripts/download_script.php?src_id=7722 -O omnicppcomplete.zip
unzip -d omnicppcomplete omnicppcomplete.zip
```

## **install cpp_src**

```shell
wget https://www.vim.org/scripts/download_script.php?src_id=9178 -O cpp_src.tar.bz2
```
### install details
1. extact and build tags
   ```shell
   tar xjvf cpp_src.tar.bz2 
   cd cpp_src
   ctags -R --sort=yes --c++-kinds=+p --fields=+iaS --extra=+q --language-force=C++ 
    mv tags cpp #or whatever 
    ```
1. In Vim: 
set tags+=/my/path/to/tags/cpp 


## **install apps**
sudo apt-get install vim-addon-mw-utils vim-tlib ctags cscope -y

## **install plugins**

```
mkdir -p ~/.vim/bundle
cp -r vim-pathogen/autoload/ ~/.vim/
cp -r syntastic/ ~/.vim/bundle/
cp -r auto-pairs/ ~/.vim/bundle/
cp -r nerdcommenter/ ~/.vim/bundle/
cp -r vim-snipmate/ ~/.vim/bundle/snipMate
cp -r taglist/ ~/.vim/bundle/
mkdir -p ~/.vim/tags
cp cpp_src/tags ~/.vim/tags/
```

## **vimrc**

```vimrc
"设置 cpp_src/tags 文件的路径
set tags+=~/.vim/tags/cpp_src/tags
set modelines=0
"设置更好的删除
set backspace=2
syntax on "语法高亮
"用浅色高亮当前行
autocmd InsertLeave * se nocul
autocmd InsertEnter * se cul
set smartindent "智能对齐
set autoindent "自动对齐
set confirm "在处理未保存或只读文件的时候，弹出确认框
set tabstop=4 "tab键的宽度
set softtabstop=4
set shiftwidth=4 "统一缩进为4
set expandtab "不要用空格替代制表符
set number "显示行号
set history=50  "历史纪录数
set hlsearch
set incsearch "搜素高亮,搜索逐渐高亮
set gdefault "行内替换
set encoding=utf-8
set fileencodings=utf-8,ucs-bom,shift-jis,gb18030,gbk,gb2312,cp936,utf-16,big5,euc-jp,latin1 "编码设置
set guifont=Menlo:h16:cANSI "设置字体
set langmenu=zn_CN.UTF-8
set helplang=cn  "语言设置
set ruler "在编辑过程中，在右下角显示光标位置的状态行
set laststatus=1  "总是显示状态行
set showcmd "在状态行显示目前所执行的命令，未完成的指令片段也会显示出来
set scrolloff=3 "光标移动到buffer的顶部和底部时保持3行的距离
set showmatch "高亮显示对应的括号
set matchtime=5 "对应括号高亮时间(单位是十分之一秒)
set autowrite "在切换buffer时自动保存当前文件
set wildmenu  "增强模式中的命令行自动完成操作
set linespace=2 "字符间插入的像素行数目
set whichwrap=b,s,<,>,[,] "开启normal 或visual模式下的backspace键空格键，左右方向键,insert或replace模式下的左方向键，右方向键的跳行功能
filetype plugin indent on "分为三部分命令:file on,file plugin on,file indent on 分别是自动识别文件类型, 用用文件类型脚本,使用缩进定义文件
set foldenable  "允许折叠
set cursorline "突出显示当前行
set magic  "设置魔术？神马东东
set ignorecase "搜索忽略大小写
filetype on "打开文件类型检测功能
set background=dark
set t_Co=256   "256色
set mouse=v  "允许鼠标
"===============================
execute pathogen#infect()
syntax on
filetype plugin indent on
filetype plugin on
"启动vim显示nerdtree
autocmd VimEnter * NERDTree
" 按下 ctrl+b 显示/隐藏 NERDTree
 map  <C-b> :NERDTreeToggle<CR>
" 将 NERDTree 的窗口设置在 vim 窗口的右侧（默认为左侧）
 let NERDTreeWinPos="left"
"设置 NERDTree 窗口宽度
 let NERDTreeWinSize=30
"这个设置 ctags 的路径，如果是 apt-get install 安装的，省略
" let Tlist_Ctags_Cmd = ...
let Tlist_Show_One_File=1    "只展示一个文件的taglist
let Tlist_Exit_OnlyWindow=1  " 当taglist是最后以个窗口时自动退出
let Tlist_Use_Right_Window=1 " 在右边显示taglist窗口
let Tlist_Sort_Type="name"   " tag按名字排序
let Tlist_Auto_Open=1  "自动打开 taglist
"让当前不被编辑的文件的方法列表自动折叠起来
let Tlist_File_Fold_Auto_Close=1
"按Ctrl+M键显示/隐藏Taglist
map <C-m> :TlistToggle<CR>
autocmd VimEnter * TlistToggle
"只有安装了supertab插件才管用
"let g:SuperTabMappingBackward= "<tab>"
"let g:SuperTabMappingForward = "c-tab"
let OmniCpp_NamespaceSearch = 1
let OmniCpp_GlobalScopeSearch = 1
let OmniCpp_ShowAccess = 1
let OmniCpp_ShowPrototypeInAbbr = 1 " 显示函数参数列表
let OmniCpp_MayCompleteDot = 1   " 输入 .  后自动补全
let OmniCpp_MayCompleteArrow = 1 " 输入 -> 后自动补全
let OmniCpp_MayCompleteScope = 1 " 输入 :: 后自动补全
let OmniCpp_DefaultNamespaces = ["std", "_GLIBCXX_STD"]
set completeopt=menuone,menu,longest
"================================

```