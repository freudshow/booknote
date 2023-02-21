# `Bus Error`

## 问题描述

今天在`arm`开发板调试互斥锁时, 遇到 `bus error`, 具体描述如下:

- 网络缓冲区结构体

  ```c
  #pragma pack(push)
  #pragma pack(1)

  //经计算, 1字节对齐时, sizeof(VNetBuf)=4124
  typedef struct              /*必须和VBuf保持一致*/
  {
      pthread_mutex_t m;/*读/写指针的互斥锁*/
      unsigned short rp;
      unsigned short wp;
      unsigned char addr[Net_BUF_SIZE];
  } VNetBuf;

  //经计算, 1字节对齐时, sizeof(VNet)=8305
  typedef struct
  {
      unsigned int  used;
      int           ifIdx;
      int           portIdx;
      int           linkNo;
      VNetBuf       rx_buf;
      VNetBuf       tx_buf;
      unsigned char rx_idle;

    TETHNET_CHANELS  tEthChanel;
    TETHNET_PORTS tEthPort;
    TETHNET_MAC tMac;
    pt_TcpServerSet ptTcpServerSet;
    unsigned char TcpClientCount;
    unsigned char TcpConnectOK;
  } VNet;

  #pragma pack(pop)
  ```

- 而程序中定义了一个缓冲区数组 `VNet g_Net[4]`, 在使用缓冲区的信号量时, `pthread_mutex_trylock(&g_Net[0].rx_buf.m)`第 0 个互斥锁可以正常使用; 但是当使用第 1 个互斥锁时 `pthread_mutex_trylock(&g_Net[1].rx_buf.m)`, 程序立即报错 `Bus error`, 出错提示 `AddressSanitizer: SEGV on unknown address 0xb22048a1`

## 问题分析

刚开始怀疑出错原因: 1. 信号量未初始化; 2. 传递的信号量地址有错. 但是经过仔细对比缓冲区的地址和检查代码后, 排除了这两种错误.

到网上查询 `Bus error`, 才知道还有可能是地址未对齐导致的. 再一次仿真调试, 查看互斥锁的地址 `&g_Net[1].rx_buf.m = 0xb22048a1`这是一个奇数, 而错误提示信息, 就是这个地址上出错了.

互斥锁的结构体定义如下

```c
typedef union
{
  struct __pthread_mutex_s
  {
    int __lock;
    unsigned int __count;
    int __owner;
    int __kind;
    unsigned int __nusers;
    __extension__ union
    {
      int __spins;
      __pthread_slist_t __list;
    };
  } __data;
  char __size[__SIZEOF_PTHREAD_MUTEX_T];//__SIZEOF_PTHREAD_MUTEX_T被定义为24
  long int __align;
} pthread_mutex_t;
```

从上述结构体的定义可以看出, 互斥锁内部的变量全部为 `int`类型(`int`类型的长度为 4 字节), 总共占据 24 字节, 所以互斥锁的地址以及其内部的变量的起始地址, 必须被放置在 4 的整数倍的地址上.

事实上, 如果不强制对结构体使用 1 字节对齐, 编译器会自动完成字节对齐, 保证每个原子变量的起始地址都被放置在其类型长度的整数倍的地址上.

> 注意: 如果在`x86`体系的个人电脑中运行 1 字节对齐的上述代码, 默认不会抛出`Bus error`. 只有在`arm`体系的开发板上运行时才会抛出`Bus error`. 原因是`x86`体系使用`CISC`复杂指令集, 默认不会进行地址总线检查; `arm`体系使用的是`RISC`精简指令集, 原子数据不能跨越一个地址总线宽度.

## 问题解决

1. 方法 1: 去掉`pragma pack(1)`等强制 1 字节对齐的相关语句, 经测试程序不再出现`Bus error`

2. 方法 2: 由于 1 字节对齐时, `sizeof(VNetBuf)=4124=1031*4, sizeof(VNet)=8305=2076*4+1`, 干脆在`VNet`结构体后面加 3 个字节的保留区(`unsigned char rsv[3];`)即可, 经测试程序不再出现`Bus error`

## 什么是 `Bus error`

维基百科给出的解释是:

> In computing, a bus error is a fault raised by hardware, notifying an operating system (OS) that a process is trying to access memory that the CPU cannot physically address: an invalid address for the address bus, hence the name. In modern use on most architectures these are much rarer than segmentation faults, which occur primarily due to memory access violations: problems in the logical address or permissions.In computing, a bus error is a fault raised by hardware, notifying an operating system (OS) that a process is trying to access memory that the CPU cannot physically address: an invalid address for the address bus, hence the name. In modern use on most architectures these are much rarer than segmentation faults, which occur primarily due to memory access violations: problems in the logical address or permissions.

翻译过来就是: 硬件抛给操作系统的错误, 软件试图访问物理上不存在的内存区域或者访问不正确的内存区域.

维基百科给出的导致`Bus error`的 3 个原因:

1. 不存在的地址: CPU 发现当前要访问的物理地址在整个计算机系统中没有对应的物理硬件, 此时 CPU 抛出异常

2. 地址不对齐: 访问原子数据时, 地址未与其类型的整数倍对应. 如`short s;`, 当`s`的起始地址被放置在`0, 2, 4, 6`等时, 不会发生`Bus error`; 但是当`s`的起始地址被放置在`1, 3, 5`等时, 就会发生`Bus error`, 原因就是`short`类型占据 2 字节, 其起始地址必须为 2 的整数倍. 再比如`int i`, 它的起始地址必须是 4 的整数倍. 而对于`char`类型, 则无所谓地址对齐.

3. 页错误: 虚拟内存页映射失败. 比如虚拟内存页丢失; 或用于分配虚拟内存的磁盘已满等.

下面是维基百科给出的演示代码:

```c
#include <stdlib.h>

int main(int argc, char **argv)
{
    int *iptr;
    char *cptr;

#if defined(__GNUC__)
# if defined(__i386__)
    /* Enable Alignment Checking on x86 */
    __asm__("pushf\norl $0x40000,(%esp)\npopf");
# elif defined(__x86_64__)
     /* Enable Alignment Checking on x86_64 */
    __asm__("pushf\norl $0x40000,(%rsp)\npopf");
# endif
#endif

    /* malloc() always provides memory which is aligned for all fundamental types */
    cptr = malloc(sizeof(int) + 1);

    /* Increment the pointer by one, making it misaligned */
    iptr = (int *) ++cptr;

    /* Dereference it as an int pointer, causing an unaligned access */
    *iptr = 42;

    /*
       Following accesses will also result in sigbus error.
       short *sptr;
       int    i;

       sptr = (short *)&i;
       // For all odd value increments, it will result in sigbus.
       sptr = (short *)(((char *)sptr) + 1);
       *sptr = 100;

    */

    return 0;
}
```

编译上述代码

```bash
gcc -ansi sigbus.c -o sigbus
```

运行程序

```bash
$ ./sigbus
Bus error
```

上述代码使用汇编指令打开 CPU 的对齐检查, 程序在执行`iptr = (int *) ++cptr;`时, 将整数类型指针`iptr`指向了 1 个奇数地址(奇数肯定不是 4 的倍数), 所以在执行`*iptr = 42;`时, 就抛出`Bus error`

## 字节对齐

下面关于字节对齐的叙述引用自[字节对齐讲解](https://blog.csdn.net/Demondai999/article/details/121640212), 这里只是部分摘抄, 完整叙述请看原文.

1. 快速理解
   1. 内存对齐原则：
      - 第一个成员的首地址为 0.
      - 每个成员的首地址是自身大小的整数倍
      - 结构体的总大小，为其成员中所含最大类型的整数倍。

   1. 什么是字节对齐？
      - 在 C 语言中，结构是一种复合数据类型，其构成元素既可以是基本数据类型（如 int、long、float 等）的变量，也可以是一些复合数据类型（如数组、结构、联合等）的数据单元。在结构中，编译器为结构的每个成员按其自然边界（alignment）分配空间。各个成员按照它们被声明的顺序在内存中顺序存储，第一个成员的地址和整个结构的地址相同。
      - 为了使 CPU 能够对变量进行快速的访问,变量的起始地址应该具有某些特性,即所谓的”对齐”. 比如 4 字节的 int 型,其起始地址应该位于 4 字节的边界上,即起始地址能够被 4 整除.

   1. 字节对齐有什么作用？
      - 字节对齐的作用不仅是便于 cpu 快速访问。
      - 同时合理的利用字节对齐可以有效地节省存储空间。
      - 对于 32 位机来说，4 字节对齐能够使 cpu 访问速度提高，比如说一个 long 类型的变量，如果跨越了 4 字节边界存储，那么 cpu 要读取两次，这样效率就低了。
      - 但是在 32 位机中使用 1 字节或者 2 字节对齐，反而会使变量访问速度降低。所以这要考虑处理器类型，另外还得考虑编译器的类型。在 vc 中默认是 4 字节对齐的，GNU gcc 是默认 4 字节对齐。

   1. 更改 C 编译器的缺省字节对齐方式
    在缺省情况下，C 编译器为每一个变量或是数据单元按其自然对界条件分配空间。一般地，可以通过下面的方法来改变缺省的对界条件：

    使用伪指令#pragma pack(n)，C 编译器将按照 n 个字节对齐。
    使用伪指令#pragma pack()，取消自定义字节对齐方式。
    另外，还有如下的一种方式：

    \_\_attribute((aligned (n)))，让所作用的结构成员对齐在 n 字节自然边界上。如果结构中有成员的长度大于 n，则按照最大成员的长度来对齐。 ·
    attribute ((packed))，取消结构在编译过程中的优化对齐，按照实际占用字节数进行对齐。

   1. 举例说明
      - 例 1

        ```c
        struct test
        {
          char x1;
          short x2;
          float x3;
          char x4;
        };
        ```

        由于编译器默认情况下会对这个struct作自然边界（有人说“自然对界”我觉得边界更顺口）对齐，结构的第一个成员x1，其偏移地址为0，占据了第1个字节。第二个成员x2为short类型，其起始地址必须2字节对界。
        因此，编译器在x2和x1之间填充了一个空字节。结构的第三个成员x3和第四个成员x4恰好落在其自然边界地址上，在它们前面不需要额外的填充字节。
        在test结构中，成员x3要求4字节对界，是该结构所有成员中要求的最大边界单元，因而test结构的自然对界条件为4字节，编译器在成员x4后面填充了3个空字节。整个结构所占据空间为12字节。

      - 例2

        ```c
        #pragma pack(1) //让编译器对这个结构作1字节对齐
        struct test
        {
          char x1;
          short x2;
          float x3;
          char x4;
        };
        #pragma pack() //取消1字节对齐，恢复为默认4字节对齐
        ```

        这时候`sizeof(struct test)`的值为8。

      - 例3

        ```c
        #define GNUC_PACKED __attribute__((packed))
        struct PACKED test
        {
          char x1;
          short x2;
          float x3;
          char x4;
        }GNUC_PACKED;
        ```

        这时候sizeof(struct test)的值仍为8。

2. 深入理解

   1. 什么是字节对齐,为什么要对齐?
       现代计算机中内存空间都是按照 byte 划分的，从理论上讲似乎对任何类型的变量的访问可以从任何地址开始。
       但实际情况是在访问特定类型变量的时候经常在特定的内存地址访问，这就需要各种类型数据按照一定的规则在空间上排列，而不是顺序的一个接一个的排放，这就是对齐。
       对齐的作用和原因：各个硬件平台对存储空间的处理上有很大的不同。一些平台对某些特定类型的数据只能从某些特定地址开始存取。比如有些架构的 CPU 在访问一个没有进行对齐的变量的时候会发生错误,那么在这种架构下编程必须保证字节对齐.其他平台可能没有这种情况，但是最常见的是如果不按照适合其平台要求对数据存放进行对齐，会在存取效率上带来损失。比如有些平台每次读都是从偶地址开始，如果一个 int 型（假设为 32 位系统）如果存放在偶地址开始的地方，那么一个读周期就可以读出这 32bit，而如果存放在奇地址开始的地方，就需要 2 个读周期，并对两次读出的结果的高低字节进行拼凑才能得到该 32bit 数据。显然在读取效率上下降很多。
   1. 字节对齐对程序的影响:

       先让我们看几个例子吧(32bit,x86 环境,gcc 编译器):

       设结构体如下定义：

       ```c
       struct A
       {
          int a;
          char b;
          short c;
       };
       struct B
       {
          char b;
          int a;
          short c;
       };
       ```

       现在已知 32 位机器上各种数据类型的长度如下:
       - char:1(有符号无符号同)
       - short:2(有符号无符号同)
       - int:4(有符号无符号同)
       - long:4(有符号无符号同)
       - float:4 double:8
       那么上面两个结构大小如何呢?
       结果是:
       sizeof(strcut A)值为 8
       sizeof(struct B)的值却是 12

       结构体 A 中包含了 4 字节长度的 int 一个，1 字节长度的 char 一个和 2 字节长度的 short 型数据一个,B 也一样;按理说 A,B 大小应该都是 7 字节。
       之所以出现上面的结果是因为编译器要对数据成员在空间上进行对齐。上面是按照编译器的默认设置进行对齐的结果,那么我们是不是可以改变编译器的这种默认对齐设置呢,当然可以.例如:

       ```c
       #pragma pack (2) /*指定按2字节对齐*/
       struct C
       {
          char b;
          int a;
          short c;
       };
       #pragma pack () /*取消指定对齐，恢复缺省对齐*/
       ```

       sizeof(struct C)值是 8。

       修改对齐值为 1：

       ```c
       #pragma pack (1) /*指定按1字节对齐*/
       struct D
       {
          char b;
          int a;
          short c;
       };
       #pragma pack () /*取消指定对齐，恢复缺省对齐*/
       ```

       sizeof(struct D)值为 7。
       后面我们再讲解#pragma pack()的作用.

## 规约解析

1. 问题分析: 在规约解析代码中, 常常使用预定义的结构体, 这个结构体往往是强制 1 字节对齐的, 以方便解析报文. 比如:
   假设在某个规约中, 定义报文头部的结构如下:

   |  68H   |  地址  |  地址  |  地址  |  地址  |  地址  |  地址  |  68H   |  CTL   | 数据域长度 |
   | :----: | :----: | :----: | :----: | :----: | :----: | :----: | :----: | :----: | :--------: |
   | 1 字节 | 1 字节 | 1 字节 | 1 字节 | 1 字节 | 1 字节 | 1 字节 | 1 字节 | 1 字节 |   4 字节   |

   定义的头部结构体如下:

   ```c
   typedef struct {
      u8 start1;   //第一个开始字
      u8 addr[6];  //逻辑地址, 小端
      u8 start2;   //第二个开始字
      u8 ctl;      //控制字
      u32 len;     //数据域的字节数, 小端
   } head645_s;
   ```

   如果此时不强制 1 字节对齐, 就必须手动对上述结构体的每个成员变量进行报文解析, 非常繁琐且易出错:

   ```c
   buff[128];
   int len = read(fd, buff, sizeof(buff));
   head645_s head;
   int pos = 0;
   head.start1 = buff[pos++];

   memcpy(head.addr, &buff[pos], sizeof(head.addr));
   pos+=sizeof(head.addr);

   head.start2 = buff[pos++];

   //如果报文中的数值是小端排列,
   //且当前平台为小端, 则可以直接memcpy;
   //否则要挨个字节解析
   memcpy(&head.len, &buff[pos], sizeof(head.len));
   pos+=sizeof(head.len);
   ```

   上面的代码中要维护一个位置变量`pos`, 记录当前解析到报文的哪个位置, 还要对每个成员变量一个个的赋值.

   而当对这个结构体强制 1 字节对齐后, 只需要 1 条语句即可:

   ```c
   #pragma pack(push)
   #pragma pack(1)
   typedef struct {
      u8 start1;   //第一个开始字
      u8 addr[6];  //逻辑地址, 小端
      u8 start2;   //第二个开始字
      u8 ctl;      //控制字
      u32 len;     //数据域的字节数, 小端
   } head645_s;
   #pragma pack(pop)

   buff[128];
   int len = read(fd, buff, sizeof(buff));
   head645_s head;
   int pos = 0;

   memcpy(&head.start1, &buff[pos], sizeof(head));
   pos+=sizeof(head);
   ```

   可以看出, 强制 1 字节对齐后, 报文的解析变得非常便利, 还不容易出错.

1. 总结:
   1. 不使用强制 1 字节对齐时, 解析规约的报文, 必须要对每个成员单独赋值, 且要保证报文缓冲区的位置指针的正确移动.
   1. 使用强制 1 字节对齐时, 不要对结构体内成员进行取地址操作, 以避免出现`Bus error`.
