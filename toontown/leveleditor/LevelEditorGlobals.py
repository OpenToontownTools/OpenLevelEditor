import string
from pandac.PandaModules import *

# Valid Toontown projects
TOONTOWN_ONLINE = 0
TOONTOWN_REWRITTEN = 1
TOONTOWN_CORPORATE_CLASH = 2
TOONTOWN_OFFLINE = 3

SERVER_TO_ID = {'online': TOONTOWN_ONLINE,
                'rewritten': TOONTOWN_REWRITTEN,
                'clash': TOONTOWN_CORPORATE_CLASH,
                'offline': TOONTOWN_OFFLINE}

HOOD_NAME_SHORTHAND = 'name_shorthand'
HOOD_NAME_LONGHAND = 'name_longhand'
HOOD_PATH = 'storage_files'


# Colors used by all color menus
DEFAULT_COLORS = [
    Vec4(1, 1, 1, 1),
    Vec4(0.75, 0.75, 0.75, 1.0),
    Vec4(0.5, 0.5, 0.5, 1.0),
    Vec4(0.25, 0.25, 0.25, 1.0)
    ]
# The list of items with color attributes
COLOR_TYPES = ['wall_color', 'window_color',
               'window_awning_color', 'sign_color', 'door_color',
               'door_awning_color', 'cornice_color',
               'prop_color']
# The list of dna components maintained in the style attribute dictionary
DNA_TYPES = ['wall', 'window', 'sign', 'door_double', 'door_single', 'cornice', 'toon_landmark',
             'anim_building', 'prop', 'anim_prop', 'interactive_prop', 'street']
BUILDING_TYPES = ['10_10', '20', '10_20', '20_10', '10_10_10',
                  '4_21', '3_22', '4_13_8', '3_13_9', '10',
                  '12_8', '13_9_8', '4_10_10', '4_10', '4_20',
                  ]
BUILDING_HEIGHTS = [10, 14, 20, 24, 25, 30]
NUM_WALLS = [1, 2, 3]
LANDMARK_SPECIAL_TYPES = ['', 'hq', 'gagshop', 'clotheshop', 'petshop', 'kartshop']
# Corporate Clash has an UNCAPTURABLE building type to flag uncapturable buildings
if base.server == TOONTOWN_CORPORATE_CLASH:
    LANDMARK_SPECIAL_TYPES.append('uncapturable')

OBJECT_SNAP_POINTS = {
    'street_5x20'                 : [(Vec3(5.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_10x20'                : [(Vec3(10.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_20x20'                : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_30x20'                : [(Vec3(30.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_40x20'                : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_80x20'                : [(Vec3(80.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_5x40'                 : [(Vec3(5.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_10x40'                : [(Vec3(10.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_20x40'                : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_20x40_15'             : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_30x40'                : [(Vec3(30.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_40x40'                : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_20x60'                : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_40x60'                : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_40x40_15'             : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_80x40'                : [(Vec3(80.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_angle_30'             : [(Vec3(0), Vec3(-30, 0, 0)),
                                     (Vec3(0), Vec3(0))],
    'street_angle_45'             : [(Vec3(0), Vec3(-45, 0, 0)),
                                     (Vec3(0), Vec3(0))],
    'street_angle_60'             : [(Vec3(0), Vec3(-60, 0, 0)),
                                     (Vec3(0), Vec3(0))],
    'street_inner_corner'         : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_outer_corner'         : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_full_corner'          : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_tight_corner'         : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_tight_corner_mirror'  : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_double_corner'        : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_curved_corner'        : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_curved_corner_15'     : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_t_intersection'       : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_y_intersection'       : [(Vec3(30.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_street_20x20'         : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_street_40x40'         : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_sidewalk_20x20'       : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_sidewalk_40x40'       : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_divided_transition'   : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_divided_40x70'        : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_divided_transition_15': [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_divided_40x70_15'     : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_stairs_40x10x5'       : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_4way_intersection'    : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_incline_40x40x5'      : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_square_courtyard'     : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_70'         : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_70_exit'    : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_90'         : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_90_exit'    : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_70_15'      : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_70_15_exit' : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_90_15'      : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_courtyard_90_15_exit' : [(Vec3(0.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_50_transition'        : [(Vec3(10.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_20x50'                : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_40x50'                : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_keyboard_10x40'       : [(Vec3(10.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_keyboard_20x40'       : [(Vec3(20.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_keyboard_40x40'       : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    'street_sunken_40x40'         : [(Vec3(40.0, 0, 0), Vec3(0)),
                                     (Vec3(0), Vec3(0))],
    }

# Precompute class types for type comparisons
DNA_CORNICE = DNACornice.getClassType()
DNA_DOOR = DNADoor.getClassType()
DNA_FLAT_DOOR = DNAFlatDoor.getClassType()
DNA_FLAT_BUILDING = DNAFlatBuilding.getClassType()
DNA_NODE = DNANode.getClassType()
DNA_GROUP = DNAGroup.getClassType()
DNA_VIS_GROUP = DNAVisGroup.getClassType()
DNA_LANDMARK_BUILDING = DNALandmarkBuilding.getClassType()
DNA_ANIM_BUILDING = DNAAnimBuilding.getClassType()
DNA_NODE = DNANode.getClassType()
DNA_PROP = DNAProp.getClassType()
DNA_ANIM_PROP = DNAAnimProp.getClassType()
DNA_INTERACTIVE_PROP = DNAInteractiveProp.getClassType()
DNA_SIGN = DNASign.getClassType()
DNA_SIGN_BASELINE = DNASignBaseline.getClassType()
DNA_SIGN_TEXT = DNASignText.getClassType()
DNA_SIGN_GRAPHIC = DNASignGraphic.getClassType()
DNA_STREET = DNAStreet.getClassType()
DNA_WALL = DNAWall.getClassType()
DNA_WINDOWS = DNAWindows.getClassType()

SUB_DNAS = [DNA_CORNICE,
            DNA_DOOR,
            DNA_FLAT_DOOR,
            DNA_SIGN,
            DNA_SIGN_BASELINE,
            DNA_SIGN_TEXT,
            DNA_SIGN_GRAPHIC,
            DNA_WALL,
            DNA_WINDOWS]



CONTROLS = '''
--Camera--
Note: All camera transformations orbit the currently selected object
Translate Camera: Alt + Middle Click and Drag
Rotate / Orbit Camera: Alt + Left Click and Drag
Zoom Camera: Alt + Right Click and Drag

--Object Insertion--
Move insertion point to currently selected object's origin: A
Move object back to insertion point: J

--Transform--
Translate X/Y by 5 units: [Up, Down, Left, or Right]
Translate X/Y by 1 unit: Shift + [Up, Down, Left, or Right]
Translate Z by 5 units: Control + [Up or Down]
Translate Z by 1 unit: Control + [Left (UP) or Right (DOWN)]
Rotate by 15 degrees: Control + Shift + [Left or Right]
Rotate by 1 degree: Control + Shift + [Up or Down]
Scale: Control + Hold Left Click + Drag
Note: you can use the [Place Selected] button to position using coordinates

--Walls--
Change full wall preset: Hold Right Click on anywhere BUT the selected wall
Change wall section preset: Hold Right Click on wall section
Change wall section texture: Shift + Hold Right Click on wall section
Change knock-knock door: Hold Right Click near bottom center of wall piece
Change windows: Hold Right Click near center of wall piece
Change number of windows: Shift + Hold right click near center of wall piece
Change cornice: Hold Right Rlick at top of wall piece
Change color of part: Control + Hold right click in the same area you would to change the texture
Change Width of wall: Shift + Hold Right click anywhere BUT the wall.
Change direction of wall part: Alt + Hold Right Click on part (MayaCam MUST be disabled)

--Landmark Buildings--
Change door: Hold Right Click bottom half of building
Change sign background: Hold Right Click on top half of building

--Flat Building Linking--
Toggle Flat Building Linking mode: Shift + K
Select Landmark Building to link to: Left Click
Link Flat Building to Landmark Building: Left click Flat Building and press K

--All Objects--
Change Color: Control + Hold Right Click on object

--Suits--
Place Suit Point: Shift + S
Place Battle Cell: Shift + C

--Misc--
Toggle Collision Boundaries: Control + C
Save: Control + S
Screenshot: F12
'''


# DNA Utility functions (possible class extensions?)
def DNARemoveChildren(dnaObject):
    """ Utility function to delete all the children of a DNANode """
    children = []
    for i in range(dnaObject.getNumChildren()):
        children.append(dnaObject.at(i))
    for child in children:
        dnaObject.remove(child)
        DNASTORE.removeDNAGroup(child)


def DNARemoveChildOfClass(dnaNode, classType, childNum = 0):
    """ Remove the nth object of that type you come across """
    childCount = 0
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            if childCount == childNum:
                dnaNode.remove(child)
                DNASTORE.removeDNAGroup(child)
                return 1
            childCount = childCount + 1
    # None found
    return 0


def DNARemoveAllChildrenOfClass(dnaNode, classType, notFromLoading = True):
    """ Remove the objects of that type """
    children = []
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            children.append(child)
    for child in children:
        dnaNode.remove(child)
        # [gjeon] because in new LE when this function is called during loading
        # we shouldn't remove dna group from the stroage since it's not added at first
        if notFromLoading:
            DNASTORE.removeDNAGroup(child)


def DNAGetChildren(dnaNode, classType = None):
    """ Return the objects of that type """
    children = []
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if ((not classType)
                or DNAClassEqual(child, classType)):
            children.append(child)
    return children


def DNAGetChild(dnaObject, type = DNA_NODE, childNum = 0):
    childCount = 0
    for i in range(dnaObject.getNumChildren()):
        child = dnaObject.at(i)
        if DNAClassEqual(child, type):
            if childCount == childNum:
                return child
            childCount = childCount + 1
    # Not found
    return None


def DNAGetChildRecursive(dnaObject, type = DNA_NODE, childNum = 0):
    childCount = 0
    for i in range(dnaObject.getNumChildren()):
        child = dnaObject.at(i)
        if DNAClassEqual(child, type):
            if childCount == childNum:
                return child
            childCount = childCount + 1
        else:
            child = DNAGetChildRecursive(child, type, childNum - childCount)
            if child:
                return child

    # Not found
    return None


def DNAGetChildOfClass(dnaNode, classType):
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            return child
    # Not found
    return None


def DNAGetClassType(dnaObject):
    return dnaObject.__class__.getClassType()


def DNAClassEqual(dnaObject, classType):
    return DNAGetClassType(dnaObject) == (classType)


def DNAIsDerivedFrom(dnaObject, classType):
    return DNAGetClassType(dnaObject).isDerivedFrom(classType)


def DNAGetWallHeights(aDNAFlatBuilding):
    """ Get a list of wall heights for a given flat building """
    # Init variables
    heightList = []
    offsetList = []
    offset = 0.0
    # Compute wall heights
    for i in range(aDNAFlatBuilding.getNumChildren()):
        child = aDNAFlatBuilding.at(i)
        if DNAClassEqual(child, DNA_WALL):
            height = child.getHeight()
            heightList.append(height)
            offsetList.append(offset)
            offset = offset + height
    return heightList, offsetList


def DNAGetBaselineString(baseline):
    s = ""
    for i in range(baseline.getNumChildren()):
        child = baseline.at(i)
        if DNAClassEqual(child, DNA_SIGN_TEXT):
            s = s + child.getLetters()
        elif DNAClassEqual(child, DNA_SIGN_GRAPHIC):
            s = s + '[' + child.getCode() + ']'
    return s


def DNASetBaselineString(baseline, text):
    # TODO: Instead of removing all the text and replacing it,
    # replace each text item and then add or remove at the end.
    # This should allow inlined graphics to stay in place.
    # end of todo.
    DNARemoveAllChildrenOfClass(baseline, DNA_SIGN_TEXT)

    # We can't just blindly iterate through the text, because it might
    # be utf-8 encoded, meaning some characters are represented using
    # multi-byte sequences.  Instead, create a TextNode and use it to
    # iterate through the characters of the text.
    t = TextNode('')
    t.setText(text)
    for i in range(t.getNumChars()):
        ch = t.getEncodedChar(i)
        text = DNASignText("text")
        text.setLetters(ch)
        baseline.add(text)


def importModule(dcImports, moduleName, importSymbols):
    """
    Imports the indicated moduleName and all of its symbols
    into the current namespace.  This more-or-less reimplements
    the Python import command.
    """

    # RAU copied from $DIRECT/src/distributed/ConnectionRepository
    module = __import__(moduleName, globals(), locals(), importSymbols)

    if importSymbols:
        # "from moduleName import symbolName, symbolName, ..."
        # Copy just the named symbols into the dictionary.
        if importSymbols == ['*']:
            # "from moduleName import *"
            if hasattr(module, "__all__"):
                importSymbols = module.__all__
            else:
                importSymbols = list(module.__dict__.keys())

        for symbolName in importSymbols:
            if hasattr(module, symbolName):
                dcImports[symbolName] = getattr(module, symbolName)
            else:
                raise Exception('Symbol %s not defined in module %s.' % (symbolName, moduleName))
    else:
        # "import moduleName"

        # Copy the root module name into the dictionary.

        # Follow the dotted chain down to the actual module.
        components = moduleName.split('.')
        dcImports[components[0]] = module
