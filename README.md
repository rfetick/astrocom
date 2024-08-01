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
    bsc [nb]              Print stars of the Bright Star Catalog
    init                  Initialize motors
    status                Print status and position of motors
    time                  Print current time
    ra [+-]               Move along the RA axis
    dec [+-]              Move along the DEC axis
    goto [hrXXXX name ra] [dec]  Define goto position with HR number, common name or RA-DEC coordinates
    start [axis]          Start moving on one or both axis
    stop [axis]           Stop moving on one or both axis
    mode [axis] [forward backward fast slow goto track]  Define axis motion mode
    exit                  Exit the command line interpreter

(astrocom) init
Assume looking at the celestial pole at startup
Speed: 15.0416 °/h
RA : 17:55:56 ( 17:55:53)    STOP TRACK FORWRD SLOW
DEC: 90°00'00 (  0°00'00)    STOP TRACK FORWRD SLOW

(astrocom) bsc 3
  HR  CONST        NAME     RA     DEC    MV   ALT  AZ
------------------------------------------------------
7001    Lyr        Vega  18:36   38°47   0.0   42°  NW
 472    Eri              01:37  -57°14   0.5    7°  SE
7557    Aql      Altair  19:50    8°52   0.8   74°  NW

(astrocom) goto vega
INFO :: do_goto :: Goto <vega>
RA : 17:56:15 ( 18:36:56)    STOP  GOTO FORWRD SLOW
DEC: 90°00'00 ( 38°47'01)    STOP  GOTO FORWRD SLOW

(astrocom) start

(astrocom) stop

(astrocom) status
RA : 02:58:07 ( 18:38:39)    STOP TRACK FORWRD SLOW
DEC: 38°47'01 ( 38°47'01)    STOP TRACK BCKWRD SLOW

(astrocom) exit

INFO :: __del__ :: Motors have been stopped
INFO :: __del__ :: Port has been closed
```

### References

[https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf](https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf)

