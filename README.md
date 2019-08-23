# PlaneSpotting


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

PlaneSpotting is a software package written in python3 which can decode ADS-B(Automatic Dependant Survelliance Broadcast) from the output provided by dump1090 (a C based Mode-S decoder which is designed for RTL-SDR devices).


The RTL-SDR devices record at 1090 MHz and outputs a binary (.dat) file. This file is processed by dump1090 which provides us with the raw ADS-B frames from that recording in 'mlat' AVR format(ascii hexdump of the frames with the sample position).
The processed files serves as the input for this project.

All ADS-B frames do not contain position information in them. To be specific only frames with Downlink Format(DF) 17-18 and Type Code(TC) 9-18 carry the location as the payload. Thus, the next part of this project is
to find the location of the plane at the point when a non-position carrying frame is sent using multilateration.

Multilateration is a method by which the location of an aircraft (can be any moving object which broadcasts a signal) using  multiple ground stations and the Time Difference of Arrival(TDOA) of a signal to each ground station.

This project is a part of **Google Summer of Code 2019** program.

# Requirements

These are the mandatory libraries required:

* numpy
* argparse
* sqlite3
* gzip
* json


Installation
------------
Clone the repositiory into a folder. Currently, the program is set to handle files from 5 stations and the location coordinates are preprogrammed. You can change the coordinates in the **gs_data.json** file
present in the **planespotting** folder.

The input folder should be present in the root directory with the name **'input'**

The directory structure should be like this and the input files from each station should be stored inside these station directories.

Run the program executing ```python3 main.py ```in the command line.
The output files will be stored in the ```data``` folder (if it doesn't exists, it will be created)



### Links


| ||
| ------ | ------ |
| Documentation | [https://planespotting.readthedocs.io/en/shoumik_dev/] |
| Technical Blogs | [https://aerospaceresearch.net/?author=17] |

### Todos

 - Testing and Implementation of trilateration on known frames
 - Multilateration on unknown frames.

License
----

MIT LCIENSE
