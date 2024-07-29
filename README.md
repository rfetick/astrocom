# astrocom
Python package to communicate with telescope mounts.

This is a work-in-progress, only Sky-Watcher mount has been implemented.

### Installation

Clone the repository to your computer.
```
git clone https://github.com/rfetick/astrocom.git
```

Add the library to your python search path. First open the `bashrc` file with
```
gedit ~/.bashrc
```
and add the following lines to setup the `pythonpath`
```
PYTHONPATH="$PYTHONPATH:<my_path_to_the_library>/astrocom"
export PYTHONPATH
```

### Usage

You can open or run the script provided in the `example` folder.
```
python example/run.py
```
It opens a command line interface to communicate with the mount.
```
user@machine:~/Documents/python/astrocom $ python example/run.py 
Initialize SynScan on /dev/ttyUSB0

Welcome to the ASTROCOM command line.
Type help or ? to list commands.

(astrocom) help

Documented commands (type help <topic>):
========================================
exit  goto  help  init  mode  start  status  stop

(astrocom) init
(astrocom) status
Thu Jul 18 11:09:56 2024
RA :    0.000°       STOP  TRACK   FORWARD  SLOW
DEC:    0.000°       STOP  TRACK   FORWARD  SLOW
(astrocom) goto 1 10
Thu Jul 18 11:10:06 2024
RA :    0.000°       STOP   GOTO   FORWARD  SLOW
DEC:    0.000°       STOP  TRACK   FORWARD  SLOW
(astrocom) start 1
(astrocom) status
Thu Jul 18 11:10:27 2024
RA :   10.000°       STOP  TRACK   FORWARD  SLOW
DEC:    0.000°       STOP  TRACK   FORWARD  SLOW
(astrocom) exit
Motors have been stopped
Port has been closed
```

### References

[https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf](https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf)

