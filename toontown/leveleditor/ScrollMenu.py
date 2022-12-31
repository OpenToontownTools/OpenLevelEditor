###########################################################
# Class to create and maintain a scrolled list
# that can be embedded in a LevelAttribute instance
###########################################################
from typing import Union, List, Tuple

from direct.gui.DirectGui import *
from panda3d.core import NodePath

from toontown.toontowngui.ToontownScrolledFrame import ToontownScrolledFrame
from toontown.toonbase import ToontownGlobals


class ScrollMenu:
    def __init__(self, nodePath, itemsList: List[Union[str, Tuple[NodePath, str]]]):
        self.action = None  # Call back fucntion
        self.itemsList = itemsList

        self.parent = nodePath
        self.frame = None

        self.initialState = None  # To maintain backward compatibility

    def createScrolledList(self, itemSize: float = 1.0, itemPadding = 0.05, itemMargin = (0.05, 0)):
        # First create a frame in which direct elements maybe placed
        self.frame = DirectFrame(scale = 1.1, relief = 1,
                                 frameSize = (-0.5, 0.2, -0.05, 0.59),
                                 frameColor = (0.737, 0.573, 0.345, 0.000))

        numItemsVisible = 9
        itemHeight = 0.05

        gui = loader.loadModel("resources/level_editor_gui.bam")

        myScrolledList = ToontownScrolledFrame(
                parent = self.frame,
                image = gui.find("**/editor_list_frame"),
                image_pos = (0, 0, 0),
                image_hpr = (0, 0, 90),
                image_scale = (1.8, 1, 1.0),
                pos = (0.0, 0, 0),
                itemMargin = itemMargin,
                useItemBoundsForPadding = False,
                itemPadding = itemPadding,
                width = .45,
                height = .6,
                manageScrollBars = False,
                verticalScroll_frameColor = (0, 0, 0, 0),
                verticalScroll_manageButtons = False,
                verticalScroll_thumb_geom = (
                    gui.find('**/scrollbar_normal'),
                    gui.find('**/scrollbar_press'),
                    gui.find('**/scrollbar_hover')),
                verticalScroll_thumb_geom_scale = ((151 / 399) * .06, 1, .06),
                verticalScroll_thumb_relief = None,
                verticalScroll_resizeThumb = False,
                verticalScroll_decButton_relief = None,
                verticalScroll_incButton_relief = None
        )

        btns = []
        for t in self.itemsList:
            if isinstance(t, str):
                btns.append(DirectButton(text = (t, t, t),
                                         text_scale = 0.05, command = self.__selected,
                                         extraArgs = [t], relief = None, text_style = 3,
                                         text_font = ToontownGlobals.getToonFont(),
                                         text0_fg = (0.152, 0.750, 0.258, 1),
                                         text1_fg = (0.152, 0.750, 0.258, 1),
                                         text2_fg = (0.977, 0.816, 0.133, 1), ))
            elif isinstance(t, tuple):
                btns.append(DirectButton(relief = None, command = self.__selected, extraArgs = [t[1]],
                                         geom = t[0], geom_scale = itemSize))
        myScrolledList.addItems(*btns)

        # An exit button
        b1 = DirectButton(parent = self.frame, text = "Exit", text_font = ToontownGlobals.getSignFont(),
                          text0_fg = (0.152, 0.750, 0.258, 1), text1_fg = (0.152, 0.750, 0.258, 1),
                          text2_fg = (0.977, 0.816, 0.133, 1), text_scale = 0.05, borderWidth = (0.01, 0.01),
                          relief = 0, command = self.__hide)
        b1.setPos(0.0, 0, -0.64)

        self.frame.reparentTo(self.parent)

    def __selected(self, text):
        if (self.action):
            self.action(text)

    def __hide(self):
        self.frame.reparentTo(self.parent)

    #######################################################
    # Functions that allow compaitibility with the
    # existing architecture that is tied into pie menu's
    #######################################################
    def spawnPieMenuTask(self):
        # Pop up menu
        self.frame.reparentTo(base.a2dRightCenter)
        self.frame.setPos(-.55, 0.0, 0)

    def removePieMenuTask(self):
        pass

    def setInitialState(self, state):
        self.initialState = state

    def getInitialState(self):
        return self.initialState
