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
user@machine:~/Documents/astrocom $ python example/run.py 
Initialize SynScan on /dev/ttyUSB0

Welcome to the SynScan command line.
Type help or ? to list commands.

(astrocom) help

Documented commands (type help <topic>):
========================================
exit  goto  help  init  mode  start  status  stop

(astrocom) init
(astrocom) status
Tue Jul 16 22:55:00 2024
RA :    0.000°       STOP  TRACK   FORWARD  SLOW
DEC:    0.000°       STOP  TRACK   FORWARD  SLOW
```
