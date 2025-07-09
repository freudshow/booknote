start_kernel 函数是入口
oom机制及其实现
Linux lazy 机制
资源利用率的USE原则
Linux 负载与吞吐量和延迟的关系
延迟的多模分布，直方分布图
进程控制块 task_struct
Linux的深度睡眠，进程的D状态
Subreaper进程，僵尸进程的清理
Fork必须要mmu支持
进程的nice值
进程调度的cfs算法
火焰图
Perf top命令
taskset命令设置进程在哪个cpu运行
cache命中
cache伪共享
cgroup调度

内存管理：
分页机制
Buddy算法
slab内存分配
OOM打分机制
CMA分配器
smem分析pss占用，vss pss uss
sanitizer原理
文件访问的read write方式和mmap方式


LRU算法
匿名页和文件背景
zRAM swap
kswapd系统线程，回收内存

git grep async_probe

IO模型
bootchart工具分析用户态程序启动速度
io复用，epoll
C10K问题

文件系统
inode
Superblock
硬链接的本质
符号链接的本质
文件写的过程
带日志的文件系统
address space operations

调试手段
LD_PRELOAD
gcov工具
C程序的多函数名链接
编译屏障
gdb attach
gdb batch 查看coredump
gcore,强制抓coredump
gdb qemu调试kernel


vfork fork区别
memfd_create函数
memfd与sealing
Unix domain socket
lsof命令用法
dma buffer跨设备共享内存
socat侦听本机socket报文
dbus monitor进程间通信
systemd journal


多线程编程
用户态与内核态，spin_lock的区别
用户态的核内自旋很危险
优先级翻转
设置保护页的大小


Kernelshark工具
火焰图的作者，主页
Top down性能分析法


Bsp 与驱动
Dts与acpi
Driver override