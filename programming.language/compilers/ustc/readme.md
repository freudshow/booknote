# </center>**中科大《编译原理》视频学习**</center>
<center>视频作者 华保健</center>

## 词法分析

### 有限状态自动机

以下内容摘抄自 《Engineering a compiler》
有限状态自动机 $(finite\space automata)$ 是一个五元组:  $(S, \Sigma, \delta, s_0, S_A)$, 其中: 
- $S$: 有限的状态的集合, 包括一个错误状态 $s_e$.
- $\Sigma$: 字母表, 也就是做状态转移时读入的字符集.
- $\delta(s, c)$: 状态转移函数, 它将 $\forall s \in S$ 和 $\forall c \in \Sigma$ 映射为 $S$ 中的一个状态. 对于状态 $s_i$ 的输入 $c$, 有限状态自动机 $FA$ 做状态转移: $s_i \stackrel{c}{\rightarrow} \delta(s_i,c)$.
- $s_0$: $s_0 \in S$, 是一个指定的开始状态.
- $S_A$: $S_A \subseteq S$, 接受状态的集合. 在状态转移图中, $\forall s_a \in S_A$ 任意一个接受状态以双圆圈的形式出现.

### 正则表达式

### DFA

### NFA

### 正则表达式转化为NFA

### NFA转化为DFA

### DFA的最小化-Hopcroft算法