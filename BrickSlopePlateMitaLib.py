"""
slope_brick_mita.py -- Paul Cobbaut, 2023-05-18
-- Michael Talarczyk, 2025-11-02 2025-11-20 
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
ring_radius_outer_mm	= 3.250 	# was 3.220 on 1028, 3.226 on 20220929 (should be 3.2500)
ring_radius_inner_mm	= 2.500		# was 2.666 pm 1029, 2.456 on 20220930, 2.556 on 20221001 (should be 2.400)

# Dimensions for slopes
slope_start_height_mm   = 1.500
roof_thickness_mm	= 1.000		# the 'roof' of a sloped tile

# Dictionary of bricks generated; name:(studs_x, studs_y, plate_z) --> (width, length, height)
bricks = {}

# Used to visually separate the bricks in FreeCAD GUI
offset = 0

import FreeCAD
from FreeCAD import Base, Vector, Gui, Console
import Part
import Sketcher
import Mesh
import MeshPart
import time

# create a standard x, y, z box in FreeCAD

def make_box(Bodyname, Partname, x, y, z):
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

def name_a_slope_brick(studs_x, studs_y, plate_z, studs_t, plusname):
    name = plusname+ '_' + str(studs_x) + 'x' + str(studs_y) + 'x' + str(plate_z) + '_top_' + str(studs_t)
    bricks[name] = (studs_x, studs_y, plate_z, studs_t, plusname)
    return name
# erzeugt einen Teil mit PartDesign::Boolean   Fuse Cut Common  Vereinigung=0 Differenz=1 Schnittmenge=2
def make_part_Boolean(Bodyname1, Bodyname2, BooleanName, VDS):

    # print("Start make_part_Boolean:",Bodyname1, Bodyname2, BooleanName, VDS)
    objVDS = FreeCAD.ActiveDocument.getObject(Bodyname1).newObject('PartDesign::Boolean',BooleanName)

    FreeCAD.ActiveDocument.getObject(BooleanName).setObjects( [FreeCAD.ActiveDocument.getObject(Bodyname2),])
    FreeCAD.ActiveDocument.getObject(BooleanName).Type = VDS
    FreeCAD.ActiveDocument.getObject(Bodyname2).BaseFeature = FreeCAD.ActiveDocument.getObject(FreeCAD.ActiveDocument.getObject(Bodyname1).Label)
    
    # FreeCAD.ActiveDocument.recompute()
    return objVDS

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
    outer_prism = make_box(brick_name+'_box001', brick_name+'_outer_box', outer_width, outer_length, outer_height)
    # inner_prism = the part that is substracted from outer_prism, thus hull has walls and ceiling
    inner_width  = outer_width  - (2 * wall_thickness_mm)
    inner_length = outer_length - (2 * wall_thickness_mm)
    inner_height = outer_height - top_thickness_mm		# because - wall_thickness_mm was too much
    # print("Debug","Box002 - inner_prism")
    inner_prism  = make_box(brick_name+'_box002', brick_name+'_inner_box', inner_width, inner_length, inner_height)
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
# creates a sketch to cut from the (to be) slope brick
def create_slope_cutout(brick_name):
    typeofslope = brick_name.split("_")[0]
    print("typeofslope",typeofslope)
    width_bottom   = convert_studs_to_mm(bricks[brick_name][0])
    length         = convert_studs_to_mm(bricks[brick_name][1])
    height         = bricks[brick_name][2] * plate_height_mm
    width_topstuds = convert_studs_to_mm(bricks[brick_name][3])
    BodyLabel   = 'Body_cut_'   + brick_name
    SketchLabel = 'Sketch_cut_' + brick_name
    PadLabel    = 'Pad_cut_'    + brick_name
    # create Body and Sketch Object
    Body_obj   = FreeCAD.ActiveDocument.addObject("PartDesign::Body", BodyLabel)
    Body_obj.Label = BodyLabel + '_label'
    Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
    Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
    Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))
    match typeofslope:
        case 'slope':
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
    
    # create Pad Object
    Pad_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject('PartDesign::Pad',PadLabel)
    Pad_obj.Profile = FreeCAD.ActiveDocument.getObject(SketchLabel)
    Pad_obj.Length = length
    Pad_obj.Label = PadLabel
    Pad_obj.Reversed = 1
    FreeCAD.ActiveDocument.getObject(SketchLabel).Visibility = False
    return Body_obj

# creates a sketch to fuse to the (to be) slope brick
def create_slope_roof(brick_name):
    typeofslope = brick_name.split("_")[0]
    print("typeofslope",typeofslope)
    width_bottom   = convert_studs_to_mm(bricks[brick_name][0])
    length         = convert_studs_to_mm(bricks[brick_name][1])
    height         = bricks[brick_name][2] * plate_height_mm
    width_topstuds = convert_studs_to_mm(bricks[brick_name][3])
    BodyLabel   = 'Body_roof_'   + brick_name + 'roof'
    SketchLabel = 'Sketch_roof_' + brick_name + 'roof'
    PadLabel    = 'Pad_roof_'    + brick_name + 'roof'
    # create Sketch Object
    Body_obj   = FreeCAD.ActiveDocument.addObject("PartDesign::Body", BodyLabel)
    Body_obj.Label = BodyLabel + '_label'
    Sketch_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject("Sketcher::SketchObject", SketchLabel)
    Sketch_obj.AttachmentSupport = [(FreeCAD.ActiveDocument.getObject('XZ_Plane'),'')]
    Sketch_obj.Placement = FreeCAD.Placement(Vector(0,0,0),FreeCAD.Rotation(Vector(1,0,0),90.000))

    match typeofslope:
        case 'slope':
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
            # create points
            print("Werte",width_bottom,width_topstuds,height,slope_start_height_mm,roof_thickness_mm)
            # width_bottom  , slope_start_height_mm
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
            
    # create Pad Object
    Pad_obj = FreeCAD.ActiveDocument.getObject(BodyLabel).newObject('PartDesign::Pad',PadLabel)
    Pad_obj.Profile = FreeCAD.ActiveDocument.getObject(SketchLabel)
    Pad_obj.Length = length
    Pad_obj.Label = PadLabel
    Pad_obj.Reversed = 1
    FreeCAD.ActiveDocument.getObject(SketchLabel).Visibility = False
    
    return Body_obj
    
def make_brick(studs_x, studs_y, plate_z, studs_t, type_of_brick):
    # name the slope brick   
    
    brick_name = name_a_slope_brick(studs_x, studs_y, plate_z, studs_t, type_of_brick)
    # print("Debug los Gehts mit",brick_name)
    
    # start as if it is a regular brick
    huelle = create_brick_hull(brick_name)

    
    compound_list = []
    
#    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
#    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    
    # compound_list.append(create_brick_hull(brick_name))
    match type_of_brick:
        case 'dslope':
            print('dslope:')
        case 'tile':
            print("tile:")
        case _:
            compound_list += add_brick_studs(brick_name)
            print("_: Diferenz Studs x - t:",studs_x-studs_t)
        
        
        
    print("Add Rings")
    compound_list += add_brick_rings(brick_name)

    ende = len(compound_list)
    # print("LEN:",ende,compound_list)
    
    for i in range(0,ende):
        # print("Debug For",i,compound_list[i].Name,compound_list[i].Label)
        make_part_Boolean(huelle.Name, compound_list[i].Name, brick_name+"_plus"+str(i), 0)

    huelle.Label = brick_name + '_brick'
    
    # brick is finished, so create a compound object with the name of the brick
    FreeCAD.ActiveDocument.recompute()
    
    
    match type_of_brick:
        case 'slope' | 'dslope':
            print("^^^^^^^^^^^^^^^^^^^^",studs_x, studs_y, plate_z, studs_t, type_of_brick,"^^^^^^^^^^^^")
            
            # print("################################## CUT beginnt")
        #    # create the cutout
            # print("create the cutout")
            cutout_part = create_slope_cutout(brick_name)
            FreeCAD.ActiveDocument.recompute()
        #    # cut the pad from the brick
            # print("cutout_part Label Name",cutout_part.Label,cutout_part.Name)
            # print("huelle Label Name",huelle.Label,huelle.Name)
        #    

            outer_width  = convert_studs_to_mm(studs_x)
            outer_length = convert_studs_to_mm(studs_y)
            outer_height = 1 * plate_height_mm

            TempBox = make_box(brick_name+'_boxtemp', brick_name+'_box_temp', outer_length, outer_width, outer_height)
            TempBox.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
            
            print("TempBox",TempBox.Name,TempBox.Label,TempBox.BaseFeature)
            print("cutout_part",cutout_part.Name,cutout_part.Label,cutout_part.BaseFeature)
                   
            make_part_Boolean(huelle.Name, TempBox.Name, brick_name+"_put_slope", 0)               
            
            make_part_Boolean(huelle.Name, cutout_part.Name, brick_name+"_cut_slope", 1)
            
            roof_part = create_slope_roof(brick_name)
            
            # print("roof_part",roof_part.Label,roof_part.Name)
            make_part_Boolean(huelle.Name, roof_part.Name, brick_name+"_put_roof", 0)

            TempBox = make_box(brick_name+'_boxtemp_d', brick_name+'_box_temp_d', outer_length, outer_width, outer_height)
            TempBox.Placement = FreeCAD.Placement(Vector(outer_width,0,-outer_height),FreeCAD.Rotation(Vector(0,0,0),90.000))
            
            make_part_Boolean(huelle.Name, TempBox.Name, brick_name+"_put_slope_d", 1) 
            
            FreeCAD.ActiveDocument.recompute()
            # print("################################## CUT beendet")
        case _:
            print("°°°°°°°°°°°°°°°°°°°°°°",studs_x, studs_y, plate_z, studs_t, type_of_brick,"°°°°°°°°°°°°")
    

#    # Put it next to the previous objects (instead of all at 0,0)
    global offset
#    # print("FreeCAD.Placement")
    huelle.Placement = FreeCAD.Placement(Vector((brick_width_mm * offset), 0, 0), FreeCAD.Rotation(0,0,0), Vector(0,0,0))
    offset += studs_x + 2

