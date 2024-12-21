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
Initialize mount on /dev/ttyUSB0

===================================
Welcome to the ASTROCOM command line.
Type help or ? to list commands.
===================================

(astrocom) help
    bsc [nb]                  Print visible stars of the Bright Star Catalog
    init                      Initialize motors
    track                     Start sideral tracking
    status                    Print status and position of motors
    time                      Print current time
    ra [arcmin]               Step move along the RA axis
    dec [arcmin]              Step move along the DEC axis
    goto [hrXXXX name ra dec] Define goto position with HR number, star name or RA-DEC coord
    start [axis]              Start moving on one or both axis
    stop [axis]               Stop moving on one or both axis
    exit                      Exit the command line interpreter

(astrocom) init
INFO :: Assume looking at the celestial pole at startup
INFO :: Motors correctly initialized
AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED
RA   20:13:13  20:13:10    stop track forwrd  slow
DEC  90°00'00   0°00'00    stop track forwrd  slow

(astrocom) bsc 3
------------------------------------------------------
  HR  CONST        NAME     RA     DEC    MV   ALT  AZ
------------------------------------------------------
5340    Boo    Arcturus  14:15   19°10  -0.0   13°   W
7001    Lyr        Vega  18:36   38°47   0.0   71°   W
7557    Aql      Altair  19:50    8°52   0.8   55°   S
------------------------------------------------------

(astrocom) goto vega
INFO :: Goto correctly defined
AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED
RA   20:13:39  18:36:56    stop  goto forwrd  slow
DEC  90°00'00  38°47'01    stop  goto forwrd  slow

(astrocom) start

(astrocom) status
AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED
RA   18:37:23  18:37:23    stop track forwrd  slow
DEC  38°47'01  38°47'01    stop track bckwrd  slow

(astrocom) track
INFO :: Start tracking

(astrocom) status
AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED
RA   18:27:10  18:37:38  moving track forwrd  slow
DEC  38°47'01  38°47'01    stop track forwrd  slow

(astrocom) stop
INFO :: Motor correctly stopped

(astrocom) exit

INFO :: Motors have been stopped
INFO :: Port has been closed

```

### References

[https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf](https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf)

