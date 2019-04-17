# `hexo` 安装与使用

> 主要参考程序羊的[手把手教你从0开始搭建自己的个人博客 |无坑版视频教程| hexo](https://www.bilibili.com/video/av44544186)

## `hexo` 安装

### 安装 `nodejs`

去nodejs的官网下载[安装包](https://nodejs.org/dist/v10.15.3/node-v10.15.3-linux-x64.tar.xz), 本文书写时的长期支持版本时10.15.13. 下载后直接解压出来即可.

假设安装包解压到了`~/node-v10.15.3-linux-x64`目录下, 那么将 `~/node-v10.15.3-linux-x64/bin` 添加到 `$PATH` 环境变量中:

```bash
    echo "export PATH=$PATH:/home/dev/soft/node-v10.15.3-linux-x64/bin">>~/.profile
    . ~/.profile
```

nodejs安装完成, 可以通过命令查看当前的nodejs版本:

```bash
    node -v
```

### 安装 `cnpm`

接着就开始安装`cnpm`:

```bash
    npm install -g cnpm --registry=https://registry.npm.taobao.org
    # 查看cnpm版本
    cnpm -v
```

几分钟后, `cnpm` 就安装到了上面 `npm` 的安装目录中.

### 安装 `hexo`

运行下面的命令安装 `hexo`

```bash
    cnpm -g install hexo-cli
    # 查看hexo版本
    hexo -v
```

## 建立blog


### 本地blog

新建一个目录用于存放博客, 叫 `blog` 好了:

```bash
    # 新建博客目录
    mkdir -p ~/blog
    cd ~/blog
    # 用hexo初始化
    hexo init
    # 查看样板blog
    hexo s
    # 新建blog
    hexo new "blog test"
    # 编辑好 位于 source/_posts/blog-test.md的文件后, 清理并生成
    hexo clean
    hexo g
```

### 推送到github

为方便起见, 以下用 `$blog` 指代博客的根目录

- 远端仓库建立, 参考github新建blog的相关文档, 或搜索引擎搜索, 很多这类的文章.
- 安装hexo git插件

```bash
    cnpm install --save hexo-deployer-git
```

- 修改blog配置, 在文件 `$blog/_config.yml` 中搜索 `# Deployment` 字段, 修改为

```hexo
    # Deployment
    ## Docs: https://hexo.io/docs/deployment.html
    deploy:
    type: git
    repo: git@github.com:eomerc/eomerc.github.io.git
    branch: master
```

- 推送到 `github`

```bash
    hexo d
```

### 安装 `yilia` 主题

```bash
    cd $blog
    git clone https://github.com/litten/hexo-theme-yilia.git themes/yilia
```

修改blog配置, 在文件 `$blog/_config.yml` 中搜索 `# theme` 字段, 修改为

```hexo
    # Extensions
    ## Plugins: https://hexo.io/plugins/
    ## Themes: https://hexo.io/themes/
    theme: yilia
```

```bash
    # 清理, 重新生成, 本地服务启动, 部署到远端
    hexo clean
    hexo g
    hexo s
    hexo d
```