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

ftp://**USER**:**PASS**@**SERVER**/**FILE**

If a log file is given, output will be written to that log, if the given log
file is '-' then the output will be printed to the screen. An example log
file can be found in the file: log
