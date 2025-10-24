# **git**

## official site

[official site](https://git-scm.com/)

## git中合并某个分支的指定文件

- 分支A_bracn和B_branch，只想将A_branch分支的某个文件f.txt合并到B_branch分支上。

```shell
    git checkout A_branch #切换到A分支；
    git checkout --patch B_branch f.txt #合并B分支上`f.txt`文件到A分支上，将B分支上 `f.txt` 文件追加补丁到A分支上 f文件。你可以接受或者拒绝补丁内容。
```

- 如果只是简单的将A_branch分支的文件f.txt copy到B_branch分支上:

```shell
    git checkout B_branch
    cd path/to/f.txt
    git checkout A_bracn  f.txt
```

## `git`报错`unsafe repository xxx is owned by someone else`解决方法

```shell
    it config --global --add safe.directory "*"
```

## `github`指定公钥

在 `~/.ssh/config` 文件中添加:

```bash
    # 针对GitHub的配置，指定使用目标密钥
    Host github.com
      HostName github.com
      User git  #替换为自己的github账户名
      IdentityFile ~/.ssh/id_ed25519_github  # 替换为你的私钥路径
      IdentitiesOnly yes  # 强制只使用指定的密钥，忽略其他密钥
```