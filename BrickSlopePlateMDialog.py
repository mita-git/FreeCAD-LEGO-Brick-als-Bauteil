"""
BrickSlopePlateMDialog.py 
-- Paul Cobbaut, 2023-05-18
-- Michael Talarczyk, 20252025-11-02 2026-01-03 auch mit spire
The goal is to make Lego-compatible pieces for use in 3D printer
The script generates .stl files in a directory.
"""



# BrickSlopePlateMitaMDialog.py


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

from FCDialog import *
from BrickSlopePlateMitaLib import *

# create a FreeCAD document and Part Design body
 
doc = FreeCAD.newDocument("Lego brick generated")

def anzeigen():
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()

# starte Dialog
dialog = Dialog()
print(sys.version)

if dialog.exec() == QDialog.Accepted:
    values = dialog.getValues()
    print("Die Werte:")
    print("Eingane:",values)
    match values[2]: # Höhe des Bricks
        case 1:
            values[4] = 'plate'
            print("Höhe 1 muss Platte sein")
            
    match values[4]: # Auswahlbox
        case 'plate':
            values[2] = 1
            print("Platte dann muss Höhe 1 sein")
        case 'tile':
            values[2] = 1
            values[3] = 0
            print("Fliese dann muss Höhe 1 sein und Studs 0")
            
    print("Verwendet:",values)
    if values[4] == 'spire':
        make_spire(values[0],values[1],values[2],values[3],values[4]) # spire 
    else:
        make_brick(values[0],values[1],values[2],values[3],values[4]) # no spire
    anzeigen()
else:
    print("Dialog wurde abgebrochen.")
    
  