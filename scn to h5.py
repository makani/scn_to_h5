# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# .scn to .h5 recursive converter
# -------------------------------
# 
# Set this script loose in a folder hierarchy and watch it go! The folder-hierarchy will be recreated in the "scn.h5" file at the top level, while the scan files will become labeled tables in the new h5 file. I haven't tested this, but I'm pretty sure that if you moved that file around between folders with this script it will append all the new data.
# 
# **pyTables Installation Instructions**
# 
# On ubuntu you can install it via apt-get:
# 
#     sudo apt-get install python-tables
# 
# Now you can run this script!
# 
# **Preamble and Row Description**
# 
# The first part of this script imports the required functions and modules, along with setting up the structures that will be needed by the recursive directory exploration. For each row of data, we have:
# 
# - Range gate (4 bit integer)
# - Doppler velocity (32 bit float)
# - Intensity (could be represented as a 16 bit fixed point number, losing the 1e-4 and 1e-5 decimal places)
# - Ray time (represent as 64 bit unix time or 16-bit milliseconds since the hour)
#     - note that the hour is represented in the group structure, although I'm unsure of how to pull it out
# - azimuth (16 bit integer or 32 bit float to allow fractional degrees)
# - elevation (as azimuth)
# - pitch (16 bit fixed-point with no loss of accuracy or 32-bit float)
# - roll (as pitch)
# 
# Our overall row size, therefore could be: most conveniently 260 bits / losslessly but a little annoyingly 180 bits / or at a minimum 132 bits.
# 
# I choose to go with the most convenient, 260 bits/row representation.

# <codecell>

from tables import *
from re import split, compile
from time import mktime
import subprocess
import os

class Point(IsDescription):
    '''A single observed point from a wind profiler's sensing ray.'''
    range_gate  = UInt8Col()   # Unsigned short integer
    doppler = Float32Col()     # float  (single-precision)
    intensity = Float32Col()
    ray_time = Time64Col()     # Unix 64bit time
    az = Float32Col()
    el = Float32Col()
    pitch = Float32Col()
    roll = Float32Col()

# Open our h5 file in "w"rite mode
filename = "scn.h5"
h5file = openFile(filename, mode = "w", title = "Recursive scan")

# <codecell>

def addG(path):
    '''Adds G's to group names in the path to get proper python variables.'''
    re = compile('/')
    return re.sub('/G', path)[:-1]

def scanFolder(path, group=None):
    '''Recursively travels down a folder hierarchy,
                snatching up any .scns it may find.'''
    local_files = os.listdir(path)
    for filename in local_files:
        if os.path.isdir(path+filename) and filename[0] != '.':
            # If it's a directory, create a new group for it and dive in!
            gpath = addG(path[1:])
            group = h5file.createGroup(gpath, 'G'+filename)
            scanFolder(path+filename+'/', group)
        elif '.scn' in filename:
            # If it's an scn file, it's time to make a table.
            # The table's name will be the filename,
            # plus a T on the front and minus the file extension
            table = h5file.createTable(group, 'T'+filename[:-4], Point)
            point = table.row
            
            with open(path+filename) as scnfile:
                for line in scnfile:
                    # Seperate the values
                    row = split(r'\t', line)
                    try: 
                        point['range_gate'] = int(row[0])
                        point['doppler'] = float(row[1])
                        point['intensity'] = float(row[2])
                        point['az'] = float(row[4])
                        point['el'] = float(row[5])
                        point['pitch'] = float(row[6])
                        point['roll'] = float(row[7])
                        
                        # Separate the elements of the time-string,
                        #   turn into Unix time, then add the ms back
                        t = split(r'[.]', row[3])
                        t_struct = split(r'[- :]', t[0]) + [0, 1, 0]
                        t_struct = [int(n) for n in t_struct]
                        point['ray_time'] = mktime(t_struct) + float(t[1])*1e-3
                        
                        point.append()
                    except ValueError:
                        # If we're in the first few rows, the first token is not an integer.
                        # That's OK.
                        pass
                table.flush()

# <codecell>

# Alright, let's run this thing!
path = './'
scanFolder(path)
# Close (and flush) the file
h5file.close()

