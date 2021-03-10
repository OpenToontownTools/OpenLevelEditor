""" Camera Radial Menu - drewcification 091720 """
from direct.directtools.DirectGeometry import *
from direct.gui.DirectFrame import DirectFrame, OnscreenImage, OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from toontown.toonbase import ToontownGlobals


class RadialItem:
    def __init__(self, nodepath: NodePath, desc: str):
        self.nodepath = nodepath
        self.description = desc


class RadialMenu(DirectObject):
    def __init__(self, *items):
        """
            Initialize using the set of items specified
            Set of items should be passed as RadialItems
        """
        DirectObject.__init__(self)
        # Initialize variables
        self.isActive: bool = False
        self.selected: int = 0

        self.items: List[RadialItem] = items

        # Load the palletized gui model
        gui: NodePath = loader.loadModel("resources/camera_gui.bam")

        # Create the frame
        self.frame = DirectFrame(geom = gui.find("**/radial_menu_bg"), parent = hidden, scale = 1.3, relief = None)

        # Create the selection indicator
        self.selector = OnscreenImage(image = gui.find("**/radial_menu_bg_quarter"), parent = self.frame)

        # Create the selected item description box
        self.descriptionBox = OnscreenText(parent = self.frame, pos = (0, -.6), style = 3,
                                           font = ToontownGlobals.getSignFont(), scale = 0.05, bg = (0, 0, 0, .4))

        # Load all the and calculate their positions
        self.itemAngle = 360 / len(items)
        self.itemImages: List[OnscreenImage] = []
        for i in range(len(items)):
            x = .38 * math.cos(i * deg2Rad(self.itemAngle))
            z = .38 * math.sin(i * deg2Rad(self.itemAngle))
            img = OnscreenImage(image = self.items[i].nodepath, scale = 0.2,
                                parent = self.frame, pos = (x, 0, z))
            self.itemImages.append(img)

    def activate(self):
        """ Shows the menu and spawns the mouse reader task """
        self.frame.reparentTo(aspect2d)
        taskMgr.add(self.radialTask, 'cam-radialTask')
        self.isActive = 1

    def deactivate(self):
        """ Hides the menu and kills the mouse reader task """
        taskMgr.remove('cam-radialTask')
        self.frame.reparentTo(hidden)
        self.isActive = 0

    def destroy(self):
        """ Destroy everything """
        self.frame.destroy()
        self.selector.destroy()
        for item in self.itemImages:
            item.destroy()
            del item

        for item in self.items:
            del item
        del self.frame
        del self.selector

    def getChoice(self) -> int:
        """ Convenience Function Get the selected item """
        return self.selected

    def radialTask(self, task):
        """ Reads the mouse position and calculates which object it is looking at """
        # Initialize these as 0 incase we can't read the mouses position
        mouseX = 0
        mouseY = 0
        # Read the mouse position
        if base.mouseWatcherNode.hasMouse():
            mouseX = base.mouseWatcherNode.getMouseX()
            mouseY = base.mouseWatcherNode.getMouseY()
        # Calculate the angle that the mouse is at from the cursor
        menuAngle = rad2Deg(math.atan2(mouseY, mouseX)) + 45

        # Get the index of the item at the mouse angle
        self.selected = int(math.floor((menuAngle % 360) / self.itemAngle))

        # Set the rotation of the selector
        # The selector image is from 12 o'clock to 3 o'clock, so we need to 
        # rotate it counter clockwise 45 degrees
        self.selector.setR(-self.itemAngle * self.selected + 45)

        # Highlight the selected item
        for i in self.itemImages:
            i.setColorScale(1.0, 1.0, 1.0, 1.0)
            i.setScale(0.2)
        self.itemImages[self.selected].setScale(0.25)
        self.itemImages[self.selected].setColorScale(0.3, 1.0, 1.0, 1.0)

        self.descriptionBox['text'] = self.items[self.selected].description

        return Task.cont
