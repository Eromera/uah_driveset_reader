# UAH-DriveSet Reader Tool
This code is a public tool to read data from the UAH-DriveSet that can be downloaded [HERE](http://www.robesafe.uah.es/personal/eduardo.romera/uah-driveset/)

![](/screenshot.png)

## Publications

If you use this software in your research, please cite our publications:

Romera, Eduardo, Luis M. Bergasa, and Roberto Arroyo. **"Need data for driver behaviour analysis? Presenting the public UAH-DriveSet."** In Intelligent Transportation Systems (ITSC), 2016 IEEE 19th International Conference on, pp. 387-392. IEEE, 2016.

Romera, Eduardo, Luis M. Bergasa, and Roberto Arroyo. **"A real-time multi-scale vehicle detection and tracking approach for smartphones."** In Intelligent Transportation Systems (ITSC), 2015 IEEE 18th International Conference on, pp. 1298-1303. IEEE, 2015.


## Installation of dependencies

This tool is developed in [Python 3](https://www.python.org/downloads/) so you need to have it installed in order to run it  (Python 2 should be also compatible with minor code tweaks, although we cannot guarantee as I haven't fully debugged it).

The code imports the following libraries: numpy, matplotlib, imageio and pyqt5. 
You can install them by using ["pip"](https://pip.pypa.io/en/stable/installing/) command from python in a terminal (Linux users: you might need to use sudo depending on your filesystem permissions): 

```
pip install numpy matplotlib==2.2.5 imageio==2.4.1 pyqt5
``` 

NOTE (Changed on June 4th 2021): I have added the matplotlib==2.2.5 and imageio==2.4.1 versions because using the new versions of these libraries results in 2 errors that are due to function deprecations (imageio when loading the video, and matplotlib when plotting the data). If you install these specific versions you will avoid the error, although these errors can be solved by updating just a few lines on the code with a suitable function replacement. Sorry for the trouble! I will update these lines and push the modifications when I find time to do it. 

## Usage

Execute the code with python: `python driveset_reader.py` or `python3 driveset_reader.py`

## License

This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License, which allows for personal and research use only. For a commercial license please contact the authors. You can view a license summary here: http://creativecommons.org/licenses/by-nc/4.0/

