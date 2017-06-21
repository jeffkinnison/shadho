Distributed Workers with Work Queue
===================================

SHADHO uses `Work\ Queue <ccl.cse.nd.edu/software/workqueue/>` to distribute
and manage workers. Work Queue uses a master/worker scheme to distribute parallel
tasks across a large number of computers. Connected computers (workers) do not
need to have the same hardware or operating system: the entire environment can
be different from machine to machine. As long as a computer can run the program
you want to execute, it can be a worker.

With Work Queue, the user

SHADHO runs a Work Queue master behind-the-scenes, and it

Installing Work Queue
---------------------

Work Queue is written in C and bound with

Configuring Work Queue
----------------------


Running Work Queue Workers
--------------------------
