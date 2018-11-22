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