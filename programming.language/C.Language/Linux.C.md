# <center>**Linux System Programming**</center>

[TOC]

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

 ***epoll_create()*** creats an ***epoll*** Instance, and returns a file descriptor referring to the new
***epoll*** instance. This file descriptor is used to refer to the ***epoll*** instance in other ***epoll***
system calls. When the file descriptor is no longer required, it should be closed in
the usual way, using ***close()*** . 

#### ***epoll_ctl()***

```C
    #include <sys/epoll.h>

    int epoll_ctl(int epfd, int op, int fd, struct epoll_event *ev);
        Returns 0 on success, or –1 on error
```

 ***epoll_ctl()*** modifying the ***epoll*** Interest List.  
 The ***fd*** argument identifies which of the file descriptors in the interest list is to have
its settings modified. This argument can be a file descriptor for a ***pipe***, ***FIFO***,
***socket***, ***POSIX message queue***, ***inotify instance***, ***terminal***, ***device***, or even another ***epoll***
descriptor (i.e., we can build a kind of hierarchy of monitored descriptors). However,
<u> ***fd*** **can’t** be a file descriptor for a **regular file** or a **directory** </u> (the error ***EPERM*** results <u>means operation not permitted</u>).  

The ***op*** argument specifies the operation to be performed, and has one of the
following values:  

- ***EPOLL_CTL_ADD***  
Add the file descriptor fd to the interest list for epfd. The set of events that
we are interested in monitoring for fd is specified in the buffer pointed to
by ev, as described below. If we attempt to add a file descriptor that is
already in the interest list, epoll_ctl() fails with the error EEXIST.
- ***EPOLL_CTL_MOD***  
Modify the events setting for the file descriptor fd, using the information
specified in the buffer pointed to by ev. If we attempt to modify the settings of a file descriptor that is not in the interest list for epfd, epoll_ctl() fails
with the error ENOENT.
- ***EPOLL_CTL_DEL***  
Remove the file descriptor fd from the interest list for epfd. The ev argument is ignored for this operation. If we attempt to remove a file descriptor
that is not in the interest list for epfd, epoll_ctl() fails with the error ENOENT.
Closing a file descriptor automatically removes it from all of the epoll interest
lists of which it is a member.

#### ***epoll_wait()***
 Waiting for Events: epoll_wait()
The epoll_wait() system call returns information about ready file descriptors from
the epoll instance referred to by the file descriptor epfd. A single epoll_wait() call can
return information about multiple ready file descriptors.

```C
    #include <sys/epoll.h>

    int epoll_wait(int epfd, struct epoll_event *evlist, int maxevents, int timeout);
        Returns number of ready file descriptors, 0 on timeout, or –1 on error

```
The information about ready file descriptors is returned in the array of ***epoll_event***
structures pointed to by ***evlist*** . The ***evlist*** array is allocated by the caller, and the number of elements
it contains is specified in ***maxevents*** .

#### steps to use ***epoll()***

1. Create an epoll instance q.
1. Open each of the files named on the command line for input w and add the
resulting file descriptor to the interest list of the epoll instance e, specifying the
set of events to be monitored as EPOLLIN.
1. Execute a loop r that calls epoll_wait() t to monitor the interest list of the epoll
instance and handles the returned events from each call. Note the following
points about this loop:  
    1. After the epoll_wait() call, the program checks for an EINTR return y, which
    may occur if the program was stopped by a signal in the middle of the
    epoll_wait() call and then resumed by SIGCONT. (Refer to Section 21.5.) If this
    occurs, the program restarts the epoll_wait() call.
    1. It the epoll_wait() call was successful, the program uses a further loop to
    check each of the ready items in evlist u. For each item in evlist, the program checks the events field for the presence of not just EPOLLIN i, but also
    EPOLLHUP and EPOLLERR o. These latter events can occur if the other end of a
    FIFO was closed or a terminal hangup occurred. If EPOLLIN was returned,
    then the program reads some input from the corresponding file descriptor
    and displays it on standard output. Otherwise, if either EPOLLHUP or EPOLLERR
    occurred, the program closes the corresponding file descriptor a and decrements the counter of open files (numOpenFds).
    1. The loop terminates when all open file descriptors have been closed (i.e.,
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

#### implementation of ***epoll()***

In Linux Kernel 4.19, ***epoll*** locates in "linux-4.19/fs/eventpoll.c".  
***epoll*** uses Red-Black Tree to store ***fd_list***

- [Red-Black Tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Red-Black Tree | Set 1](https://www.geeksforgeeks.org/red-black-tree-set-1-introduction-2/)
- [Red-Black Tree Visualization](https://www.cs.usfca.edu/~galles/visualization/RedBlack.html)
- [自己动手实现Epoll](http://blog.51cto.com/wangbojing/2090885)