# <center>**Linux System Programming**</center>

## ALTERNATIVE I/O MODELS
**《the Linux Programming Interface》Chapter 63**

### Level-Triggered and Edge-Triggered Notification
- 电平触发([Level-Triggered](https://en.wikipedia.org/wiki/Interrupt#Level-triggered)): 是在高或低电平保持的时间内触发, 
- 边沿触发([Edge-triggered](https://en.wikipedia.org/wiki/Interrupt#Edge-triggered)): 是由高到低或由低到高这一瞬间触发

### The ***select()*** System Call
The ***select()*** system call blocks until one or more of a set of file descriptors becomes
ready.  

```C
    #include <sys/time.h> /* For portability */
    #include <sys/select.h>

    int select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds,
    struct timeval *timeout);

    Returns number of ready file descriptors, 0 on timeout, or –1 on error

```
#### **arguments**
The ***nfds***, ***readfds***, ***writefds***, and ***exceptfds*** arguments specify the file descriptors that
***select()*** is to monitor. The timeout argument can be used to set an upper limit on the
time for which ***select()*** will block. 

- ***readfds*** is the set of file descriptors to be tested to see if input is possible;
- ***writefds*** is the set of file descriptors to be tested to see if output is possible; and
- ***exceptfds*** is the set of file descriptors to be tested to see if an exceptional condition has occurred.

#### ***fd_set***

```C
/* The fd_set member is required to be an array of longs.  */
typedef long int __fd_mask;

/* Number of descriptors that can fit in an `fd_set'.  */
#define __FD_SETSIZE		1024

/* Some versions of <linux/posix_types.h> define this macros.  */
#undef	__NFDBITS
/* It's easier to assume 8-bit bytes than to get CHAR_BIT.  */
#define __NFDBITS	(8 * (int) sizeof (__fd_mask))
#define	__FD_ELT(d)	((d) / __NFDBITS)
#define	__FD_MASK(d)	((__fd_mask) (1UL << ((d) % __NFDBITS)))

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

- ***FD_ZERO()*** : initializes the set pointed to by fdset to be empty.
- ***FD_SET()*** : adds the file descriptor fd to the set pointed to by fdset.
- ***FD_CLR()*** : removes the file descriptor fd from the set pointed to by fdset.
- ***FD_ISSET()*** :  returns true if the file descriptor fd is a member of the set pointed to
by fdset.

### The ***epoll()*** API
The epoll API is Linux-specific, and is new in Linux 2.6.
The central data structure of the ***epoll*** API is an ***epoll*** instance, which is referred
to via an open file descriptor. This file descriptor is not used for I/O. Instead, it is a
handle for kernel data structures that serve two purposes:  
- recording a list of file descriptors that this process has declared an interest in
monitoring—the interest list; and
- maintaining a list of file descriptors that are ready for I/O—the ready list.

The ***epoll*** API consists of three system calls:  
- The ***epoll_create()*** system call creates an epoll instance and returns a file descriptor
referring to the instance.
1356 Chapter 63
- The ***epoll_ctl()*** system call manipulates the interest list associated with an epoll
instance. Using epoll_ctl(), we can add a new file descriptor to the list, remove
an existing descriptor from the list, and modify the mask that determines
which events are to be monitored for a descriptor.
- The ***epoll_wait()*** system call returns items from the ready list associated with an
epoll instance.

#### ***epoll_create()***

```C
    #include <sys/epoll.h>
    
    int epoll_create(int size);
        Returns file descriptor on success, or –1 on error
```