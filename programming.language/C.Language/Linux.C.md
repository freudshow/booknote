# `<center>`**Linux System Programming** `</center>`

[TOC]

## ALTERNATIVE I/O MODELS

`《the Linux Programming Interface》 Chapter 63`

### Level-Triggered and Edge-Triggered Notification

- 电平触发([Level-Triggered](https://en.wikipedia.org/wiki/Interrupt#Level-triggered)): 是在高或低电平保持的时间内触发,
- 边沿触发([Edge-triggered](https://en.wikipedia.org/wiki/Interrupt#Edge-triggered)): 是由高到低或由低到高这一瞬间触发

### The **_select()_** System Call

The **_select()_** system call blocks until one or more of a set of file descriptors becomes
ready.

```C
    #include <sys/time.h> /* For portability */
    #include <sys/select.h>

    int select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds,
    struct timeval *timeout);

    Returns number of ready file descriptors, 0 on timeout, or –1 on error
```

#### **arguments**

The **_nfds_**, **_readfds_**, **_writefds_**, and **_exceptfds_** arguments specify the file descriptors that
**_select()_** is to monitor. The timeout argument can be used to set an upper limit on the
time for which **_select()_** will block.

- **_readfds_** is the set of file descriptors to be tested to see if input is possible;
- **_writefds_** is the set of file descriptors to be tested to see if output is possible; and
- **_exceptfds_** is the set of file descriptors to be tested to see if an exceptional condition has occurred.

#### **_fd_set_**

```C
/* The fd_set member is required to be an array of longs.  */
typedef long int __fd_mask;

/* Number of descriptors that can fit in an `fd_set'.  */
#define __FD_SETSIZE        1024

/* Some versions of <linux/posix_types.h> define this macros.  */
#undef    __NFDBITS
/* It's easier to assume 8-bit bytes than to get CHAR_BIT.  */
#define __NFDBITS    (8 * (int) sizeof (__fd_mask))
#define    __FD_ELT(d)    ((d) / __NFDBITS)
#define    __FD_MASK(d)    ((__fd_mask) (1UL << ((d) % __NFDBITS)))

/* fd_set for select and pselect.  */
typedef struct
  {
    /* XPG4.2 requires this member name.  Otherwise avoid the name
       from the global namespace.  */
    __fd_mask fds_bits[__FD_SETSIZE / __NFDBITS];
# define __FDS_BITS(set) ((set)->fds_bits)
  } fd_set;
```

four macros to manipulate fd_set:

```C
#include <sys/select.h>
void FD_ZERO(fd_set *fdset);
void FD_SET(int fd, fd_set *fdset);
void FD_CLR(int fd, fd_set *fdset);
int FD_ISSET(int fd, fd_set *fdset);
    Returns true (1) if fd is in fdset, or false (0) otherwise
```

- **_FD_ZERO()_** : initializes the set pointed to by fdset to be empty.
- **_FD_SET()_** : adds the file descriptor fd to the set pointed to by fdset.
- **_FD_CLR()_** : removes the file descriptor fd from the set pointed to by fdset.
- **_FD_ISSET()_** : returns true if the file descriptor fd is a member of the set pointed to
  by fdset.

### The **_epoll()_** API

The epoll API is Linux-specific, and is new in Linux 2.6.
The central data structure of the **_epoll_** API is an **_epoll_** instance, which is referred
to via an open file descriptor. This file descriptor is not used for I/O. Instead, it is a
handle for kernel data structures that serve two purposes:

- recording a list of file descriptors that this process has declared an interest in
  monitoring—the interest list; and
- maintaining a list of file descriptors that are ready for I/O—the ready list.

The **_epoll_** API consists of three system calls:

- The **_epoll_create()_** system call creates an epoll instance and returns a file descriptor
  referring to the instance.
  1356 Chapter 63
- The **_epoll_ctl()_** system call manipulates the interest list associated with an epoll
  instance. Using epoll_ctl(), we can add a new file descriptor to the list, remove
  an existing descriptor from the list, and modify the mask that determines
  which events are to be monitored for a descriptor.
- The **_epoll_wait()_** system call returns items from the ready list associated with an
  epoll instance.

#### **_epoll_create()_**

```C
    #include <sys/epoll.h>

    int epoll_create(int size);
        Returns file descriptor on success, or –1 on error
```

**_epoll_create()_** creats an **_epoll_** Instance, and returns a file descriptor referring to the new
**_epoll_** instance. This file descriptor is used to refer to the **_epoll_** instance in other **_epoll_**
system calls. When the file descriptor is no longer required, it should be closed in
the usual way, using **_close()_** .

#### **_epoll_ctl()_**

```C
    #include <sys/epoll.h>

    int epoll_ctl(int epfd, int op, int fd, struct epoll_event *ev);
        Returns 0 on success, or –1 on error
```

**_epoll_ctl()_** modifying the **_epoll_** Interest List.
The **_fd_** argument identifies which of the file descriptors in the interest list is to have
its settings modified. This argument can be a file descriptor for a **_pipe_**, **_FIFO_**,
**_socket_**, **_POSIX message queue_**, **_inotify instance_**, **_terminal_**, **_device_**, or even another **_epoll_**
descriptor (i.e., we can build a kind of hierarchy of monitored descriptors). However,
`<u>` **_fd_** **can’t** be a file descriptor for a **regular file** or a **directory** `</u>` (the error **_EPERM_** results `<u>`means operation not permitted `</u>`).

The **_op_** argument specifies the operation to be performed, and has one of the
following values:

- **_EPOLL_CTL_ADD_**Add the file descriptor fd to the interest list for epfd. The set of events that
  we are interested in monitoring for fd is specified in the buffer pointed to
  by ev, as described below. If we attempt to add a file descriptor that is
  already in the interest list, epoll_ctl() fails with the error EEXIST.
- **_EPOLL_CTL_MOD_**Modify the events setting for the file descriptor fd, using the information
  specified in the buffer pointed to by ev. If we attempt to modify the settings of a file descriptor that is not in the interest list for epfd, epoll_ctl() fails
  with the error ENOENT.
- **_EPOLL_CTL_DEL_**
  Remove the file descriptor fd from the interest list for epfd. The ev argument is ignored for this operation. If we attempt to remove a file descriptor
  that is not in the interest list for epfd, epoll_ctl() fails with the error ENOENT.
  Closing a file descriptor automatically removes it from all of the epoll interest
  lists of which it is a member.

#### **_epoll_wait()_**

Waiting for Events: epoll_wait()
The epoll_wait() system call returns information about ready file descriptors from
the epoll instance referred to by the file descriptor epfd. A single epoll_wait() call can
return information about multiple ready file descriptors.

```C
    #include <sys/epoll.h>

    int epoll_wait(int epfd, struct epoll_event *evlist, int maxevents, int timeout);
        Returns number of ready file descriptors, 0 on timeout, or –1 on error
```

The information about ready file descriptors is returned in the array of **_epoll_event_**
structures pointed to by **_evlist_** . The **_evlist_** array is allocated by the caller, and the number of elements
it contains is specified in **_maxevents_** .

#### steps to use **_epoll()_**

1. Create an epoll instance q.

2. Open each of the files named on the command line for input w and add the
   resulting file descriptor to the interest list of the epoll instance e, specifying the
   set of events to be monitored as EPOLLIN.

3. Execute a loop r that calls epoll_wait() t to monitor the interest list of the epoll
   instance and handles the returned events from each call. Note the following
   points about this loop:

   1. After the epoll_wait() call, the program checks for an EINTR return y, which
      may occur if the program was stopped by a signal in the middle of the
      epoll_wait() call and then resumed by SIGCONT. (Refer to Section 21.5.) If this
      occurs, the program restarts the epoll_wait() call.
   2. It the epoll_wait() call was successful, the program uses a further loop to
      check each of the ready items in evlist u. For each item in evlist, the program checks the events field for the presence of not just EPOLLIN i, but also
      EPOLLHUP and EPOLLERR o. These latter events can occur if the other end of a
      FIFO was closed or a terminal hangup occurred. If EPOLLIN was returned,
      then the program reads some input from the corresponding file descriptor
      and displays it on standard output. Otherwise, if either EPOLLHUP or EPOLLERR
      occurred, the program closes the corresponding file descriptor a and decrements the counter of open files (numOpenFds).
   3. The loop terminates when all open file descriptors have been closed (i.e.,
      when numOpenFds equals 0).

   example code:

```C
/*************************************************************************\
*                  Copyright (C) Michael Kerrisk, 2017.                   *
 *                                                                         *
 * This program is free software. You may use, modify, and redistribute it *
 * under the terms of the GNU General Public License as published by the   *
 * Free Software Foundation, either version 3 or (at your option) any      *
 * later version. This program is distributed without any warranty.  See   *
 * the file COPYING.gpl-v3 for details.                                    *
 \*************************************************************************/

/* Listing 63-5 */

/* epoll_input.c

 Example of the use of the Linux epoll API.

 Usage: epoll_input file...

 This program opens all of the files named in its command-line arguments
 and monitors the resulting file descriptors for input events.

 This program is Linux (2.6 and later) specific.
 */
#include <sys/select.h>
#include <sys/epoll.h>
#include <fcntl.h>
#include "tlpi_hdr.h"

#define MAX_BUF     1000        /* Maximum bytes fetched by a single read() */
#define MAX_EVENTS     5        /* Maximum number of events to be returned from
                                   a single epoll_wait() call */

int main(int argc, char *argv[])
{
    int epfd, ready, fd, s, j, numOpenFds;
    struct epoll_event ev;
    struct epoll_event evlist[MAX_EVENTS];
    char buf[MAX_BUF];

    fprintf(stderr, "sizeof __fd_mask: %ld, sizeof fd_set: %ld, __NFDBITS: %d, __FD_SETSIZE: %d\n",
        sizeof(__fd_mask), sizeof(fd_set), __NFDBITS, __FD_SETSIZE);

    if (argc < 2 || strcmp(argv[1], "--help") == 0)
        usageErr("%s file...\n", argv[0]);

    epfd = epoll_create(argc - 1);
    if (epfd == -1)
        errExit("epoll_create");

    /* Open each file on command line, and add it to the "interest
     list" for the epoll instance */

    for (j = 1; j < argc; j++) {
        fd = open(argv[j], O_RDONLY);
        if (fd == -1)
            errExit("open");
        printf("Opened \"%s\" on fd %d\n", argv[j], fd);

        ev.events = EPOLLIN; /* Only interested in input events */
        ev.data.fd = fd;
        if (epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1)
            errExit("[%s][%d]epoll_ctl", __FILE__,__LINE__);
    }

    numOpenFds = argc - 1;

    while (numOpenFds > 0) {

        /* Fetch up to MAX_EVENTS items from the ready list of the
         epoll instance */

        printf("About to epoll_wait()\n");
        ready = epoll_wait(epfd, evlist, MAX_EVENTS, -1);
        if (ready == -1) {
            if (errno == EINTR)
                continue; /* Restart if interrupted by signal */
            else
                errExit("epoll_wait");
        }

        printf("Ready: %d\n", ready);

        /* Deal with returned list of events */

        for (j = 0; j < ready; j++) {
            printf("  fd=%d; events: %s%s%s\n", evlist[j].data.fd,
                    (evlist[j].events & EPOLLIN) ? "EPOLLIN " : "",
                    (evlist[j].events & EPOLLHUP) ? "EPOLLHUP " : "",
                    (evlist[j].events & EPOLLERR) ? "EPOLLERR " : "");

            if (evlist[j].events & EPOLLIN) {
                s = read(evlist[j].data.fd, buf, MAX_BUF);
                if (s == -1)
                    errExit("read");
                printf("    read %d bytes: %.*s\n", s, s, buf);

            } else if (evlist[j].events & (EPOLLHUP | EPOLLERR)) {

                /* After the epoll_wait(), EPOLLIN and EPOLLHUP may both have
                 been set. But we'll only get here, and thus close the file
                 descriptor, if EPOLLIN was not set. This ensures that all
                 outstanding input (possibly more than MAX_BUF bytes) is
                 consumed (by further loop iterations) before the file
                 descriptor is closed. */

                printf("    closing fd %d\n", evlist[j].data.fd);
                if (close(evlist[j].data.fd) == -1)
                    errExit("close");
                numOpenFds--;
            }
        }
    }

    printf("All file descriptors closed; bye\n");
    exit(EXIT_SUCCESS);
}
```

#### implementation of **_epoll()_**

In Linux Kernel 4.19, **_epoll_** locates in "linux-4.19/fs/eventpoll.c".**_epoll_** uses Red-Black Tree to store **_fd_list_**

- [Red-Black Tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Red-Black Tree | Set 1](https://www.geeksforgeeks.org/red-black-tree-set-1-introduction-2/)
- [Red-Black Tree Visualization](https://www.cs.usfca.edu/~galles/visualization/RedBlack.html)
- [自己动手实现 Epoll](http://blog.51cto.com/wangbojing/2090885)

## FILE IO

### `read()`

by default, a read() from a terminal reads characters only
up to the next newline (\n) character.

## `SYSTEM V` IPC

### `semaphore`

System V semaphores are rendered unusually complex by the fact that they are allocated in groups called semaphore sets. The number of semaphores in a set is specified when the set is created using the semget() system call. While it is common to operate on a single semaphore at a time, the semop() system call allows us to atomically perform a group of operations on multiple semaphores in the same set.

The general steps for using a System V semaphore are the following:

- Create or open a semaphore set using semget().
- Initialize the semaphores in the set using the semctl() SETVAL or SETALL operation. (Only one process should do this.)
- Perform operations on semaphore values using semop(). The processes using the semaphore typically use these operations to indicate acquisition and release of a shared resource.
- When all processes have finished using the semaphore set, remove the set using the semctl() IPC_RMID operation. (Only one process should do this.)

#### `semget()`

The semget() system call creates a new semaphore set or obtains the identifier of an existing set.

```c
#include <sys/types.h> /* For portability */
#include <sys/sem.h>

int semget(key_t key, int nsems, int semflg);
            Returns semaphore set identifier on success, or –1 on error
```

The `key` argument is a key generated using one of the methods described in Section 45.2 (i.e., usually the value IPC_PRIVATE or a key returned by ftok()).

If we are using semget() to create a new semaphore set, then `nsems` specifies the number of semaphores in that set, and must be greater than 0. If we are using semget() to obtain the identifier of an existing set, then `nsems` must be less than or equal to the size of the set (or the error EINVAL results). It is not possible to change the number of semaphores in an existing set.

The `semflg` argument is a bit mask specifying the permissions to be placed on a new semaphore set or checked against an existing set. These permissions are specified in the same manner as for files (Table 15-4, on page 295). In addition, zero or more of the following flags can be ORed (|) in semflg to control the operation of semget():

```C
    IPC_CREAT
        If no semaphore set with the specified key exists, create a new set.

    IPC_EXCL
        If IPC_CREAT was also specified, and a semaphore set with the specified key already exists, fail with the error EEXIST.
```

### `shared memory`

In order to use a shared memory segment, we typically perform the following steps:

- Call shmget() to create a new shared memory segment or obtain the identifier of an existing segment (i.e., one created by another process). This call returns a shared memory identifier for use in later calls.
- Use shmat() to attach the shared memory segment; that is, make the segment part of the virtual memory of the calling process.
- At this point, the shared memory segment can be treated just like any other memory available to the program. In order to refer to the shared memory, the program uses the addr value returned by the shmat() call, which is a pointer to the start of the shared memory segment in the process’s virtual address space.
- Call shmdt() to detach the shared memory segment. After this call, the process can no longer refer to the shared memory. This step is optional, and happens automatically on process termination.
- Call shmctl() to delete the shared memory segment. The segment will be
  destroyed only after all currently attached processes have detached it. Only one process needs to perform this step.

## Shared Libraries

### summary

- standard locations: `/lib`, `/usr/lib`, `/usr/local/lib`
- **`ldconfig`** is used to refresh shared library `/etc/ld.so.cache`.
- `/etc/ld.so.conf` indicates where shared library locate.
- Non Standard Library Locations: Add the path to `/etc/ld.so.conf` file; or add `include /etc/ld.so.conf.d/*.conf` at the end of `/etc/ld.so.conf`, then create a `.conf` file in directory `/etc/ld.so.conf.d`, then run `ldconfig` command to refresh cache

### how to create a shared library

write two files `shared.c` and `shared.h`:

```c
// shared.c
#include "shared.h"
unsigned int add(unsigned int a, unsigned int b)
{
    printf("\n Inside add()\n");
    return (a+b);
}

//shared.h
#include<stdio.h>
extern unsigned int add(unsigned int a, unsigned int b);
```

Run the following two commands to create a shared library:

```bash
#compiles the code shared.c into position independent code which is required for a shared library.
gcc -c -Wall -Werror -fPIC shared.c

#creates a shared library with name "libshared.so"
gcc -shared -o libshared.so shared.o
```

Here is the code of the program that uses the shared library function "add()":

```c
//add.c
#include<stdio.h>
#include"shared.h"
int main(void)
{
    unsigned int a = 1;
    unsigned int b = 2;
    unsigned int result = 0;

    result = add(a,b);

    printf("\n The result is [%u]\n",result);
    return 0;
}
```

run the following command:

```bash
# compiles the add.c code and tells gcc to link the code
# with shared library libshared.so (by using flag -l)
# and also tells the location of shared file(by using flag -L).
gcc -L/pathtolib/ -Wall add.c -o add -lshared

# export the path where the newly created shared library is kept
export LD_LIBRARY_PATH=/home/himanshu/practice:$LD_LIBRARY_PATH
```

run the executable

```shell
$ ./add
Inside add()
The result is [3]
```

## `Bus Error`

### 问题描述

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

### 问题分析

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

### 问题解决

1. 方法 1: 去掉`pragma pack(1)`等强制 1 字节对齐的相关语句, 经测试程序不再出现`Bus error`

2. 方法 2: 由于 1 字节对齐时, `sizeof(VNetBuf)=4124=1031*4, sizeof(VNet)=8305=2076*4+1`, 干脆在`VNet`结构体后面加 3 个字节的保留区(`unsigned char rsv[3];`)即可, 经测试程序不再出现`Bus error`

### 什么是 `Bus error`

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

```shell
gcc -ansi sigbus.c -o sigbus
```

运行程序

```shell
$ ./sigbus
Bus error
```

上述代码使用汇编指令打开 CPU 的对齐检查, 程序在执行`iptr = (int *) ++cptr;`时, 将整数类型指针`iptr`指向了 1 个奇数地址(奇数肯定不是 4 的倍数), 所以在执行`*iptr = 42;`时, 就抛出`Bus error`

### 字节对齐

下面关于字节对齐的叙述引用自[字节对齐讲解](https://blog.csdn.net/Demondai999/article/details/121640212), 这里只是部分摘抄, 完整叙述请看原文.

1.  快速理解

    1. 内存对齐原则：

    - 第一个成员的首地址为 0.
    - 每个成员的首地址是自身大小的整数倍
    - 结构体的总大小，为其成员中所含最大类型的整数倍。

    2. 什么是字节对齐？

    - 在 C 语言中，结构是一种复合数据类型，其构成元素既可以是基本数据类型（如 int、long、float 等）的变量，也可以是一些复合数据类型（如数组、结构、联合等）的数据单元。在结构中，编译器为结构的每个成员按其自然边界（alignment）分配空间。各个成员按照它们被声明的顺序在内存中顺序存储，第一个成员的地址和整个结构的地址相同。

    - 为了使 CPU 能够对变量进行快速的访问,变量的起始地址应该具有某些特性,即所谓的”对齐”. 比如 4 字节的 int 型,其起始地址应该位于 4 字节的边界上,即起始地址能够被 4 整除.

    3. 字节对齐有什么作用？

    - 字节对齐的作用不仅是便于 cpu 快速访问。
    - 同时合理的利用字节对齐可以有效地节省存储空间。
    - 对于 32 位机来说，4 字节对齐能够使 cpu 访问速度提高，比如说一个 long 类型的变量，如果跨越了 4 字节边界存储，那么 cpu 要读取两次，这样效率就低了。
    - 但是在 32 位机中使用 1 字节或者 2 字节对齐，反而会使变量访问速度降低。所以这要考虑处理器类型，另外还得考虑编译器的类型。在 vc 中默认是 4 字节对齐的，GNU gcc 是默认 4 字节对齐。
      4、 更改 C 编译器的缺省字节对齐方式

    在缺省情况下，C 编译器为每一个变量或是数据单元按其自然对界条件分配空间。一般地，可以通过下面的方法来改变缺省的对界条件：

    使用伪指令#pragma pack (n)，C 编译器将按照 n 个字节对齐。
    使用伪指令#pragma pack()，取消自定义字节对齐方式。
    另外，还有如下的一种方式：

    \_\_attribute((aligned (n)))，让所作用的结构成员对齐在 n 字节自然边界上。如果结构中有成员的长度大于 n，则按照最大成员的长度来对齐。 ·
    attribute ((packed))，取消结构在编译过程中的优化对齐，按照实际占用字节数进行对齐。
    5、 举例说明
    例 1

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

        例2

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

        这时候sizeof(struct test)的值为8。

        例3

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

       对齐的作用和原因：各个硬件平台对存储空间的处理上有很大的不同。一些平台对某些特定类型的数据只能从某些特定地址开始存取。比如有些架构的 CPU 在访问一个没有进行对齐的变量的时候会发生错误,那么在这种架构下编程必须保证字节对齐.其他平台可能没有这种情况，但是最常见的是如果不按照适合其平台要求对数据存放进行对齐，会在存取效率上带来损失。比如有些平台每次读都是从偶地址开始，如果一个 int 型（假设为 32 位系统）如果存放在偶地址开始的地方，那么一个读周期就可以读出这 32bit，而如果存放在奇地址开始的地方，就需要 2 个读周期，并对两次读出的结果的高低字节进行拼凑才能得到该 32bit 数据。显然在读取效率上下降很多。 2. 字节对齐对程序的影响:

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
       char:1(有符号无符号同)
       short:2(有符号无符号同)
       int:4(有符号无符号同)
       long:4(有符号无符号同)
       float:4 double:8
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

### 规约解析

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

2. 总结:
   1. 不使用强制 1 字节对齐时, 解析规约的报文, 必须要对每个成员单独赋值, 且要保证报文缓冲区的位置指针的正确移动.
   2. 使用强制 1 字节对齐时, 不要对结构体内成员进行取地址操作, 以避免出现`Bus error`.
