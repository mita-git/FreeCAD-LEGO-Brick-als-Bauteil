"""
BrickSlopePlateODialog.py 
-- Paul Cobbaut, 2023-05-18
-- Michael Talarczyk, 2025-11-02 2026-01-03 auch mit spire
The goal is to make Lego-compatible pieces for use in 3D printer
The script generates .stl files in a directory.
"""

# The directory to export the .stl files to
export_directory = "C:\\Users\\micha\\Documents\\CAD\\FreeCAD-Brick-main\\"
#export_directory = "C:\" for Windows, not tested.

import FreeCAD
from FreeCAD import Base, Vector, Gui, Console
import Part
import Sketcher
import Mesh
import MeshPart
import time

import sys
import os.path

# get the path of the current python script
current_path = os.path.dirname(os.path.realpath(__file__))

# check if this path belongs to the PYTHONPATH variable and if not add it
if not sys.path.__contains__(str(current_path)):
    sys.path.append(str(current_path))

from BrickSlopePlateMitaLib import *

# create a FreeCAD document and Part Design body
 
doc = FreeCAD.newDocument("Lego brick generated")

def anzeigen():
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()



### Example: to create single slope bricks
### make_brick(width_in_studs, length_in_studs, height_in_plates, studded_width)
# make_brick(2, 2, 3, 1) # standard slope, bottom 2x2, top half 2x1 studs and half slope
# make_brick(2, 4, 3, 1) # standard slope, bottom 2x4, top half 2x1 studs and half slope
# make_brick(2, 6, 3, 1) # standard slope, bottom 2x6, top half 2x1 studs and half slope

# make_brick(4, 6, 9, 1) # standard slope, bottom 2x6, top half 2x1 studs and half slope by mita


#make_brick(9, 2, 3, 1) 
#make_brick(5, 9, 3, 4) 
#make_brick(4, 2, 3, 1) 
#make_brick(3, 3, 3, 1) 
#make_brick(6, 1, 3, 1) 
#make_brick(6, 3, 3, 4) 
#make_brick(4, 4, 6, 2) 


########################################################  mita ###################################################
# slope: make_brick(x Stups,y Stups,z Dicke einer Platte,wie viele Stubs in x bleiben sollen => die Ringe von unten)
# Brick Plate: make_brick(x Stups,y Stups,z Dicke einer Platte, immer x - 1 => die Ringe von unten)

## make_brick(1, 6, 3, 1, 'brick') # standard brick 1 x 6 
## anzeigen()
## 
## make_brick(2, 2, 3, 1, 'slope') # standard slope, bottom 2x2, top half 2x1 studs and half slope
## anzeigen()
## 
## make_brick(2, 2, 3, 1, 'brick') # standard brick, bottom 2x2, 
## anzeigen()
## 
## make_brick(2, 4, 3, 1, 'slope') # standard slope, bottom 2x4, top half 2x1 studs and half slope
## anzeigen()
## 
## make_brick(2, 4, 3, 1, 'brick') # standard brick, bottom 2x4,
## anzeigen()
## 
## make_brick(2, 6, 3, 1, 'slope') # standard slope, bottom 2x6, top half 2x1 studs and half slope
## anzeigen()
## 
## make_brick(2, 6, 3, 2, 'brick') # standard brick, bottom 2x6, 
## anzeigen()
##
## make_brick(4, 6, 1, 3, 'plate') # standard plate, bottom 2x6,
## anzeigen()
##  
## make_brick(2, 4, 3, 1, 'slope') # standard slope, bottom 2x4 45°
## anzeigen()
## #
## make_brick(2, 2, 3, 1, 'slope') # standard slope, bottom 2x4 45°
## anzeigen()
## #
## make_brick(3, 2, 3, 1, 'slope') # standard slope, bottom 3x2 33°
## anzeigen()
## # 
## make_brick(3, 4, 3, 1, 'slope') # standard slope, bottom 3x4 33°
## anzeigen()
# 
# 
## make_brick(2, 6, 1, 0, 'tile') # Fliese 3x4 33°
## anzeigen()
## 
## make_brick(2, 6, 3, 1, 'slope') # slope 3x6 45°
## anzeigen()
## 
## make_brick(1, 6, 3, 1, 'brick') # brick 1x6 
## anzeigen()
## 
## make_brick(2, 6, 3, 0, 'dslope') # dslope 3x4 45°
## anzeigen()
## 
## make_brick(3, 6, 3, 1, 'slope') # slope 3x6 33°
## anzeigen()
## 
## make_brick(3, 6, 3, 0, 'dslope') # dslope 3x4 ??°
## anzeigen()
## 
## make_brick(2, 6, 2, 0, 'dslope') # dslope 3x4 33°
## anzeigen()
## 
## make_brick(4, 6, 4, 0, 'dslope') # dslope 3x4 33°
## anzeigen()

# make_spire(2, 2, 3, 0, 'spire') # spire 
# anzeigen()
# 
# 
# 
# make_spire(4, 6, 3, 0, 'spire') # spire 
# anzeigen()
# 
# make_spire(4, 4, 9, 0, 'spire') # spire 
# anzeigen()

make_spire(6, 4, 9, 0, 'spire') # spire 
anzeigen()

## make_brick(4, 4, 9, 2, 'slope') # slope 
## anzeigen()
##  
## make_brick(4, 6, 9, 0, 'dslope') # dslope 
## anzeigen()
## 
## make_brick(4, 4, 9, 0, 'spire') # spire 
## anzeigen()
## 
## 
## make_brick(4, 6, 9, 0, 'spire') # spire 
## anzeigen()


## 

# make_brick(4, 4, 3, 2, 'slope')
#   
# make_brick(3, 2, 3, 1, 'slope')
# make_brick(3, 4, 3, 1, 'slope')
# 
# make_brick(2, 1, 3, 1, 'slope')
# make_brick(3, 1, 3, 1, 'slope')
# make_brick(8, 1, 9, 1, 'slope')
# make_brick(2, 2, 6, 1, 'slope')
# make_brick(2, 2, 9, 1, 'slope')
# make_brick(8, 2, 9, 2, 'slope')
# 
# make_brick(2, 8, 3, 1, 'brick')

# make_brick(x Stups,y Stups,z Diche einer Platte,wievile Stubs in x bleiben sollen)

# make_brick(7, 3, 3, 5, 'slope')
# make_brick(8, 3, 3, 5, 'slope')  
# make_brick(4, 3, 3, 2, 'slope')
# make_brick(8, 3, 3, 4, 'slope')
# make_brick(8, 3, 3, 2, 'slope')
# make_brick(8, 3, 3, 1, 'slope')
# make_brick(8, 3, 3, 0, 'slope')

# slope_3x4x3_top_1_cut_slope: Result has multiple solids: that is not currently supported.
# slope_6x3x3_top_4_cut_slope: Result has multiple solids: that is not currently supported
# slope_4x3x3_top_1_cut_slope: Result has multiple solids: that is not currently supported.
# slope_4x6x3_top_1_cut_slope: Result has multiple solids: that is not currently supported

# 
# 


