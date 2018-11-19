# Parallel ftp

Implementation of single threaded and multi-threaded ftp download

Single thread ftp example where USER is username and PASS is password:
```
python pftp.py -s ftp1.cs.uchicago.edu -f cs23300.txt -n USER -P PASS
```

To run multi-threaded ftp download you must give a config file specified by the
-t flag. An example config file is given called para-config-example.txt,
follow the structure given in the example file. Additional arguments such as
log file and port can still be given from the command line.
Multi-thread example:
```
python pftp.py -t para-config-example.txt
```

Structure of a single line in the config file is:

ftp://**user**:**pass**@**server**/**file**

If a log file is given, output will be written to that log, if the given log
file is '-' then the output will be printed to the screen. An example log
file can be found in the file: log

**Note on performance:** Currently you will not see a large difference in the
download speeds between single and multiple threads. This is because the
server we are testing on contains files that are quite small where
multi-threading may not beneficial and actually may hurt download speeds if
too many threads are created due to costs of creating a thread

## Design

The pftp.py file is divided into 4 sections:
- argument parser: parses the command line arguments given by the user
- error codes: each function represents a different error, will print to stderr
and then give the appropriate exit code
- socket operations: these functions reimplement recv and send so that we can
check for errors and write to log file if needed. This also includes
functions that help to open up new connections to receive data sent by the
ftp server
- ftp operations: uses the socket operations to create connections and
send/receive messages, is also responsible for putting together the data and
writing it to a file. The config file is also parsed here and checks are done
to make sure that the config file is formatted properly
