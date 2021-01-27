# 简易TTU/分支LTU嵌入式升级程序

## 简易TTU升级程序设计

### 原来的升级流程概述

1. 片内flash的划分: 512K空间, 0x8000000开始, 120K为正常的app程序空间; 紧接着的250K左右, 为Fatfs空间; 紧接着20K, 为boot程序空间; 剩下的空间, 0x8023000~0x8080000, 为放置升级程序的空间.

2. 升级过程开始后, app将升级文件放入Fatfs中; 当升级文件下发完毕, 就将Fatfs中的升级包复制到flash后面的裸空间中, 关闭终端和外设, 然后跳转到boot程序.

3. boot程序将flash开始的app擦除, 将flash后面的裸空间中的升级包复制到app空间中, 重启芯片.

4. 重启后, 芯片就直接加载了升级后的程序.

### 知识点

#### 跳转前的程序栈顶指针比较

BootLoader跳转程序时有这样的判断`if(((*(uint32_t *)app_addr)&0x2FFE0000) == 0x20000000)`什么意思？
0x20000000是SRAM的首地址，为什么要`*(uint32_t *)app_addr`获得APP栈顶地址的内容，然后与上0x2FFE0000？

你说的这个应该是stm32的芯片，而且是128 Kbytes 的 SRAM，主流STM32芯片的SRAM地址2113范围都是从 0x2000 0000处开始

好，答案来了

- 128 Kbytes的SRAM 地址范围是 0x2000 0000  --0x2001 FFFF;

- 堆栈指针(SP) 必须在 0x2000 0000 -- 0x2001 FFFF 这块Region，这很好理解对吧，因为SRAM就在这嘛，只要SP位于这块Region即可。

- 所以 SP & 0x2FFE 0000 == 0x2000 0000，不去管SP的bit16 - 0，只检查bit27-17。

- 假如是 64 Kbytes 的 RAM，地址Region为 0x2000 0000 -- 0x2000 FFFF，那么此时应该这样写  SP & 0x2FFF 0000 == 0x2000 0000。当然，写成 SP & 0x2FFE 0000 也能执行，只是会带来隐患，这种Bug很讨厌的，因为不好发现。

#### 内部flash操作

#### boot mode

- `stm32f103zet6`有2个boot引脚, `boot0`和`boot1`, 见数据手册

#### spi操作

#### fatfs配置

- 需要配置 `ffconfig.h`, $#define _VOLUMES 2$, 配置有几个卷, 这里配置成2, 一个是内部flash, 一个是外部`W25Q64BV`.
- 需要实现`diskio.c`, 其中有5个函数: `disk_initialize()`-初始化外设, `disk_status()`-获取设备状态, `disk_read()`-读取数据, `disk_write()`-写入数据, `disk_ioctl()`-获取分区大小, 扇区大小等信息
- `diskio.c`, 用宏定义规定每种外设的索引号, $#define Stm_flash 0$, $#define SPI_FLASH  1$
- `disk_read()`与`disk_write()`, 都会将外部`W25Q64BV`的最开始的2M区域留出来, 作为备用区域

#### iap程序要点
