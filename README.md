.scn to .h5 recursive converter
-------------------------------

Set this script loose in a folder hierarchy and watch it go! The folder-hierarchy will be recreated in the "scn.h5" file at the top level, while the scan files will become labeled tables in the new h5 file. I haven't tested this, but I'm pretty sure that if you moved that file around between folders with this script it will append all the new data.

**pyTables Installation Instructions**

On ubuntu you can install it via apt-get:

    sudo apt-get install python-tables

Now you can run this script!

**Preamble and Row Description**

The first part of this script imports the required functions and modules, along with setting up the structures that will be needed by the recursive directory exploration. For each row of data, we have:

- Range gate (4 bit integer)
- Doppler velocity (32 bit float)
- Intensity (could be represented as a 16 bit fixed point number, losing the 1e-4 and 1e-5 decimal places)
- Ray time (represent as 64 bit unix time or 16-bit milliseconds since the hour)
    - note that the hour is represented in the group structure, although I'm unsure of how to pull it out
- azimuth (16 bit integer or 32 bit float to allow fractional degrees)
- elevation (as azimuth)
- pitch (16 bit fixed-point with no loss of accuracy or 32-bit float)
- roll (as pitch)

Our overall row size, therefore could be: most conveniently 260 bits / losslessly but a little annoyingly 180 bits / or at a minimum 132 bits.

I choose to go with the most convenient, 260 bits/row representation.
