# C language related

## typeof keyword
$typeof$ 关键字是 GCC 为C语言扩展的, 用于推导一个表达式的数据类型.  
如:

```C
int main(void)
{
    int a;
    typeof(a) b = 9;//这个表达式与 "int b = 9;"是等效的
    printf("b: %d\n", b);//将输出整型9

    return 0;
}
```