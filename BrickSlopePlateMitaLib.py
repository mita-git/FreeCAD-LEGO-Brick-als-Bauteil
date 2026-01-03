"""
BrickSlopePlateMitaLib.py 
-- Paul Cobbaut, 2023-05-18
-- Michael Talarczyk, 2025-11-02 2026-01-03 auch mit spire
The goal is to make Lego-compatible pieces for use in 3D printer
The script generates .stl files in a directory.
"""
# Dimensions for studs
# stud_radius_mm		= 2.400		# Lego official is 2.400
stud_radius_mm		= 2.475		# my radius
stud_center_spacing_mm	= 8.000

# stud_height_mm		= 1.600		# Lego official is 1.600
stud_height_mm		= 1.700		# my height

# Dimensions for plates
plate_height_mm		= 3.200
plate_width_mm		= 7.800

# The gap that is added to the width/length for each extra stud
gap_mm 			= 0.200

# Dimensions for bricks
brick_height_mm		= 9.600		# plate_height_mm * 3
brick_width_mm		= 7.800		# = plate_width_mm

# Wall thickness for bricks and plates
wall_thickness_mm	= 1.500		# 1.2 and 0.3 for new small beams or 1.5 for old bricks
top_thickness_mm	= 0.500		# the 'ceiling' of a brick is thinner than the sides

# Dimensions underside rings
ring_radius_outer_mm	= 3.255 	# was 3.220 on 1028, 3.226 on 20220929 (should be 3.2500) (Christoph Bartneck 6.51/2=3.255)
ring_radius_inner_mm	= 2.400		# was 2.666 pm 1029, 2.456 on 20220930, 2.556 on 20221001 (should be 2.400) (Christoph Bartneck 4.8/2=2.4)

# Dimensions underside pinn
pin_radius_outer_mm	= 1.6	# 20251227 by mita (Christoph Bartneck Technic 3.2/2=1.6)
pin_radius_inner_mm	= 0.5   # 20251227 by mita

# Dimensions for slopes
slope_start_height_mm   = 1.500
roof_thickness_mm	= 1.000		# the 'roof' of a sloped tile

# Dictionary of bricks generated; name:(studs_x, studs_y, plate_z) --> (width, length, height)
bricks = {}

# Used to visually separate the bricks in FreeCAD GUI
offset = 0
ibox = 0
box = 0

import FreeCAD
from FreeCAD import Base, Vector, Gui, Console
import Part
import Sketcher
import Mesh
import MeshPart
import time

# create a standard x, y, z box in FreeCAD

def make_box(Bodyname, Partname, x, y, z):
    global box
    box += 1
    Bodyname = Bodyname+str(box)
    Partname = Partname+str(box)
    obj = FreeCAD.ActiveDocument.addObject('PartDesign::Body',Bodyname)
    # FreeCAD.ActiveDocument.recompute()

    FreeCAD.ActiveDocument.getObject(Bodyname).Label = Partname+"_label"

    FreeCAD.ActiveDocument.addObject('PartDesign::AdditiveBox',Partname)
    FreeCAD.ActiveDocument.getObject(Bodyname).addObject(FreeCAD.ActiveDocument.getObject(Partname))
    # FreeCAD.ActiveDocument.recompute()

    FreeCAD.ActiveDocument.getObject(Partname).Length=x
    FreeCAD.ActiveDocument.getObject(Partname).Width=y
    FreeCAD.ActiveDocument.getObject(Partname).Height=z

    #FreeCAD.ActiveDocument.recompute()
    
    return obj

# convert studs to mm for bricks and plates
# one stud on brick	= 1 * brick_width_mm
# two studs on brick	= 2 * brick_width_mm + 1 * gap_mm
# three studs on brick	= 3 * brick_width_mm + 2 * gap_mm
# plate_width_mm is identical to brick_width_mm

def convert_studs_to_mm(studs):
    mm = (studs * brick_width_mm) + ((studs - 1) * gap_mm)
    return mm

# the stud template is created once then always copied

# erzeugt einen Zylinder aus Radius und Höhe    
def make_stud(name):
    Bodyname = name+"_body" 
    Partname = name+"_part"
    obj = FreeCAD.ActiveDocument.addObject('PartDesign::Body',Bodyname)
    FreeCAD.ActiveDocument.getObject(Bodyname).Label = Partname

    FreeCAD.ActiveDocument.addObject('PartDesign::AdditiveCylinder',Partname)
    FreeCAD.ActiveDocument.getObject(Bodyname).addObject(FreeCAD.ActiveDocument.getObject(Partname))
    # FreeCAD.ActiveDocument.recompute()

    FreeCAD.ActiveDocument.getObject(Partname).Radius=stud_radius_mm
    FreeCAD.ActiveDocument.getObject(Partname).Height=stud_height_mm
    FreeCAD.ActiveDocument.getObject(Partname).Angle='360,00 °'
    FreeCAD.ActiveDocument.getObject(Partname).FirstAngle='0,00 °'
    FreeCAD.ActiveDocument.getObject(Partname).SecondAngle='0,00 °'

    # FreeCAD.ActiveDocument.recompute()
    
    return obj

def make_Cylinder(name, r, h):
    Bodyname = name+"_body"
    Partname = name+"_cylinder" 
    obj = FreeCAD.ActiveDocument.addObject('PartDesign::Body',Bodyname)
    FreeCAD.ActiveDocument.getObject(Bodyname).Label = Partname

    FreeCAD.ActiveDocument.addObject('PartDesign::AdditiveCylinder',Partname)
    FreeCAD.ActiveDocument.getObject(Bodyname).addObject(FreeCAD.ActiveDocument.getObject(Partname))
    # FreeCAD.ActiveDocument.recompute()

    FreeCAD.ActiveDocument.getObject(Partname).Radius=r
    FreeCAD.ActiveDocument.getObject(Partname).Height=h
    FreeCAD.ActiveDocument.getObject(Partname).Angle='360,00 °'
    FreeCAD.ActiveDocument.getObject(Partname).FirstAngle='0,00 °'
    FreeCAD.ActiveDocument.getObject(Partname).SecondAngle='0,00 °'

    # FreeCAD.ActiveDocument.recompute()
    
    return obj

def make_a_name(studs_x, studs_y, plate_z, studs_t, plusname):
    name = plusname+ '_' + str(studs_x) + 'x' + str(studs_y) + 'x' + str(plate_z) + '_stud_' + str(studs_t) + '_no_' + str(offset)
    bricks[name] = (studs_x, studs_y, plate_z, studs_t, plusname)
    return name
    
# erzeugt einen Teil mit PartDesign::Boolean   Fuse Cut Common  Vereinigung=0 Differenz=1 Schnittmenge=2
def make_part_Boolean(Bodyname1, Bodyname2, BooleanName, VDS):

    FreeCAD.ActiveDocument.getObject(Bodyname2).BaseFeature = FreeCAD.ActiveDocument.getObject(FreeCAD.ActiveDocument.getObject(Bodyname1).Label)

    # print("Start make_part_Boolean:",Bodyname1, Bodyname2, BooleanName, VDS)
    objVDS = FreeCAD.ActiveDocument.getObject(Bodyname1).newObject('PartDesign::Boolean',BooleanName)

    FreeCAD.ActiveDocument.getObject(BooleanName).setObjects( [FreeCAD.ActiveDocument.getObject(Bodyname2),])
    FreeCAD.ActiveDocument.getObject(BooleanName).Type = VDS
    
    # FreeCAD.ActiveDocument.recompute()
    return objVDS

def create_outer_box(brick_name):
    # create the hull without studs and without rings
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    # outer_prism = the brick block completely full
    outer_width  = convert_studs_to_mm(x)
    outer_length = convert_studs_to_mm(y)
    outer_height = z * plate_height_mm
    # print("Debug","Box001 - outer_prism")
    outer_prism = make_box(brick_name+'_box', brick_name+'_out_box', outer_width, outer_length, outer_height)
    outer_prism.Label = brick_name + "_outer_box"
    return outer_prism


def get_inner_box(brick_name):
    # create the hull without studs and without rings
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    # outer_prism = the brick block completely full
    outer_width  = convert_studs_to_mm(x)
    outer_length = convert_studs_to_mm(y)
    outer_height = z * plate_height_mm
    # inner_prism = the part that is substracted from outer_prism, thus hull has walls and ceiling
    inner_width  = outer_width  - (2 * wall_thickness_mm)
    inner_length = outer_length - (2 * wall_thickness_mm)
    inner_height = outer_height - top_thickness_mm		# because - wall_thickness_mm was too much
    return (inner_width,inner_length,inner_height)


def create_inner_box(brick_name):
    # create the hull without studs and without rings
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    # outer_prism = the brick block completely full
    outer_width  = convert_studs_to_mm(x)
    outer_length = convert_studs_to_mm(y)
    outer_height = z * plate_height_mm
    # inner_prism = the part that is substracted from outer_prism, thus hull has walls and ceiling
    inner_width  = outer_width  - (2 * wall_thickness_mm)
    inner_length = outer_length - (2 * wall_thickness_mm)
    inner_height = outer_height - top_thickness_mm		# because - wall_thickness_mm was too much
    # print("Debug","Box002 - inner_prism")
    inner_prism  = make_box(brick_name+'_box', brick_name+'_in_box', inner_width, inner_length, inner_height)
    # place the inner_prism at x and y exactly one wall thickness
    inner_prism.Placement = FreeCAD.Placement(Vector(wall_thickness_mm, wall_thickness_mm, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    inner_prism.Label = brick_name + "_inner_box"
    return inner_prism


def create_brick_hull(brick_name):
    # create the hull without studs and without rings
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    # outer_prism = the brick block completely full
    outer_width  = convert_studs_to_mm(x)
    outer_length = convert_studs_to_mm(y)
    outer_height = z * plate_height_mm
    # print("Debug","Box001 - outer_prism")
    outer_prism = make_box(brick_name+'_box', brick_name+'_out_box', outer_width, outer_length, outer_height)
    # inner_prism = the part that is substracted from outer_prism, thus hull has walls and ceiling
    inner_width  = outer_width  - (2 * wall_thickness_mm)
    inner_length = outer_length - (2 * wall_thickness_mm)
    inner_height = outer_height - top_thickness_mm		# because - wall_thickness_mm was too much
    # print("Debug","Box002 - inner_prism")
    inner_prism  = make_box(brick_name+'_box', brick_name+'_inner_box', inner_width, inner_length, inner_height)
    # place the inner_prism at x and y exactly one wall thickness
    inner_prism.Placement = FreeCAD.Placement(Vector(wall_thickness_mm, wall_thickness_mm, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    # now cut the inner part out of the outer part    
    make_part_Boolean(outer_prism.Name, inner_prism.Name, brick_name+"_cut", 1)
    outer_prism.Label = brick_name + "_hull"
    return outer_prism
    
def add_brick_studs(brick_name):
    # Add the studs on top
    # create the studs and append each one to a compound_list
    compound_list=[]
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    height = z * plate_height_mm
    for i in range(int(x)):
        for j in range(int(y)):
            StudName = "stud_" + brick_name + '_' + str(i) + '_' + str(j)
            # print(StudName)
            stud = make_stud(StudName)
            xpos = ((i+1) * stud_center_spacing_mm) - (stud_center_spacing_mm / 2) - (gap_mm / 2)
            ypos = ((j+1) * stud_center_spacing_mm) - (stud_center_spacing_mm / 2) - (gap_mm / 2)
            stud.Placement = FreeCAD.Placement(Vector(xpos, ypos, height), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
            compound_list.append(stud)
    return compound_list
    
def add_brick_rings(brick_name):
    # Add the rings on the bottom of the brick
    compound_list = []
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    t = bricks[brick_name][3]
    typeofbrick = bricks[brick_name][4]
    
    # Create a template ring (all rings for a single brick are the same height)
    height = z * plate_height_mm
    
#    print("vars",x,y,t,typeofbrick)
#    diff = x - t
    for i in range(int(x - 1)):
        for j in range(int(y - 1)):
            RingName = 'ring_' + brick_name + str(i) + '_' + str(j)
            # print(RingName)
            outer_cylinder = make_Cylinder("outer_cylinder_"+RingName,ring_radius_outer_mm,(height - top_thickness_mm))
            
            # # print("Namen:",outer_cylinder.Name, inner_cylinder.Name, RingName+"Boolean")
            
            xpos = (brick_width_mm + gap_mm) * (i + 1) - (gap_mm/2)
            ypos = (brick_width_mm + gap_mm) * (j + 1) - (gap_mm/2)
            outer_cylinder.Placement = FreeCAD.Placement(Vector(xpos, ypos, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
            FreeCAD.ActiveDocument.recompute()
    
            # print("################################## Beginn Bohrung")
    
            Holename = outer_cylinder.Label + "_hole"
            outer_cylinder.newObject('PartDesign::Hole',Holename)
            
            FreeCAD.ActiveDocument.getObject(Holename).Profile = (FreeCAD.ActiveDocument.getObject(outer_cylinder.Label), ['Face3',])
            # FreeCAD.ActiveDocument.recompute()
            FreeCAD.ActiveDocument.getObject(Holename).Diameter = ring_radius_inner_mm*2
            FreeCAD.ActiveDocument.getObject(Holename).Depth = (height - top_thickness_mm)
            # FreeCAD.ActiveDocument.recompute()
            FreeCAD.ActiveDocument.getObject(outer_cylinder.Label).Visibility = False
            
            # print("################################## Ende Bohrung")
    
            compound_list.append(outer_cylinder)

    return compound_list

def add_brick_pins(brick_name):
    # Add the pins on the bottom of the brick
    compound_list = []
    x = bricks[brick_name][0]
    y = bricks[brick_name][1]
    z = bricks[brick_name][2]
    t = bricks[brick_name][3]
    typeofbrick = bricks[brick_name][4]
    
    # Create a template ring (all rings for a single brick are the same height)
    height = z * plate_height_mm
    
#    print("vars",x,y,t,typeofbrick)
#    diff = x - t
    for j in range(int(y - 1)):
        PinName = 'pin_' + brick_name + '_' + str(j)
        # print(PinName)
        outer_cylinder = make_Cylinder("outer_cylinder_"+PinName,pin_radius_outer_mm,(height - top_thickness_mm))
        
        # # print("Namen:",outer_cylinder.Name, inner_cylinder.Name, PinName+"Boolean")
        
        xpos = brick_width_mm/2
        ypos = (brick_width_mm + gap_mm) * (j + 1) - (gap_mm/2)
        outer_cylinder.Placement = FreeCAD.Placement(Vector(xpos, ypos, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
        FreeCAD.ActiveDocument.recompute()

        # print("################################## Beginn Bohrung")

        Holename = outer_cylinder.Label + "_hole"
        outer_cylinder.newObject('PartDesign::Hole',Holename)
        
        FreeCAD.ActiveDocument.getObject(Holename).Profile = (FreeCAD.ActiveDocument.getObject(outer_cylinder.Label), ['Face3',])
        # FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.getObject(Holename).Diameter = pin_radius_inner_mm*2
        FreeCAD.ActiveDocument.getObject(Holename).Depth = (height - top_thickness_mm)
        # FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.getObject(outer_cylinder.Label).Visibility = False
        
        # print("################################## Ende Bohrung")

        compound_list.append(outer_cylinder)

    return compound_list

# creates a sketch to cut from the (to be) slope brick
def create_slope_cutout(brick_name,plane):
    typeofslope = brick_name.split("_")[0]
    print("create_slope_cutout typeofslope",typeofslope)
    width_bottom   = convert_studs_to_mm(bricks[brick_name][0])
    length         = convert_studs_to_mm(bricks[brick_name][1])
    height         = bricks[brick_name][2] * plate_height_mm
    width_topstuds = convert_studs_to_mm(bricks[brick_name][3])
    BodyLabel   = 'Body_cut_'   + brick_name + "_i" + str(ibox) + "_" + plane
    SketchLabel = 'Sketch_cut_' + brick_name + "_i" + str(ibox) + "_" + plane
    PadLabel    = 'Pad_cut_'    + brick_name + "_i" + str(ibox) + "_" + plane
    # create Body and Sketch Object
    Body_obj   = FreeCAD.ActiveDocument.addObject("PartDesign::Body", BodyLabel)
    Body_obj.Label = BodyLabel + '_label'
    mplane = plane.split("_")[0]
    print("mplane:",mplane)
    match typeofslope:
        case 'slope':
            SketchLabel = SketchLabel + "_" + plane
            Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
            Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
            Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
            # create points
            point0 = Vector(width_bottom  , slope_start_height_mm  , 0)
            point1 = Vector(width_bottom  , height + stud_height_mm, 0)
            point2 = Vector(width_topstuds, height + stud_height_mm, 0)
            point3 = Vector(width_topstuds, height                 , 0)
            # create lines that kinda surround a fork
            Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
            Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
            Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
            Sketch_obj.addGeometry(Part.LineSegment(point3,point0),False)
        case 'dslope':
            SketchLabel = SketchLabel + "_" + plane
            Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
            Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
            Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
            # create points
            print("Werte",width_bottom,width_topstuds,height,slope_start_height_mm)
            point0 = Vector(width_bottom  , slope_start_height_mm  , 0)
            point1 = Vector(width_bottom  , height + stud_height_mm, 0)
            point2 = Vector(0, height + stud_height_mm, 0)
            point3 = Vector(0, slope_start_height_mm , 0)
            point4 = Vector(width_bottom/2, height , 0)
            
            # create lines that kinda surround a fork
            Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
            Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
            Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
            Sketch_obj.addGeometry(Part.LineSegment(point3,point4),False)
            Sketch_obj.addGeometry(Part.LineSegment(point4,point0),False)

        case 'qslope' | 'spire':
            match mplane:
                case 'xz':
                    print("plane",plane)
######################################################################################################################################        
                    SketchLabel = SketchLabel + "_" + plane
                    Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
                    Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
                    Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
                    # create points
                    print("Werte_XZ",width_bottom,width_topstuds,height,slope_start_height_mm)
                    point0xz = Vector(width_bottom  , slope_start_height_mm  , 0)
                    point1xz = Vector(width_bottom  , height + stud_height_mm, 0)
                    point2xz = Vector(0, height + stud_height_mm, 0)
                    point3xz = Vector(0, slope_start_height_mm , 0)
                    point4xz = Vector(width_bottom/2, height , 0)
                    
                    # create lines that kinda surround a fork
                    Sketch_obj.addGeometry(Part.LineSegment(point0xz,point1xz),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point1xz,point2xz),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point2xz,point3xz),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point3xz,point4xz),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point4xz,point0xz),False)             
 
######################################################################################################################################        
                case 'yz':
                    print("plane",plane)
                    SketchLabel = SketchLabel + "_" + plane
                    Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
                    Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('YZ_Plane'),'')]
                    Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(0.58,0.58,0.58),120.000))
                    # create points
                    print("Werte_YZ",length,width_topstuds,height,slope_start_height_mm)
                    point0 = Vector(length  , slope_start_height_mm  , 0)
                    point1 = Vector(length  , height + stud_height_mm, 0)
                    point2 = Vector(0, height + stud_height_mm, 0)
                    point3 = Vector(0, slope_start_height_mm , 0)
                    point4 = Vector(length/2, height , 0)
                    
                    # create lines that kinda surround a fork
                    Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point3,point4),False)
                    Sketch_obj.addGeometry(Part.LineSegment(point4,point0),False)
    
    # create Pad Object
    # print("PadLabel:",PadLabel)
    Pad_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject('PartDesign::Pad',PadLabel)
    Pad_obj.Profile = FreeCAD.ActiveDocument.getObject(SketchLabel)

    match mplane:
        case 'xz':
            Pad_obj.Reversed = 1
            Pad_obj.Length = length
        case 'yz':
            Pad_obj.Reversed = 0
            Pad_obj.Length = width_bottom
            
                        
    Pad_obj.Label = PadLabel
    FreeCAD.ActiveDocument.getObject(SketchLabel).Visibility = True
    
    return Body_obj

# creates a sketch to fuse to the (to be) slope brick
def create_slope_roof(brick_name):
    typeofslope = brick_name.split("_")[0]
    # print("typeofslope",typeofslope)
    width_bottom   = convert_studs_to_mm(bricks[brick_name][0])
    length         = convert_studs_to_mm(bricks[brick_name][1])
    height         = bricks[brick_name][2] * plate_height_mm
    width_topstuds = convert_studs_to_mm(bricks[brick_name][3])
    BodyLabel   = 'Body_roof_'   + brick_name
    SketchLabel = 'Sketch_roof_' + brick_name
    PadLabel    = 'Pad_roof_'    + brick_name
    # create Sketch Object
    Body_obj   = FreeCAD.ActiveDocument.addObject("PartDesign::Body", BodyLabel)
    Body_obj.Label = BodyLabel + '_label'

    match typeofslope:
        case 'slope':
            SketchLabel = SketchLabel + "_xz"
            # print("Werte",width_bottom,width_topstuds,height,slope_start_height_mm,roof_thickness_mm)
            Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
            Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
            Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
            # create points
            point0 = Vector(width_bottom  , slope_start_height_mm                    , 0)
            point1 = Vector(width_topstuds, height                                   , 0)
            point2 = Vector(width_topstuds, height                - roof_thickness_mm, 0)
            point3 = Vector(width_bottom  , slope_start_height_mm - roof_thickness_mm, 0)
            # create lines that kinda surround a fork
            Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
            Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
            Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
            Sketch_obj.addGeometry(Part.LineSegment(point3,point0),False)
        case 'dslope':
            SketchLabel = SketchLabel + "_xz"
            # print("Werte",width_bottom,width_topstuds,height,slope_start_height_mm,roof_thickness_mm)
            # width_bottom  , slope_start_height_mm
            Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
            Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
            Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
            # create points
            point0 = Vector(width_bottom  , slope_start_height_mm                    , 0)
            point1 = Vector(width_bottom/2, height                                   , 0)
            point2 = Vector(0 , slope_start_height_mm, 0)
            point3 = Vector(0 , slope_start_height_mm - roof_thickness_mm, 0)
            point4 = Vector(width_bottom/2, height - roof_thickness_mm, 0)
            point5 = Vector(width_bottom  ,slope_start_height_mm - roof_thickness_mm , 0)
            
            # create lines that kinda surround a fork
            Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
            Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
            Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
            Sketch_obj.addGeometry(Part.LineSegment(point3,point4),False)
            Sketch_obj.addGeometry(Part.LineSegment(point4,point5),False)
            Sketch_obj.addGeometry(Part.LineSegment(point5,point0),False)

        case 'qslope':

####################################################################################################################################
            
            SketchLabel = SketchLabel + "_yz"
            # print("Werte",length,width_topstuds,height,slope_start_height_mm,roof_thickness_mm)
            Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
            Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('YZ_Plane'),'')]
            Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(0.58,0.58,0.58),120.000))
            # create points
            point0 = Vector(length  , slope_start_height_mm                    , 0)
            point1 = Vector(length/2, height                                   , 0)
            point2 = Vector(0 , slope_start_height_mm, 0)
            point3 = Vector(0 , slope_start_height_mm - roof_thickness_mm, 0)
            point4 = Vector(length/2, height - roof_thickness_mm, 0)
            point5 = Vector(length  ,slope_start_height_mm - roof_thickness_mm , 0)
            
            # create lines that kinda surround a fork
            Sketch_obj.addGeometry(Part.LineSegment(point0,point1),False)
            Sketch_obj.addGeometry(Part.LineSegment(point1,point2),False)
            Sketch_obj.addGeometry(Part.LineSegment(point2,point3),False)
            Sketch_obj.addGeometry(Part.LineSegment(point3,point4),False)
            Sketch_obj.addGeometry(Part.LineSegment(point4,point5),False)
            Sketch_obj.addGeometry(Part.LineSegment(point5,point0),False)

                     
    # create Pad Object
    Pad_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject('PartDesign::Pad',PadLabel)
    Pad_obj.Profile = FreeCAD.ActiveDocument.getObject(SketchLabel)
    match typeofslope:
        case 'slope' | 'dslope':
            Pad_obj.Length = length
            Pad_obj.Reversed = 1
    match typeofslope:
        case 'qslope':
            Pad_obj.Length = width_bottom
            Pad_obj.Reversed = 0
    Pad_obj.Label = PadLabel
    
    FreeCAD.ActiveDocument.getObject(SketchLabel).Visibility = False
    
    return Body_obj

########################################################################################################### make_brick ################        
    
def make_brick(studs_x, studs_y, plate_z, studs_t, type_of_brick):
    # name the slope brick   
    brick_name = make_a_name(studs_x, studs_y, plate_z, studs_t, type_of_brick)
    global offset

    
    compound_list = []
    
    # print("Debug los Gehts mit",brick_name)
    match studs_x:
        case 1:
            match type_of_brick:
                case 'slope' | 'dslope'| 'qslope':
                    print("studs_x = ",studs_x,"and type_of_brick = ",type_of_brick,"Nicht Möglich")
                    return "Abbruch"
                case _:
                    print("Add Pins")
                    compound_list += add_brick_pins(brick_name)
                
        case _:
            print("Add Rings")
            compound_list += add_brick_rings(brick_name)
                
    
    # start as if it is a regular brick
    huelle = create_brick_hull(brick_name)
    

    
    match type_of_brick:
        case 'dslope' | 'qslope':
            print('dslope | qslope')
        case 'tile':
            print("tile")
        case _:
            compound_list += add_brick_studs(brick_name)
            print("_: type_of_brick:",type_of_brick)
        
        
        
    # print("LEN:",ende,compound_list)
    ende = len(compound_list)
    
    for i in range(0,ende):
        # print("Debug For",i,compound_list[i].Name,compound_list[i].Label)
        make_part_Boolean(huelle.Name, compound_list[i].Name, brick_name+"_plus"+str(i), 0)

    huelle.Label = brick_name
      
    FreeCAD.ActiveDocument.recompute()

    outer_width  = convert_studs_to_mm(studs_x)
    outer_length = convert_studs_to_mm(studs_y)
    outer_height = 1 * plate_height_mm
    
    match type_of_brick:
        case 'slope' | 'dslope':
            print("^^^^^^^^^^^^^^^^^^^^",studs_x, studs_y, plate_z, studs_t, type_of_brick,"^^^^^^^^^^^^")
            
            cutout_part = create_slope_cutout(brick_name,'xz')
            FreeCAD.ActiveDocument.recompute()

            TempBox = make_box(brick_name+'_boxtemp', brick_name+'_box_temp', outer_length, outer_width, outer_height)
            TempBox.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
            
            # print("TempBox",TempBox.Name,TempBox.Label,TempBox.BaseFeature)
            
            # print("cutout_part",cutout_part.Name,cutout_part.Label,cutout_part.BaseFeature)
                   
            make_part_Boolean(huelle.Name, TempBox.Name, brick_name+"_put_slope", 0)               
            
            make_part_Boolean(huelle.Name, cutout_part.Name, brick_name+"_cut_slope", 1)
            
            roof_part = create_slope_roof(brick_name)
            
            # print("roof_part",roof_part.Label,roof_part.Name)
            make_part_Boolean(huelle.Name, roof_part.Name, brick_name+"_put_roof", 0)

            TempBox = make_box(brick_name+'_boxtemp_d', brick_name+'_box_temp_d', outer_length, outer_width, outer_height)
            TempBox.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
            
            make_part_Boolean(huelle.Name, TempBox.Name, brick_name+"_put_slope_d", 1) 
            
            FreeCAD.ActiveDocument.recompute()

        case 'qslope':
        
########################################################################################################################### qslope ###############        
            print("^^^^^^^^^^^^^^^^^^^^",studs_x, studs_y, plate_z, studs_t, type_of_brick,"^^^^^^^^^^^^")           
                        
            TempBox1 = make_box(brick_name+'_boxtemp1', brick_name+'_box_temp1', outer_length, outer_width, outer_height)
            TempBox1.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
                        
            # print("TempBox1",TempBox1.Name,TempBox1.Label,TempBox1.BaseFeature)
            
            # print("huelle",huelle.Name,huelle.Label,huelle.BaseFeature)
                   
            Temp2 = make_part_Boolean(huelle.Name, TempBox1.Name, brick_name+"_put_slope_1", 0)     

            FreeCAD.ActiveDocument.recompute()            
            # print("Temp2",Temp2.Name,Temp2.Label,Temp2.BaseFeature)

            cutout_part1 = create_slope_cutout(brick_name,'yz')
            # cutout_part1.BaseFeature = str(cutout_part1.Name)
            # print("cutout_part1 qslope",cutout_part1.Name,cutout_part1.Label,cutout_part1.BaseFeature)
            
            Temp3 = make_part_Boolean(huelle.Name, cutout_part1.Name, brick_name+"_cut_slope_1", 1)           
                       
            FreeCAD.ActiveDocument.recompute()
            # print("Temp3",Temp3.Name,Temp3.Label,Temp3.BaseFeature)

################################################################################################################## qslope roof #################### 
           
            roof_part = create_slope_roof(brick_name)
            
            # print("roof_part",roof_part.Label,roof_part.Name)
            make_part_Boolean(huelle.Name, roof_part.Name, brick_name+"_put_roof", 0)
            
            TempBox3 = make_box(brick_name+'_boxtemp_d', brick_name+'_box_temp_d', outer_length, outer_width, outer_height)
            TempBox3.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
            
            make_part_Boolean(huelle.Name, TempBox3.Name, brick_name+"_put_slope_d", 1) 
            
            FreeCAD.ActiveDocument.recompute()
            # print("################################## CUT beendet")


###########################################################################################################################  ###############        

           

########################################################################################################################### _ ###############        
            
        case _:
            print("°°°°°°°°°°°°°°°°°°°°°°",studs_x, studs_y, plate_z, studs_t, type_of_brick,"°°°°°°°°°°°°")

    huelle.Placement = FreeCAD.Placement(Vector((brick_width_mm * offset), 0, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    offset += studs_x + 2
    print("ENDE: make_brick",brick_name)

def make_inner_spire(brick_name):

    inner_cutout_part_xz = create_slope_cutout(brick_name,'xz_i')
    
    FreeCAD.ActiveDocument.recompute()
   
    inner_cutout_part_yz = create_slope_cutout(brick_name,'yz_i')
    
    FreeCAD.ActiveDocument.recompute()
        
    newname = brick_name+"_cut_spire_inner_"+str(ibox)
    
    make_part_Boolean(inner_cutout_part_xz.Name, inner_cutout_part_yz.Name, newname, 0)
    
      
    FreeCAD.ActiveDocument.recompute()

    # print("Label:",inner_cutout_part_xz.Label[:-6],inner_cutout_part_yz.Label[:-6])
    # Label: Body_cut_spire_4x6x9_stud_0_no_0_xz_i Body_cut_spire_4x6x9_stud_0_no_0_yz_i
    inner_cutout_part_xz.BaseFeature = inner_cutout_part_yz
    inner_cutout_part_xz.Placement = FreeCAD.Placement(Vector(-wall_thickness_mm, -wall_thickness_mm, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    inner_box = create_inner_box(brick_name)
           
    make_part_Boolean(inner_box.Name, inner_cutout_part_xz.Name, newname+"_B", 1)
      
    FreeCAD.ActiveDocument.recompute()
    
    return inner_box

def make_outer_spire(brick_name):
    # brick is finished, so create a compound object with the name of the brick
   
    cutout_part_xz = create_slope_cutout(brick_name,'xz_o')
    
    FreeCAD.ActiveDocument.recompute()
   
    cutout_part_yz = create_slope_cutout(brick_name,'yz_o')
    
    FreeCAD.ActiveDocument.recompute()
    
    cutout_part_xyz = make_part_Boolean(cutout_part_xz.Name, cutout_part_yz.Name, brick_name+"_cut_spire_out", 0)
      
    FreeCAD.ActiveDocument.recompute()

    # print("Label:",cutout_part_xz.Label[:-6],cutout_part_yz.Label[:-6])
    # Label: Body_cut_spire_4x6x9_stud_0_no_0_xz_o Body_cut_spire_4x6x9_stud_0_no_0_yz_o
    cutout_part_xz.BaseFeature = cutout_part_yz
    
    outer_box = create_outer_box(brick_name)
    # no Placement
    make_part_Boolean(outer_box.Name, cutout_part_xz.Name, brick_name+"_cut_spire_A", 1)
      
    FreeCAD.ActiveDocument.recompute()
    
    return outer_box

def make_spire(studs_x, studs_y, plate_z, studs_t, type_of_brick):
    # name the slope brick   
    brick_name = make_a_name(studs_x, studs_y, plate_z, studs_t, type_of_brick)
    global offset
    global ibox
    global box
################################################################################################################################################

    outer_box = make_outer_spire(brick_name)

################################################################################################################################################
    
    ibox += 1
    inner_box = make_inner_spire(brick_name)
    inner_box.Placement = FreeCAD.Placement(Vector(wall_thickness_mm, wall_thickness_mm, -wall_thickness_mm), FreeCAD.Rotation(0,0,0), Vector(0,0,0))

################################################################################################################################################

    # print("Names:",inner_box.Name,outer_box.Name,inner_box.Label,outer_box.Label)
    
    make_part_Boolean(outer_box.Name, inner_box.Name, brick_name+"_cut", 1)
    
    # print("Names:",inner_box.Name,outer_box.Name,inner_box.Label,outer_box.Label)
    
    outer_box.Label = brick_name
    
    huelle = outer_box
    
    # print('Hülle:',huelle.Label,'fertig')
    
#     print("huelle",huelle.Name,huelle.Label,huelle.BaseFeature)
# 

    FreeCAD.ActiveDocument.recompute()
    
#    outer_box.Placement = FreeCAD.Placement(Vector(30, 0, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
#    offset += studs_x + 2

################################################################################################################################################


    compound_list = []
    compound_list += add_brick_rings(brick_name)
    

    # print("LEN:",ende,compound_list)
    ende = len(compound_list)

    box += 1
    
    for i in range(0,ende):
        # print("Debug For",i,compound_list[i].Name,compound_list[i].Label)
        
        ibox += 1
        inner_box_c = make_inner_spire(brick_name) 
        zwei_stellig = f"{i:02}"
        SchnittName = brick_name+"_common_"+zwei_stellig
        BooleanName = brick_name+"_plus_"+zwei_stellig
        neuesObj = FreeCAD.ActiveDocument.addObject('PartDesign::Body',SchnittName)
        BoolObj = neuesObj.newObject('PartDesign::Boolean',BooleanName)
        BoolObj.addObjects([inner_box_c,])
        FreeCAD.ActiveDocument.recompute()
        BoolObj.setObjects( [inner_box_c,compound_list[i],])
        BoolObj.Type = 2
        FreeCAD.ActiveDocument.recompute()
        
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.ActiveDocument.ActiveView.fitAll()
    
    NeuBoolGrossObj = FreeCAD.ActiveDocument.addObject('PartDesign::Body',brick_name)
    BoolGrossObj = NeuBoolGrossObj.newObject('PartDesign::Boolean','BoolGross_'+str(box))
    zwei_stellig = '00'
    BoolGrossObj.setObjects( [FreeCAD.ActiveDocument.getObject(neuesObj.Name[:-2]+zwei_stellig),outer_box,])
    FreeCAD.ActiveDocument.recompute()
    for i in range(1,ende):
        zwei_stellig = f"{i:02}"
        # print(neuesObj.Name[:-2]+zwei_stellig)
        BoolGrossObj.addObjects([FreeCAD.ActiveDocument.getObject(neuesObj.Name[:-2]+zwei_stellig),])
        FreeCAD.ActiveDocument.recompute()
        BoolGrossObj.Type = 0
        FreeCAD.ActiveDocument.recompute()

    FreeCAD.ActiveDocument.recompute()
    
    outer_box.Placement = FreeCAD.Placement(Vector((brick_width_mm * offset), 0, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    offset += studs_x + 2
    print("ENDE: make_spire",brick_name)
