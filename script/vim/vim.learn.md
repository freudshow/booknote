# <center>**Vim学习指南**</center>

## **源地址**

转载自: [$Vim$学习指南](https://www.linuxidc.com/Linux/2013-08/89096.htm)  
英文原版地址: [Learn Vim Progressively](http://yannesposito.com/Scratch/en/blog/Learn-Vim-Progressively/)
## **提纲**

1. 适应
1. 感觉舒适
1. 感觉很好,强壮,快速
1. 使用$vim$的高级技能

## **第一层次 - 适应**

- `i`$\rightarrow$ 插入模式. 按ESC键返回普通模式
- `x`$\rightarrow$ 删除光标所在的字符
- `:wq`$\rightarrow$ 保存退出(`:w` 保存,`:q` 退出)
- `dd`$\rightarrow$ 删除(+拷贝)当前行
- `p`$\rightarrow$ 粘贴
- `hjkl`(高度推荐)$\rightarrow$基本的光标移动$(\leftarrow\rightarrow\uparrow\downarrow)$, `hj`按行移动. 
- `:help <command>`$\rightarrow$ 显示关于`<command>`的帮助,可以使用`help`不带`<command>`获得常规帮助. 

&emsp;只有5个命令,一开始只需掌握这些,当适应了这些命令后（大概需要一天或更多的诗句）,你可以转到第二层级了.   
&emsp;但首先,稍回顾一下普通模式. 在标准编辑器里,要复制的话你需要使用**ctrl**键(**Ctrl-c**). 实际上,当你按下**ctrl**键时所有的按键的意义都改变了. 在**vim**普通模式下就像在ctrl键自动按下的情况下使用编辑器. 

## **第二层 - 爽一把**

1. 插入模式变种命令：
    - `a`$\rightarrow$ 在光标后插入
    - `o`$\rightarrow$ 在当前行之后插入新行
    - `O`$\rightarrow$ 在当前行之前插入新行
    - `cw`$\rightarrow$ 替换从光标到单词结束
1. 基本移动命令
    - `0`$\rightarrow$ 跳到第一列
    - `^`$\rightarrow$ 跳到本行第一个非空字符
    - `$`$\rightarrow$ 跳到本行末尾
    - `g_`$\rightarrow$ 跳到本行最后一个非空字符
    - `/pattern`$\rightarrow$ 搜索pattern
1. 复制/粘贴
    - `P`$\rightarrow$ 在当前位置之前粘贴,记住 p 是在当前位置之前粘贴.
    - `yy`$\rightarrow$ 复制当前行,与dd和P命令相比更简单. 
1. 取消/恢复
    - `u`$\rightarrow$ 取消
    - `<C-r>`$\rightarrow$ 恢复
1. 加载/保存/退出/修改 文件(缓存)
    - `:e <文件路径>`$\rightarrow$ 打开
    - `:w`$\rightarrow$ 保存
    - `:saveas <文件路径>`$\rightarrow$ 保存到这个文件
    - `:x,ZZ`或者`:wq`$\rightarrow$ 保存和退出 (`:x` 如果可能的话,只保存)
    - `:q!`$\rightarrow$ 退出但不保存,使用`:qa!`,即使在缓存中还有已经修改的也会退出. 
    - `:bn`(对比`:bp`)$\rightarrow$ 显示下一个(上一个)文件缓存

## **第三层次 - 更好,更强,更快**
&emsp;为达到这一步表示祝贺！现在我们可以开始这有趣的东西. 在第三层次,我们将只讨论命令,它兼容旧的vi编辑器. 

### **更好**
&emsp;让我们看看vim是怎么帮你做重复事情的. 

1. `.`(点)$\rightarrow$ 可以重复最后一个命令,
1. N<命令>会重复命令N次:
    - `2dd`$\rightarrow$ 删除2行 
    - `3p`$\rightarrow$ 粘贴3次文本
    - `100idesu [ESC]`$\rightarrow$ 插入100个`desu`
    - `.`$\rightarrow$ 紧接着上一条命令后, 又插入了100个`desu`. 
    - 3.$\rightarrow$ Will write 3 “desu” (and not 300, how clever).

### **更强**
&emsp;知道怎么有效的移动对vim是非常重要的. 请不要跳过这一节. 
1. `NG`$\rightarrow$ 定位到第N行
1. `gg`$\rightarrow$ 相当于命令`1G`, 定位到第一行
1. `G`$\rightarrow$ 定位到最后一行
1. 单词移动：
    - `w`$\rightarrow$ 定位到当前单词的开始位置,
    - `e`$\rightarrow$  定位到当前单词的最后位置. 
    - 默认情况下, 单词由字符和下划线组成. 我们称一句话是由一组被空格符号分隔的单词组成. 如果你想定位一句话,那么就用大写字符:
        - W$\rightarrow$  定位到当前句子的开始位置,
        - E$\rightarrow$  定位到当前这句话的最后位置.

>&emsp;下面是单词位置:

```

      ew                E W
      ||                | |
(name_1,<w1>vision3)<w2>; #this is a comment.

```

&emsp;现在让我们来谈谈几个非常有效率的移动：

- `%`$\rightarrow$ 直接跳转到对应的括号处, (,{,[
- `*`, `#`$\rightarrow$ 跳转到当前光标所指单词的上一个/下一个出现处

### **更快**
&emsp;还记得vi移动的重要性吗? 原因是, 大多数命令使用下面这种通用格式：

```
<开始位置><命令><结束位置>
```

&emsp;例如： `0y$`意味着  
&emsp;`0`$\rightarrow$ 跳到本行开头  
&emsp;`y`$\rightarrow$ 从这里开始复制  
&emsp;`$`$\rightarrow$ 直到本行结束  
&emsp;我们也可以使用`ye`,从当前位置复制到单词的末尾.   
&emsp;`y2/foo`会从当前位置一直复制到第二个foo出现的地方.   
&emsp;且对于y（yank, 复制, 原意为: 猛地一拉）有效的上述用法, 对于d(删除), v(visual 选择), gU(大写), gu(小写)等等命令都是有效的.   


## **第四层次 - Vim 超能量**
&emsp;使用上述的命令，你就觉得很爽了。但是下面才是杀手锏。

1. 在当前行移动:`0^$g_fFtT,;`
    - `0`$\rightarrow$ 跳到第一列
    - `^`$\rightarrow$ 跳到当前行的第一个字符
    - `$`$\rightarrow$ 跳到最后一列
    - `g_`$\rightarrow$ 跳到这行的最后一个字符
    - `fa`$\rightarrow$ 跳到这行a字母的下一个出现的地方。（对比 ; ）会查找下一个（上一个）地`方
    - `ta`$\rightarrow$ 跳到'`a`' 字符的前一个字符.
    - `3fa`$\rightarrow$ 在这行中查找'`a`' 出现的第三个位置.
    - `F` 和 `T`$\rightarrow$ 与f和t相似， 但是方向相反.
    - `dtn`$\rightarrow$ 删除所有字符, 直到后面第一个`n`之前

```
0   ^               fi tn              4fi         g_  $
|   |                |  |               |           |  |
    x = (name_1,<w1>vision3)<w2>; #this is a comment.   

```

