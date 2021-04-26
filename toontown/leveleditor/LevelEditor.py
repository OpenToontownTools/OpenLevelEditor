import builtins
import glob
import json
import os
import re
import random
from datetime import datetime
from tkinter.filedialog import *
from tkinter.messagebox import showinfo

from direct.controls import ControlManager
from direct.controls import NonPhysicsWalker
from direct.gui import DirectGui
from panda3d.core import BoundingHexahedron

from otp.otpbase import OTPGlobals
from toontown.hood.GenericAnimatedProp import *
from toontown.toon import RobotToon, LEAvatar
from . import LevelEditorGlobals
from . import LevelEditorPanel
from . import VisGroupsEditor
from .AutoSaver import AutoSaver
from .DNASerializer import DNASerializer
from .EditorUtil import *
from .LevelStyleManager import *
from .PieMenu import *
from .RadialMenu import RadialMenu, RadialItem

# Force direct and tk to be on
base.startDirect(fWantDirect = 1, fWantTk = 1)

visualizeZones = base.config.GetBool("visualize-zones", 0)
dnaBuiltDirectory = Filename.expandFrom(base.config.GetString("dna-built-directory", "$TTMODELS/built"))
useSnowTree = base.config.GetBool("use-snow-tree", 0)

builtins.DNASTORE = DNASTORE = DNAStorage()

loadDNAFile(DNASTORE, 'phase_4/dna/storage.dna', CSDefault, 1)
loadDNAFile(DNASTORE, 'phase_5/dna/storage_town.dna', CSDefault, 1)

builtins.NEIGHBORHOODS = []
NEIGHBORHOOD_CODES = {}
for hood in base.hoods:
    with open(f'{userfiles}/hoods/{hood}.json') as info:
        data = json.load(info)
        hoodName = data.get(LevelEditorGlobals.HOOD_NAME_LONGHAND)
        NEIGHBORHOOD_CODES[hoodName] = hood
        NEIGHBORHOODS.append(hoodName)
        storages = data.get(LevelEditorGlobals.HOOD_PATH)
        # Holidays
        holiday = ConfigVariableString("holiday", "none")
        if LevelEditorGlobals.HOOD_HOLIDAY_PATH in data:
            if holiday == 'halloween':
                if LevelEditorGlobals.HOOD_HALLOWEEN_PATH in data[LevelEditorGlobals.HOOD_HOLIDAY_PATH]:
                    storages += data[LevelEditorGlobals.HOOD_HOLIDAY_PATH][LevelEditorGlobals.HOOD_HALLOWEEN_PATH]
            elif holiday == 'winter':
                if LevelEditorGlobals.HOOD_WINTER_PATH in data[LevelEditorGlobals.HOOD_HOLIDAY_PATH]:
                    storages += data[LevelEditorGlobals.HOOD_HOLIDAY_PATH][LevelEditorGlobals.HOOD_WINTER_PATH]
        for storage in storages:
            loadDNAFile(DNASTORE, storage, CSDefault, 1)

DNASTORE.storeFont('humanist', ToontownGlobals.getInterfaceFont())
DNASTORE.storeFont('mickey', ToontownGlobals.getSignFont())
DNASTORE.storeFont('suit', ToontownGlobals.getSuitFont())
builtins.dnaLoaded = True


class LevelEditor(NodePath, DirectObject):
    """Class used to create a Toontown LevelEditor object"""
    notify = DirectNotifyGlobal.directNotify.newCategory('LevelEditor')

    # Init the list of callbacks:
    selectedNodePathHookHooks = []
    deselectedNodePathHookHooks = []

    # Primary variables:
    # DNAData: DNA object holding DNA info about level
    # DNAToplevel: Top level DNA Node, all DNA objects descend from this node
    # NPToplevel: Corresponding Node Path
    # DNAParent: Current DNA Node that new objects get added to
    # NPParent: Corresponding Node Path
    # DNAVisGroup: Current DNAVisGroup that new objects get added to
    # NPVisGroup: Corresponding Node Path
    # selectedDNARoot: DNA Node of currently selected object
    # selectedNPRoot: Corresponding Node Path
    # DNATarget: Subcomponent being modified by Pie Menu
    def __init__(self):
        # Make the level editor a node path so that you can show/hide
        # The level editor separately from loading/saving the top level node
        # Initialize superclass
        NodePath.__init__(self)
        # Become the new node path
        self.assign(hidden.attachNewNode('LevelEditor'))

        # Enable replaceSelected by default:
        self.replaceSelectedEnabled = 1

        self.removeHookList = [self.landmarkBlockRemove]

        # Start block ID at 0 (it will be incremented before use (to 1)):
        self.landmarkBlock = 0

        # Create ancillary objects
        # Style manager for keeping track of styles/colors
        self.styleManager = LevelStyleManager(NEIGHBORHOODS, NEIGHBORHOOD_CODES)
        # Load neighborhood maps
        self.createLevelMaps()
        # Marker for showing next insertion point
        self.createInsertionMarker()

        self.panel = LevelEditorPanel.LevelEditorPanel(self)

        # Used to store whatever edges and points are loaded in the level
        self.edgeDict = {}
        self.np2EdgeDict = {}
        self.pointDict = {}
        self.point2edgeDict = {}
        self.cellDict = {}

        self.visitedPoints = []
        self.visitedEdges = []

        self.zoneLabels = []
        self.bldgLabels = []
        self.animPropDict = {}

        self.collisionsToggled = False
        self.suitPreviewsToggled = False
        self.orthCam = False

    def startUp(self, dnaPath = None):
        # Initialize LevelEditor variables DNAData, DNAToplevel, NPToplevel
        # DNAParent, NPParent, groupNum, lastAngle
        # Pass in the new toplevel group and don't clear out the old
        # toplevel group (since it doesn't exist yet)
        self.reset(fDeleteToplevel = 0, fCreateToplevel = 1)

        self.orthLens = OrthographicLens()
        self.orthLens.setFilmSize(1024, 1024)
        # The list of events the level editor responds to
        self.actionEvents = [
            # Node path events
            ('preRemoveNodePath', self.removeNodePathHook),
            # Actions in response to DIRECT operations
            ('DIRECT_selectedNodePath', self.selectedNodePathHook),
            ('DIRECT_deselectedNodePath', self.deselectedNodePathHook),
            ('DIRECT_manipulateObjectCleanup', self.updateSelectedPose),
            ('DIRECT_nodePathSetName', self.setName),
            ('DIRECT_activeParent', self.setActiveParent),
            ('DIRECT_reparent', self.reparent),
            ('RGBPanel_setColor', self.setColor),
            # Actions in response to Level Editor Panel operations
            ('SGE_Add Group', self.addGroup),
            ('SGE_Add Vis Group', self.addVisGroup),
            # Actions in response to Pie Menu interaction
            ('select_building_style_all', self.setBuildingStyle),
            ('select_building_type', self.setBuildingType),
            ('select_building_width', self.setBuildingWidth),
            ('select_cornice_color', self.setDNATargetColor),
            ('select_cornice_orientation', self.setDNATargetOrientation),
            ('select_cornice_texture', self.setDNATargetCode, ['cornice']),
            ('select_sign_color', self.setDNATargetColor),
            ('select_sign_orientation', self.setDNATargetOrientation),
            ('select_sign_texture', self.setDNATargetCode, ['sign']),
            ('select_baseline_style', self.panel.setSignBaselineStyle),
            ('select_door_color', self.setDNATargetColor),
            ('select_door_orientation', self.setDNATargetOrientation),
            ('select_door_single_texture', self.setDNATargetCode, ['door']),
            ('select_door_double_texture', self.setDNATargetCode, ['door']),
            ('select_door_awning_texture', self.setDNATargetCode, ['door_awning']),
            ('select_door_awning_color', self.setDNATargetColor),
            ('select_window_color', self.setDNATargetColor),
            ('select_window_count', self.setWindowCount),
            ('select_window_orientation', self.setDNATargetOrientation),
            ('select_window_texture', self.setDNATargetCode, ['windows']),
            ('select_window_awning_texture', self.setDNATargetCode, ['window_awning']),
            ('select_window_awning_color', self.setDNATargetColor),
            ('select_wall_style', self.setWallStyle),
            ('select_wall_color', self.setDNATargetColor),
            ('select_wall_orientation', self.setDNATargetOrientation),
            ('select_wall_texture', self.setDNATargetCode, ['wall']),
            ('select_toon_landmark_texture', self.setDNATargetCode, ['landmark']),
            ('select_toon_landmark_door_color', self.setDNATargetColor),
            ('select_toon_landmark_door_orientation', self.setDNATargetOrientation),
            ('select_landmark_door_texture', self.setDNATargetCode, ['landmark_door']),
            ('select_street_texture', self.setDNATargetCode, ['street']),
            ('select_prop_texture', self.setDNATargetCode, ['prop']),
            ('select_prop_color', self.setDNATargetColor),
            # All Hot key actions
            # Translate X,Y Axis Functions Per Grid Spacing
            ('arrow_left', self.keyboardXformSelected, ['left', 'xlate']),
            ('arrow_right', self.keyboardXformSelected, ['right', 'xlate']),
            ('arrow_up', self.keyboardXformSelected, ['up', 'xlate']),
            ('arrow_down', self.keyboardXformSelected, ['down', 'xlate']),
            # Translate X,Y Axis Functions Per One(1) Panda Unit
            ('shift-arrow_left', self.keyboardXformSelected, ['left', 'xlate']),
            ('shift-arrow_right', self.keyboardXformSelected, ['right', 'xlate']),
            ('shift-arrow_up', self.keyboardXformSelected, ['up', 'xlate']),
            ('shift-arrow_down', self.keyboardXformSelected, ['down', 'xlate']),
            # Translate Z Axis Functions
            ('control-arrow_up', self.keyboardXformSelected, ['up', 'zlate']),
            ('control-arrow_down', self.keyboardXformSelected, ['down', 'zlate']),
            ('control-arrow_left', self.keyboardXformSelected, ['left', 'zlate']),
            ('control-arrow_right', self.keyboardXformSelected, ['right', 'zlate']),
            # Rotation Z Axis Functions
            ('shift-control-arrow_left', self.keyboardXformSelected, ['left', 'rotate']),
            ('shift-control-arrow_right', self.keyboardXformSelected, ['right', 'rotate']),
            ('shift-control-arrow_up', self.keyboardXformSelected, ['up', 'rotate']),
            ('shift-control-arrow_down', self.keyboardXformSelected, ['down', 'rotate']),
            # Misc Hotkey Functions
            ('a', self.autoPositionGrid),
            ('j', self.jumpToInsertionPoint),
            ('shift-s', self.placeSuitPoint),
            ('shift-c', self.placeBattleCell),
            ('k', self.addToLandmarkBlock),
            ('shift-k', self.toggleShowLandmarkBlock),
            ('%', self.pdbBreak),
            ('page_up', self.pageUp),
            ('page_down', self.pageDown),
            ('shift-o', self.toggleOrth),
            ('f12', self.screenshot),
            ('shift-f12', self.renderMapScaled),
            ('alt-f12', self.renderMap),  # doesnt do automatic stuff, likely wont get used, but just incase
            ('control-c', self.toggleVisibleCollisions),
            ('control-s', DNASerializer.outputDNADefaultFile),
            ('tab', self.enterGlobalRadialMenu),
            ('s', self.beginBoxSelection),
            ('alt-s', self.toggleSuitBuildingPreviews),
            # This already exists, but we will override it to show an input
            ('p', self.setReparentTarget)
            ]

        self.overrideEvents = [
            ('page_up', base.direct),
            ('page_down', base.direct),
            ('p', base.direct)
            ]

        self.labelsOnTop = False
        # Initialize state
        # Make sure direct is running
        base.direct.enable()
        # And only the appropriate handles are showing
        base.direct.widget.disableHandles(['x-ring', 'x-disc',
                                           'y-ring', 'y-disc',
                                           'z-disc', 'z-post'])

        base.direct.grid.setXyzSnap(0)
        base.direct.grid.setHprSnap(0)
        # Initialize camera
        base.camLens.setNear(1.0)
        base.camLens.setFar(3000)
        base.camLens.setMinFov(65)
        base.direct.camera.setPos(0, -10, 10)
        # Initialize drive mode
        self.configureDriveModeCollisionData()
        # Init visibility variables
        self.__zoneId = None
        # Hide (disable) grid initially
        self.showGrid(0)
        # Create variable for vis groups panel
        self.vgpanel = None
        # Start off enabled
        self.enable()

        base.direct.selectedNPReadout['font'] = ToontownGlobals.getToonFont()
        base.direct.activeParentReadout['font'] = ToontownGlobals.getToonFont()
        base.direct.directMessageReadout['font'] = ToontownGlobals.getToonFont()

        # SUIT POINTS
        # Create a sphere model to show suit points
        self.suitPointMarker = loader.loadModel('models/misc/sphere')
        self.suitPointMarker.setScale(0.25)

        # Initialize the suit points
        self.startSuitPoint = None
        self.endSuitPoint = None
        self.currentSuitPointType = DNASuitPoint.STREETPOINT

        # BATTLE CELLS
        self.battleCellMarker = loader.loadModel('models/misc/sphere')
        self.battleCellMarker.setName('battleCellMarker')
        self.currentBattleCellType = "20w 20l"

        # Update panel
        # Editing the first hood id on the list
        self.outputFile = None
        self.setEditMode(NEIGHBORHOODS[0])
        # Start of with first item in lists
        self.panel.streetSelector.selectitem(0)
        self.panel.streetSelector.invoke()
        self.panel.toonBuildingSelector.selectitem(0)
        self.panel.toonBuildingSelector.invoke()
        if hasattr(self.panel, 'landmarkBuildingSelector'):
            self.panel.landmarkBuildingSelector.selectitem(0)
            self.panel.landmarkBuildingSelector.invoke()
        self.panel.propSelector.selectitem(0)
        self.panel.propSelector.invoke()
        # Start off with 20 foot buildings
        self.panel.twentyFootButton.invoke()
        # Update scene graph explorer
        self.panel.sceneGraphExplorer.update()

        # Karting
        # the key is the barricade number,  the data is a two element list,
        # first number is the first bldg group that uses this
        # the second is the last bldg group that uses this
        self.outerBarricadeDict = {}
        self.innerBarricadeDict = {}

        self.mouseMayaCamera = True

        self.fDrive = False

        self.controlManager = None
        self.avatar = None

        self.fov = 65
        self.isPageUp = 0
        self.isPageDown = 0

        # [gjeon] to hold pos for new object
        self.startT = None
        self.startF = None
        self.newObjPos = Point3(0)

        # Load the DNA file passed (normally through an argument)
        if dnaPath:
            DNASerializer.loadDNAFromFile(dnaPath)
            DNASerializer.outputFile = os.path.abspath(dnaPath)

        # box selection stuff
        self.isSelecting: bool = False
        self.boxStartMouse: Tuple[float, float] = (0, 0)
        self.boxEndMouse: Tuple[float, float] = (0, 0)

        AutoSaver.initializeAutoSaver()

    # ENABLE/DISABLE
    def enable(self):
        """ Enable level editing and show level """
        self.reparentTo(base.direct.group)
        self.show()

        for event in self.overrideEvents:
            event[1].ignore(event[0])

        # Add all the action events
        for event in self.actionEvents:
            if len(event) == 3:
                self.accept(event[0], event[1], event[2])
            else:
                self.accept(event[0], event[1])
        self.enableMouse()
        self.spawnInsertionMarkerTask()

    def disable(self):
        """ Disable level editing and hide level """
        base.direct.deselectAll()
        self.reparentTo(hidden)
        for eventPair in self.actionEvents:
            self.ignore(eventPair[0])
        # These are added outside of actionEvents list
        self.ignore('insert')
        self.ignore('space')
        self.disableMouse()
        taskMgr.remove('insertionMarkerTask')

    def reset(self, fDeleteToplevel = 1, fCreateToplevel = 1,
              fUpdateExplorer = 1):
        """
        Reset level and re-initialize main class variables
        Pass in the new top level group
        """
        self.resetPathMarkers()
        self.resetBattleCellMarkers()

        if fDeleteToplevel:
            self.deleteToplevel()

        DNASTORE.resetDNAGroups()
        DNASTORE.resetDNAVisGroups()
        DNASTORE.resetSuitPoints()
        DNASTORE.resetBattleCells()

        self.DNAData = DNAData('level_data')

        if fCreateToplevel:
            self.createToplevel(DNAGroup('level'))

        # Reset grid
        base.direct.grid.setPosHprScale(0, 0, 0, 0, 0, 0, 1, 1, 1)
        # The selected DNA Object/NodePath
        self.selectedDNARoot = None
        self.selectedNPRoot = None
        self.selectedSuitPoint = None
        self.lastLandmarkBuildingDNA = None
        self.showLandmarkBlockToggleGroup = None
        # Set active target (the subcomponent being modified)
        self.DNATarget = None
        self.DNATargetParent = None
        # Set count of groups added to level
        self.setGroupNum(0)
        self.setLastAngle(0.0)
        self.lastSign = None
        self.lastWall = None
        self.lastBuilding = None
        self.snapList = []
        self.activeMenu = None
        self.visitedPoints = []
        self.visitedEdges = []

        self.animPropDict = {}

        if fUpdateExplorer:
            self.panel.sceneGraphExplorer.update()

        self.outputFile = None
        self.panel["title"] = 'Open Level Editor: No file loaded'

    def deleteToplevel(self):
        self.DNAData.remove(self.DNAToplevel)
        self.NPToplevel.removeNode()

    def createToplevel(self, dnaNode, nodePath = None):
        # When you create a new level, data is added to this node
        # When you load a DNA file, you replace this node with the new data
        self.DNAToplevel = dnaNode
        self.DNAData.add(self.DNAToplevel)
        if nodePath:
            self.NPToplevel = nodePath
            self.NPToplevel.reparentTo(self)
        else:
            self.NPToplevel = self.DNAToplevel.traverse(self, DNASTORE, 1)
        self.DNAParent = self.DNAToplevel
        self.NPParent = self.NPToplevel
        self.VGParent = None
        self.suitPointToplevel = self.NPToplevel.attachNewNode('suitPoints')

    def destroy(self):
        """ Disable level editor and destroy node path """
        self.disable()
        self.removeNode()
        self.panel.destroy()
        if self.vgpanel:
            self.vgpanel.destroy()

    def useDirectFly(self):
        """ Disable player camera controls/enable direct camera control """
        self.traversalOff()
        self.collisionsOff()
        self.visibilityOff()
        base.camera.wrtReparentTo(render)
        base.camera.iPos(base.cam)
        base.cam.iPosHpr()
        self.enableMouse()
        base.direct.enable()

        if self.avatar:
            self.avatar.reparentTo(hidden)
            self.avatar.stopUpdateSmartCamera()
        if self.controlManager:
            self.controlManager.disable()

        self.fDrive = False

    def lerpCameraP(self, p, time):
        """
        lerp the camera P over time (used by the battle)
        """
        taskMgr.remove('cam-p-lerp')
        if self.avatar:
            self.avatar.stopUpdateSmartCamera()

        def setCamP(p):
            base.camera.setP(p)

        if self.isPageUp:
            fromP = 36.8699  # REVIEW: Weird magic numbers?
        elif self.isPageDown:
            fromP = -27.5607
        else:
            fromP = 0

        self.camLerpInterval = LerpFunctionInterval(setCamP,
                                                    fromData = fromP, toData = p, duration = time,
                                                    name = 'cam-p-lerp')
        self.camLerpInterval.start()

    def clearPageUpDown(self):
        if self.isPageDown or self.isPageUp:
            self.lerpCameraP(0, 0.6)
            self.isPageDown = 0
            self.isPageUp = 0

        if self.avatar:
            self.avatar.startUpdateSmartCamera()

    def pageUp(self):
        if not self.isPageUp:
            self.lerpCameraP(36.8699, 0.6)  # REVIEW: more magic numbers, seem to coinside with above
            self.isPageDown = 0
            self.isPageUp = 1
        else:
            self.clearPageUpDown()

    def pageDown(self):
        if not self.isPageDown:
            self.lerpCameraP(-27.5607, 0.6)
            self.isPageUp = 0
            self.isPageDown = 1
        else:
            self.clearPageUpDown()

    def useDriveMode(self):
        """ Lerp down to eye level then switch to Drive mode """
        if self.avatar is None:
            self.avatar = LEAvatar.LEAvatar(None, None, None)
            base.localAvatar = self.avatar
            self.avatar.doId = 0
            self.avatar.robot = RobotToon.RobotToon()
            self.avatar.robot.reparentTo(self.avatar)
            self.avatar.setHeight(self.avatar.robot.getHeight())
            self.avatar.setName("The Inspector")
            self.avatar.robot.loop('neutral')

        self.avatar.setPos(base.camera.getPos())
        self.avatar.reparentTo(render)

        self.switchToDriveMode(None)
        self.fDrive = True
        base.direct.selected.deselect(base.direct.selected.last)

    def switchToDriveMode(self, state):
        """ Disable direct camera manipulation and enable player drive mode """
        # Update vis data
        self.initVisibilityData()

        base.camera.wrtReparentTo(self.avatar)
        base.camera.setHpr(0, 0, 0)
        base.camera.setPos(0, -11.8125, 3.9375)

        if self.panel.fColl.get():
            self.collisionsOn()
        if self.panel.fVis.get():
            self.visibilityOn()
        if self.panel.fColl.get() or self.panel.fVis.get():
            self.traversalOn()

        if self.controlManager is None:
            self.controlManager = ControlManager.ControlManager()
            avatarRadius = 1.4
            floorOffset = OTPGlobals.FloorOffset
            reach = 4.0

            walkControls = NonPhysicsWalker.NonPhysicsWalker()
            walkControls.setWallBitMask(OTPGlobals.WallBitmask)
            walkControls.setFloorBitMask(OTPGlobals.FloorBitmask)
            walkControls.initializeCollisions(self.cTrav, self.avatar,
                                              avatarRadius, floorOffset, reach)
            self.controlManager.add(walkControls, "walk")
            self.controlManager.use("walk", self)

            # set speeds after adding controls to the control manager
            self.controlManager.setSpeeds(
                    OTPGlobals.ToonForwardSpeed,
                    OTPGlobals.ToonJumpForce,
                    OTPGlobals.ToonReverseSpeed,
                    OTPGlobals.ToonRotateSpeed
                    )
        else:
            self.controlManager.enable()

        self.avatarAnimTask = taskMgr.add(self.avatarAnimate, 'avatarAnimTask', 24)
        self.avatar.startUpdateSmartCamera()

        self.avatarMoving = 0

    # animate avatar model based on if it is moving
    def avatarAnimate(self, task = None):
        if self.controlManager:
            moving = self.controlManager.currentControls.speed or self.controlManager.currentControls.slideSpeed or self.controlManager.currentControls.rotationSpeed
            if (moving and
                    self.avatarMoving == 0):
                self.clearPageUpDown()
                # moving, play walk anim
                if (self.controlManager.currentControls.speed < 0 or
                        self.controlManager.currentControls.rotationSpeed):
                    self.avatar.robot.loop('walk')
                else:
                    self.avatar.robot.loop('run')
                self.avatarMoving = 1
            elif (moving == 0 and
                  self.avatarMoving == 1):
                # no longer moving, play neutral anim
                self.avatar.robot.loop('neutral')
                self.avatarMoving = 0
        return Task.cont

    def configureDriveModeCollisionData(self):
        """
        Set up the local avatar for collisions
        """
        # Set up the collision sphere
        # This is a sphere on the ground to detect barrier collisions
        self.cSphere = CollisionSphere(0.0, 0.0, 0.0, 1.5)
        self.cSphereNode = CollisionNode('cSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = camera.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereBitMask = BitMask32.bit(0)
        self.cSphereNode.setFromCollideMask(self.cSphereBitMask)
        self.cSphereNode.setIntoCollideMask(BitMask32.allOff())

        # Set up the collison ray
        # This is a ray cast from your head down to detect floor polygons
        self.cRay = CollisionRay(0.0, 0.0, 6.0, 0.0, 0.0, -1.0)
        self.cRayNode = CollisionNode('cRayNode')
        self.cRayNode.addSolid(self.cRay)
        self.cRayNodePath = camera.attachNewNode(self.cRayNode)
        self.cRayNodePath.hide()
        self.cRayBitMask = BitMask32.bit(1)
        self.cRayNode.setFromCollideMask(self.cRayBitMask)
        self.cRayNode.setIntoCollideMask(BitMask32.allOff())

        # set up wall collision mechanism
        self.pusher = CollisionHandlerPusher()
        self.pusher.setInPattern("enter%in")
        self.pusher.setOutPattern("exit%in")

        # set up floor collision mechanism
        self.lifter = CollisionHandlerFloor()
        self.lifter.setInPattern("on-floor")
        self.lifter.setOutPattern("off-floor")
        self.floorOffset = 0.1
        self.lifter.setOffset(self.floorOffset)

        # Limit our rate-of-fall with the lifter.
        # If this is too low, we actually "fall" off steep stairs
        # and float above them as we go down. I increased this
        # from 8.0 to 16.0 to prevent this
        self.lifter.setMaxVelocity(16.0)

        self.cTrav = CollisionTraverser("LevelEditor")
        self.cTrav.setRespectPrevTransform(1)

        # activate the collider with the traverser and pusher
        self.nodeDict = {}
        self.zoneDict = {}
        self.nodeList = []
        self.fVisInit = 0

    def traversalOn(self):
        base.cTrav = self.cTrav

    def traversalOff(self):
        base.cTrav = 0

    def collisionsOff(self):
        self.cTrav.removeCollider(self.cSphereNodePath)

    def collisionsOn(self):
        self.collisionsOff()
        self.cTrav.addCollider(self.cSphereNodePath, self.pusher)

    def toggleCollisions(self):
        if self.panel.fColl.get():
            self.collisionsOn()
            self.traversalOn()
        else:
            self.collisionsOff()
            if not (self.panel.fColl.get() or self.panel.fVis.get()):
                self.traversalOff()

    def toggleVisibleCollisions(self):
        self.collisionsToggled = not self.collisionsToggled
        if self.collisionsToggled:
            render.findAllMatches('**/+CollisionNode').show()
            self.popupNotification("Enabled Collision view")
        else:
            render.findAllMatches('**/+CollisionNode').hide()
            self.popupNotification("Disabled Collision view")

    def toggleSuitBuildingPreviews(self):
        """
            Toggle Suit Building Previews

            This is used to show where a suit building is placed in relation
            to a toon building. this ensures you line up your buildings and walls
            properly to prevent walls clipping through elevators, or gaps in the wall
        """

        self.suitPreviewsToggled = not self.suitPreviewsToggled

        if self.suitPreviewsToggled:
            self.suitBuildings = []

            suitBuildings = [DNASTORE.findNode("suit_landmark_l1"),
                             DNASTORE.findNode("suit_landmark_c1"),
                             DNASTORE.findNode("suit_landmark_s1"),
                             DNASTORE.findNode("suit_landmark_m1")]
            suitNames = ['Lawbot', 'Bossbot', 'Sellbot', 'Cashbot']

            if base.server == TOONTOWN_CORPORATE_CLASH:
                suitBuildings.append(DNASTORE.findNode("suit_landmark_g1"))
                suitNames.append('Boardbot')

            # temporary fix for duplicate sb's
            sb = []
            for bldg in self.NPToplevel.findAllMatches('**/*sb*:toon_landmark*'):
                # We don't do this to HQs.
                if 'hq' in bldg.getName():
                    continue

                bldgnum = bldg.getName()[2:4].replace(':', '')

                # If we have a duplicate SB, delete it
                if bldgnum in sb:
                    bldg.removeNode()
                    del bldg
                    continue
                sb.append(bldgnum)

                tb = self.NPToplevel.find(f'**/*tb{bldgnum}:toon_landmark*')

                bldg.setPosHpr(tb.getPos(), tb.getHpr())

                # clash has 5, the rest have 4
                numCorps = 5 if base.server == TOONTOWN_CORPORATE_CLASH else 4
                suitType = random.randint(0, numCorps - 1)

                suitBuilding = suitBuildings[suitType]

                newsuit = suitBuilding.copyTo(bldg)

                elevator = loader.loadModel("phase_4/models/modules/elevator")
                elevator.reparentTo(bldg.find("**/*_door_origin"))

                elevator.setScale(render, 1.0, 1.0, 1.0)

                self.suitBuildings.append(newsuit)

                # Hide the toon building
                tb.hide()

                # Setup the sign:

                tbDNA = self.findDNANode(tb)
                buildingTitle = tbDNA.getTitle()

                # Clash uses unique extensions for different corps
                suitExt = ['Assoc.',
                           'Corp.',
                           'Co.',
                           'C.U.',
                           'Inc.'][suitType] if base.server == TOONTOWN_CORPORATE_CLASH else 'Inc.'

                if not buildingTitle:
                    buildingTitle = f'COGS, {suitExt}'
                else:
                    buildingTitle += f', {suitExt}'
                buildingTitle += f"\n{suitNames[suitType]}"

                # Try to find this signText in the node map
                textNode = TextNode("sign")
                textNode.setTextColor(1.0, 1.0, 1.0, 1.0)
                textNode.setFont(ToontownGlobals.getSuitFont())
                textNode.setAlign(TextNode.ACenter)
                textNode.setWordwrap(17.0)
                textNode.setText(buildingTitle)

                # Since the text is wordwrapped, it may flow over more
                # than one line.  Try to adjust the scale and position of
                # the sign accordingly.
                textHeight = textNode.getHeight()
                zScale = (textHeight + 2) / 3.0

                # Determine where the sign should go:
                signOrigin = newsuit.find("**/sign_origin;+s")
                assert (not signOrigin.isEmpty())

                # Get the background:
                backgroundNP = loader.loadModel("phase_5/models/modules/suit_sign")
                assert (not backgroundNP.isEmpty())
                backgroundNP.reparentTo(signOrigin)
                backgroundNP.setPosHprScale(0.0, 0.0, textHeight * 0.8 / zScale,
                                            0.0, 0.0, 0.0,
                                            8.0, 8.0, 8.0 * zScale)

                signTextNodePath = backgroundNP.attachNewNode(textNode.generate())
                assert (not signTextNodePath.isEmpty())

                signTextNodePath.setPosHprScale(0.0, -0.001, -0.21 + textHeight * 0.1 / zScale,
                                                0.0, 0.0, 0.0,
                                                0.1, 0.1, 0.1 / zScale)
                # Clear parent color higher in the hierarchy
                signTextNodePath.setColor(1.0, 1.0, 1.0, 1.0)
                # Decal sign onto the front of the building:
                frontNP = newsuit.find("**/*_front/+GeomNode;+s")
                assert (not frontNP.isEmpty())
                backgroundNP.wrtReparentTo(frontNP)
                frontNP.node().setEffect(DecalEffect.make())

            self.popupNotification("Enabled Suit Building View")

        else:
            for bldg in self.suitBuildings:
                # Incase an edit is made to the suit buildings position,
                # apply it to the actual building
                bldgnum = bldg.getParent().getName()[2:4].replace(':', '')
                tb = self.NPToplevel.find(f'**/*tb{bldgnum}:toon_landmark*')

                tb.setPosHpr(bldg.getParent().getPos(), bldg.getParent().getHpr())

                # Unhide the toon building
                tb.show()

                # Remove the suit building
                bldg.removeNode()
                del bldg
            self.suitBuildings = []
            self.popupNotification("Disabled Suit Building View")

    def setReparentTarget(self):
        if base.direct.selected.last:
            base.direct.setActiveParent(base.direct.selected.last)
            self.popupNotification(f'Set reparent target to {base.direct.selected.last}')

    def initVisibilityData(self):
        self.showAllVisibles()
        self.nodeDict = {}
        self.zoneDict = {}
        self.nodeList = []
        # FIXME: this should change to find the groupnodes in
        # the dna storage instead of searching through the tree
        for i in range(DNASTORE.getNumDNAVisGroups()):
            groupFullName = DNASTORE.getDNAVisGroupName(i)
            groupName = self.extractGroupName(groupFullName)
            zoneId = int(groupName)
            self.nodeDict[zoneId] = []
            self.zoneDict[zoneId] = self.NPToplevel.find("**/" + groupName)

            # TODO: we only need to look from the top of the hood
            # down one level to find the vis groups as an optimization
            groupNode = self.NPToplevel.find("**/" + groupFullName)
            if groupNode.isEmpty():
                print("Could not find visgroup")
            self.nodeList.append(groupNode)
            for j in range(DNASTORE.getNumVisiblesInDNAVisGroup(i)):
                visName = DNASTORE.getVisibleName(i, j)
                visNode = self.NPToplevel.find("**/" + visName)
                self.nodeDict[zoneId].append(visNode)
        # Rename the floor polys to have the same name as the
        # visgroup they are in... This makes visibility possible.
        self.renameFloorPolys(self.nodeList)
        self.fVisInit = 1

    def extractGroupName(self, groupFullName):
        # The Idea here is that group names may have extra flags associated
        # with them that tell more information about what is special about
        # the particular vis zone. A normal vis zone might just be "13001",
        # but a special one might be "14356:safe_zone" or
        # "345:safe_zone:exit_zone"... These are hypotheticals. The main
        # idea is that there are colon separated flags after the initial
        # zone name.
        return groupFullName.split(':', 1)[0]

    def renameFloorPolys(self, nodeList):
        for i in nodeList:
            # Get all the collision nodes in the vis group
            collNodePaths = i.findAllMatches("**/+CollisionNode")
            numCollNodePaths = collNodePaths.getNumPaths()
            visGroupName = i.node().getName()
            for j in range(numCollNodePaths):
                collNodePath = collNodePaths.getPath(j)
                bitMask = collNodePath.node().getIntoCollideMask()
                if bitMask.getBit(1):
                    # Bit 1 is the floor collision bit. This renames
                    # all floor collision polys to the same name as their
                    # visgroup.
                    collNodePath.node().setName(visGroupName)

    def hideAllVisibles(self):
        for i in self.nodeList:
            i.hide()

    def showAllVisibles(self):
        for i in self.nodeList:
            i.show()
            i.clearColor()

    def visibilityOn(self):
        self.visibilityOff()
        self.accept("on-floor", self.enterZone)
        self.cTrav.addCollider(self.cRayNodePath, self.lifter)
        self.lifter.clear()
        self.fVisInit = 1

    def visibilityOff(self):
        self.ignore("on-floor")
        self.cTrav.removeCollider(self.cRayNodePath)
        self.showAllVisibles()

    def toggleVisibility(self):
        if self.panel.fVis.get():
            self.visibilityOn()
            self.traversalOn()
        else:
            self.visibilityOff()
            if not (self.panel.fColl.get() or self.panel.fVis.get()):
                self.traversalOff()

    def enterZone(self, newZone):
        return
        """
        Puts the toon in the indicated zone.  newZone may either be a
        CollisionEntry object as determined by a floor polygon, or an
        integer zone id.  It may also be None, to indicate no zone.
        """
        # First entry into a zone, hide everything
        if self.fVisInit:
            self.hideAllVisibles()
            self.fVisInit = 0
        if isinstance(newZone, CollisionEntry):
            # Get the name of the collide node
            try:
                newZoneId = int(newZone.getIntoNode().getName())
            except:
                newZoneId = 0
        else:
            newZoneId = newZone
        # Ensure we have vis data
        assert self.nodeDict
        if self.__zoneId is not None:
            for i in self.nodeDict[self.__zoneId]:
                i.hide()
        if newZoneId is not None:
            for i in self.nodeDict[newZoneId]:
                i.show()
        # Make sure we changed zones
        if newZoneId != self.__zoneId:
            if self.panel.fVisZones.get():
                # Set a color override on our zone to make it obvious what
                # zone we're in.
                if self.__zoneId is not None:
                    self.zoneDict[self.__zoneId].clearColor()
                if newZoneId is not None:
                    self.zoneDict[newZoneId].setColor(0, 0, 1, 1, 100)
            # The new zone is now old
            self.__zoneId = newZoneId

    def enableMouse(self):
        """ Enable Pie Menu interaction (and disable player camera control) """
        # Turn off player camera control
        base.disableMouse()
        self.accept('DIRECT-mouse3', self.levelHandleMouse3)
        self.accept('DIRECT-mouse3Up', self.levelHandleMouse3Up)

    def disableMouse(self):
        """ Disable Pie Menu interaction """
        self.ignore('DIRECT-mouse3')
        self.ignore('DIRECT-mouse3Up')

    # LEVEL OBJECT MANAGEMENT FUNCTIONS
    def findDNANode(self, nodePath):
        """ Find node path's DNA Object in DNAStorage (if any) """
        if nodePath:
            return DNASTORE.findDNAGroup(nodePath.node())
        else:
            return None

    def replaceSelected(self):
        if self.replaceSelectedEnabled:
            # Update visible geometry using new DNA
            newRoot = self.replace(self.selectedNPRoot, self.selectedDNARoot)
            # Reselect node path and respawn followSelectedNodePathTask
            base.direct.select(newRoot)

    def replace(self, nodePath, dnaNode):
        """ Replace a node path with the results of a DNANode traversal """
        if not nodePath:
            return None
        parent = nodePath.getParent()
        dnaParent = dnaNode.getParent()
        # Get rid of the old node path and remove its DNA and
        # node relations from the DNA Store
        self.remove(dnaNode, nodePath)
        # Traverse the old (modified) dna to create the new node path
        try:
            newNodePath = dnaNode.traverse(parent, DNASTORE, 1)
        except Exception:
            self.notify.debug("Couldn't traverse existing DNA! Do not trust replace. Failed on: %s" % dnaNode)
            return None
        # Add it back to the dna parent
        dnaParent.add(dnaNode)

        if DNAClassEqual(dnaNode, DNA_ANIM_BUILDING):
            self.createAnimatedBuilding(dnaNode, newNodePath)

        # self.panel.sceneGraphExplorer.update()
        return newNodePath

    def remove(self, dnaNode, nodePath):
        """
        Delete DNA and Node relation from DNA Store and remove the node
        path from the scene graph.
        """
        if dnaNode:
            parentDNANode = dnaNode.getParent()
            if parentDNANode:
                parentDNANode.remove(dnaNode)
            DNASTORE.removeDNAGroup(dnaNode)
        if nodePath:
            # Next deselect nodePath to avoid having bad node paths in the dict
            base.direct.deselect(nodePath)
            nodePath.removeNode()

    def removeNodePathHook(self, nodePath):
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            for hook in self.removeHookList:
                hook(dnaNode, nodePath)
            parentDNANode = dnaNode.getParent()
            if parentDNANode:
                parentDNANode.remove(dnaNode)
            DNASTORE.removeDNAGroup(dnaNode)
            self.popupNotification(f"Removed {dnaNode.getName()}")
        else:
            pointOrCell, type = self.findPointOrCell(nodePath)
            if pointOrCell and type:
                if type == 'suitPointMarker':
                    print('Suit Point:', pointOrCell)
                    if DNASTORE.removeSuitPoint(pointOrCell):
                        print("Removed from DNASTORE")
                    else:
                        print("Not found in DNASTORE")
                    del self.pointDict[pointOrCell]
                    # Remove point from visitedPoints list
                    if pointOrCell in self.visitedPoints:
                        self.visitedPoints.remove(pointOrCell)
                    # Update edge related dictionaries
                    for edge in self.point2edgeDict[pointOrCell]:
                        oldEdgeLine = self.edgeDict.get(edge, None)
                        if oldEdgeLine:
                            del self.edgeDict[edge]
                            oldEdgeLine.reset()
                            del oldEdgeLine
                        # Find other endpoints of edge and clear out
                        # corresponding point2edgeDict entry
                        startPoint = edge.getStartPoint()
                        endPoint = edge.getEndPoint()
                        if pointOrCell == startPoint:
                            self.point2edgeDict[endPoint].remove(edge)
                        elif pointOrCell == endPoint:
                            self.point2edgeDict[startPoint].remove(edge)
                        if edge in self.visitedEdges:
                            self.visitedEdges.remove(edge)
                    # Now delete point2edgeDict entry for this point
                    del (self.point2edgeDict[pointOrCell])
                elif type == 'battleCellMarker':
                    visGroupNP, visGroupDNA = self.findParentVisGroup(nodePath)
                    print('Battle Cell:', pointOrCell)
                    if visGroupNP and visGroupDNA:
                        if visGroupDNA.removeBattleCell(pointOrCell):
                            print("Removed from Vis Group")
                        else:
                            print("Not found in Vis Group")
                    else:
                        print("Parent Vis Group not found")
                    if DNASTORE.removeBattleCell(pointOrCell):
                        print("Removed from DNASTORE")
                    else:
                        print("Not found in DNASTORE")
                    del self.cellDict[pointOrCell]

    def reparent(self, nodePath, oldParent, newParent):
        """ Move node path (and its DNA) to active parent """
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            oldParentDNANode = self.findDNANode(oldParent)
            if oldParentDNANode:
                oldParentDNANode.remove(dnaNode)
            if newParent:
                self.setActiveParent(newParent)
                if self.DNAParent is not None:
                    self.DNAParent.add(dnaNode)
                    if DNAIsDerivedFrom(dnaNode, DNA_NODE):
                        self.updatePose(dnaNode, nodePath)
        elif newParent:
            suitEdge, oldVisGroup = self.np2EdgeDict.get(hash(nodePath), (None, None))
            # And see if the new parent is a vis group
            newVisGroupNP, newVisGroupDNA = self.findParentVisGroup(newParent)
            if suitEdge and DNAClassEqual(newVisGroupDNA, DNA_VIS_GROUP):
                # If so, remove suit edge from old vis group and add it to the new group
                oldVisGroup.removeSuitEdge(suitEdge)
                suitEdge.setZoneId(newVisGroupDNA.getName())
                newVisGroupDNA.addSuitEdge(suitEdge)
                self.np2EdgeDict[hash(nodePath)] = [suitEdge, newVisGroupDNA]

        self.popupNotification(f"{nodePath.getName()} reparented to {newParent.getName()}")

    def setActiveParent(self, nodePath = None):
        """ Set NPParent and DNAParent to node path and its DNA """
        if nodePath:
            newDNAParent = self.findDNANode(nodePath)
            if newDNAParent:
                self.DNAParent = newDNAParent
                self.NPParent = nodePath
            else:
                print('LevelEditor.setActiveParent: nodePath not found')
        else:
            print('LevelEditor.setActiveParent: nodePath == None')

    def setName(self, nodePath, newName):
        """ Set name of nodePath's DNA (if it exists) """
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            dnaNode.setName(newName)

    def updateSelectedPose(self, nodePathList):
        """
        Update the DNA database to reflect selected objects current positions
        """
        for selectedNode in nodePathList:
            dnaObject = self.findDNANode(selectedNode)
            if dnaObject:
                if DNAIsDerivedFrom(dnaObject, DNA_NODE):
                    pos = selectedNode.getPos(base.direct.grid)
                    snapPos = base.direct.grid.computeSnapPoint(pos)
                    if self.panel.fPlaneSnap.get():
                        zheight = 0
                    else:
                        zheight = snapPos[2]
                    selectedNode.setPos(base.direct.grid,
                                        snapPos[0], snapPos[1], zheight)
                    h = base.direct.grid.computeSnapAngle(selectedNode.getH())
                    if base.direct.grid.getHprSnap():
                        selectedNode.setH(h)
                    if selectedNode == base.direct.selected.last:
                        self.setLastAngle(h)
                    self.updatePose(dnaObject, selectedNode)
            else:
                pointOrCell, type = self.findPointOrCell(selectedNode)
                if pointOrCell and type:
                    # First snap selected node path to grid
                    pos = selectedNode.getPos(base.direct.grid)
                    snapPos = base.direct.grid.computeSnapPoint(pos)
                    if self.panel.fPlaneSnap.get():
                        zheight = 0
                    else:
                        zheight = snapPos[2]
                    selectedNode.setPos(
                            base.direct.grid,
                            snapPos[0], snapPos[1], zheight)
                    newPos = selectedNode.getPos(self.NPToplevel)
                    # Update DNA
                    pointOrCell.setPos(newPos)
                    if type == 'suitPointMarker':
                        print("Found suit point!", pointOrCell)
                        self.startSuitPoint = pointOrCell
                        # Ok, now update all the lines into that node
                        for edge in self.point2edgeDict[pointOrCell]:
                            oldEdgeLine = self.edgeDict.get(edge, None)
                            if oldEdgeLine:
                                del self.edgeDict[edge]
                                oldEdgeLine.reset()
                                oldEdgeLine.removeNode()
                                del oldEdgeLine
                                newEdgeLine = self.drawSuitEdge(
                                        edge, self.NPParent)
                                self.edgeDict[edge] = newEdgeLine
                    elif type == 'battleCellMarker':
                        print("Found battle cell!", pointOrCell)

    def updatePose(self, dnaObject, nodePath):
        """
        Update a DNA Object's pos, hpr, and scale based on nodePath
        """
        dnaObject.setPos(nodePath.getPos())
        dnaObject.setHpr(nodePath.getHpr())
        dnaObject.setScale(nodePath.getScale())

    def loadAnimatedProps(self, npRoot):
        for np in npRoot.findAllMatches('**/animated_prop_*'):
            dnaNode = self.findDNANode(np)
            if dnaNode and DNAClassEqual(dnaNode, DNA_ANIM_PROP):
                self.createAnimatedProp(dnaNode, np)

        for np in npRoot.findAllMatches('**/interactive_prop_*'):
            dnaNode = self.findDNANode(np)
            if dnaNode and DNAClassEqual(dnaNode, DNA_INTERACTIVE_PROP):
                self.createAnimatedProp(dnaNode, np, isInteractiveProp = True)

    def createAnimatedProp(self, dnaNode, newNodePath, isInteractiveProp = False):
        modelName = DNASTORE.findNode(dnaNode.getCode()).getAncestors()[-1].getName()
        tokens = modelName.split('.')[0].split('_r_')

        code = dnaNode.getCode()
        if isInteractiveProp:
            pathStr = code[len('interactive_prop_'):].split('__')[0]
        elif code.startswith('animated_prop_generic_'):
            pathStr = code[len('animated_prop_generic_'):].split('__')[0]
        elif code.startswith('animated_prop_'):
            # we expect generic to be replaced with the class name
            tempStr = code[len('animated_prop_'):]
            nextUnderscore = tempStr.find('_')
            finalStr = tempStr[nextUnderscore + 1:]
            pathStr = finalStr.split('__')[0]
        else:
            self.notify.error("dont know what to do with code=%s" % code)
        phaseDelimeter = len('phase_') + pathStr[len('phase_'):].find('_')
        phaseStr = pathStr[:phaseDelimeter]
        pathTokens = pathStr[phaseDelimeter + 1:].split('_')
        modelPathStr = phaseStr
        for path in pathTokens:
            modelPathStr += '/'
            modelPathStr += path

        animFileList = glob.glob(f"{modelPathStr}/{tokens[0]}_a_{tokens[1]}_*.bam")

        animNameList = []
        for animFile in animFileList:
            animName = os.path.basename(animFile[:animFile.rfind('.')])
            animNameList.append(animName)

        if not animNameList:
            self.notify.warning("no anims found for %s " % animFileList)

        if dnaNode.getAnim() == '':
            dnaNode.setAnim(animNameList[0])

        newNodePath.setTag('DNAAnim', dnaNode.getAnim())
        className = 'GenericAnimatedProp'
        if code.startswith('animated_prop_') and \
                not code.startswith('animated_prop_generic_'):
            splits = code.split('_')
            className = splits[2]

        # do some special python magic to get a handle to class
        # from the name of the class
        # FIXME: this sucks
        symbols = {}
        importModule(symbols, 'toontown.hood', [className])
        classObj = getattr(symbols[className], className)
        animPropObj = classObj(newNodePath)

        animPropObj.enter()
        self.animPropDict[dnaNode] = animPropObj
        self.styleManager.createMiscAttribute('animlist_%s' % dnaNode.getCode(), animNameList, makePieMenu = False)
        self.accept('select_animlist_%s' % dnaNode.getCode(), self.setAnimPropAnim)

        # [gjeon] connect interactive prop and battle cell
        if DNAClassEqual(dnaNode, DNA_INTERACTIVE_PROP):
            cellId = dnaNode.getCellId()
            if cellId != -1:
                visGroup = self.getVisGroup(newNodePath)
                if visGroup is None:
                    return
                for battleCellMarkerNP in visGroup.findAllMatches("**/battleCellMarker"):
                    if battleCellMarkerNP.getTag('cellId') == '%d' % cellId:
                        battleCellNP = battleCellMarkerNP.find('Sphere')
                        self.drawLinkLine(battleCellNP, newNodePath)
                        return

    def createAnimatedBuilding(self, dnaNode, newNodePath):
        # [gjeon] try to find proper animations
        modelName = DNASTORE.findNode(dnaNode.getCode()).getAncestors()[-1].getName()
        tokens = modelName.split('.')[0].split('_r_')

        # [gjeon] to find path from code
        code = dnaNode.getCode()
        pathStr = code[len('animated_building_'):].split('__')[0]
        phaseDelimeter = len('phase_') + pathStr[len('phase_'):].find('_')
        phaseStr = pathStr[:phaseDelimeter]
        pathTokens = pathStr[phaseDelimeter + 1:].split('_')
        modelPathStr = phaseStr
        for path in pathTokens:
            modelPathStr += '/'
            modelPathStr += path

        animFileList = glob.glob(f"{modelPathStr}/{tokens[0]}_a_{tokens[1]}_*.bam")
        print(animFileList)

        animNameList = []
        for animFile in animFileList:
            animName = os.path.basename(animFile[:animFile.rfind('.')])
            animNameList.append(animName)

        if dnaNode.getAnim() == '':
            dnaNode.setAnim(animNameList[0])
        dnaNode.setBuildingType("animbldg")

        newNodePath.setTag('DNAAnim', dnaNode.getAnim())
        animBuildingObj = GenericAnimatedProp(newNodePath)
        animBuildingObj.enter()
        self.animPropDict[dnaNode] = animBuildingObj
        self.styleManager.createMiscAttribute('animlist_%s' % dnaNode.getCode(), animNameList, makePieMenu = False)
        self.accept('select_animlist_%s' % dnaNode.getCode(), self.setAnimPropAnim)

    def getVisGroup(self, np):
        for ancestor in np.getAncestors():
            dnaNode = self.findDNANode(ancestor)
            if dnaNode and DNAClassEqual(dnaNode, DNA_VIS_GROUP):
                return ancestor

        return None

    # LEVEL OBJECT CREATION FUNCTIONS
    def initDNANode(self, dnaNode):
        """
        This method adds a new DNA object to the scene and adds hooks that
        allow duplicate copies of this DNA node to be added using the
        space bar. For DNAFlatBuildings, a new copy with random style is
        generated by hitting the insert key.
        """
        try:
            self.initNodePath(dnaNode)
        except AssertionError as error:
            self.notify.debug("Error loading %s" % dnaNode)
        self.addReplicationHooks(dnaNode)

        ## Move selected objects
        # for selectedNode in base.direct.selected:
        #    # Move it
        #    selectedNode.setPos(render, base.direct.cameraControl.coaMarker.getPos(render))
        #    #selectedNode.setPos(render, self.newObjPos)

    def addReplicationHooks(self, dnaNode):
        # Now add hook to allow placement of a new dna Node of this type
        # by simply hitting the space bar or insert key.  Note, extra paramter
        # indicates new dnaNode should be a copy
        self.accept('space', self.initNodePath, [dnaNode, 'space'])
        self.accept('insert', self.initNodePath, [dnaNode, 'insert'])

    def setRandomBuildingStyle(self, dnaNode, name = 'building'):
        """ Initialize a new DNA Flat building to a random building style """
        buildingType = self.getCurrent('building_type')
        if buildingType == 'random':
            buildingHeight = self.getCurrent('building_height')
            heightList = self.getRandomHeightList(buildingHeight)
            buildingType = createHeightCode(heightList)
        else:
            # Use specified height list
            heightList = [atof(l) for l in buildingType.split('_')]
            height = calcHeight(heightList)
            # Is this a never before seen height list?  If so, record it.
            try:
                attr = self.getAttribute(repr(height) + '_ft_wall_heights')
                if heightList not in attr.getList():
                    print('Adding new height list entry')
                    attr.add(heightList)
            except KeyError:
                print('Non standard height building')

        # See if this building type corresponds to existing style dict
        try:
            dict = self.getDict(buildingType + '_styles')
        except KeyError:
            dict = {}

        # No specific dict or empty dict, pick dict based on number of walls
        if not dict:
            numWalls = len(heightList)
            dict = self.getDict(repr(numWalls) + '_wall_styles')

        if not dict:
            styleList = []
            for height in heightList:
                wallStyle = self.getRandomDictionaryEntry(
                        self.getDict('wall_style'))
                styleList.append((wallStyle, height))
            style = DNAFlatBuildingStyle(styleList = styleList)
        else:
            style = self.getRandomDictionaryEntry(dict)

        # Set style....finally
        self.styleManager.setDNAFlatBuildingStyle(
                dnaNode, style, width = self.getRandomWallWidth(),
                heightList = heightList, name = name)

    def getRandomHeightList(self, buildingHeight):
        # Select a list of wall heights
        heightLists = self.getList(repr(buildingHeight) + '_ft_wall_heights')
        l = len(heightLists)
        if l > 0:
            return heightLists[random.randint(0, l - 1)]
        else:
            # No height lists exists for this building height, generate
            # FIXME: ugh fix this
            chance = random.randint(0, 100)
            if buildingHeight <= 10:
                return [buildingHeight]
            elif buildingHeight <= 14:
                return [4, 10]
            elif buildingHeight <= 20:
                if chance <= 30:
                    return [20]
                elif chance <= 80:
                    return [10, 10]
                else:
                    return [12, 8]
            elif buildingHeight <= 24:
                if chance <= 50:
                    return [4, 10, 10]
                else:
                    return [4, 20]
            elif buildingHeight <= 25:
                if chance <= 25:
                    return [3, 22]
                elif chance <= 50:
                    return [4, 21]
                elif chance <= 75:
                    return [3, 13, 9]
                else:
                    return [4, 13, 8]
            else:
                if chance <= 20:
                    return [10, 20]
                elif chance <= 35:
                    return [20, 10]
                elif chance <= 75:
                    return [10, 10, 10]
                else:
                    return [13, 9, 8]

    def getRandomWallWidth(self):
        chance = random.randint(0, 100)
        if chance <= 15:
            return 5.0
        elif chance <= 30:
            return 10.0
        elif chance <= 65:
            return 15.0
        elif chance <= 85:
            return 20.0
        else:
            return 25.0

    def initNodePath(self, dnaNode, hotKey = None):
        """
        Update DNA to reflect latest style choices and then generate
        new node path and add it to the scene graph
        """
        # Determine dnaNode Class Type
        nodeClass = DNAGetClassType(dnaNode)
        # Did the user hit insert or space?
        if hotKey:
            # Yes, make a new copy of the dnaNode
            dnaNode = dnaNode.__class__(dnaNode)
            # And determine dnaNode type and perform any type specific updates
            if nodeClass == DNA_PROP:
                dnaNode.setCode(self.getCurrent('prop_texture'))
            elif nodeClass == DNA_ANIM_PROP:
                dnaNode.setCode(self.getCurrent('anim_prop_texture'))
            elif nodeClass == DNA_INTERACTIVE_PROP:
                dnaNode.setCode(self.getCurrent('interactive_prop_texture'))
            elif nodeClass == DNA_ANIM_BUILDING:
                dnaNode.setCode(self.getCurrent('anim_building_texture'))
            elif nodeClass == DNA_STREET:
                dnaNode.setCode(self.getCurrent('street_texture'))
            elif nodeClass == DNA_FLAT_BUILDING:
                # If insert, pick a new random style
                if hotKey == 'insert':
                    self.setRandomBuildingStyle(dnaNode, dnaNode.getName())
                    # Get a new building width
                    self.setCurrent('building_width',
                                    self.getRandomWallWidth())
                dnaNode.setWidth(self.getCurrent('building_width'))

        # Position it
        taskMgr.remove('autoPositionGrid')
        # Now find where to put node path
        if (hotKey is not None) and (nodeClass == DNA_PROP or nodeClass == DNA_ANIM_PROP):
            # If its a prop and a copy, place it based upon current mouse position
            hitPt = self.getGridIntersectionPoint()
            tempNode = hidden.attachNewNode('tempNode')
            tempNode.setPos(base.direct.grid, hitPt)
            dnaNode.setPos(tempNode.getPos())
            tempNode.removeNode()
        else:
            dnaNode.setPos(base.direct.grid.getPos())

        dnaNode.setHpr(Vec3(self.getLastAngle(), 0, 0))

        self.DNAParent.add(dnaNode)
        try:
            newNodePath = dnaNode.traverse(self.NPParent, DNASTORE, 1)
        except Exception as error:
            print(error)
            self.notify.warning("Error while adding: %s" % dnaNode)
            return
        # self.panel.sceneGraphExplorer.update()

        if DNAClassEqual(dnaNode, DNA_STREET):
            self.snapList = self.getSnapPoint(dnaNode.getCode())

        if DNAClassEqual(dnaNode, DNA_ANIM_PROP):
            self.createAnimatedProp(dnaNode, newNodePath)
        elif DNAClassEqual(dnaNode, DNA_INTERACTIVE_PROP):
            self.createAnimatedProp(dnaNode, newNodePath, isInteractiveProp = True)
        elif DNAClassEqual(dnaNode, DNA_ANIM_BUILDING):
            self.createAnimatedBuilding(dnaNode, newNodePath)

        base.direct.select(newNodePath)
        self.lastNodePath = newNodePath

        self.autoPositionGrid()

    def getSnapPoint(self, code):
        return OBJECT_SNAP_POINTS.get(code, [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))])

    def addGroup(self, nodePath):
        """ Add a new DNA Node Group to the specified Node Path """
        base.direct.setActiveParent(nodePath)
        self.createNewGroup()

    def addVisGroup(self, nodePath):
        """ Add a new DNA Group to the specified Node Path """
        # Set the node path as the current parent
        base.direct.setActiveParent(nodePath)
        # Add a new group to the selected parent
        self.createNewGroup(type = 'vis')

    def createNewGroup(self, type = 'dna'):
        print("createNewGroup")
        """ Create a new DNA Node group under the active parent """
        if type == 'dna':
            newDNANode = DNAGroup('GROUP.' + repr(self.getGroupNum()))
        else:
            newDNANode = DNAVisGroup('VIS.' + repr(self.getGroupNum()))
            # Increment group counter
        self.setGroupNum(self.getGroupNum() + 1)
        # Add new DNA Node group to the current parent DNA Object
        self.DNAParent.add(newDNANode)
        # The new Node group becomes the active parent
        self.DNAParent = newDNANode
        # Traverse it to generate the new node path as a child of NPParent
        newNodePath = self.DNAParent.traverse(self.NPParent, DNASTORE, 1)
        # Update NPParent to point to the new node path
        self.NPParent = newNodePath
        # Update scene graph explorer
        # self.panel.sceneGraphExplorer.update()

    def addFlatBuilding(self, buildingType):
        # Create new building
        newDNAFlatBuilding = DNAFlatBuilding()
        self.setRandomBuildingStyle(newDNAFlatBuilding, name = f'tb0:FLAT_DNARoot')
        # Now place new building in the world
        self.initDNANode(newDNAFlatBuilding)

    def getNextLandmarkBlock(self):
        self.landmarkBlock = self.landmarkBlock + 1
        return str(self.landmarkBlock)

    def addLandmark(self, landmarkType, specialType, title = ''):
        # Record new landmark type
        self.setCurrent('toon_landmark_texture', landmarkType)
        block = self.getNextLandmarkBlock()
        print(landmarkType)
        if self.panel.bldgIsSafeZone.get() and specialType == '':
            prefix = 'sz'
        else:
            prefix = 'tb'
        newDNALandmarkBuilding = DNALandmarkBuilding(
                f"{prefix}{block}:{landmarkType}_DNARoot")
        newDNALandmarkBuilding.setCode(landmarkType)
        newDNALandmarkBuilding.setTitle(title)
        newDNALandmarkBuilding.setBuildingType(specialType)
        newDNALandmarkBuilding.setPos(VBase3(0))
        newDNALandmarkBuilding.setHpr(VBase3(0))
        # Headquarters do not have doors
        if specialType not in ['hq', 'kartshop']:
            newDNADoor = self.createDoor('landmark_door')
            newDNALandmarkBuilding.add(newDNADoor)
        self.initDNANode(newDNALandmarkBuilding)

    def renameLandmark(self, title = ''):
        """ Rename selected landmark building """
        selectedNode = base.direct.selected.last
        if selectedNode:
            dnaNode = self.findDNANode(selectedNode)
            if DNAGetClassType(dnaNode) == DNA_LANDMARK_BUILDING:
                dnaNode.setTitle(title)
        if self.panel.bldgLabels.get():
            self.labelBldgs()

    def addAnimBuilding(self, animBuildingType):
        print("addAnimBuilding %s " % animBuildingType)
        # Record new anim building type
        self.setCurrent('anim_building_texture', animBuildingType)
        block = self.getNextLandmarkBlock()
        simpleName = re.sub(r'phase_\d_models_char__', '', animBuildingType).replace('animated_building_', '').upper()
        newDNAAnimBuilding = DNAAnimBuilding(f"tb{block}:ALND.{simpleName}_DNARoot")
        newDNAAnimBuilding.setCode(animBuildingType)
        newDNAAnimBuilding.setPos(VBase3(0))
        newDNAAnimBuilding.setHpr(VBase3(0))

        self.initDNANode(newDNAAnimBuilding)

    def addProp(self, propType):
        print(base.direct.cameraControl.coaMarker.getPos(render))
        print("addProp %s " % propType)
        # Record new prop type
        self.setCurrent('prop_texture', propType)
        newDNAProp = DNAProp(f"PROP.{propType.upper()}_DNARoot")
        newDNAProp.setCode(propType)
        newDNAProp.setPos(VBase3(0))
        newDNAProp.setHpr(VBase3(0))
        # Now place new prop in the world
        self.initDNANode(newDNAProp)

    def addAnimProp(self, animPropType):
        print("addAnimProp %s " % animPropType)
        # Record new anim prop type
        self.setCurrent('anim_prop_texture', animPropType)
        simpleName = re.sub(r'phase_\d_models_char__', '', animPropType).replace('animated_prop_', '').upper()
        newDNAAnimProp = DNAAnimProp(f"ANIM.{simpleName}_DNARoot")
        newDNAAnimProp.setCode(animPropType)
        newDNAAnimProp.setPos(VBase3(0))
        newDNAAnimProp.setHpr(VBase3(0))
        # Now place new prop in the world
        self.initDNANode(newDNAAnimProp)

    def addInteractiveProp(self, interactivePropType):
        print("addInteractiveProp %s " % interactivePropType)
        # Record new interactive prop type
        self.setCurrent('interactive_prop_texture', interactivePropType)
        simpleName = re.sub(r'phase_\d_models_char__', '', interactivePropType).replace('interactive_prop_', '').upper()
        newDNAInteractiveProp = DNAInteractiveProp(f"INTR.{simpleName}_DNARoot")
        newDNAInteractiveProp.setCode(interactivePropType)
        newDNAInteractiveProp.setPos(VBase3(0))
        newDNAInteractiveProp.setHpr(VBase3(0))
        # Now place new prop in the world
        self.initDNANode(newDNAInteractiveProp)

    def addStreet(self, streetType):
        # Record new street type
        self.setCurrent('street_texture', streetType)
        newDNAStreet = DNAStreet(f"STR.{streetType.replace('street_', '').upper()}_DNARoot")
        newDNAStreet.setCode(streetType)
        newDNAStreet.setPos(VBase3(0))
        newDNAStreet.setHpr(VBase3(0))
        newDNAStreet.setStreetTexture(
                'street_street_' + self.neighborhoodCode + '_tex')
        newDNAStreet.setSidewalkTexture(
                'street_sidewalk_' + self.neighborhoodCode + '_tex')
        newDNAStreet.setCurbTexture(
                'street_curb_' + self.neighborhoodCode + '_tex')
        # Now place new street in the world
        self.initDNANode(newDNAStreet)

    def createCornice(self):
        newDNACornice = DNACornice('cornice')
        newDNACornice.setCode(self.getCurrent('cornice_texture'))
        newDNACornice.setColor(self.getCurrent('cornice_color'))
        return newDNACornice

    def createDoor(self, type):
        if type == 'landmark_door':
            newDNADoor = DNADoor('door')
            print("createDoor %s" % type)
            if not (self.getCurrent('door_double_texture')):
                doorStyles = self.styleManager.attributeDictionary['door_double_texture'].getList()[1:]
                defaultDoorStyle = random.choice(doorStyles)
                self.setCurrent('door_double_texture', defaultDoorStyle)
            newDNADoor.setCode(self.getCurrent('door_double_texture'))
            print("doorcolor = %s" % self.getCurrent('door_color'))
            newDNADoor.setColor(self.getCurrent('door_color'))
        elif type == 'door':
            newDNADoor = DNAFlatDoor('door')
            if not (self.getCurrent('door_single_texture')):
                doorStyles = self.styleManager.attributeDictionary['door_single_texture'].getList()[1:]
                defaultDoorStyle = random.choice(doorStyles)
                self.setCurrent('door_single_texture', defaultDoorStyle)
            newDNADoor.setCode(self.getCurrent('door_single_texture'))
            newDNADoor.setColor(self.getCurrent('door_color'))
        return newDNADoor

    def createSign(self):
        if not (self.getCurrent('sign_texture')):
            defaultSignStyle = self.styleManager.attributeDictionary['sign_texture'].getList()[0]
            self.setCurrent('sign_texture', defaultSignStyle)
        newDNASign = DNASign('sign')
        newDNASign.setCode(self.getCurrent('sign_texture'))
        newDNASign.setColor(self.getCurrent('sign_color'))

        baseline = DNASignBaseline('baseline')
        baseline.setCode("humanist")
        baseline.setColor(VBase4(0.0, 0.0, 0.0, 1.0))
        baseline.setScale(VBase3(0.7, 1.0, 0.7))
        newDNASign.add(baseline)

        DNASetBaselineString(baseline, "Toon Shop")
        return newDNASign

    def createWindows(self):
        newDNAWindows = DNAWindows()
        newDNAWindows.setCode(self.getCurrent('window_texture'))
        newDNAWindows.setWindowCount(self.getCurrent('window_count'))
        newDNAWindows.setColor(self.getCurrent('window_color'))
        return newDNAWindows

    def removeCornice(self, cornice, parent):
        self.setCurrent('cornice_color', cornice.getColor())
        DNARemoveChildOfClass(parent, DNA_CORNICE)

    def removeLandmarkDoor(self, door, parent):
        self.setCurrent('door_color', door.getColor())
        DNARemoveChildOfClass(parent, DNA_DOOR)

    def removeSign(self, sign, parent):
        self.setCurrent('sign_color', sign.getColor())
        DNARemoveChildOfClass(parent, DNA_SIGN)

    def removeDoor(self, door, parent):
        self.setCurrent('door_color', door.getColor())
        DNARemoveChildOfClass(parent, DNA_FLAT_DOOR)

    def removeWindows(self, windows, parent):
        # And record number of windows
        self.setCurrent('window_texture', windows.getCode())
        self.setCurrent('window_color', windows.getColor())
        self.setCurrent('window_count', windows.getWindowCount())
        DNARemoveChildOfClass(parent, DNA_WINDOWS)

    def levelHandleMouse2(self, modifiers):
        # Record time of start of mouse interaction
        self.startT = globalClock.getFrameTime()
        self.startF = globalClock.getFrameCount()
        if base.direct.cameraControl.useMayaCamControls and modifiers == 4:  # alt is down, use maya controls
            self.mouseMayaCamera = True
        else:
            self.mouseMayaCamera = False

    def levelHandleMouse2Up(self):
        if self.startT is None or self.startF is None:
            return
        stopT = globalClock.getFrameTime()
        deltaT = stopT - self.startT
        stopF = globalClock.getFrameCount()
        deltaF = stopF - self.startF
        if not self.mouseMayaCamera and (deltaT <= 0.25) or (deltaF <= 1):
            # Check for a hit point based on current mouse position
            # Allow intersection with unpickable objects
            # And then spawn task to determine mouse mode
            # Don't intersect with hidden or backfacing objects
            base.direct.cameraControl.coaMarker.stash()
            skipFlags = SKIP_HIDDEN | SKIP_BACKFACE | SKIP_CAMERA  # | SKIP_UNPICKABLE
            base.direct.cameraControl.computeCOA(base.direct.iRay.pickGeom(skipFlags = skipFlags))
            self.newObjPos = base.direct.cameraControl.coaMarker.getPos(render)

    # LEVEL-OBJECT MODIFICATION FUNCTIONS
    def levelHandleMouse3(self, modifiers):
        if base.direct.cameraControl.useMayaCamControls and modifiers == 4:  # alt is down, use maya controls
            self.mouseMayaCamera = True
            return
        else:
            self.mouseMayaCamera = False

        if self.isSelecting: return
        self.DNATarget = None

        if not self.selectedNPRoot:
            return

        dnaObject = self.findDNANode(self.selectedNPRoot)
        if not dnaObject:
            return

        # Pick a menu based upon object type
        if DNAClassEqual(dnaObject, DNA_FLAT_BUILDING):
            # FLAT BUILDING OPERATIONS
            menuMode, wallNum = self.getFlatBuildingMode(dnaObject, modifiers)
            if menuMode is None:
                return
            # Find appropriate target
            wall = self.getWall(dnaObject, wallNum)
            self.lastBuilding = dnaObject
            self.lastWall = wall
            if menuMode.find('wall') >= 0:
                self.DNATarget = wall
                self.DNATargetParent = dnaObject
            elif menuMode.find('door') >= 0:
                self.DNATarget = DNAGetChildOfClass(wall, DNA_FLAT_DOOR)
                self.DNATargetParent = wall
            elif menuMode.find('window') >= 0:
                self.DNATarget = DNAGetChildOfClass(wall, DNA_WINDOWS)
                self.DNATargetParent = wall
            elif menuMode.find('cornice') >= 0:
                self.DNATarget = DNAGetChildOfClass(wall, DNA_CORNICE)
                self.DNATargetParent = wall
            else:
                self.DNATarget = dnaObject
        elif DNAClassEqual(dnaObject, DNA_PROP):
            # PROP OPERATIONS
            self.DNATarget = dnaObject
            if base.direct.gotControl(modifiers):
                menuMode = 'prop_color'
            elif base.direct.gotAlt(modifiers) and self.panel.currentBaselineDNA:
                menuMode = 'baseline_style'
            elif base.direct.gotShift(modifiers):
                menuMode = 'sign_texture'
                self.DNATarget = DNAGetChildOfClass(dnaObject, DNA_SIGN)
                self.DNATargetParent = dnaObject
            else:
                menuMode = 'prop_texture'
        elif DNAClassEqual(dnaObject, DNA_LANDMARK_BUILDING):
            # INSERT HERE
            # LANDMARK BUILDING OPERATIONS
            menuMode = self.getLandmarkBuildingMode(dnaObject, modifiers)
            if menuMode.find('door') >= 0:
                self.DNATarget = DNAGetChildOfClass(dnaObject, DNA_DOOR)
                self.DNATargetParent = dnaObject
            elif menuMode.find('sign') >= 0:
                self.DNATarget = DNAGetChildOfClass(dnaObject, DNA_SIGN)
                self.DNATargetParent = dnaObject
            else:
                self.DNATarget = dnaObject
        elif DNAClassEqual(dnaObject, DNA_STREET):
            # STREET OPERATIONS
            self.DNATarget = dnaObject
            menuMode = 'street_texture'
        elif DNAClassEqual(dnaObject, DNA_ANIM_PROP) or \
                DNAClassEqual(dnaObject, DNA_INTERACTIVE_PROP):
            # ANIM PROP OPERATIONS
            self.DNATarget = dnaObject
            if base.direct.gotControl(modifiers):
                menuMode = 'prop_color'
            else:
                menuMode = 'animlist_%s' % dnaObject.getCode()
        elif DNAClassEqual(dnaObject, DNA_ANIM_BUILDING):
            # ANIM BUILDING OPERATIONS
            if base.direct.gotShift(modifiers):
                self.DNATarget = dnaObject
                menuMode = 'animlist_%s' % dnaObject.getCode()
            else:
                menuMode = self.getLandmarkBuildingMode(dnaObject, modifiers)
                if menuMode.find('door') >= 0:
                    self.DNATarget = DNAGetChildOfClass(dnaObject, DNA_DOOR)
                    self.DNATargetParent = dnaObject
                elif menuMode.find('sign') >= 0:
                    self.DNATarget = DNAGetChildOfClass(dnaObject, DNA_SIGN)
                    self.DNATargetParent = dnaObject
                else:
                    self.DNATarget = dnaObject

        if menuMode is None:
            return

        self.activeMenu = self.getMenu(menuMode)

        state = None
        if self.DNATarget:
            if menuMode.find('texture') >= 0:
                state = self.DNATarget.getCode()
            elif menuMode.find('color') >= 0:
                state = self.DNATarget.getColor()
                self.panel.setCurrentColor(state)
                self.panel.setResetColor(state)
            elif menuMode.find('orientation') >= 0:
                state = self.DNATarget.getCode()[-2:]
            elif menuMode == 'building_width':
                state = self.DNATarget.getWidth()
            elif menuMode == 'window_count':
                state = self.DNATarget.getWindowCount()
            elif menuMode == 'building_style_all':
                state = DNAFlatBuildingStyle(building = self.DNATarget)
            elif menuMode == 'baseline_style':
                state = DNABaselineStyle(baseline = self.panel.currentBaselineDNA)
            elif menuMode == 'wall_style':
                state = DNAWallStyle(wall = self.DNATarget)
            elif menuMode.startswith('animlist_'):
                state = self.DNATarget.getAnim()

        self.activeMenu.setInitialState(state)

        self.activeMenu.spawnPieMenuTask()

    def getLandmarkBuildingMode(self, dnaObject, modifiers):
        # Where are we hitting the building?
        hitPt = self.getWallIntersectionPoint(self.selectedNPRoot)
        if hitPt[2] < 10.0:
            # Do door operations
            if base.direct.gotControl(modifiers):
                menuMode = 'door_color'
            elif base.direct.gotAlt(modifiers):
                menuMode = 'door_orientation'
            else:
                menuMode = 'door_double_texture'
        else:
            # Do sign operations
            if base.direct.gotControl(modifiers):
                menuMode = 'sign_color'
            elif base.direct.gotAlt(modifiers) and self.panel.currentBaselineDNA:
                menuMode = 'baseline_style'
            elif base.direct.gotAlt(modifiers):
                menuMode = 'sign_orientation'
            else:
                menuMode = 'sign_texture'
        return menuMode

    def getFlatBuildingMode(self, dnaObject, modifiers):
        # Where are we hitting the building?
        hitPt = self.getWallIntersectionPoint(self.selectedNPRoot)
        wallNum = self.computeWallNum(dnaObject, hitPt)
        if wallNum < 0:
            # Do building related operations
            # If we are using maya mode, allow the user to adjust width holding SHIFT instead of alt
            if base.direct.gotShift(modifiers):
                menuMode = 'building_width'
            else:
                menuMode = 'building_style_all'
        else:
            # Otherwise, do wall specific operations
            # Figure out where you are hitting on the wall
            wallHeights, offsetList = DNAGetWallHeights(dnaObject)
            # Find a normalized X and Z coordinate
            xPt = hitPt[0] / dnaObject.getWidth()
            # Adjust zPt depending on what wall you are pointing at
            wallHeight = wallHeights[wallNum]
            zPt = (hitPt[2] - offsetList[wallNum]) / wallHeight
            self.setCurrent('wall_height', wallHeight)
            # Determine which zone you are pointing at
            if zPt > 0.8:
                # Do cornice operations
                if base.direct.gotControl(modifiers):
                    menuMode = 'cornice_color'
                elif base.direct.gotAlt(modifiers):
                    menuMode = 'cornice_orientation'
                else:
                    menuMode = 'cornice_texture'
            elif (xPt < 0.3) or (xPt > 0.7):
                # Do wall operations
                if base.direct.gotControl(modifiers):
                    menuMode = 'wall_color'
                elif base.direct.gotAlt(modifiers):
                    menuMode = 'wall_orientation'
                elif base.direct.gotShift(modifiers):
                    menuMode = 'wall_texture'
                else:
                    menuMode = 'wall_style'
            elif zPt < 0.4:
                # Do door operations
                if base.direct.gotControl(modifiers):
                    menuMode = 'door_color'
                elif base.direct.gotAlt(modifiers):
                    menuMode = 'door_orientation'
                else:
                    menuMode = 'door_single_texture'
            else:
                # Do window operations
                if base.direct.gotControl(modifiers):
                    menuMode = 'window_color'
                elif base.direct.gotAlt(modifiers):
                    menuMode = 'window_orientation'
                elif base.direct.gotShift(modifiers):
                    menuMode = 'window_count'
                else:
                    menuMode = 'window_texture'
        return menuMode, wallNum

    def levelHandleMouse3Up(self):
        if self.activeMenu:
            self.activeMenu.removePieMenuTask()
        # Update panel color if appropriate
        if self.DNATarget:
            objClass = DNAGetClassType(self.DNATarget)
            if objClass in [DNA_WALL, DNA_WINDOWS, DNA_DOOR, DNA_FLAT_DOOR, DNA_CORNICE, DNA_PROP]:
                self.panel.setCurrentColor(self.DNATarget.getColor())

    def setDNATargetColor(self, color):
        if self.DNATarget:
            self.DNATarget.setColor(color)
            self.replaceSelected()

    def setAnimPropAnim(self, anim):
        if self.DNATarget is None:
            return
        self.DNATarget.setAnim(anim)
        animPropObj = self.animPropDict.get(self.DNATarget)
        if animPropObj is None:
            return

        animPropObj.exit()
        animPropObj.node.loadAnims({'anim': "%s/%s" % (animPropObj.path, anim)})
        animPropObj.enter()

    def setDNATargetCode(self, type, code):
        if (self.DNATarget is not None) and (code is not None):
            # Update code
            self.DNATarget.setCode(code)
        elif (self.DNATarget is not None) and (code is None):
            # Delete object, record pertinant properties for restore later
            if type == 'cornice':
                self.removeCornice(self.DNATarget, self.DNATargetParent)
            elif type == 'sign':
                self.removeSign(self.DNATarget, self.DNATargetParent)
            elif type == 'landmark_door':
                self.removeLandmarkDoor(self.DNATarget, self.DNATargetParent)
            elif type == 'door':
                self.removeDoor(self.DNATarget, self.DNATargetParent)
            elif type == 'windows':
                self.removeWindows(self.DNATarget, self.DNATargetParent)
            self.DNATarget = None
        elif (self.DNATarget is None) and (code is not None):
            # Add new object
            if type == 'cornice':
                self.DNATarget = self.createCornice()
            elif type == 'sign':
                self.DNATarget = self.createSign()
            elif type == 'landmark_door':
                self.DNATarget = self.createDoor('landmark_door')
            elif type == 'door':
                self.DNATarget = self.createDoor('door')
            elif type == 'windows':
                # Make sure window_count n.e. 0
                if self.getCurrent('window_count') == 0:
                    self.setCurrent('window_count', self.getRandomWindowCount())
                self.DNATarget = self.createWindows()
            if self.DNATarget:
                self.DNATargetParent.add(self.DNATarget)
        # Update visible representation
        self.replaceSelected()

    def setDNATargetOrientation(self, orientation):
        if (self.DNATarget is not None) and (orientation is not None):
            oldCode = self.DNATarget.getCode()[:-2]
            # Suit walls only have two orientations!
            if oldCode.find('wall_suit') >= 0:
                orientation = 'u' + orientation[1]
            self.DNATarget.setCode(oldCode + orientation)
            self.replaceSelected()

    def setBuildingStyle(self, style):
        if (self.DNATarget is not None) and (style is not None):
            self.styleManager.setDNAFlatBuildingStyle(
                    self.DNATarget, style,
                    width = self.DNATarget.getWidth(),
                    name = self.DNATarget.getName())
            # TODO: Need to disable dna store warning
            self.replaceSelected()
            # Re-add replication hooks so we get right kind of copy
            # self.addReplicationHooks(self.DNATarget)

    def setBuildingType(self, type):
        print('setBuildingType: ', repr(type))

    def setBuildingWidth(self, width):
        if self.DNATarget:
            self.DNATarget.setWidth(width)
            self.replaceSelected()

    def setWindowCount(self, count):
        if (self.DNATarget is not None) and (count != 0):
            self.DNATarget.setWindowCount(count)
        elif (self.DNATarget is not None) and (count == 0):
            self.removeWindows(self.DNATarget, self.DNATargetParent)
            self.DNATarget = None
        elif (self.DNATarget is None) and (count != 0):
            self.DNATarget = self.createWindows()
            self.DNATargetParent.add(self.DNATarget)
        self.replaceSelected()

    def setWallStyle(self, style):
        if (self.DNATarget is not None) and (style is not None):
            self.styleManager.setDNAWallStyle(
                    self.DNATarget, style,
                    self.DNATarget.getHeight())
            self.replaceSelected()

    def setColor(self, nodePath, r, g, b, a):
        """ This is used to set color of dnaNode subparts """
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            objClass = DNAGetClassType(dnaNode)
            if objClass in [DNA_WALL, DNA_WINDOWS, DNA_DOOR, DNA_FLAT_DOOR, DNA_CORNICE, DNA_PROP, DNA_SIGN,
                            DNA_SIGN_BASELINE, DNA_SIGN_TEXT, DNA_SIGN_GRAPHIC]:
                # Update dna information
                dnaNode.setColor(VBase4(r / 255.0, g / 255.0, b / 255.0, a / 255.0))

    # SELECTION FUNCTIONS
    def selectedNodePathHook(self, nodePath):
        """
        Hook called upon selection of a node path used to restrict
        selection to DNA Objects.  Press control to select any type of
        DNA Object, with no control key pressed, hook selects only
        DNA Root objects
        """
        self.selectedDNARoot = None
        self.selectedNPRoot = None
        self.selectedSuitPoint = None
        # Now process newly selected node path
        dnaParent = None
        dnaNode = self.findDNANode(nodePath)
        if base.direct.fControl:
            if not dnaNode:
                dnaParent = self.findDNAParent(nodePath.getParent())
        else:
            # Is the current node a DNA Root object?
            if nodePath.getName()[-8:] != '_DNARoot':
                # No it isn't, look for a parent DNA Root object
                dnaParent = self.findDNARoot(nodePath.getParent())
        # Do we need to switch selection to a parent object?
        if dnaParent:
            base.direct.deselect(nodePath)
            base.direct.select(dnaParent, base.direct.fShift)
        elif dnaNode:
            self.selectedNPRoot = nodePath
            self.selectedDNARoot = dnaNode
            # Reset last landmark
            if DNAClassEqual(dnaNode, DNA_LANDMARK_BUILDING):
                self.lastLandmarkBuildingDNA = dnaNode
                self.panel.landmarkBuildingNameString.set(dnaNode.getTitle())
                if self.showLandmarkBlockToggleGroup:
                    # Toggle old highlighting off:
                    self.toggleShowLandmarkBlock()
                    # Toggle on the the new highlighting:
                    self.toggleShowLandmarkBlock()
            # Reset last Code (for autoPositionGrid)
            if DNAClassEqual(dnaNode, DNA_STREET):
                self.snapList = self.getSnapPoint(dnaNode.getCode())
        else:
            pointOrCell, type = self.findPointOrCell(nodePath)
            if pointOrCell and (type == 'suitPointMarker'):
                print("Found suit point!", pointOrCell)
                self.selectedSuitPoint = pointOrCell
            elif pointOrCell and (type == 'battleCellMarker'):
                print("Found battle cell!", pointOrCell)
            else:
                if nodePath.getName() != 'suitEdge':
                    suitEdge = self.findSuitEdge(nodePath.getParent())
                    if suitEdge:
                        base.direct.deselect(nodePath)
                        base.direct.select(suitEdge, base.direct.fShift)

        for hook in self.selectedNodePathHookHooks:
            hook()

        if self.fDrive:
            base.direct.deselect(nodePath)

    def deselectedNodePathHook(self, nodePath):
        self.selectedDNARoot = None
        self.selectedNPRoot = None
        self.selectedSuitPoint = None
        for hook in self.deselectedNodePathHookHooks:
            hook()

    def findDNAParent(self, nodePath):
        """ Walk up a node path's ancestry looking for its DNA Root """
        if self.findDNANode(nodePath):
            return nodePath
        else:
            if not nodePath.hasParent():
                return 0
            else:
                return self.findDNAParent(nodePath.getParent())

    def findDNARoot(self, nodePath):
        """ Walk up a node path's ancestry looking for its DNA Root """
        if nodePath.getName()[-8:] == '_DNARoot':
            return nodePath
        else:
            if not nodePath.hasParent():
                return None
            else:
                return self.findDNARoot(nodePath.getParent())

    def findSuitEdge(self, nodePath):
        """ Walk up a node path's ancestry looking for a suit edge """
        if nodePath.getName() == 'suitEdge':
            return nodePath
        else:
            if not nodePath.hasParent():
                return None
            else:
                return self.findSuitEdge(nodePath.getParent())

    def findPointOrCell(self, nodePath):
        """
        Walk up a node path's ancestry to see if its a suit point marker
        or a battle cell marker
        """
        if nodePath.getName() == 'suitPointMarker':
            # See if point is in pointDict
            point = self.getSuitPointFromNodePath(nodePath)
            return point, 'suitPointMarker'
        elif nodePath.getName() == 'battleCellMarker':
            # See if cell is in cell Dict
            cell = self.getBattleCellFromNodePath(nodePath)
            return cell, 'battleCellMarker'
        else:
            if not nodePath.hasParent():
                return None, None
            else:
                return self.findPointOrCell(nodePath.getParent())

    def drawLinkLine(self, battleCellNP, propNP):
        linkLine = battleCellNP.find('linkLine')
        if not linkLine.isEmpty():
            linkLine.removeNode()

        linkLine = battleCellNP.attachNewNode('linkLine')
        lines = LineNodePath(linkLine)
        lines.setColor(VBase4(1, 1, 0, 1))
        lines.setThickness(3)
        lines.moveTo(0, 0, 0)
        toPos = propNP.getPos(battleCellNP)
        lines.drawTo(toPos)
        lines.create()

    def connectToCell(self, disconnect = False):
        selectedNPs = base.direct.selected.getSelectedAsList()
        if len(selectedNPs) != 2:
            if not disconnect:
                message = 'To connect a cell to a prop, make sure that "Show Cells" are enabled, select a prop you want to connect with,\n' + \
                          'and while holding shift, click on the cell you want to connect to (this will select both at the same time),\n' + \
                          'And then click on "Connect prop to cell" again.  You should see a line connecting the two if you\'ve done everything correctly.'
                showinfo('Level Editor', message)
            return

        if self.selectedNPRoot:  # when interactiveProp is selected last
            battleCellNP = selectedNPs[0]
            propNP = selectedNPs[1]

        else:  # when battle cell marker is selected last
            battleCellNP = selectedNPs[1]
            propNP = selectedNPs[0]

        dnaNode = self.findDNANode(propNP)
        poitnOrCell, type = self.findPointOrCell(battleCellNP)
        cellId = battleCellNP.getParent().getTag('cellId')
        if dnaNode is None or not DNAClassEqual(dnaNode, DNA_INTERACTIVE_PROP):
            return
        if type != 'battleCellMarker' or cellId == '':
            return

        oldCellId = dnaNode.getCellId()
        if oldCellId != -1:
            visGroup = self.getVisGroup(battleCellNP)
            if visGroup is None:
                return
            for battleCellMarkerNP in visGroup.findAllMatches("**/battleCellMarker"):
                if battleCellMarkerNP.getTag('cellId') == '%d' % oldCellId:
                    markerGeom = battleCellMarkerNP.find('Sphere')
                    if not markerGeom.isEmpty():
                        linkLine = markerGeom.find('linkLine')
                        if not linkLine.isEmpty():
                            linkLine.removeNode()
                    break

        if disconnect:
            dnaNode.setCellId(-1)
            return

        dnaNode.setCellId(int(cellId))
        self.drawLinkLine(battleCellNP, propNP)

    # MANIPULATION FUNCTIONS
    def keyboardRotateSelected(self, arrowDirection):
        """ Rotate selected objects using arrow keys """
        # Get current snap angle
        if (arrowDirection == 'up') or (arrowDirection == 'down'):
            oldSnapAngle = base.direct.grid.snapAngle
            base.direct.grid.setSnapAngle(1.0)
        snapAngle = base.direct.grid.snapAngle
        # Compute new Snap Angle
        if arrowDirection in ['left', 'up']:
            self.setLastAngle(self.getLastAngle() + snapAngle)
        if arrowDirection in ['right', 'down']:
            self.setLastAngle(self.getLastAngle() - snapAngle)

        if self.getLastAngle() < -180.0:
            self.setLastAngle(self.getLastAngle() + 360.0)
        elif self.getLastAngle() > 180.0:
            self.setLastAngle(self.getLastAngle() - 360.0)
        for selectedNode in base.direct.selected:
            selectedNode.setHpr(self.getLastAngle(), 0, 0)
        # Snap objects to grid and update DNA if necessary
        self.updateSelectedPose(base.direct.selected.getSelectedAsList())
        if (arrowDirection == 'up') or (arrowDirection == 'down'):
            base.direct.grid.setSnapAngle(oldSnapAngle)

    def keyboardZTranslateSelected(self, arrowDirection):
        gridToCamera = base.direct.grid.getMat(base.direct.camera)
        camXAxis = gridToCamera.xformVec(X_AXIS)
        xxDot = camXAxis.dot(X_AXIS)
        xzDot = camXAxis.dot(Z_AXIS)

        # what is the current grid spacing?
        if (arrowDirection == 'left') or (arrowDirection == 'right'):
            oldGridSpacing = base.direct.grid.gridSpacing
            # Use back door to set grid spacing to avoid grid update
            base.direct.grid.gridSpacing = 1.0
        deltaMove = base.direct.grid.gridSpacing

        # Compute the specified delta
        deltaPos = Vec3(0)
        if abs(xxDot) > abs(xzDot):
            if xxDot < 0.0:
                deltaMove = -deltaMove

            # Compute delta
            if (arrowDirection == 'up') or (arrowDirection == 'left'):
                deltaPos.setZ(deltaPos[2] + deltaMove)
            elif (arrowDirection == 'down') or (arrowDirection == 'right'):
                deltaPos.setZ(deltaPos[2] - deltaMove)
        else:
            if xzDot < 0.0:
                deltaMove = -deltaMove
            # Compute delta
            if (arrowDirection == 'down') or (arrowDirection == 'right'):
                deltaPos.setZ(deltaPos[2] + deltaMove)
            elif (arrowDirection == 'up') or (arrowDirection == 'left'):
                deltaPos.setZ(deltaPos[2] - deltaMove)

        for selectedNode in base.direct.selected:
            selectedNode.setPos(base.direct.grid, selectedNode.getPos(base.direct.grid) + deltaPos)
        # Snap objects to grid and update DNA if necessary
        self.updateSelectedPose(base.direct.selected.getSelectedAsList())
        if (arrowDirection == 'left') or (arrowDirection == 'right'):
            base.direct.grid.gridSpacing = oldGridSpacing

    def keyboardTranslateSelected(self, arrowDirection):
        gridToCamera = base.direct.grid.getMat(base.direct.camera)
        camXAxis = gridToCamera.xformVec(X_AXIS)
        xxDot = camXAxis.dot(X_AXIS)
        xzDot = camXAxis.dot(Z_AXIS)

        # Get the current Grid Spacing?
        if base.direct.fShift:
            oldGridSpacing = base.direct.grid.gridSpacing
            # Use back door to set grid spacing to avoid grid update
            base.direct.grid.gridSpacing = 1.0
        deltaMove = base.direct.grid.gridSpacing

        # Compute the specified delta
        deltaPos = Vec3(0)
        if abs(xxDot) > abs(xzDot):
            if xxDot < 0.0:
                deltaMove = -deltaMove
            # Compute delta
            if arrowDirection == 'right':
                deltaPos.setX(deltaPos[0] + deltaMove)
            elif arrowDirection == 'left':
                deltaPos.setX(deltaPos[0] - deltaMove)
            elif arrowDirection == 'up':
                deltaPos.setY(deltaPos[1] + deltaMove)
            elif arrowDirection == 'down':
                deltaPos.setY(deltaPos[1] - deltaMove)
        else:
            if xzDot < 0.0:
                deltaMove = -deltaMove
            # Compute delta
            if arrowDirection == 'right':
                deltaPos.setY(deltaPos[1] - deltaMove)
            elif arrowDirection == 'left':
                deltaPos.setY(deltaPos[1] + deltaMove)
            elif arrowDirection == 'up':
                deltaPos.setX(deltaPos[0] - deltaMove)
            elif arrowDirection == 'down':
                deltaPos.setX(deltaPos[0] + deltaMove)

        for selectedNode in base.direct.selected:
            selectedNode.setPos(base.direct.grid, selectedNode.getPos(base.direct.grid) + deltaPos)
        # Snap objects to grid and update DNA if necessary
        self.updateSelectedPose(base.direct.selected.getSelectedAsList())
        # Restore grid spacing
        if base.direct.fShift:
            # Use back door to set grid spacing to avoid grid update
            base.direct.grid.gridSpacing = oldGridSpacing

    def keyboardXformSelected(self, arrowDirection, mode):
        if mode == 'rotate':
            self.keyboardRotateSelected(arrowDirection)
        elif mode == 'zlate':
            self.keyboardZTranslateSelected(arrowDirection)
        else:
            self.keyboardTranslateSelected(arrowDirection)

    # VISIBILITY FUNCTIONS
    def editDNAVisGroups(self):
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        if visGroups:
            self.vgpanel = VisGroupsEditor.VisGroupsEditor(self, visGroups)
        else:
            showinfo('Vis Groups Editor', 'No DNA Vis Groups Found!')

    def getDNAVisGroups(self, nodePath):
        """ Find the highest level vis groups in the scene graph """
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            if DNAClassEqual(dnaNode, DNA_VIS_GROUP):
                return [[nodePath, dnaNode]]
        childVisGroups = []
        children = nodePath.getChildren()
        for child in children:
            childVisGroups = (childVisGroups + self.getDNAVisGroups(child))
        return childVisGroups

    def findParentVisGroup(self, nodePath):
        """ Find the containing vis group """
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            if DNAClassEqual(dnaNode, DNA_VIS_GROUP):
                return nodePath, dnaNode
        elif nodePath.hasParent():
            return self.findParentVisGroup(nodePath.getParent())
        return None, None

    def showGrid(self, flag):
        """ toggle direct grid """
        if flag:
            base.direct.grid.enable()
        else:
            base.direct.grid.disable()

    # LEVEL MAP/MARKER FUNCTIONS
    def createLevelMaps(self):
        """
        Load up the various neighborhood maps
        """
        self.levelMap = hidden.attachNewNode('level-map')
        self.activeMap = None
        self.mapDictionary = {}
        """
        for neighborhood in NEIGHBORHOODS:
            self.createMap(neighborhood)
        """

    def createMap(self, neighborhood):
        map = loader.loadModel('models/level_editor/' + neighborhood +
                               '_layout')
        if map:
            map.setTransparency(1)
            map.setColor(Vec4(1, 1, 1, .4))
            self.mapDictionary[neighborhood] = map
            # Make sure this item isn't pickable
            base.direct.addUnpickable(neighborhood + '_layout')

    def selectMap(self, neighborhood):
        if self.activeMap:
            self.activeMap.reparentTo(hidden)
        if neighborhood in self.mapDictionary:
            self.activeMap = self.mapDictionary[neighborhood]
            self.activeMap.reparentTo(self.levelMap)

    def toggleMapVis(self, flag):
        if flag:
            self.levelMap.reparentTo(base.direct.group)
        else:
            self.levelMap.reparentTo(hidden)

    def createInsertionMarker(self):
        self.insertionMarker = LineNodePath(self)
        self.insertionMarker.lineNode.setName('insertionMarker')
        self.insertionMarker.setColor(VBase4(0.785, 0.785, 0.5, 1))
        self.insertionMarker.setThickness(1)
        self.insertionMarker.reset()
        self.insertionMarker.moveTo(-75, 0, 0)
        self.insertionMarker.drawTo(75, 0, 0)
        self.insertionMarker.moveTo(0, -75, 0)
        self.insertionMarker.drawTo(0, 75, 0)
        self.insertionMarker.moveTo(0, 0, -75)
        self.insertionMarker.drawTo(0, 0, 75)
        self.insertionMarker.create()

    def spawnInsertionMarkerTask(self):
        taskMgr.add(self.insertionMarkerTask, 'insertionMarkerTask')

    def insertionMarkerTask(self, state):
        self.insertionMarker.setPosHpr(base.direct.grid, 0, 0, 0, 0, 0, 0)
        return Task.cont

    # UTILITY FUNCTIONS
    def getRandomDictionaryEntry(self, dict):
        numKeys = len(dict)
        if numKeys > 0:
            keys = list(dict.keys())
            key = keys[random.randint(0, numKeys - 1)]
            return dict[key]
        else:
            return None

    def getRandomWindowCount(self):
        if (self.lastWall is not None) and (self.lastBuilding is not None):
            h = ROUND_INT(self.lastWall.getHeight())
            w = ROUND_INT(self.lastBuilding.getWidth())
            if w == 5:
                # 5 ft walls can have 1 window
                return 1
            elif h == 10:
                # All other 10 ft high bldgs can have 1 or 2
                return random.randint(1, 2)
            else:
                # All others can have 1 - 4
                return random.randint(1, 4)
        else:
            return 1

    def autoPositionGrid(self, fLerp = 0):
        taskMgr.remove('autoPositionGrid')
        # Move grid to prepare for placement of next object
        selectedNode = base.direct.selected.last
        if selectedNode:
            dnaNode = self.findDNANode(selectedNode)
            if dnaNode is None:
                return
            nodeClass = DNAGetClassType(dnaNode)
            deltaPos = Point3(20, 0, 0)
            deltaHpr = VBase3(0)
            if nodeClass == DNA_FLAT_BUILDING:
                deltaPos.setX(dnaNode.getWidth())
            elif nodeClass == DNA_STREET:
                objectCode = dnaNode.getCode()
                deltas = self.getNextSnapPoint()
                deltaPos.assign(deltas[0])
                deltaHpr.assign(deltas[1])
            elif nodeClass == DNA_LANDMARK_BUILDING:
                objectCode = dnaNode.getCode()
                if objectCode[-2:-1] == 'A':
                    deltaPos.setX(25.0)
                elif objectCode[-2:-1] == 'B':
                    deltaPos.setX(15.0)
                elif objectCode[-2:-1] == 'C':
                    deltaPos.setX(20.0)
            if fLerp:
                # Position grid for placing next object
                # Eventually we need to setHpr too
                t = base.direct.grid.lerpPosHpr(
                        0.25, deltaPos, deltaHpr,
                        other = selectedNode,
                        blendType = 'easeInOut',
                        task = 'autoPositionGrid')
                t.deltaPos = deltaPos
                t.deltaHpr = deltaHpr
                t.selectedNode = selectedNode
                t.setUponDeath(self.autoPositionCleanup)
            else:
                base.direct.grid.setPosHpr(selectedNode, deltaPos, deltaHpr)

        if self.mouseMayaCamera:
            return
        taskMgr.remove('autoMoveDelay')
        handlesToCam = base.direct.widget.getPos(base.direct.camera)
        handlesToCam = handlesToCam * (base.direct.dr.near / handlesToCam[1])
        if ((abs(handlesToCam[0]) > (base.direct.dr.nearWidth * 0.4)) or
                (abs(handlesToCam[2]) > (base.direct.dr.nearHeight * 0.4))):
            taskMgr.remove('manipulateCamera')
            base.direct.cameraControl.centerCamIn(0.5)

    def autoPositionCleanup(self, state):
        base.direct.grid.setPosHpr(state.selectedNode, state.deltaPos, state.deltaHpr)
        if base.direct.grid.getHprSnap():
            # Clean up grid angle
            base.direct.grid.setH(ROUND_TO(base.direct.grid.getH(),
                                           base.direct.grid.snapAngle))

    def getNextSnapPoint(self):
        """ Pull next pos hpr deltas off of snap list then rotate list """
        if self.snapList:
            deltas = self.snapList[0]
            # Rotate list by one
            self.snapList = self.snapList[1:] + self.snapList[:1]
            return deltas
        else:
            return ZERO_VEC, ZERO_VEC

    def getWallIntersectionPoint(self, selectedNode):
        """
        Return point of intersection between building's wall and line from cam
        through mouse.
        """
        # Find mouse point on near plane
        mouseX = base.direct.dr.mouseX
        mouseY = base.direct.dr.mouseY
        nearX = (math.tan(deg2Rad(base.direct.dr.fovH) / 2.0) *
                 mouseX * base.direct.dr.near)
        nearZ = (math.tan(deg2Rad(base.direct.dr.fovV) / 2.0) *
                 mouseY * base.direct.dr.near)
        # Initialize points
        mCam2Wall = base.direct.camera.getMat(selectedNode)
        mouseOrigin = Point3(0)
        mouseOrigin.assign(mCam2Wall.getRow3(3))
        mouseDir = Vec3(0)
        mouseDir.set(nearX, base.direct.dr.near, nearZ)
        mouseDir.assign(mCam2Wall.xformVec(mouseDir))
        # Calc intersection point
        return planeIntersect(mouseOrigin, mouseDir, ZERO_POINT, NEG_Y_AXIS)

    def getGridSnapIntersectionPoint(self):
        """
        Return point of intersection between ground plane and line from cam
        through mouse. Return false, if nothing selected. Snap to grid.
        """
        return base.direct.grid.computeSnapPoint(self.getGridIntersectionPoint())

    def getGridIntersectionPoint(self):
        """
        Return point of intersection between ground plane and line from cam
        through mouse. Return false, if nothing selected
        """
        # Find mouse point on near plane
        mouseX = base.direct.dr.mouseX
        mouseY = base.direct.dr.mouseY
        nearX = (math.tan(deg2Rad(base.direct.dr.fovH) / 2.0) *
                 mouseX * base.direct.dr.near)
        nearZ = (math.tan(deg2Rad(base.direct.dr.fovV) / 2.0) *
                 mouseY * base.direct.dr.near)
        # Initialize points
        mCam2Grid = base.direct.camera.getMat(base.direct.grid)
        mouseOrigin = Point3(0)
        mouseOrigin.assign(mCam2Grid.getRow3(3))
        mouseDir = Vec3(0)
        mouseDir.set(nearX, base.direct.dr.near, nearZ)
        mouseDir.assign(mCam2Grid.xformVec(mouseDir))
        # Calc intersection point
        return planeIntersect(mouseOrigin, mouseDir, ZERO_POINT, Z_AXIS)

    def jumpToInsertionPoint(self):
        """ Move selected object to insertion point """
        selectedNode = base.direct.selected.last
        if selectedNode:
            dnaNode = self.findDNANode(selectedNode)
            if dnaNode:
                selectedNode.setPos(base.direct.grid, 0, 0, 0)
                selectedNode.setHpr(self.getLastAngle(), 0, 0)
                dnaNode.setPos(selectedNode.getPos())
                dnaNode.setHpr(selectedNode.getHpr())
                self.autoPositionGrid()

    # GETTERS/SETTERS
    # DNA Object elements
    def getWall(self, dnaFlatBuilding, wallNum):
        wallCount = 0
        for i in range(dnaFlatBuilding.getNumChildren()):
            child = dnaFlatBuilding.at(i)
            if DNAClassEqual(child, DNA_WALL):
                if wallCount == wallNum:
                    return child
                wallCount = wallCount + 1
        return None

    def computeWallNum(self, aDNAFlatBuilding, hitPt):
        """
        Given a hitPt, return wall number if cursor is over building
        Return -1 if cursor is outside of building
        """
        xPt = hitPt[0]
        zPt = hitPt[2]
        # Left or right of building
        if (xPt < 0) or (xPt > aDNAFlatBuilding.getWidth()):
            return -1
        # Below the building
        if zPt < 0:
            return -1
        # Above z = 0 and within wall width, check height of walls
        heightList, offsetList = DNAGetWallHeights(aDNAFlatBuilding)
        wallNum = 0
        for i in range(len(heightList)):
            # Compute top of wall segment
            top = offsetList[i] + heightList[i]
            if zPt < top:
                return wallNum
            wallNum = wallNum + 1
        return -1

    def getWindowCount(self, dnaWall):
        windowCount = 0
        for i in range(dnaWall.getNumChildren()):
            child = dnaWall.at(i)
            if DNAClassEqual(child, DNA_WINDOWS):
                windowCount = windowCount + 1
        return windowCount

    def setEditMode(self, neighborhood):
        self.neighborhood = neighborhood
        self.neighborhoodCode = NEIGHBORHOOD_CODES[self.neighborhood]
        if neighborhood == 'toontown_central':
            self.outputDir = 'ToontownCentral'
        elif neighborhood == 'donalds_dock':
            self.outputDir = 'DonaldsDock'
        elif neighborhood == 'minnies_melody_land':
            self.outputDir = 'MinniesMelodyLand'
        elif neighborhood == 'the_burrrgh':
            self.outputDir = 'TheBurrrgh'
        elif neighborhood == 'daisys_garden':
            self.outputDir = 'DaisysGarden'
        elif neighborhood == 'donalds_dreamland':
            self.outputDir = 'DonaldsDreamland'
        self.panel.editMenu.selectitem(neighborhood)
        self.styleManager.setEditMode(neighborhood)
        self.panel.updateHeightList(self.getCurrent('building_height'))
        self.selectMap(neighborhood)

    def getEditMode(self):
        return self.styleManager.getEditMode()

    # Level Style Attributes
    def __getitem__(self, attribute):
        """ Return top level entry in attribute dictionary """
        return self.styleManager.attributeDictionary[attribute]

    def getAttribute(self, attribute):
        """ Return specified attribute for current neighborhood """
        return self.styleManager.getAttribute(attribute)

    def hasAttribute(self, attribute):
        """ Return specified attribute for current neighborhood """
        return self.styleManager.hasAttribute(attribute)

    def getCurrent(self, attribute):
        """ Return neighborhood's current selection for specified attribute """
        return self.getAttribute(attribute).getCurrent()

    def setCurrent(self, attribute, newCurrent):
        """ Set neighborhood's current selection for specified attribute """
        self.getAttribute(attribute).setCurrent(newCurrent, fEvent = 0)

    def getMenu(self, attribute):
        """ Return neighborhood's Pie Menu object for specified attribute """
        return self.getAttribute(attribute).getMenu()

    def getDict(self, attribute):
        """ Return neighborhood's Dictionary for specified attribute """
        return self.getAttribute(attribute).getDict()

    def getList(self, attribute):
        """ Return neighborhood's List for specified attribute """
        return self.getAttribute(attribute).getList()

    # DNA variables
    def getDNAData(self):
        return self.DNAData

    def getDNAToplevel(self):
        return self.DNAToplevel

    def getDNAParent(self):
        return self.DNAParent

    def getDNATarget(self):
        return self.DNATarget

    # Node Path variables
    def getNPToplevel(self):
        return self.NPToplevel

    def getNPParent(self):
        return self.NPParent

    # Count of groups added to level
    def setGroupNum(self, num):
        self.groupNum = num

    def getGroupNum(self):
        return self.groupNum

    # Angle of last object added to level
    def setLastAngle(self, angle):
        self.lastAngle = angle

    def getLastAngle(self):
        return self.lastAngle

    def drawSuitEdge(self, edge, parent):
        # Draw a line from start to end
        edgeLine = LineNodePath(parent)
        edgeLine.lineNode.setName('suitEdge')
        edgeLine.setColor(VBase4(0.0, 0.0, 0.5, 1))
        edgeLine.setThickness(1)
        edgeLine.reset()
        # We need to draw the arrow relative to the parent, but the
        # point positions are relative to the NPToplevel. So get the
        # start and end positions relative to the parent, then draw
        # the arrow using those points
        tempNode = self.NPToplevel.attachNewNode('tempNode')
        mat = self.NPToplevel.getMat(parent)
        relStartPos = Point3(mat.xformPoint(edge.getStartPoint().getPos()))
        relEndPos = Point3(mat.xformPoint(edge.getEndPoint().getPos()))
        # Compute offset: a vector rotated 90 degrees clockwise
        offset = Vec3(relEndPos - relStartPos)
        offset.normalize()
        offset *= 0.1
        a = offset[0]
        offset.setX(offset[1])
        offset.setY(-1 * a)
        # Just to get it above the street
        offset.setZ(0.05)
        # Add offset to start and end to help differentiate lines
        relStartPos += offset
        relEndPos += offset
        edgeLine.drawArrow(relStartPos, relEndPos, 15, 1)  # startpos, endpos, ang, len
        edgeLine.create()
        # Add a clickable sphere
        marker = self.suitPointMarker.copyTo(edgeLine)
        marker.setName('suitEdgeMarker')
        midPos = (relStartPos + relEndPos) / 2.0
        marker.setPos(midPos)
        # Adjust color of highlighted lines
        if edge in self.visitedEdges:
            NodePath.setColor(edgeLine, 1, 0, 0, 1)
        tempNode.removeNode()
        return edgeLine

    def drawSuitPoint(self, suitPoint, pos, type, parent):
        marker = self.suitPointMarker.copyTo(parent)
        marker.setName("suitPointMarker")
        marker.setPos(pos)
        label = DirectGui.DirectLabel(text = '%d' % suitPoint.getIndex(),
                                      pos = (0.0, 0.0, 2),
                                      text_font = ToontownGlobals.getSignFont(),
                                      parent = marker.getChild(0), relief = None, scale = 3)
        label.setBillboardPointWorld()
        label.setDepthWrite(False)
        label.setDepthTest(not self.labelsOnTop)
        label.setScale(3)
        label.setName(f'suit_point_label_{suitPoint.getIndex()}')
        if not self.panel.pathLabels.get():
            label.hide()
        if type == DNASuitPoint.STREETPOINT:
            color = Vec4(0.0, 0.0, 1.0, 1.0)
            marker.setScale(0.4)
        elif type == DNASuitPoint.FRONTDOORPOINT:
            color = Vec4(0.0, 0.6, 1.0, 1.0)
            marker.setScale(0.5)
        elif type == DNASuitPoint.SIDEDOORPOINT:
            color = Vec4(0.0, 1.0, 0.2, 1.0)
            marker.setScale(0.5)
        else:
            color = (0.0, 0.0, 1.0, 1.0)
        # Highlight if necessary
        if suitPoint in self.visitedPoints:
            marker.setColor(1, 0, 0, 1)

        marker.setColor(color)
        label['text_fg'] = color
        return marker

    def placeSuitPoint(self):
        v = self.getGridSnapIntersectionPoint()
        # get the absolute pos relative to the top level.
        # That is what gets stored in the point
        mat = base.direct.grid.getMat(self.NPToplevel)
        absPos = Point3(mat.xformPoint(v))
        print('Suit point: ' + repr(absPos))
        # Store the point in the DNA. If this point is already in there, it returns the existing point
        suitPoint = DNASTORE.storeSuitPoint(self.currentSuitPointType, absPos)
        print("placeSuitPoint: ", suitPoint)
        # In case the point returned is a different type, update our type
        self.currentSuitPointType = suitPoint.getPointType()
        if suitPoint not in self.pointDict:
            marker = self.drawSuitPoint(suitPoint,
                                        absPos, self.currentSuitPointType,
                                        self.suitPointToplevel)
            self.pointDict[suitPoint] = marker
        self.currentSuitPointIndex = suitPoint.getIndex()
        if self.startSuitPoint:
            self.endSuitPoint = suitPoint
            # Make a new dna edge
            if DNAClassEqual(self.DNAParent, DNA_VIS_GROUP):
                zoneId = self.DNAParent.getName()

                suitEdge = DNASuitEdge(self.startSuitPoint, self.endSuitPoint, zoneId)
                DNASTORE.storeSuitEdge(suitEdge)
                # Add edge to the current vis group so it can be written out
                self.DNAParent.addSuitEdge(suitEdge)
                # Draw a line to represent the edge
                edgeLine = self.drawSuitEdge(suitEdge, self.NPParent)
                # Store the line in a dict so we can hide/show them
                self.edgeDict[suitEdge] = edgeLine
                self.np2EdgeDict[hash(edgeLine)] = [suitEdge, self.DNAParent]
                # Store the edge on each point in case we move the point
                # we can update the edge
                for point in [self.startSuitPoint, self.endSuitPoint]:
                    if point in self.point2edgeDict:
                        self.point2edgeDict[point].append(suitEdge)
                    else:
                        self.point2edgeDict[point] = [suitEdge]

                # If this is a building point, you need edges in both directions
                # so just make the other edge automatically
                if ((self.endSuitPoint.getPointType() == DNASuitPoint.FRONTDOORPOINT)
                        or (self.endSuitPoint.getPointType() == DNASuitPoint.SIDEDOORPOINT)):

                    suitEdge = DNASuitEdge(
                            self.endSuitPoint, self.startSuitPoint, zoneId)
                    DNASTORE.storeSuitEdge(suitEdge)
                    self.DNAParent.addSuitEdge(suitEdge)
                    edgeLine = self.drawSuitEdge(suitEdge, self.NPParent)
                    self.edgeDict[suitEdge] = edgeLine
                    self.np2EdgeDict[hash(edgeLine)] = [suitEdge, self.DNAParent]
                    for point in [self.startSuitPoint, self.endSuitPoint]:
                        if point in self.point2edgeDict:
                            self.point2edgeDict[point].append(suitEdge)
                        else:
                            self.point2edgeDict[point] = [suitEdge]
                else:  # If it's a door point, we don't set the last selected point
                    base.direct.select(self.pointDict.get(suitPoint, None).getChild(0))
                    self.updateSelectedPose(base.direct.selected.getSelectedAsList())

                print('Added dnaSuitEdge to zone: ' + zoneId)
            else:
                print('Error: DNAParent is not a dnaVisGroup. Did not add edge')
            self.endSuitPoint = None
        else:
            self.startSuitPoint = suitPoint

    def highlightConnected(self, nodePath = None, fReversePath = 0):
        if nodePath is None:
            nodePath = base.direct.selected.last
        if nodePath:
            suitPoint = self.findPointOrCell(nodePath)[0]
            if suitPoint:
                self.clearPathHighlights()
                self.highlightConnectedRec(suitPoint, fReversePath)

    def highlightConnectedRec(self, suitPoint, fReversePath):
        nodePath = self.pointDict.get(suitPoint, None)
        if nodePath:
            # highlight marker
            nodePath.setColor(1, 0, 0, 1)
            self.visitedPoints.append(suitPoint)
            # highlight connected edges
            for edge in self.point2edgeDict[suitPoint]:
                if ((fReversePath or (suitPoint == edge.getStartPoint())) and
                        (edge not in self.visitedEdges)):
                    edgeLine = self.edgeDict[edge]
                    # Call node path not LineNodePath setColor
                    NodePath.setColor(edgeLine, 1, 0, 0, 1)
                    # Add edge to visited edges
                    self.visitedEdges.append(edge)
                    # Color components connected to the edge
                    if fReversePath:
                        startPoint = edge.getStartPoint()
                        if startPoint not in self.visitedPoints:
                            self.highlightConnectedRec(startPoint,
                                                       fReversePath)
                    endPoint = edge.getEndPoint()
                    type = endPoint.getPointType()
                    if ((endPoint not in self.visitedPoints) and
                            (fReversePath or (type == DNASuitPoint.STREETPOINT))):
                        self.highlightConnectedRec(endPoint,
                                                   fReversePath)

    def clearPathHighlights(self):
        for point in list(self.pointDict.keys()):
            type = point.getPointType()
            marker = self.pointDict[point]
            if type == DNASuitPoint.STREETPOINT:
                marker.setColor(0, 0, 0.6)
            elif type == DNASuitPoint.FRONTDOORPOINT:
                marker.setColor(0, 0, 1)
            elif type == DNASuitPoint.SIDEDOORPOINT:
                marker.setColor(0, 0.6, 0.2)
        for edge in list(self.edgeDict.values()):
            edge.clearColor()
        self.visitedPoints = []
        self.visitedEdges = []

    def drawBattleCell(self, cell, parent, cellId = 0):
        marker = self.battleCellMarker.copyTo(parent)
        marker.setTag('cellId', '%d' % cellId)

        label = DirectGui.DirectLabel(text = '%d' % cellId, parent = marker,
                                      text_fg = (0.25, 1.0, 0.25, 1.0),
                                      text_font = ToontownGlobals.getSignFont(),
                                      relief = None, scale = 3)
        label.setBillboardPointEye(0)
        label.setScale(0.4)
        if not marker.getBounds().isEmpty():
            center = marker.getBounds().getCenter()
            label.setPos(center[0], center[1], .3)

        # Greenish
        marker.setColor(0.25, 1.0, 0.25, 0.5)
        marker.setTransparency(1)
        marker.setPos(cell.getPos())
        # scale to radius
        marker.setScale(cell.getWidth() / 2.0, cell.getHeight() / 2.0, 1)
        return marker

    def placeBattleCell(self):
        # Store the battle cell in the current vis group
        if not DNAClassEqual(self.DNAParent, DNA_VIS_GROUP):
            print('Error: DNAParent is not a dnaVisGroup. Did not add battle cell')
            return

        v = self.getGridSnapIntersectionPoint()
        mat = base.direct.grid.getMat(self.NPParent)
        absPos = Point3(mat.xformPoint(v))
        if self.currentBattleCellType == '20w 20l':
            cell = DNABattleCell(20, 20, absPos)
        elif self.currentBattleCellType == '20w 30l':
            cell = DNABattleCell(20, 30, absPos)
        elif self.currentBattleCellType == '30w 20l':
            cell = DNABattleCell(30, 20, absPos)
        elif self.currentBattleCellType == '30w 30l':
            cell = DNABattleCell(30, 30, absPos)
        DNASTORE.storeBattleCell(cell)
        i = self.DNAParent.getNumBattleCells()
        marker = self.drawBattleCell(cell, self.NPParent, i)
        self.cellDict[cell] = marker
        self.DNAParent.addBattleCell(cell)

    def createSuitPaths(self):
        numPoints = DNASTORE.getNumSuitPoints()
        for i in range(numPoints):
            point = DNASTORE.getSuitPointAtIndex(i)
            marker = self.drawSuitPoint(point,
                                        point.getPos(), point.getPointType(),
                                        self.suitPointToplevel)
            self.pointDict[point] = marker

        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            dnaVisGroup = visGroup[1]
            numSuitEdges = dnaVisGroup.getNumSuitEdges()
            for i in range(numSuitEdges):
                edge = dnaVisGroup.getSuitEdge(i)
                edgeLine = self.drawSuitEdge(edge, np)
                self.edgeDict[edge] = edgeLine
                self.np2EdgeDict[hash(edgeLine)] = [edge, dnaVisGroup]
                # Store the edge on each point in case we move the point
                # we can update the edge
                for point in [edge.getStartPoint(), edge.getEndPoint()]:
                    if point in self.point2edgeDict:
                        self.point2edgeDict[point].append(edge)
                    else:
                        self.point2edgeDict[point] = [edge]

    def getSuitPointFromNodePath(self, nodePath):
        """
        Given a node path, attempt to find the point, nodePath pair
        in the pointDict. If it is there, return the point. If we
        cannot find it, return None.
        TODO: a reverse lookup pointDict would speed this up quite a bit
        """
        for point, marker in list(self.pointDict.items()):
            if marker == nodePath:
                return point
        return None

    def screenshot(self):
        """
        Generic screenshots. Hides insertion markers, keeps dropshadows.
        """
        markers = render.findAllMatches('**/*insertionMarker')
        for marker in markers:
            marker.hide()
        aspect2d.hide()
        render2d.hide()

        base.graphicsEngine.renderFrame()
        base.screenshot("screenshots/screenshot")

        for marker in markers:
            marker.show()
        aspect2d.show()
        render2d.hide()

    async def renderMap(self):
        """
        Screenshot for making maps. Hides drop shadows and markers

        Steps to making a screenshot:
        1. Shift + O to toggle ORTHO camera
        2. press '5' to position camera directly overhead
        3. Position the camera to contain the entire street
        4. Press Shift + F12 to save a map render
        """

        hasMeter = base.frameRateMeter
        base.setFrameRateMeter(0)

        # Save the users window size so we can set it back after
        normX = base.win.getXSize()
        normY = base.win.getYSize()

        props = WindowProperties()
        props.setSize(2048, 2048)
        base.win.requestProperties(props)

        # Hide insertion marker, dropshadows, and the ui
        markers = render.findAllMatches('**/*insertionMarker')
        for marker in markers:
            marker.hide()
        shadows = render.findAllMatches('**/*shadow*')
        for shadow in shadows:
            shadow.hide()

        aspect2d.hide()
        render2d.hide()

        # Unfortunately, if we only render once, it doesnt end up working properly
        # So we render again to ensure the engine caught up with us resizing the window
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

        # We can't resize the window if the user has it maximized
        # We abort the process and show a message letting the user know
        if base.win.getProperties().getSize() != (2048, 2048):
            # Unhide the marker, dropshadows, and ui
            for marker in markers:
                marker.show()
            for shadow in shadows:
                shadow.show()

            aspect2d.show()
            render2d.show()

            base.setFrameRateMeter(hasMeter)

            txt = OnscreenText(parent = aspect2d, pos = (0, 0), style = 3,
                               font = ToontownGlobals.getSignFont(),
                               wordwrap = 36,
                               text = "Unable to resize screen. Render aborted.\n"
                                      "Ensure engine window is not maximized, as that prevents resizing\n\n"
                                      "Press SPACE to acknowledge.",
                               scale = 0.1, bg = (0, 0, 0, .4), fg = (1, 0, 0, 1))

            # Destroy the message when the user hits space
            await messenger.future("space")
            txt.destroy()
            del txt

            return

        # Save the above frame to the maps folder
        # Saves as map_neighborhood_{datetime}.png
        base.screenshot(f"maps/map_{self.neighborhood}_{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}.png",
                        defaultFilename = 0)

        for marker in markers:
            marker.show()
        for shadow in shadows:
            shadow.show()

        aspect2d.show()
        render2d.show()

        base.setFrameRateMeter(hasMeter)

        props.setSize(normX, normY)
        base.win.requestProperties(props)

    async def renderMapScaled(self):
        """
        Render a map with automatic scaling and data
        """

        tl = self.getNPToplevel()
        bounds = tl.getBounds()
        radius = bounds.getRadius()
        center = bounds.getCenter()

        size = (radius * 2)

        self.orthLens.setFilmSize(size, size)

        base.camera.setPos(center)
        base.camera.setZ(100)
        base.camera.setHpr(0, -90, 0)

        # Force orth cam
        self.orthCam = True
        base.cam.node().setLens(self.orthLens)

        # Export the map
        await self.renderMap()

        # Calculate the corners
        tr = Vec3(center[0] + radius, center[1] + radius, 0)
        bl = Vec3(center[0] - radius, center[1] - radius, 0)

        data = "This file is automatically generated by the Open Level Editor\n" \
               "https://github.com/OpenToontownTools/TTOpenLevelEditor\n" \
               "This data is to be entered in $TOONTOWN/src/quest/QuestMapGlobals\n\n"

        # Write the top right, and bottom left corners
        # This is the order used in $TOONTOWN/src/quest/QuestMapGlobals
        data += f"Corners:(Top Right, Bottom Left):\n    {tr}, {bl}\n"

        # Get the HQ position (if there is one)
        hq = tl.find("**/*toon_landmark_hq*")
        if not hq.isEmpty():
            data += f"HQ Position:\n    {hq.getPos()}\n"

        # Get the Fishing Pond position (if there is one)
        pond = tl.find("**/*_pond*")
        if not pond.isEmpty():
            data += f"Fishing Pond Position:\n    {pond.getPos()}"

        # Write the data to a txt file
        file = open(f"maps/map_{self.neighborhood}_{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}_data.txt", 'w')
        file.write(data)
        file.close()

    def toggleOrth(self):
        if not self.orthCam:
            base.cam.node().setLens(self.orthLens)
        else:
            base.cam.node().setLens(base.camLens)
        self.orthCam = not self.orthCam

    def resetPathMarkers(self):
        for edge, edgeLine in list(self.edgeDict.items()):
            if not edgeLine.isEmpty():
                edgeLine.reset()
                edgeLine.removeNode()
        self.edgeDict = {}
        self.np2EdgeDict = {}
        for point, marker in list(self.pointDict.items()):
            if not marker.isEmpty():
                marker.removeNode()
        self.pointDict = {}

    def hideSuitPaths(self):
        for edge, edgeLine in list(self.edgeDict.items()):
            edgeLine.hide()
        for point, marker in list(self.pointDict.items()):
            marker.hide()

    def showSuitPaths(self):
        for edge, edgeLine in list(self.edgeDict.items()):
            edgeLine.show()
        for point, marker in list(self.pointDict.items()):
            marker.show()

    def createBattleCells(self):
        # Edges
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            dnaVisGroup = visGroup[1]
            numCells = dnaVisGroup.getNumBattleCells()
            for i in range(numCells):
                cell = dnaVisGroup.getBattleCell(i)
                marker = self.drawBattleCell(cell, np, i)
                self.cellDict[cell] = marker

    def resetBattleCellMarkers(self):
        for cell, marker in list(self.cellDict.items()):
            if not marker.isEmpty():
                marker.removeNode()
        self.cellDict = {}

    def hideBattleCells(self):
        for cell, marker in list(self.cellDict.items()):
            marker.hide()

    def showBattleCells(self):
        for cell, marker in list(self.cellDict.items()):
            marker.show()

    def getBattleCellFromNodePath(self, nodePath):
        """
        Given a node path, attempt to find the battle cell, nodePath pair
        in the cellDict. If it is there, return the cell. If we
        cannot find it, return None.
        TODO: a reverse lookup cellDict would speed this up quite a bit
        """
        for cell, marker in list(self.cellDict.items()):
            if marker == nodePath:
                return cell
        return None

    def toggleZoneColors(self):
        if self.panel.zoneColor.get():
            self.colorZones()
        else:
            self.clearZoneColors()

    def colorZones(self):
        # Give each zone a random color to see them better
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            np.setColorScale(0.5 + random.random() / 2.0,
                             0.5 + random.random() / 2.0,
                             0.5 + random.random() / 2.0, 1.0)

    def clearZoneColors(self):
        # Clear random colors
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            np.clearColorScale()

    def labelZones(self):
        self.clearZoneLabels()
        visGroups = self.getDNAVisGroups(self.NPToplevel)

        for np, dna in visGroups:
            name = dna.getName()
            label = DirectGui.DirectLabel(text = name,
                                          text_font = ToontownGlobals.getSignFont(),
                                          text_fg = (0.152, 0.750, 0.258, 1),
                                          parent = np.getParent(),
                                          relief = None, scale = 3)
            label.setBillboardPointWorld()
            label.setDepthWrite(False)
            label.setDepthTest(not self.labelsOnTop)
            if not np.getBounds().isEmpty():
                center = np.getBounds().getCenter()
                label.setPos(center[0], center[1], .1)
                self.zoneLabels.append(label)

    def clearZoneLabels(self):
        for label in self.zoneLabels:
            label.removeNode()
        self.zoneLabels = []

    def labelBldgs(self):
        """ Draws a text label above Landmark bldgs displaying their title and block # """
        self.clearBldgLabels()
        for bldg in self.NPToplevel.findAllMatches('**/*tb*:toon_landmark*'):
            dnanode = self.findDNANode(bldg)
            block = self.getBlockFromName(dnanode.getName())
            title = dnanode.getTitle()
            fg = (0.8, 0.4, 0.2, 1)
            if not title:
                title = '(unnamed)'
                fg = (1.0, 0.1, 0.1, 1)
            label = DirectGui.DirectLabel(text = f"TB{block}\n{title}",
                                          text_font = ToontownGlobals.getSignFont(),
                                          text_fg = fg, text_wordwrap = 20,
                                          parent = bldg,
                                          relief = None, scale = 4)
            label.setBillboardPointWorld()
            label.setDepthWrite(False)
            label.setDepthTest(not self.labelsOnTop)
            if not bldg.find('**/**front').getBounds().isEmpty():
                center = bldg.find('**/**front').getBounds().getCenter()
                label.setPos(center[0], center[1], 50)
            self.bldgLabels.append(label)

    def clearBldgLabels(self):
        for label in self.bldgLabels:
            label.removeNode()
        self.bldgLabels = []

    def getBlockFromName(self, name):
        block = name[2:name.find(':')]
        return block

    def addToLandmarkBlock(self):
        dnaRoot = self.selectedDNARoot
        if dnaRoot and self.lastLandmarkBuildingDNA:
            if DNAClassEqual(dnaRoot, DNA_FLAT_BUILDING):
                n = dnaRoot.getName()
                n = n[n.find(':'):]
                block = self.lastLandmarkBuildingDNA.getName()
                block = block[2:block.find(':')]
                dnaRoot.setName('tb' + block + n)
                self.replaceSelected()
                # If we're highlighting the landmark blocks:
                if self.showLandmarkBlockToggleGroup:
                    # then highlight this one:
                    np = self.selectedNPRoot
                    self.showLandmarkBlockToggleGroup.append(np)
                    np.setColorScale(0, 1, 0, 1)
        elif self.selectedSuitPoint and self.lastLandmarkBuildingDNA:
            block = self.lastLandmarkBuildingDNA.getName()
            block = block[2:block.find(':')]
            print(("associate point with building: " + str(block)))
            self.selectedSuitPoint.setLandmarkBuildingIndex(int(block))
            marker = self.pointDict[self.selectedSuitPoint]
            marker.setColor(0, 1, 0, 1)

    def findHighestLandmarkBlock(self, dnaRoot, npRoot):
        npc = npRoot.findAllMatches("**/*:toon_landmark_*")
        highest = 0
        for i in range(npc.getNumPaths()):
            path = npc.getPath(i)
            block = path.getName()
            block = int(block[2:block.find(':')])
            if block > highest:
                highest = block
        # Make a list of flat building names, outside of the
        # recursive function:
        self.flatNames = ['random'] + BUILDING_TYPES
        self.flatNames = [n + '_DNARoot' for n in self.flatNames]
        # Search/recurse the dna:
        newHighest = self.convertToLandmarkBlocks(highest, dnaRoot)
        del self.flatNames

        needToTraverse = (highest != newHighest)
        return newHighest, needToTraverse

    def convertToLandmarkBlocks(self, block, dnaRoot):
        """
        Find all the buildings without landmark blocks and
        assign them one.
        """
        for i in range(dnaRoot.getNumChildren()):
            child = dnaRoot.at(i)
            if DNAClassEqual(child, DNA_LANDMARK_BUILDING):
                # Landmark buildings:
                name = child.getName()
                if name.find('toon_landmark_') == 0:
                    block = block + 1
                    child.setName('tb' + str(block) + ':' + name)
            elif DNAClassEqual(child, DNA_FLAT_BUILDING):
                # Flat buildings:
                name = child.getName()
                if name in self.flatNames:
                    child.setName('tb0:' + name)
            else:
                block = self.convertToLandmarkBlocks(block, child)
        return block

    def revertLandmarkBlock(self, block):
        """
        un-block flat buildings (set them to block zero).
        """
        npc = self.NPToplevel.findAllMatches("**/tb" + block + ":*_DNARoot")
        for i in range(npc.getNumPaths()):
            nodePath = npc.getPath(i)
            name = nodePath.getName()
            if name[name.find(':'):][:15] != ':toon_landmark_':
                name = 'tb0' + name[name.find(':'):]
                dna = self.findDNANode(nodePath)
                dna.setName(name)
                nodePath = self.replace(nodePath, dna)
                # If we're highlighting the landmark blocks:
                if self.showLandmarkBlockToggleGroup:
                    # then highlight this one:
                    self.showLandmarkBlockToggleGroup.append(nodePath)
                    nodePath.setColorScale(0, 1, 0, 1)

    def landmarkBlockRemove(self, dna, nodePath):
        if dna:
            name = dna.getName()
            # Get the underscore index within the name:
            usIndex = name.find(':')
            if name[usIndex:][:15] == ':toon_landmark_':
                block = name[2:usIndex]
                self.lastLandmarkBuildingDNA = None
                self.revertLandmarkBlock(block)

    def toggleShowLandmarkBlock(self):
        dna = self.lastLandmarkBuildingDNA
        if dna:
            if not self.showLandmarkBlockToggleGroup:
                group = []
                block = dna.getName()
                block = block[2:block.find(':')]

                # Get current landmark buildings:
                npc = self.NPToplevel.findAllMatches("**/tb" + block + ":*_DNARoot")
                for i in range(npc.getNumPaths()):
                    nodePath = npc.getPath(i)
                    group.append(nodePath)
                    nodePath.setColorScale(0, 1, 0, 1)

                # Get block zero buildings (i.e. non-blocked):
                npc = self.NPToplevel.findAllMatches("**/tb0:*_DNARoot")
                for i in range(npc.getNumPaths()):
                    nodePath = npc.getPath(i)
                    group.append(nodePath)
                    nodePath.setColorScale(1, 0, 0, 1)

                # Get the suit point for this lb
                for point, marker in list(self.pointDict.items()):
                    if ((point.getPointType() == DNASuitPoint.FRONTDOORPOINT)
                            or (point.getPointType() == DNASuitPoint.SIDEDOORPOINT)):
                        lbIndex = point.getLandmarkBuildingIndex()
                        if lbIndex == int(block):
                            marker.setColor(0, 1, 0, 1)
                            marker.setScale(1.0)
                            # There should only be one, so break now
                        elif lbIndex == -1:
                            # This point belongs to no block
                            marker.setColor(1, 0, 0, 1)

                self.showLandmarkBlockToggleGroup = group
            else:
                for i in self.showLandmarkBlockToggleGroup:
                    if not i.isEmpty():
                        i.clearColorScale()
                for point, marker in list(self.pointDict.items()):
                    if point.getPointType() == DNASuitPoint.FRONTDOORPOINT:
                        marker.setColor(0, 0, 1, 1)
                        marker.setScale(0.5)
                    elif point.getPointType() == DNASuitPoint.SIDEDOORPOINT:
                        marker.setColor(0, 0.6, 0.2, 1)
                        marker.setScale(0.5)
                self.showLandmarkBlockToggleGroup = None

    def pdbBreak(self):
        pdb.set_trace()

    def reparentStreetBuildings(self, nodePath):
        dnaNode = self.findDNANode(nodePath)
        if dnaNode:
            if (DNAClassEqual(dnaNode, DNA_FLAT_BUILDING) or
                    DNAClassEqual(dnaNode, DNA_LANDMARK_BUILDING)):
                base.direct.reparent(nodePath, fWrt = 1)
        children = nodePath.getChildren()
        for child in children:
            self.reparentStreetBuildings(child)

    def consolidateStreetBuildings(self):
        # First put everything under the ATR group so the leftover can be easily deleted
        originalChildren = self.NPToplevel.getChildren()
        self.addGroup(self.NPToplevel)
        atrGroup = self.NPParent
        atrGroup.setName('ATR')
        self.setName(atrGroup, 'ATR')
        base.direct.setActiveParent(atrGroup)
        for child in originalChildren:
            base.direct.reparent(child)
        # Now create a new group with just the buildings
        self.addGroup(self.NPToplevel)
        newGroup = self.NPParent
        newGroup.setName('LongStreet')
        self.setName(newGroup, 'LongStreet')
        base.direct.setActiveParent(newGroup)
        self.reparentStreetBuildings(self.NPToplevel)
        return newGroup

    def makeNewBuildingGroup(self, sequenceNum, side, curveName):
        print("-------------------------- new building group %s  curveName=%s------------------------" % (
            sequenceNum, curveName))
        # Now create a new group with just the buildings
        self.addGroup(self.NPToplevel)
        newGroup = self.NPParent
        groupName = ''

        if 'curveside' in curveName:
            # we want to preserve which group the side street is closest to
            print("special casing %s" % curveName)
            parts = curveName.split('_')
            groupName = 'Buildings_' + side + "-" + parts[3] + "_" + parts[4]
            print("groupname = %s" % groupName)
        else:
            groupName = 'Buildings_' + side + "-" + str(sequenceNum)
        newGroup.setName(groupName)
        self.setName(newGroup, groupName)
        base.direct.setActiveParent(newGroup)

        if 'barricade_curve' in curveName:
            parts = curveName.split('_')
            origBarricadeNum = parts[3]
            self.updateBarricadeDict(side, int(origBarricadeNum), sequenceNum)

    def adjustPropChildren(self, nodePath, maxPropOffset = -4):
        for np in nodePath.getChildren():
            dnaNode = self.findDNANode(np)
            if dnaNode:
                if DNAClassEqual(dnaNode, DNA_PROP):
                    if np.getY() < maxPropOffset:
                        np.setY(maxPropOffset)
                        self.updateSelectedPose([np])

    def getBuildingWidth(self, bldg):
        dnaNode = self.findDNANode(bldg)
        bldgWidth = 0
        if DNAClassEqual(dnaNode, DNA_FLAT_BUILDING):
            bldgWidth = dnaNode.getWidth()
        elif DNAClassEqual(dnaNode, DNA_LANDMARK_BUILDING):
            objectCode = dnaNode.getCode()
            if objectCode[-2:-1] == 'A':
                bldgWidth = 25.0
            elif objectCode[-2:-1] == 'B':
                bldgWidth = 15.0
            elif objectCode[-2:-1] == 'C':
                bldgWidth = 20.0
        return bldgWidth

    def calcLongStreetLength(self, bldgs):
        streetLength = 0
        for bldg in bldgs:
            streetLength += self.getBuildingWidth(bldg)
        return streetLength

    def addStreetUnits(self, streetLength):
        base.direct.grid.setPosHpr(0, -40, 0, 0, 0, 0)
        currLength = 0
        while currLength < streetLength:
            self.addStreet('street_80x40')
            currLength += 80

    def makeLongStreet(self):
        bldgGroup = self.consolidateStreetBuildings()
        bldgs = bldgGroup.getChildren()
        numBldgs = len(bldgs)
        streetLength = self.calcLongStreetLength(bldgs) / 2.0
        ref = None
        base.direct.grid.fXyzSnap = 0
        currLength = 0
        for i in range(numBldgs):
            bldg = bldgs[i]
            if ref is None:
                base.direct.grid.iPosHpr(bldgGroup)
            else:
                ref.select()
                self.autoPositionGrid(fLerp = 0)
            if base.direct.grid.getX() >= streetLength:
                base.direct.grid.setPosHpr(base.direct.grid, 0, -40, 0, 180, 0, 0)
            bldg.iPosHpr(base.direct.grid)
            self.updateSelectedPose([bldg])
            self.adjustPropChildren(bldg)
            ref = bldg
        self.addStreetUnits(streetLength)

    def duplicateFlatBuilding(self, oldDNANode):
        # Yes, make a new copy of the dnaNode
        print("a")
        dnaNode = oldDNANode.__class__(oldDNANode)
        print("b")
        dnaNode.setWidth(oldDNANode.getWidth())
        # Add the DNA to the active parent
        print("c")
        self.DNAParent.add(dnaNode)
        # And create the geometry
        print("d %s" % oldDNANode)
        newNodePath = dnaNode.traverse(self.NPParent, DNASTORE, 1)
        print("e")
        return newNodePath

    def getBldg(self, bldgIndex, bldgs, forceDuplicate = False):
        numBldgs = len(bldgs)
        if bldgIndex < numBldgs and not forceDuplicate:
            print("using original bldg")
            bldg = bldgs[bldgIndex]
            bldgIndex += 1
        else:
            # Make a copy
            oldBldg = bldgs[bldgIndex % numBldgs]
            bldgIndex += 1

            oldBldg.select()
            oldDNANode = self.findDNANode(oldBldg)
            nodeClass = DNAGetClassType(oldDNANode)
            if nodeClass == DNA_LANDMARK_BUILDING:
                print("making landmark copy")
                # Remove white and dark grey doors from color list
                colorList = self.getAttribute('door_color').getList()
                colorList = colorList[1:3] + colorList[4:len(colorList)]
                # Set a random door color
                doorColor = random.choice(colorList)
                self.setCurrent('door_color', doorColor)
                self.addLandmark(oldDNANode.getCode(), oldDNANode.getBuildingType())
                bldg = self.lastNodePath
            else:
                print("making flatbuilding copy")
                bldg = self.duplicateFlatBuilding(oldDNANode)
        return bldg, bldgIndex

    def updateBarricadeDict(self, side, barricadeOrigNum, curBldgGroupIndex):
        barricadeDict = None
        if side == 'outer':
            barricadeDict = self.outerBarricadeDict
        elif side == 'inner':
            barricadeDict = self.innerBarricadeDict
        else:
            print(("unhandled side %s" % side))
            return

        if barricadeOrigNum not in barricadeDict:
            barricadeDict[barricadeOrigNum] = [curBldgGroupIndex, curBldgGroupIndex]

        if curBldgGroupIndex < barricadeDict[barricadeOrigNum][0]:
            barricadeDict[barricadeOrigNum][0] = curBldgGroupIndex

        if barricadeDict[barricadeOrigNum][1] < curBldgGroupIndex:
            barricadeDict[barricadeOrigNum][1] = curBldgGroupIndex

        print("---------- %s barricadeDict origNum=%d  data=(%d, %d)" % (
            side, barricadeOrigNum, barricadeDict[barricadeOrigNum][0], barricadeDict[barricadeOrigNum][1]))

    def makeStreetAlongCurve(self):
        curves = self.loadStreetCurve()
        if curves is None:
            return

        self.outerBarricadeDict = {}
        self.innerBarricadeDict = {}

        base.direct.grid.fXyzSnap = 0
        base.direct.grid.fHprSnap = 0
        self.panel.fPlaneSnap.set(0)
        bldgGroup = self.consolidateStreetBuildings()
        bldgs = bldgGroup.getChildren()

        # streetWidth puts buildings on the edge of the street, not the middle
        currPoint = Point3(0)
        bldgIndex = 0

        # populate side streets
        self.makeSideStreets(curves)

        # Populate buildings on both sides of the street
        # sides = ['inner', 'outer','innersidest','outersidest']
        sides = ['inner', 'outer']
        maxGroupWidth = 500
        for side in sides:
            print("Building street for %s side" % side)
            # Subdivide the curve into different groups.
            bldgGroupIndex = 0
            curGroupWidth = 0
            curveName = ''
            if len(curves[side]):
                initialCurve, initialCurveType = curves[side][0]
                if initialCurve:
                    curveName = initialCurve.getName()
            self.makeNewBuildingGroup(bldgGroupIndex, side, curveName)

            for curve, curveType in curves[side]:
                print("----------------- curve(%s, %s): %s --------------- " % (side, curve.getName(), curve))
                currT = 0
                endT = curve.getMaxT()

                while currT < endT:
                    if curveType == 'urban':
                        bldg, bldgIndex = self.getBldg(bldgIndex, bldgs)
                        curve.getPoint(currT, currPoint)

                        if side == "inner" or side == "innersidest":
                            heading = 90
                        else:
                            heading = -90
                        bldg.setPos(currPoint)
                        bldgWidth = self.getBuildingWidth(bldg)

                        curGroupWidth += bldgWidth
                        # Adjust grid orientation based upon next point along curve
                        currT, currPoint = self.findBldgEndPoint(bldgWidth, curve, currT, currPoint, rd = 0)
                        bldg.lookAt(Point3(currPoint))
                        bldg.setH(bldg, heading)

                        # Shift building forward if it is on the out track, since we just turned it away from the direction of the track
                        if side == "outer" or side == "outersidest":
                            bldg.setPos(currPoint)

                        self.updateSelectedPose([bldg])
                        self.adjustPropChildren(bldg)
                        base.direct.reparent(bldg, fWrt = 1)
                        print(bldgIndex)
                    elif curveType == 'trees':
                        curve.getPoint(currT, currPoint)
                        # trees are spaced anywhere from 40-80 ft apart
                        treeWidth = random.randint(40, 80)
                        curGroupWidth += treeWidth
                        # Adjust grid orientation based upon next point along curve
                        currT, currPoint = self.findBldgEndPoint(treeWidth, curve, currT, currPoint, rd = 0)
                        # Add some trees
                        tree = random.choice(DNA_PROP_SETS['tree'])
                        # use snow if necessary
                        if useSnowTree:
                            tree = random.choice(DNA_PROP_SETS['snow_tree'])

                        self.addProp(tree)
                        for selectedNode in base.direct.selected:
                            # Move it
                            selectedNode.setPos(currPoint)
                            # Snap objects to grid and update DNA if necessary
                            self.updateSelectedPose(base.direct.selected.getSelectedAsList())
                    elif curveType == 'bridge':
                        # Don't add any dna for the bridge sections, but add the length of the bridge so we can increment our building groups correctly
                        print("adding bridge (%s), curT = %s" % (side, currT))
                        bridgeWidth = 1050
                        curGroupWidth += bridgeWidth
                        # currT, currPoint = self.findBldgEndPoint(bridgeWidth, curve, currT, currPoint, rd = 0)
                        print("currT after adding bridge = %s" % currT)
                        # force move to next curve
                        currT = endT + 1
                    elif curveType == 'tunnel':
                        # Don't add any dna for the tunnel sections, but add the length of the bridge so we can increment our building groups correctly
                        print("adding tunnel (%s), curT = %s" % (side, currT))
                        tunnelWidth = 775
                        curGroupWidth += tunnelWidth
                        # currT, currPoint = self.findBldgEndPoint(tunnelWidth, curve, currT, currPoint, rd = 0)
                        print("currT after adding tunnel = %s" % currT)
                        # force move to next curve
                        currT = endT + 1
                    elif curveType == 'barricade':
                        print("adding barricade (%s) %s, curT = %d" % (side, curve.getName(), currT))
                        barricadeWidth = curve.calcLength()
                        print("barricade width = %f" % barricadeWidth)
                        simple = 1
                        if simple:
                            curGroupWidth += barricadeWidth
                            # force move to next curve
                            currT = endT + 1
                        else:
                            # add a prop_tree to force it to be shown
                            curve.getPoint(currT, currPoint)
                            # trees are spaced anywhere from 40-80 ft apart
                            # treeWidth = random.randint(40, 80)
                            treeWidth = barricadeWidth
                            curGroupWidth += treeWidth
                            # Adjust grid orientation based upon next point along curve
                            currT, currPoint = self.findBldgEndPoint(treeWidth, curve, currT, currPoint, rd = 0)

                            # Add some trees
                            tree = random.choice(DNA_PROP_SETS['tree'])
                            self.addProp(tree)
                            for selectedNode in base.direct.selected:
                                # Move it
                                selectedNode.setPos(currPoint)
                                # Snap objects to grid and update DNA if necessary
                                self.updateSelectedPose(base.direct.selected.getSelectedAsList())

                    # Check if we need a new group yet
                    if curGroupWidth > maxGroupWidth:
                        print("curGroupWidth %s > %s" % (curGroupWidth, maxGroupWidth))
                        diffGroup = curGroupWidth - maxGroupWidth
                        while diffGroup > 0:
                            bldgGroupIndex += 1
                            self.makeNewBuildingGroup(bldgGroupIndex, side, curve.getName())
                            print("adding group %s (%s)" % (bldgGroupIndex, diffGroup))
                            diffGroup -= maxGroupWidth
                        curGroupWidth = 0
                    print(currT, curGroupWidth)

    def makeSideStreets(self, curves):
        """ Each side in a sidestreet MUST be in 1 building group, otherwise the 2nd half
        of a building group could be very far away. This would cause the stashing and
        unstashing code to go off kilter.
        """

        base.direct.grid.fXyzSnap = 0
        base.direct.grid.fHprSnap = 0
        self.panel.fPlaneSnap.set(0)
        bldgGroup = self.consolidateStreetBuildings()
        bldgs = bldgGroup.getChildren()

        # streetWidth puts buildings on the edge of the street, not the middle
        currPoint = Point3(0)
        bldgIndex = 0

        # Populate buildings on both sides of the street
        # sides = ['inner', 'outer','innersidest','outersidest']
        sides = ['innersidest', 'outersidest']
        maxGroupWidth = 50000
        for side in sides:
            print("Building street for %s side" % side)
            # Subdivide the curve into different groups.
            bldgGroupIndex = 0
            curGroupWidth = 0

            for curve, curveType in curves[side]:
                print("----------------- curve(%s, %s): %s --------------- " % (side, curve.getName(), curve))
                currT = 0
                endT = curve.getMaxT()

                print(("endT = %f" % endT))

                currGroupWidth = 0
                self.makeNewBuildingGroup(bldgGroupIndex, side, curve.getName())

                while currT < endT:
                    if curveType == 'urban':
                        bldg, bldgIndex = self.getBldg(bldgIndex, bldgs, forceDuplicate = True)
                        curve.getPoint(currT, currPoint)

                        if side == "inner" or side == "innersidest":
                            heading = 90
                        else:
                            heading = -90
                        bldg.setPos(currPoint)
                        bldgWidth = self.getBuildingWidth(bldg)

                        curGroupWidth += bldgWidth
                        # Adjust grid orientation based upon next point along curve
                        currT, currPoint = self.findBldgEndPoint(bldgWidth, curve, currT, currPoint, rd = 0)
                        bldg.lookAt(Point3(currPoint))
                        bldg.setH(bldg, heading)

                        # Shift building forward if it is on the out track, since we just turned it away from
                        # the direction of the track
                        if side == "outer" or side == "outersidest":
                            bldg.setPos(currPoint)

                        self.updateSelectedPose([bldg])
                        self.adjustPropChildren(bldg)
                        base.direct.reparent(bldg, fWrt = 1)
                        print(bldgIndex)
                    elif curveType == 'trees':
                        curve.getPoint(currT, currPoint)
                        # trees are spaced anywhere from 40-80 ft apart
                        treeWidth = random.randint(40, 80)
                        curGroupWidth += treeWidth
                        # Adjust grid orientation based upon next point along curve
                        currT, currPoint = self.findBldgEndPoint(treeWidth, curve, currT, currPoint, rd = 0)

                        # Add some trees
                        tree = random.choice(DNA_PROP_SETS['tree'])
                        # use snow tree if necessary
                        if useSnowTree:
                            tree = random.choice(DNA_PROP_SETS['snow_tree'])

                        self.addProp(tree)
                        for selectedNode in base.direct.selected:
                            # Move it
                            selectedNode.setPos(currPoint)
                            # Snap objects to grid and update DNA if necessary
                            self.updateSelectedPose(base.direct.selected.getSelectedAsList())
                    elif curveType == 'bridge':
                        # Don't add any dna for the bridge sections, but add the length of the bridge so we can increment our building groups correctly
                        print("adding bridge (%s), curT = %s" % (side, currT))
                        bridgeWidth = 1050
                        curGroupWidth += bridgeWidth
                        # currT, currPoint = self.findBldgEndPoint(bridgeWidth, curve, currT, currPoint, rd = 0)
                        print("currT after adding bridge = %s" % currT)
                        # force move to next curve
                        currT = endT + 1
                    elif curveType == 'tunnel':
                        # Don't add any dna for the tunnel sections, but add the length
                        # of the bridge so we can increment our building groups correctly
                        print("adding tunnel (%s), curT = %s" % (side, currT))
                        tunnelWidth = 775
                        curGroupWidth += tunnelWidth
                        # currT, currPoint = self.findBldgEndPoint(tunnelWidth, curve, currT, currPoint, rd = 0)
                        print("currT after adding tunnel = %s" % currT)
                        # force move to next curve
                        currT = endT + 1
                    elif curveType == 'barricade':
                        print("adding barricade (%s) %s, curT = %d" % (side, curve.getName(), currT))
                        barricadeWidth = curve.calcLength()
                        print("barricade width = %f" % barricadeWidth)

                        simple = 1
                        if simple:
                            curGroupWidth += barricadeWidth
                            # force move to next curve
                            currT = endT + 1
                        else:
                            # add a prop_tree to force it to be shown
                            curve.getPoint(currT, currPoint)
                            # trees are spaced anywhere from 40-80 ft apart
                            # treeWidth = random.randint(40, 80)
                            treeWidth = barricadeWidth
                            curGroupWidth += treeWidth
                            # Adjust grid orientation based upon next point along curve
                            currT, currPoint = self.findBldgEndPoint(treeWidth, curve, currT, currPoint, rd = 0)

                            # Add some trees
                            tree = random.choice(DNA_PROP_SETS['tree'])
                            self.addProp(tree)
                            for selectedNode in base.direct.selected:
                                # Move it
                                selectedNode.setPos(currPoint)
                                # Snap objects to grid and update DNA if necessary
                                self.updateSelectedPose(base.direct.selected.getSelectedAsList())

                # done with for loop, increment bldgGroupIndex
                bldgGroupIndex += 1

    def findBldgEndPoint(self, bldgWidth, curve, currT, currPoint, startT = None, endT = None, tolerance = 0.1, rd = 0):
        if startT is None:
            startT = currT
        if endT is None:
            endT = curve.getMaxT()
        if rd > 100:
            import pdb
            pdb.set_trace()
        midT = (startT + endT) / 2.0
        midPoint = Point3(0)
        curve.getPoint(midT, midPoint)
        separation = Vec3(midPoint - currPoint).length()
        error = separation - bldgWidth
        if abs(error) < tolerance:
            return midT, midPoint
        elif error > 0:
            # Mid point was beyond building end point, focus on first half
            return self.findBldgEndPoint(bldgWidth, curve, currT, currPoint, startT = startT, endT = midT, rd = rd + 1)
        else:
            # End point beyond Mid point, focus on second half
            # But make sure buildind end point is not beyond curve end point
            endPoint = Point3(0)
            curve.getPoint(endT, endPoint)
            separation = Vec3(endPoint - currPoint).length()
            if bldgWidth > separation:
                # Must have reached end of the curve
                return endT, endPoint
            else:
                return self.findBldgEndPoint(bldgWidth, curve, currT, currPoint, startT = midT, endT = endT,
                                             rd = rd + 1)

    async def enterGlobalRadialMenu(self):
        """ Radial Menu with general commands """

        # Load the gui model
        gui = await loader.loadModel("resources/level_editor_gui.bam", blocking = False)

        # Create the menu with the items
        rm = RadialMenu(
                RadialItem(gui.find("**/icon_cancel"), 'Cancel'),
                RadialItem(gui.find("**/icon_save"), 'Save'),
                RadialItem(gui.find("**/icon_landmark"), 'Toggle Landmark / Flat Wall Linking Mode'),
                RadialItem(gui.find("**/icon_suit"), 'Toggle Suit Building Previews'),
                RadialItem(gui.find("**/icon_collision"), 'Toggle Collision Boundry Display')
                )
        rm.activate()

        del gui

        # Wait for the user to release tab, simpler way of accept('tab-up', exitGlobalRadialMenu)
        await messenger.future('tab-up')

        # Now that the user has released tab,
        # Get the choice
        result = rm.getChoice()

        # Destroy everything
        rm.deactivate()
        rm.destroy()

        # Do the selected action
        if result == 1:
            self.outputDNADefaultFile()
        if result == 2:
            self.toggleShowLandmarkBlock()
        if result == 3:
            self.toggleSuitBuildingPreviews()
        if result == 4:
            self.toggleVisibleCollisions()

    @staticmethod
    def popupNotification(string: str):
        """ Generic Popup notifications. These appear in the
            top right for a couple of seconds """
        if base.config.GetBool('disable-notifications', False):
            return
        txt = OnscreenText(parent = base.a2dTopRight, pos = (0.1, 0, -0.2), style = 3,
                           wordwrap = 36, align = TextNode.ARight,
                           text = string, font = ToontownGlobals.getToonFont(),
                           scale = 0.05, bg = (0, 0, 0, .4), fg = (1, 1, 1, 1))

        def destroyTxt(ost: OnscreenText):
            ost.destroy
            del ost

        Parallel(
                LerpColorScaleInterval(txt, 0.3, (1, 1, 1, 1), (1, 1, 1, 0)),
                Sequence(
                        txt.posInterval(0.3, Point3(-.15, 0, -0.2), Point3(.1, 0, -0.2), blendType = 'easeOut'),
                        txt.posInterval(2.7, Point3(-.15, 0, -0.1), blendType = 'easeOut')
                        ),
                Sequence(
                        Wait(2),
                        LerpColorScaleInterval(txt, 1, (1, 1, 1, 0), (1, 1, 1, 1)),
                        Func(destroyTxt, txt)
                        )
                ).start()

    async def beginBoxSelection(self):
        self.popupNotification('entered selection mode')

        self.isSelecting = True
        await messenger.future('mouse1')
        if not base.mouseWatcherNode.hasMouse():
            return
        self.boxStartMouse = (base.mouseWatcherNode.getMouseX(), base.mouseWatcherNode.getMouseY())

        self.boxLines = (LineNodePath(render2d), LineNodePath(render2d), LineNodePath(render2d), LineNodePath(render2d))
        for line in self.boxLines:
            line.setColor(VBase4(1))
            line.setThickness(1)
            line.reset()
            line.moveTo(0, 0, 0)
            line.drawTo(0, 0, 0)
            line.create()

        taskMgr.add(self.selectionBoxTask, 'boxselection')

        await messenger.future('mouse1-up')

        taskMgr.remove('boxselection')
        self.isSelecting = False

        for line in self.boxLines:
            line.removeNode()
            del line

        self.finishBoxSelection()

        self.popupNotification('Exited Selection Mode')

    def selectionBoxTask(self, task):
        """ calculate the selection box positions """
        if not base.mouseWatcherNode.hasMouse():
            return task.again
        self.boxEndMouse = (base.mouseWatcherNode.getMouseX(), base.mouseWatcherNode.getMouseY())

        # left side
        self.boxLines[0].setVertex(0, self.boxStartMouse[0], 0, self.boxStartMouse[1])
        self.boxLines[0].setVertex(1, self.boxStartMouse[0], 0, self.boxEndMouse[1])

        # right side
        self.boxLines[1].setVertex(0, self.boxEndMouse[0], 0, self.boxStartMouse[1])
        self.boxLines[1].setVertex(1, self.boxEndMouse[0], 0, self.boxEndMouse[1])

        # top side
        self.boxLines[2].setVertex(0, self.boxStartMouse[0], 0, self.boxStartMouse[1])
        self.boxLines[2].setVertex(1, self.boxEndMouse[0], 0, self.boxStartMouse[1])

        # bottom side
        self.boxLines[3].setVertex(0, self.boxStartMouse[0], 0, self.boxEndMouse[1])
        self.boxLines[3].setVertex(1, self.boxEndMouse[0], 0, self.boxEndMouse[1])

        return task.again

    def finishBoxSelection(self):
        """ Calculates all the stuff in the selection """
        base.direct.deselectAll()

        # The following is mostly from direct.directtools.DirectManipulation, but modified
        # for dnanodes instead of geom nodes.
        # TODO: Optimize as the first time u make a selection it takes a while.
        startX = self.boxStartMouse[0]
        startY = self.boxStartMouse[1]
        endX = self.boxEndMouse[0]
        endY = self.boxEndMouse[1]

        fll: Point3 = Point3(0, 0, 0)
        flr: Point3 = Point3(0, 0, 0)
        fur: Point3 = Point3(0, 0, 0)
        ful: Point3 = Point3(0, 0, 0)
        nll: Point3 = Point3(0, 0, 0)
        nlr: Point3 = Point3(0, 0, 0)
        nur: Point3 = Point3(0, 0, 0)
        nul: Point3 = Point3(0, 0, 0)

        lens: Lens = base.cam.node().getLens()
        lens.extrude((startX, startY), nul, ful)
        lens.extrude((endX, startY), nur, fur)
        lens.extrude((endX, endY), nlr, flr)
        lens.extrude((startX, endY), nll, fll)
        selFrustum: BoundingHexahedron = BoundingHexahedron(fll, flr, fur, ful, nll, nlr, nur, nul);
        selFrustum.xform(base.cam.getNetTransform().getMat())

        selectionList = []
        for geom in self.NPToplevel.findAllMatches("**/*_DNARoot"):

            nodePath: NodePath = geom
            if nodePath in selectionList:
                continue

            bb = geom.getBounds()
            bbc = bb.makeCopy()
            bbc.xform(geom.getParent().getNetTransform().getMat())

            boundingSphereTest = selFrustum.contains(bbc)
            if boundingSphereTest > 1:
                if boundingSphereTest == 7:
                    if nodePath not in selectionList:
                        selectionList.append(nodePath)
                else:
                    tMat = Mat4(geom.getMat())
                    geom.clearMat()
                    # Get bounds
                    min = Point3(0)
                    max = Point3(0)
                    geom.calcTightBounds(min, max)
                    # Restore transform
                    geom.setMat(tMat)

                    fll = Point3(min[0], max[1], min[2])
                    flr = Point3(max[0], max[1], min[2])
                    fur = max
                    ful = Point3(min[0], max[1], max[2])
                    nll = min
                    nlr = Point3(max[0], min[1], min[2])
                    nur = Point3(max[0], min[1], max[2])
                    nul = Point3(min[0], min[1], max[2])

                    tbb = BoundingHexahedron(fll, flr, fur, ful, nll, nlr, nur, nul)

                    tbb.xform(geom.getNetTransform().getMat())

                    tightBoundTest = selFrustum.contains(tbb)

                    if tightBoundTest > 1:
                        if nodePath not in selectionList:
                            selectionList.append(nodePath)

        for nodePath in selectionList:
            base.direct.select(nodePath, 1)
