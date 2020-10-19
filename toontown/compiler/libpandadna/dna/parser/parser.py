import os
from toontown.compiler.libpandadna.dna.components.DNAAnimBuilding import DNAAnimBuilding
from toontown.compiler.libpandadna.dna.components.DNAAnimProp import DNAAnimProp
from toontown.compiler.libpandadna.dna.components.DNABattleCell import DNABattleCell
from toontown.compiler.libpandadna.dna.components.DNACornice import DNACornice
from toontown.compiler.libpandadna.dna.components.DNADoor import DNADoor
from toontown.compiler.libpandadna.dna.components.DNAFlatBuilding import DNAFlatBuilding
from toontown.compiler.libpandadna.dna.components.DNAFlatDoor import DNAFlatDoor
from toontown.compiler.libpandadna.dna.components.DNAGroup import DNAGroup
from toontown.compiler.libpandadna.dna.components.DNAInteractiveProp import DNAInteractiveProp
from toontown.compiler.libpandadna.dna.components.DNALandmarkBuilding import DNALandmarkBuilding
from toontown.compiler.libpandadna.dna.components.DNANode import DNANode
from toontown.compiler.libpandadna.dna.components.DNAProp import DNAProp
from toontown.compiler.libpandadna.dna.components.DNASign import DNASign
from toontown.compiler.libpandadna.dna.components.DNASignBaseline import DNASignBaseline
from toontown.compiler.libpandadna.dna.components.DNASignGraphic import DNASignGraphic
from toontown.compiler.libpandadna.dna.components.DNASignText import DNASignText
from toontown.compiler.libpandadna.dna.components.DNAStreet import DNAStreet
from toontown.compiler.libpandadna.dna.components.DNASuitPoint import DNASuitPoint
from toontown.compiler.libpandadna.dna.components.DNAVisGroup import DNAVisGroup
from toontown.compiler.libpandadna.dna.components.DNAWall import DNAWall
from toontown.compiler.libpandadna.dna.components.DNAWindows import DNAWindows


def p_dna(p):
    pass
p_dna.__doc__ = '''\
dna : dna object
    | object'''


def p_object(p):
    p[0] = p[1]
p_object.__doc__ = '''\
object : suitpoint
       | group
       | model
       | font
       | store_texture'''


def p_number(p):
    p[0] = p[1]
p_number.__doc__ = '''\
number : FLOAT
       | INTEGER'''


def p_lpoint3f(p):
    lpoint3f = (p[1], p[2], p[3])
    p[0] = lpoint3f
p_lpoint3f.__doc__ = '''\
lpoint3f : number number number'''


def p_suitpoint(p):
    argCount = len(p)
    if argCount == 9:
        index = p[3]
        pointTypeStr = p[5]
        pos = p[7]
        landmarkBuildingIndex = -1
    else:
        index = p[3]
        pointTypeStr = p[5]
        pos = p[7]
        landmarkBuildingIndex = p[9]
    point = DNASuitPoint(index, pointTypeStr, pos,
                         landmarkBuildingIndex=landmarkBuildingIndex)
    p.parser.dnaStore.storeSuitPoint(point)
p_suitpoint.__doc__ = '''\
suitpoint : STORE_SUIT_POINT "[" number "," suitpointtype "," lpoint3f "]"
          | STORE_SUIT_POINT "[" number "," suitpointtype "," lpoint3f "," number "]"'''


def p_suitpointtype(p):
    pointTypeStr = p[1]
    p[0] = DNASuitPoint.pointTypeMap[pointTypeStr]
p_suitpointtype.__doc__ = '''\
suitpointtype : STREET_POINT
              | FRONT_DOOR_POINT
              | SIDE_DOOR_POINT
              | COGHQ_IN_POINT
              | COGHQ_OUT_POINT'''


def p_string(p):
    p[0] = p[1]
p_string.__doc__ = '''\
string : QUOTED_STRING
       | UNQUOTED_STRING'''


def p_dnagroupdef(p):
    name = p[2]
    p[0] = DNAGroup(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_dnagroupdef.__doc__ = '''\
dnagroupdef : GROUP string'''


def p_dnanodedef(p):
    name = p[2]
    p[0] = DNANode(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_dnanodedef.__doc__ = '''\
dnanodedef : NODE string'''


def p_visgroupdef(p):
    name = p[2]
    p[0] = DNAVisGroup(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_visgroupdef.__doc__ = '''\
visgroupdef : VISGROUP string'''


def p_dnagroup(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_dnagroup.__doc__ = '''\
dnagroup : dnagroupdef "[" subgroup_list "]"'''


def p_visgroup(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_visgroup.__doc__ = '''\
visgroup : visgroupdef "[" subvisgroup_list "]"'''


def p_string_opt_list(p):
    argCount = len(p)
    if argCount == 2:
        p[0] = []
    elif (argCount == 3) and (p[2] is not None):
        p[0] = p[1]
        p[0].append(p[2])
p_string_opt_list.__doc__ = '''\
string_opt_list : string_opt_list string
                | empty'''


def p_vis(p):
    parentVis, visList = p[3], p[4]
    p.parser.parentGroup.addVisible(parentVis)
    for vis in visList:
        p.parser.parentGroup.addVisible(vis)
p_vis.__doc__ = '''\
vis : VIS "[" string string_opt_list "]"'''


def p_empty(p):
    pass
p_empty.__doc__ = '''\
empty : '''


def p_group(p):
    p[0] = p[1]
p_group.__doc__ = '''\
group : dnagroup
      | visgroup
      | dnanode
      | windows
      | cornice
      | door'''


def p_dnanode(p):
    p[0] = p[1]
p_dnanode.__doc__ = '''\
dnanode : prop
        | sign
        | signbaseline
        | signtext
        | flatbuilding
        | wall
        | landmarkbuilding
        | street
        | signgraphic
        | dnanode_grp'''


def p_dnanode_grp(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_dnanode_grp.__doc__ = '''\
dnanode_grp : dnanodedef "[" subdnanode_list "]"'''


def p_sign(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_sign.__doc__ = '''\
sign : signdef "[" subprop_list "]"'''


def p_signgraphic(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_signgraphic.__doc__ = '''\
signgraphic : signgraphicdef "[" subsigngraphic_list "]"'''


def p_prop(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_prop.__doc__ = '''\
prop : propdef "[" subprop_list "]"
     | animpropdef "[" subanimprop_list "]"
     | interactivepropdef "[" subinteractiveprop_list "]"'''


def p_signbaseline(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_signbaseline.__doc__ = '''\
signbaseline : baselinedef "[" subbaseline_list "]"'''


def p_signtest(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_signtest.__doc__ = '''\
signtext : signtextdef "[" subtext_list "]"'''


def p_flatbuilding(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_flatbuilding.__doc__ = '''\
flatbuilding : flatbuildingdef "[" subflatbuilding_list "]"'''


def p_wall(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_wall.__doc__ = '''\
wall : walldef "[" subwall_list "]"'''


def p_windows(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_windows.__doc__ = '''\
windows : windowsdef "[" subwindows_list "]"'''


def p_cornice(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_cornice.__doc__ = '''\
cornice : cornicedef "[" subcornice_list "]"'''


def p_landmarkbuilding(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_landmarkbuilding.__doc__ = '''\
landmarkbuilding : landmarkbuildingdef "[" sublandmarkbuilding_list "]"
                 | animbuildingdef "[" subanimbuilding_list "]"'''


def p_street(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_street.__doc__ = '''\
street : streetdef "[" substreet_list "]"'''


def p_door(p):
    p[0] = p[1]
    p.parser.parentGroup = p[0].parent
p_door.__doc__ = '''\
door : doordef "[" subdoor_list "]"
     | flatdoordef "[" subdoor_list "]"'''


def p_propdef(p):
    name = p[2]
    p[0] = DNAProp(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_propdef.__doc__ = '''\
propdef : PROP string'''


def p_animpropdef(p):
    name = p[2]
    p[0] = DNAAnimProp(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_animpropdef.__doc__ = '''\
animpropdef : ANIM_PROP string'''


def p_interactivepropdef(p):
    name = p[2]
    p[0] = DNAInteractiveProp(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_interactivepropdef.__doc__ = '''\
interactivepropdef : INTERACTIVE_PROP string'''


def p_flatbuildingdef(p):
    name = p[2]
    p[0] = DNAFlatBuilding(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_flatbuildingdef.__doc__ = '''\
flatbuildingdef : FLAT_BUILDING string'''


def p_walldef(p):
    p[0] = DNAWall('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_walldef.__doc__ = '''\
walldef : WALL'''


def p_windowsdef(p):
    p[0] = DNAWindows('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_windowsdef.__doc__ = '''\
windowsdef : WINDOWS'''


def p_cornicedef(p):
    p[0] = DNACornice('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_cornicedef.__doc__ = '''\
cornicedef : CORNICE'''


def p_landmarkbuildingdef(p):
    name = p[2]
    p[0] = DNALandmarkBuilding(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
    blockNumber = int(p.parser.dnaStore.getBlock(name))
    p.parser.dnaStore.storeBlockNumber(blockNumber)
    zoneId = 0
    try:
        zoneId = int(p[0].getVisGroup().name.split(':')[0])
    except:
        pass
    finally:
        p.parser.dnaStore.storeBlockZone(blockNumber, zoneId)
p_landmarkbuildingdef.__doc__ = '''\
landmarkbuildingdef : LANDMARK_BUILDING string'''


def p_animbuildingdef(p):
    name = p[2]
    p[0] = DNAAnimBuilding(name)
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
    blockNumber = int(p.parser.dnaStore.getBlock(name))
    p.parser.dnaStore.storeBlockNumber(blockNumber)
    zoneId = int(p[0].getVisGroup().name.split(':')[0])
    p.parser.dnaStore.storeBlockZone(blockNumber, zoneId)
p_animbuildingdef.__doc__ = '''\
animbuildingdef : ANIM_BUILDING string'''


def p_doordef(p):
    p[0] = DNADoor('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_doordef.__doc__ = '''\
doordef : DOOR'''


def p_flatdoordef(p):
    p[0] = DNAFlatDoor('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup.parent.setHasDoor(True)
    p.parser.parentGroup = p[0]
p_flatdoordef.__doc__ = '''\
flatdoordef : FLAT_DOOR'''


def p_streetdef(p):
    p[0] = DNAStreet(p[2])
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_streetdef.__doc__ = '''\
streetdef : STREET string'''


def p_signdef(p):
    p[0] = DNASign()
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_signdef.__doc__ = '''\
signdef : SIGN'''


def p_signgraphicdef(p):
    p[0] = DNASignGraphic('')
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_signgraphicdef.__doc__ = '''\
signgraphicdef : GRAPHIC'''


def p_baselinedef(p):
    p[0] = DNASignBaseline()
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_baselinedef.__doc__ = '''\
baselinedef : BASELINE'''


def p_signtextdef(p):
    p[0] = DNASignText()
    p.parser.parentGroup.add(p[0])
    p[0].setParent(p.parser.parentGroup)
    p.parser.parentGroup = p[0]
p_signtextdef.__doc__ = '''\
signtextdef : TEXT'''


def p_suitedge(p):
    startPointIndex, endPointIndex = p[3], p[4]
    zoneId = int(p.parser.parentGroup.name)
    edge = p.parser.dnaStore.storeSuitEdge(
        startPointIndex, endPointIndex, zoneId)
    p.parser.parentGroup.addSuitEdge(edge)
p_suitedge.__doc__ = '''\
suitedge : SUIT_EDGE "[" number number "]"'''


def p_battlecell(p):
    width, height, pos = p[3], p[4], p[5]
    p[0] = DNABattleCell(width, height, pos)
    p.parser.parentGroup.addBattleCell(p[0])
p_battlecell.__doc__ = '''\
battlecell : BATTLE_CELL "[" number number lpoint3f "]"'''


def p_subgroup_list(p):
    p[0] = p[1]
    argCount = len(p)
    if argCount == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subgroup_list.__doc__ = '''\
subgroup_list : subgroup_list group
              | empty'''


def p_subvisgroup_list(p):
    p[0] = p[1]
    argCount = len(p)
    if argCount == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subvisgroup_list.__doc__ = '''\
subvisgroup_list : subvisgroup_list group
                 | subvisgroup_list suitedge
                 | subvisgroup_list battlecell
                 | subvisgroup_list vis
                 | empty'''


def p_pos(p):
    p.parser.parentGroup.setPos(p[3])
p_pos.__doc__ = '''\
pos : POS "[" lpoint3f "]"'''


def p_hpr(p):
    p.parser.parentGroup.setHpr(p[3])
p_hpr.__doc__ = '''\
hpr : HPR "[" lpoint3f "]"
    | NHPR "[" lpoint3f "]"'''


def p_scale(p):
    p.parser.parentGroup.setScale(p[3])
p_scale.__doc__ = '''\
scale : SCALE "[" lpoint3f "]"'''


def p_flags(p):
    p.parser.parentGroup.setFlags(p[3])
p_flags.__doc__ = '''\
flags : FLAGS "[" string "]"'''


def p_dnanode_sub(p):
    p[0] = p[1]
p_dnanode_sub.__doc__ = '''\
dnanode_sub : group
            | pos
            | hpr
            | scale'''


def p_dnaprop_sub(p):
    p[0] = p[1]
p_dnaprop_sub.__doc__ = '''\
dnaprop_sub : code
            | color'''


def p_dnaanimprop_sub(p):
    p[0] = p[1]
p_dnaanimprop_sub.__doc__ = '''\
dnaanimprop_sub : anim'''


def p_dnainteractiveprop_sub(p):
    p[0] = p[1]
p_dnainteractiveprop_sub.__doc__ = '''\
dnainteractiveprop_sub : cell_id'''


def p_anim(p):
    p.parser.parentGroup.setAnim(p[3])
p_anim.__doc__ = '''\
anim : ANIM "[" string "]"'''


def p_cell_id(p):
    p.parser.parentGroup.setCellId(p[3])
p_cell_id.__doc__ = '''\
cell_id : CELL_ID "[" number "]"'''


def p_baseline_sub(p):
    p[0] = p[1]
p_baseline_sub.__doc__ = '''\
baseline_sub : code
             | color
             | width
             | height
             | indent
             | kern
             | stomp
             | stumble
             | wiggle
             | flags'''


def p_text_sub(p):
    p[0] = p[1]
p_text_sub.__doc__ = '''\
text_sub : letters'''


def p_signgraphic_sub(p):
    p[0] = p[1]
p_signgraphic_sub.__doc__ = '''\
signgraphic_sub : width
                | height
                | code
                | color'''


def p_flatbuilding_sub(p):
    p[0] = p[1]
p_flatbuilding_sub.__doc__ = '''\
flatbuilding_sub : width'''


def p_wall_sub(p):
    p[0] = p[1]
p_wall_sub.__doc__ = '''\
wall_sub : height
         | code
         | color'''


def p_windows_sub(p):
    p[0] = p[1]
p_windows_sub.__doc__ = '''\
windows_sub : code
            | color
            | windowcount'''


def p_cornice_sub(p):
    p[0] = p[1]
p_cornice_sub.__doc__ = '''\
cornice_sub : code
            | color'''


def p_landmarkbuilding_sub(p):
    p[0] = p[1]
p_landmarkbuilding_sub.__doc__ = '''\
landmarkbuilding_sub : code
                     | title
                     | article
                     | building_type
                     | wall_color'''


def p_animbuilding_sub(p):
    p[0] = p[1]
p_animbuilding_sub.__doc__ = '''\
animbuilding_sub : anim'''


def p_door_sub(p):
    p[0] = p[1]
p_door_sub.__doc__ = '''\
door_sub : code
         | color'''


def p_street_sub(p):
    p[0] = p[1]
p_street_sub.__doc__ = '''\
street_sub : code
           | texture
           | color'''


def p_texture(p):
    p.parser.parentGroup.setTexture(p[3])
p_texture.__doc__ = '''\
texture : TEXTURE "[" string "]"'''


def p_title(p):
    title = p[3]
    p.parser.parentGroup.setTitle(title)
    parentName = p.parser.parentGroup.name
    blockNumber = int(p.parser.dnaStore.getBlock(parentName))
    p.parser.dnaStore.storeBlockTitle(blockNumber, title)
p_title.__doc__ = '''\
title : TITLE "[" string "]"'''


def p_article(p):
    article = p[3]
    p.parser.parentGroup.setArticle(article)
    parentName = p.parser.parentGroup.name
    blockNumber = int(p.parser.dnaStore.getBlock(parentName))
    p.parser.dnaStore.storeBlockArticle(blockNumber, article)
p_article.__doc__ = '''\
article : ARTICLE "[" string "]"'''


def p_building_type(p):
    buildingType = p[3]
    p.parser.parentGroup.setBuildingType(buildingType)
    parentName = p.parser.parentGroup.name
    blockNumber = int(p.parser.dnaStore.getBlock(parentName))
    p.parser.dnaStore.storeBlockBuildingType(blockNumber, buildingType)
p_building_type.__doc__ = '''\
building_type : BUILDING_TYPE "[" string "]"'''


def p_wall_color(p):
    wallColor = (p[3], p[4], p[5], p[6])
    p.parser.parentGroup.setWallColor(wallColor)
p_wall_color.__doc__ = '''\
wall_color : COLOR "[" number number number number "]"'''


def p_count(p):
    p.parser.parentGroup.setWindowCount(p[3])
p_count.__doc__ = '''\
windowcount : COUNT "[" number "]"'''


def p_letters(p):
    p.parser.parentGroup.setLetters(p[3])
p_letters.__doc__ = '''\
letters : LETTERS "[" string "]"'''


def p_width(p):
    p.parser.parentGroup.setWidth(p[3])
p_width.__doc__ = '''\
width : WIDTH "[" number "]"'''


def p_height(p):
    p.parser.parentGroup.setHeight(p[3])
p_height.__doc__ = '''\
height : HEIGHT "[" number "]"'''


def p_stomp(p):
    p.parser.parentGroup.setStomp(p[3])
p_stomp.__doc__ = '''\
stomp : STOMP "[" number "]"'''


def p_indent(p):
    p.parser.parentGroup.setIndent(p[3])
p_indent.__doc__ = '''\
indent : INDENT "[" number "]"'''


def p_kern(p):
    p.parser.parentGroup.setKern(p[3])
p_kern.__doc__ = '''\
kern : KERN "[" number "]"'''


def p_stumble(p):
    p.parser.parentGroup.setStumble(p[3])
p_stumble.__doc__ = '''\
stumble : STUMBLE "[" number "]"'''


def p_wiggle(p):
    p.parser.parentGroup.setWiggle(p[3])
p_wiggle.__doc__ = '''\
wiggle : WIGGLE "[" number "]"'''


def p_code(p):
    p.parser.parentGroup.setCode(p[3])
p_code.__doc__ = '''\
code : CODE "[" string "]"'''


def p_color(p):
    p.parser.parentGroup.setColor((p[3], p[4], p[5], p[6]))
p_color.__doc__ = '''\
color : COLOR "[" number number number number "]"'''


def p_subprop_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subprop_list.__doc__ = '''\
subprop_list : subprop_list dnanode_sub
             | subprop_list dnaprop_sub
             | empty'''


def p_subanimprop_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subanimprop_list.__doc__ = '''\
subanimprop_list : subanimprop_list dnanode_sub
                 | subanimprop_list dnaprop_sub
                 | subanimprop_list dnaanimprop_sub
                 | empty'''


def p_subinteractiveprop_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subinteractiveprop_list.__doc__ = '''\
subinteractiveprop_list : subinteractiveprop_list dnanode_sub
                        | subinteractiveprop_list dnaprop_sub
                        | subinteractiveprop_list dnaanimprop_sub
                        | subinteractiveprop_list dnainteractiveprop_sub
                        | empty'''


def p_subbaseline_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subbaseline_list.__doc__ = '''\
subbaseline_list : subbaseline_list dnanode_sub
                 | subbaseline_list baseline_sub
                 | empty'''


def p_subtext_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subtext_list.__doc__ = '''\
subtext_list : subtext_list dnanode_sub
             | subtext_list text_sub
             | empty'''


def p_subdnanode_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subdnanode_list.__doc__ = '''\
subdnanode_list : subdnanode_list dnanode_sub
                | empty'''


def p_subsigngraphic_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subsigngraphic_list.__doc__ = '''\
subsigngraphic_list : subsigngraphic_list dnanode_sub
                    | subsigngraphic_list signgraphic_sub
                    | empty'''


def p_subflatbuilding_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subflatbuilding_list.__doc__ = '''\
subflatbuilding_list : subflatbuilding_list dnanode_sub
                     | subflatbuilding_list flatbuilding_sub
                     | empty'''


def p_subwall_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subwall_list.__doc__ = '''\
subwall_list : subwall_list dnanode_sub
             | subwall_list wall_sub
             | empty'''


def p_subwindows_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subwindows_list.__doc__ = '''\
subwindows_list : subwindows_list dnanode_sub
                | subwindows_list windows_sub
                | empty'''


def p_subcornice_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subcornice_list.__doc__ = '''\
subcornice_list : subcornice_list dnanode_sub
                | subcornice_list cornice_sub
                | empty'''


def p_sublandmarkbuilding_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_sublandmarkbuilding_list.__doc__ = '''\
sublandmarkbuilding_list : sublandmarkbuilding_list dnanode_sub
                         | sublandmarkbuilding_list landmarkbuilding_sub
                         | empty'''


def p_subanimbuilding_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subanimbuilding_list.__doc__ = '''\
subanimbuilding_list : subanimbuilding_list dnanode_sub
                     | subanimbuilding_list landmarkbuilding_sub
                     | subanimbuilding_list animbuilding_sub
                     | empty'''


def p_subdoor_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_subdoor_list.__doc__ = '''\
subdoor_list : subdoor_list dnanode_sub
             | subdoor_list door_sub
             | empty'''


def p_substreet_list(p):
    p[0] = p[1]
    if len(p) == 3:
        group = p[2]
        p[0].append(group)
    else:
        p[0] = []
p_substreet_list.__doc__ = '''\
substreet_list : substreet_list dnanode_sub
               | substreet_list street_sub
               | empty'''


def p_modeldef(p):
    modelType, filename = p[1], p[2]
    filename, extension = os.path.splitext(filename)
    if not extension:
        extension = '.bam'
    filename += extension
    p.parser.modelType = modelType
    p.parser.modelName = filename
p_modeldef.__doc__ = '''\
modeldef : MODEL string
         | HOODMODEL string
         | PLACEMODEL string'''


def p_model(p):
    pass
p_model.__doc__ = '''\
model : modeldef "[" modelnode_list "]"'''


def p_modelnode_list(p):
    pass
p_modelnode_list.__doc__ = '''\
modelnode_list : modelnode_list node
               | empty'''


def p_node(p):
    argCount = len(p)
    if argCount == 6:
        root, code, search = p[3], p[4], p[4]
    else:
        root, code, search = p[3], p[4], p[5]
    p.parser.dnaStore.storeCatalogCode(root, code)
    modelName = p.parser.modelName
    if p.parser.modelType == 'hood_model':
        p.parser.dnaStore.storeHoodNode(code, modelName, search)
    elif p.parser.modelType == 'place_model':
        p.parser.dnaStore.storePlaceNode(code, modelName, search)
    else:
        p.parser.dnaStore.storeNode(code, modelName, search)
p_node.__doc__ = '''\
node : STORE_NODE "[" string string "]"
     | STORE_NODE "[" string string string "]"'''


def p_store_texture(p):
    argCount = len(p)
    if argCount == 6:
        code, filename = p[3], p[4]
    else:
        root, code, filename = p[3], p[4], p[5]
        p.parser.dnaStore.storeCatalogCode(root, code)
    p.parser.dnaStore.storeTexture(code, filename)
p_store_texture.__doc__ = '''\
store_texture : STORE_TEXTURE "[" string string "]"
              | STORE_TEXTURE "[" string string string "]"'''


def p_font(p):
    root, code, filename = p[3], p[4], p[5]
    filename, extension = os.path.splitext(filename)
    if not extension:
        extension = '.bam'
    filename += extension
    p.parser.dnaStore.storeCatalogCode(root, code)
    p.parser.dnaStore.storeFont(filename, code)
p_font.__doc__ = '''\
font : STORE_FONT "[" string string string "]"'''


def p_error(p):
    if p is None:
        raise DNAError('Syntax error unexpected EOF')
    sub = (str(p.lexer.lineno), str(p))
    raise DNAError('Syntax error at line %s token=%s' % sub)
