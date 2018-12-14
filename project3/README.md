# Project 3: High Throughput Web Crawler

**Note:** Programs run in python 3

The project is split into 2 parts:
- mcrawl1.py
- mcrawl2.py

Both versions allow the user to set:

- [-n] max number of threads, default is 1

- [-h] hostname of HTTP server, no default value

- [-p] port number, default is 80

- [-f] directory to save the crawled files, **Note:** By default the crawler
will save the downloaded files into your current directory although
it is highly recommended that the user **does not** use the default
setting here. Furthermore, **if the specified directory does not exist**
the program will try to create the specified directory for you. Finally,
in order to make the testing of this crawler cleaner, the program will
**remove** any files that are currently in the user specified directory.
Thus, after finishing running only the crawled files from the last run
will be in the directory.

**Differences between the programs:** There is only 1 major difference
between the two programs. mcrawl1.py uses *only 1 cookie* even if the
user wants to use multiple threads. Each thread still uses the same
cookie. On the other hand, mcrawl2.py will give each thread its own
cookie.

## Quickstart

Example commands to use and run the program:

Using different cookies for each thread
```
python mcrawl2.py -n 5 -h eychtipi.cs.uchicago.edu -p 80 -f tmp/
```

Using the same cookie for all threads
```
python mcrawl2.py -n 5 -h eychtipi.cs.uchicago.edu -p 80 -f tmp/
```

## Implementation Details

**mcrawl1**

Multiple threads are used to crawl through a website and download each
file. A single cookie is shared across all threads. A global array is
shared across all of the threads to keep track of the state of each
thread. Threads return back to the main process when it observes that no
threads are currently actively processing links and the link queue is
empty. Every time a 402 error is encountered the program will drop the
currently globally shared cookie and get a new one. In between retrieving
links the threads will sleep for between 1-2 seconds in order to prevent
multiple threads rapidly making requests at the same time.

**mcrawl2**

Multiple processes are used to crawl through a website and download each
file where each thread is responsible for its own cookie. When a process
encounters a 402 error the cookie is abandoned and the process gets a
new cookie. Processes are used instead of threads here in an attempt
to speed up execution time as threads in python do not truly run in
parallel although this crawler uses very little CPU so we see little to
no speedup in using processes over threads. Similar to mcrawl1, all
processes will sleep between 1-2 seconds in between retrieving files to
prevent processes from rapidly making requests at the same time.
