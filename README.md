# astrocom
Python package to communicate with amateur astronomical hardware.

* Sky-Watcher equatorial mount (work in progress, successfully tested on Raspberry Pi)
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

See [https://github.com/rfetick/astrocom/wiki](https://github.com/rfetick/astrocom/wiki)
