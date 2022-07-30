# C language related

## typeof keyword

$typeof$ 关键字是 GCC 为C语言扩展的, 用于推导一个表达式的数据类型.  
如:

```C

#include <stdio.h>
#include <stdlib.h>

#define MAX(x, y)   ({\
                        typeof(x) _x = x;\
                        typeof(y) _y = y;\
                        _x > _y ? _x : _y;\
                    })

#define auto_max(x,y) ({\
                        __auto_type _x = x;\
                        __auto_type _y = y;\
                        _x > _y ? _x : _y;\
                    })

float foo(float a)
{
    return a;
}

int main(void)
{
    int a = 5, b = 8;
    float c = 9.4;

    printf("max of a, b: %d\n", MAX(a,b));
    printf("max of a, c: %d\n", MAX(a,c));
    printf("max of a, c: %d\n", auto_max(a,c));
    typeof(foo(4.5)) d = 8.9;
    printf("d: %f\n", d);
    return 0;
}

```

运行结果:
>`$`gcc typeof.c
`$`./a.out
max of a, b: 8
max of a, c: 1814155280
max of a, c: 1814155280
d: 8.900000

更复杂的用法见[GCC使用手册](https://gcc.gnu.org/onlinedocs/gcc-5.3.0/gcc/Typeof.html)

## 数组的越界访问 BUG

1. 场景描述:  在 1376.2-2013 报文中, 有一个1字节的序列号, 用来使异步传输过程中的上下帧保持一个一一对应关系. 由于是1个字节, 无符号整型, 所以这个序列号的取值范围在 0~255 之间, 共256个元素.
      我在程序中设定了一个数组, 用来记录每一帧报文中的重要信息, 代码如下:

      ``` C
            #include <limits.h>
      
            typedef struct {
                uint8   taskid;
                uint16  items;
                .
                .
                .
            }  info3762_s;
      
            static info3762_s  info3762_table[UCHAR_MAX];//全局表, 用来记录发送报文中的重要信息, 以便对应答的报文进行拆解和存储
      
      ```

2. BUG描述: 当程序在运行时, 总是发现当报文在序列号 255 时, 信息表 info3762_table 中的元素都是0!  后来查出来,  是因为信息表 info3762_table[255]  这个元素根本不存在!
3. 问题解决:

    ```C
        static info3762_s  info3762_table[UCHAR_MAX];//UCHAR_MAX在arm-none-linux-gnueabi-gcc中的定义为 255, 所以数组info3762_table只有255个合法的元素, 根本不是期望的 256个元素
    
        info3762_table[256];//当把 info3762_table 定义为255个元素时,  info3762_table[256]是可以正确访问的,  不论是在上位机还是下位机, 这不得不说是一个陷阱.   之前我一直以为C语言有越界访问的控制, 现在看来就算有, 也并不完全可靠!
        static info3762_s  info3762_table[UCHAR_MAX+1];//重新把信息表定义为256个!!!
    ```

## `!` 运算符

`!` 是单目逻辑运算符, 将非0数转换成0, 将0转换成1:

```c
printf("%d, %d, %d\n",!(1111), !(0), !(-1));
```

输出结果:

```bash
    0, 1, 0
```

## `sizeof` 运算符

`sizeof` 运算符是编译时求值参考`K&R` C 的120页, `C provides a compile-time unary operator called sizeof that can be used to compute the size of any object`

## `NaN`, `INFINITY`

`math.h`中定义了`float`类型的几个特殊值:

```C
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <math.h>

int main()
{
    unsigned char *p = NULL;
    float f = 0.0;

    p = (unsigned char *)&f;
    f=INFINITY;
    printf("%f, 0x%02X%02X%02X%02X\n", f, p[3],p[2],p[1],p[0]);

    f=NAN;
    printf("%f, 0x%02X%02X%02X%02X\n", f, p[3],p[2],p[1],p[0]);

    return 0;
}

```

>输出:

```bash
inf, 0x7F800000 //0111 1111 1000 0000 0000 0000 0000 0000
nan, 0x7FC00000 //0111 1111 1100 0000 0000 0000 0000 0000
```

与`IEEE 754`规定的特殊值格式一致, 所以程序在启动时, 为了将`float`类型的数据标记为无效, 可以用到`NaN`, `INFINITY`这两个宏定义

## 匹配C语言函数名

参考:　[利用正则表达式匹配C语言函数名](https://www.cnblogs.com/Summerio/p/13940959.html)

```C
(static\s*){0,1}\w{1,}\s{1,}\w{1,}\s*\([\s\w\*,]*\)[^;]
```

## undefined reference to `dlopen`, `dlerror`, `dlsym`, `dlsym`, `dlsym`, `dlclose`

添加头文件`#include <dlfcn.h>`, 链接器添加链接库文件`-ldl`即可
