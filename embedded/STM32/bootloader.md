# bootloader升级程序设计

## 空间划分

1. 内部flash划分

   1. 空间大小: 内部flash空间512K, 划分为256页, 每页大小2K
   1. 地址映射: 内部flash起始地址0x0800 0000, 结束地址0x0807 FFFF
   1. 划分给bootloader的大小为32K, 即0x8000, 所以其起始地址应设置为 $0x0807\  FFFF- 0x8000 = 0x0807\ 7FFF$
   1. 划分给app的大小为 $512K - 32K = 480K = 0x7\ 8000$, 起始地址为 0x0800 0000

1. 片外flash划分

   1. $W25Q64BV$的8M芯片, 分为32,768个页(page), 每页256字节; 每16页为1个扇区(sector), 每8或16个扇区为1个块(block)
   1. 外部flash使用 $W25Q64BV: 64M-bit$ 的芯片, 存储空间共8M Byte, 使用$SPI$总线与$MCU$通信
   1. 由于app的大小不可能超过480K, 则在外部flash的起始空间(以前的程序将文件系统分配到了外部flash的高6M区间内, 低2M空闲)分配512K空间即可, 剩下的32K空间留作余量, 为后期加上其他信息, 如升级文件的大小, 其实地址等信息做准备

## 简易ttu软件

1. 去掉片内flash的文件系统, 在`ffconfig.h`中, 定义

    ```C
    #define _VOLUMES 1
    ```

    这样, 在文件`file.c`定义的`FATFS fs[_VOLUMES];`就只有1个文件系统了.

1. bootloader程序的起始地址的宏定义

    ```C
    #define  UpdateProgramAppAddr      0x801e000
    ```

    改为

    ```C
    #define  UpdateProgramAppAddr      0x08077FFF
    ```

1. `jump_iap()`中的栈顶指针判断语句

    ```C
    if (((*(__IO uint32_t *)UpdateProgramAppAddr) & 0x2FFE0000) == 0x20000000)
    ```

    应改为

    ```C
    if (((*(__IO uint32_t *)UpdateProgramAppAddr) & 0x2FFF0000) == 0x20000000)
    ```

    因为STM32F103ZET6的片内`SRAM`大小是64KByte, 即`SRAM`的地址区间是`0x20000000~0x2000FFFF`, 如果`bootloader`的栈顶指针落在这个区间内, 它的高16位的数据肯定是`0x2000`, 所以只需比较其高16位是否为`0x2000`即可; 而如果`bootloader`程序起始段的栈顶指针的值在`SRAM`地址范围之外, 比如`0x2001xxxx`, 则

    ```C
    ( (0x2001xxxx & 0x2FFE0000) == 0x20000000 ) = true
    ```

    比较值也为true, 所以就有出现bug的风险. 经查证, 值`0x2FFE0000`是针对片内`SRAM`为128K(地址范围`0x20000000~0x2001FFFF`)的产品而言的.

1. 升级包`ltudev.bin`下装完毕后, 将文件系统中的升级包复制到 $W25Q64BV$ 的起始部分, 同时跳转到地址`UpdateProgramAppAddr`
1. 应用app将升级包`ltudev.bin`向`RAW`区复制时, 最好要关闭`RTX`操作系统的调度(此时应闪烁运行灯, 提示用户正在升级), 一次性将升级包复制完成, 尽力保证升级包的完整性, 避免一帧一帧(因为进行`SPI`)的复制, 出现问题
1. 复制到$W25Q64BV$的`RAW`区时, 先使用函数`SPI_FLASH_SectorErase()`擦除目标区域, 再用函数`SPI_FLASH_BufferWrite()`写入数据

## bootloader软件

1. 现有`SPI`程序的梳理
   1. `SPI`文件系统程序采用分层设计
      1. 最顶层的是文件系统的初始化, 读, 写等函数, 如`f_mkfs()`, `f_mount()`, `f_open()`等
      1. 第2层的函数在`spi_flash.c`模块中, `SPI_FLASH_Init()`, `SPI_FLASH_SectorErase()`, `SPI_FLASH_BufferRead()`, `SPI_FLASH_BufferWrite()`等, 这些函数被`diskio.c`调用
      1. 第3层的函数在`spi_core.c`模块中, 负责跟`RTX`操作系统相关的操作, 比如`互斥`, `信号量`的`初始化`, `申请`, `释放`等; 读/写`SPI`设备时的锁操作, bootloader完全可以去掉这一层
      1. 第4层的函数在`spi_hw.c`模块中, `stm32_spi_bus_xfer()`负责数据的收/发, `stm32_spi_gpio_init`负责总线的初始化
1. 现有`SPI`程序的移植
   1. 结构体
      1. `struct spi_dev_message`, 用于数据的发送/接受

         ```C
         struct spi_dev_message
         {
            const void *send_buf;          //发送缓冲区
            void *recv_buf;                //接受缓冲区
            int length;                    //长度
            unsigned char cs_take    : 1;  //片选
            unsigned char cs_release : 1;  //片选
         };
         ```

      2. `spi_bus_device`, 用于`SPI`总线相关操作

      ```C
      struct spi_bus_device
      {
         int (*spi_bus_xfer)(struct spi_dev_device *spi_bus,struct spi_dev_message *msg); //数据收/发函数指针
         _SPI_MUX_SEM_t      spi_mux;                                                     //SPI总线操作信号量, 每条SPI总线都对应一个信号量, 由于bootloader是裸程序, 没有操作系统, 这个成员可以去掉
         void *spi_phy;                                                                   //SPI控制器, 对应的实际结构体是CMSIS库中的(SPI_TypeDef *)
         unsigned char data_width;                                                        //数据宽度
      };
      ```

      1. `spi_dev_device`, 用于`SPI`设备的抽象操作

         ```C
         struct spi_dev_device
         {
            int InitFlag;                            //设备是否被初始化
            void (*spi_cs)(unsigned char state);     //片选操作的函数指针
            struct spi_bus_device *spi_bus;          //SPI设备对应的SPI总线
         };
         ```

   2. 头文件
      1. `spi_core.h`, 定义了上述3各结构体; 定义了SPI的4种模式; `spi_core.c`中定义了数组`SpiModeSet`, 这些都要一并移植, 除此之外的其他函数/结构定义不需要移植
      2. `spi_hw.h`, 定义了SPI时钟, 引脚, 等宏; SPI发送/接受函数, 初始化函数等, 这些一并移植
      3. `spi_flash.h`, 定义了`W25Q64`相关的总线设置, 命令, 引脚, 操作函数等, 一并移植
