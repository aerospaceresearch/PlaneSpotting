###############
Getting Started
###############




Requirements
------------
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

.. image:: /images/input1.png
    :alt: Input directory structure

The directory structure should be like this and the input files from each station should be stored inside these station directories.

Run the program executing **python3 main.py** in the command line.
The output files will be stored in the **data** folder (if it doesn't exists, it will be created)
