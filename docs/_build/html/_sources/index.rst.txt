.. PlaneSpotting documentation master file, created by
   sphinx-quickstart on Thu Jun 27 16:15:58 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PlaneSpotting's documentation!
=========================================

PlaneSpotting is a software package written in python3 which can decode ADS-B(Automatic Dependant Survelliance Broadcast) from the output provided by dump1090 (a C based Mode-S decoder which is designed for RTL-SDR devices).


The RTL-SDR devices records at 1090 MHz and outputs a binary (.dat) file. This file is processed by dump1090 which provides us with the raw ADS-B frames from that recording in 'mlat' AVR format(ascii hexdump of the frames with the sample position).
The processed files serves as the input for this project.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   gettingstarted.rst
   modules.rst
   tutorials.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
