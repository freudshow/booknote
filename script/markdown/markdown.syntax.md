# Markdown 语法

本文请用vscode+markdown preview插件渲染查看

## 标题

在 Markdown 中, 你只需要在文本前面加上 `#`  即可, 同理、你还可以增加二级标题、三级标题、四级标题、五级标题和六级标题, 总共六级, 只需要增加 # 即可, 标题字号相应降低.例如:  

# 标题1
## 标题2
### 标题3
#### 标题4

## 列表

### 无序列表

只需要在文字前面加上 `-` 就可以了:

- 无序表
- 无序表
- 无序表
- 无序表
- 无序表

### 有序表

只需要在文字前面加上 `1.` 就可以了:

1. 有序表
2. 有序表
3. 有序表
4. 有序表

### 列表的嵌套

只要相对于上层列表缩进一次就行

1. 有序表
   1. 嵌套
   2. 嵌套
      - 嵌套
      - 嵌套
        - 嵌套
        - 嵌套
2. 有序表
3. 有序表
4. 有序表

## 区块引用

在每行的最前面加上 `>`:

>这是一个引用
>>这是一个嵌套的引用
>>>这又是一个嵌套的引用

## 代码区块

- 要在 Markdown 中建立代码区块很简单, 只要简单地缩进 4 个空格或是 1 个制表符就可以.  

这是一个普通段落：

    这是一个代码区块.

- 也可以输入3个反引号, 紧跟着语言名, 再以3个反引号结束:  

```C
int main(int argc, char* argv[])
{
    printf("hello world!\n");

    exit(0);
}
 ```

```bash
if condition
then
    command1
    command2
else
    command
fi
 ```

## 分隔线

在一行中用三个以上的星号、减号、底线来建立一个分隔线, 行内不能有其他东西. 也可以在星号或是减号中间插入空格.

* * *

***

*****

- - -

---------------------------------------

## 链接

Markdown 支持两种形式的链接语法： 行内式和参考式两种形式. 不管是哪一种, 链接文字都是用 `[方括号]` 来标记. 

要建立一个行内式的链接，只要在方块括号后面紧接着圆括号并插入网址链接即可，如果你还想要加上链接的 title 文字，只要在网址后面，用双引号把 title 文字包起来即可，例如：

This is [an example](http://example.com/"Title") inline link.

[This link](http://example.net/) has no title attribute.

如果你是要链接到同样主机的资源，你可以使用相对路径：

See my [About](/about/) page for details.

参考式的链接是在链接文字的括号后面再接上另一个方括号，而在第二个方括号里面要填入用以辨识链接的标记：

This is [an example][id1] reference-style link.  

也可以选择性地在两个方括号中间加上一个空格：

This is [an example] [id2] reference-style link.  

接着，在文件的任意处，你可以把这个标记的链接内容定义出来：  

[id1]: http://example.com/  "Optional Title Here"
[id2]: http://example.com/  "Optional Title Here"