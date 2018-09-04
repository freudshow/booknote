<center>递归函数</center>
===========
***

# 转载于云栖社区
* [递归函数（一）：开篇](https://yq.aliyun.com/articles/72770?spm=a2c4e.11153940.blogcont72768.7.1ad39fc7Fyq0sf)
* [递归函数（二）：编写递归函数的思路和技巧](https://yq.aliyun.com/articles/72769?spm=a2c4e.11153940.blogcont72770.9.5e48b9ffUrhVeC)
* [递归函数（三）：归纳原理](https://yq.aliyun.com/articles/72768?spm=a2c4e.11153940.blogcont72770.10.5e48b9ffUrhVeC)
* [递归函数（四）：全函数与计算的可终止性](https://yq.aliyun.com/articles/72783?spm=a2c4e.11153940.blogcont72770.11.5e48b9ffUrhVeC)
* [递归函数（五）：递归集与递归可枚举集](https://yq.aliyun.com/articles/72757?spm=a2c4e.11153940.blogcont72770.12.5e48b9ffUrhVeC)
* [递归函数（六）：最多有多少个程序](https://yq.aliyun.com/articles/72782?spm=a2c4e.11153940.blogcont72770.13.5e48b9ffUrhVeC)
* [递归函数（七）：不动点算子](https://yq.aliyun.com/articles/72781?spm=a2c4e.11153940.blogcont72770.14.5e48b9ffUrhVeC)
* [递归函数（八）：偏序结构](https://yq.aliyun.com/articles/72767?spm=a2c4e.11153940.blogcont72770.15.5e48b9ffUrhVeC)
* [递归函数（九）：最小不动点定理](https://yq.aliyun.com/articles/72771?spm=a2c4e.11153940.blogcont72770.16.5e48b9ffUrhVeC)

# 归纳原理

## 自然数归纳

&emsp;为证明对每一个自然数 $n$, 命题 $P(n)$ 为真, 只需要证明两件事:

1. 对于自然数 $1$, 命题 $P(1)$为真
1. 如果对于自然数 $m$, 命题 $P(m)$ 为真, 那么对于自然数 $m+1$, 命题 $P(m+1)$ 也为真

&emsp;其中, 第(1)条称为起始条件, 第(2)条称为递推条件, 或者称为归纳步骤.
第(2)条中, 为了证明 $P(m+1)$ 而假设的 $P(m)$, 称为归纳假设.

## 关系

&emsp;直观的说, 集合$A$的元素和集合$B$的元素之间的关系是一个二元性质$R$, 使得对于每个$a\in A$和$b\in B$而言, $R(a,b)$ 要么为真, 要么为假.  
&emsp;关系通常表示为一个集合, 它是笛卡尔积的子集, 即, 集合$A$和集合$B$之间的关系$R$是它们笛卡尔积的一个子集 $R\subseteq A \times B$.  
&emsp;如果序对 $(a,b)\in R$, 则认为$a$与$b$之间的关系为真, 否则认为$a$与$b$之间的关系为假. 通常关系直接描述为$R(a,b)$, 或者$aRb$, 而不用 $(a,b)\in R$.  
&emsp;除了二元关系之外, 对任何正整数 $k$, 还可以定义$k$元关系.<br>如果$A_1,\cdots,A_k$为集合, 则在$A_1,\cdots,A_k$上的$k$元关系是笛卡尔积$A_1\times \cdots \times A_k$的一个子集.  
&emsp;某个集合上的二元关系有很多性质, 例如自反性, 对称性, 反对称性, 传递性.  
1. 一个关系$R\subset A\times A$是自反的, 如果 $R(a,a)$ 对于所有的 $a \in A$ 成立;
1. 是对称的, 如果 $R(a,b)$ 就有 $R(b,a)$, 对于所有的$a,bin A$都成立;
1. 是反对称的, 如果 $R(a,b)$ 且 $R(b,a)$, 则$a,b$是同一个元素, 对于所有的 $a,b\in A$ 都成立;
1. 是传递的, 如果 $R(a,b)$ 和 $R(b,c)$ 蕴含 $R(a,c)$, 对于所有的 $a,b,c \in A$都成立.

&emsp;(注意, 反对称性不是对称性的否定.
等价关系是同时具有自反性, 对称性和传递性的关系.)  
&emsp;偏序关系是具有自反性, 反对称性和传递性的关系.
&emsp;等价关系的一个例子就是相等性, 相等性关系 $R(a,b)$ 当且仅当 $a,b$ 是同一个元素.  
&emsp;偏序关系, 例如通常的序关系 $R\subseteq N\times N$, $R(a,b)$ 当且仅当$a\leqslant b$.

## 良基关系

&emsp;集合 $A$ 上的良基关系$(well-founded$ $relation)$, 是 $A$ 上的一个二元关系 $\prec$,
如果不存在无限下降序列 $(infinite$ $descending$ $sequence)$ $(a0 \succ a1\succ a2\cdots)$.
&emsp;例如, 自然数上的关系<, 就是一个良基关系.
但是 $\leqslant$ 却不是, 因为存在一个无限下降序列 $(a0 \geqslant a1 \geqslant a2 \cdots)$.
&emsp;根据良基关系, 我们可以定义集合中的最小元, $a\in A$ 为最小元, 如果不存在 $a′ \in A$, 使得$a′ \prec a$.
&emsp;对于良基关系, 有一个等价的定义,
 $A$上的二元关系 $\prec$是良基的, 当且仅当 $A$的每一个非空子集B有最小元.

&emsp;我们可以证明一下这两种说法等价性.
要证当且仅当, 我们需要证明充分性和必要性,
1. 充分性:  
往证: $A$上的二元关系 $\prec$是良基的, 则 $A$的每一个非空子集 $B$ 有最小元.  
使用反证法, 如果 $B$ 没有最小元, 则对于每个 $a\in B$, 总可以找到 $a′\in B$, 使得 $a′ \prec a$.  
但是, 如果这样的话, 我们就可以对任何 $a\in B$, 以 $a_0$开始构造一个无限下降序列 $a_0 \succ a_1\succ a_2\cdots$,
这与 $\prec$是一个良基关系矛盾.充分性证毕.

1. 必要性:  
>往证: 如果 $A$的每一个非空子集 $B$ 都有最小元, 则 $A$上用于比较的二元关系 $\prec$是良基的.  
>由于 $A$的每一个非空子集 $B$ 都有最小元, 则不可能存在无限下降序列  $a_0 \succ a_1\succ a_2\cdots$,
因此,  $\prec$是良基的.必要性证毕.

&emsp;因此,  $A$上的二元关系 $\prec$是良基的, 当且仅当 $A$的每一个非空子集 $B$ 有最小元.  

## 良基归纳法

&emsp;设 $\prec$ 为集合 $A$ 上的良基二元关系, 并且设 $P$ 为关于 $A$中元素的某个命题,  
&emsp;如果 $P(b)$ 对于所有的 $b \prec a$ 成立, 就必然有 $P(b)$ 成立,那么 $P(a)$ 就对所有的 $a\in A$ 成立.  
&emsp;我们看到 < 确实是自然数集上的良基关系, 因此自然数归纳法只是良基归纳法的一种特例.  
&emsp;现在我们有了足够的能力来证明自然数归纳法的正确性了, 只要我们证明了良基归纳法是正确的.

&emsp;还是用反证法:  
&emsp;我们期望证明,
&emsp;前提：如果$P(b)$对于所有的$b≺a$成立, 必然有$P(a)$成立,
&emsp;结论：那么对于所有的$a\in A$, $P(a)$都成立.

&emsp;如若不然, 假设存在 $x\in A$, 使得 $P(x)$ 不成立,
&emsp;则集合 $B=\{ a\in A | \neg P(a)\}$ 非空, 因此根据良基关系的等价定义, 集合 $B$ 必有最小元 $m\prec B\subseteq A$, 而且,  $\neg P(m)$ 成立.  
&emsp;则根据前提的逆否命题, 一定存在 $b\prec m$, 使得 $\neg P(b)$ 成立,  
所以, 我们有 $b\in B$, 且 $b\prec m$, 与 $m$ 是 $B$ 的最小元矛盾.  
&emsp;证毕.  
&emsp;由此, 我们证明了良基归纳法的正确性.  
&emsp;理解良基关系和偏序关系, 是理解递归和不动点算子的第一步.

# 全函数与计算的可终止性

## 函数
### 部分函数
&emsp;集合$A,B$上的关系, 是笛卡尔积$A\times B$的一个子集.  
&emsp;而函数$f:A\rightarrow B$, 则是集合$A,B$上的一种特殊关系, 
它要求$A$中的每一个元素, 都有$B$中唯一确定的元素与之对应. 
其中, 集合$A$称为函数$f$的定义域, 集合$B$称为函数的值域.  
&emsp;函数是我们熟悉的概念, 这里只是提到了它本质上是集合上的一个关系.  
&emsp;如果$f$是从$A$到$B$的二元关系, 且$\forall a \in A$, $f(a)=\varnothing$或$\lbrace b\rbrace$, 则称$f$是从$A$到$B$的部分函数, 或$A$上的部分函数.  
&emsp;其中, 如果$f(a)=\lbrace b\rbrace$, 则称$f(a)$有定义, 记为$f(a)\downarrow$, 也称$b$为$f$在$a$点的函数值, 记为$f(a)=b$. 如果$f(a)=\varnothing$, 则称$f(a)$无定义, 记为$f(a)\uparrow$.  

### 全函数$(total$ $function)$

如果$\forall a\in A$都有$f(a)\downarrow$，则称$f$是$A$上的全函数，此时，可以记为$f:A\rightarrow B$。

>可见，我们熟悉的函数，指是全函数. 值得注意的是，部分函数的定义已经包含了我们学过的“函数”的定义, 后文中，我们提到的“函数”如果不强调它的完全性的话，都泛指部分函数。









