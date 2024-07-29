# astrocom
Python package to communicate with amateur astronomical hardware.

* Sky-Watcher equatorial mount (work in progress)
* ZWO guiding camera (to be done)
* ZWO imaging camera (to be done)

### Installation

##### Clone the repository to your computer

```
git clone https://github.com/rfetick/astrocom.git
```

##### Add the library to your python search path

First open the `bashrc` file with any text editor
```
gedit ~/.bashrc
```
and then add the following lines to setup the `pythonpath`
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
INFO :: __init__ :: Initialize SynScan on /dev/ttyUSB0

===================================
Welcome to the ASTROCOM command line.
Type help or ? to list commands.
===================================

(astrocom) help
    init                  Initialize motors
    status                Print status and position of motors
    time                  Print current time
    goto [axis] [degree]  Define goto position on an axis
    start [axis]          Start moving on one or both axis
    stop [axis]           Stop moving on one or both axis
    mode [axis] [forward backward fast slow goto track]  Define axis motion mode
    exit                  Exit the command line interpreter
(astrocom) init
Speed: 15.0416 °/h
RA : 12:36:20      STOP  TRACK  FORWARD  SLOW
DEC: 00°00'00"     STOP  TRACK  FORWARD  SLOW
(astrocom) goto 1 10
RA : 12:36:49      STOP   GOTO  FORWARD  SLOW
DEC: 00°00'00"     STOP  TRACK  FORWARD  SLOW
(astrocom) start 1
(astrocom) status
RA : 11:57:08      STOP  TRACK  FORWARD  SLOW
DEC: 00°00'00"     STOP  TRACK  FORWARD  SLOW
(astrocom) exit
INFO :: __del__ :: Motors have been stopped
INFO :: __del__ :: Port has been closed
```

### References

[https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf](https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf)

