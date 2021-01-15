import sys
import Pmw

from tkinter import *
from tkinter import ttk

from direct.showbase.TkGlobal import *
from direct.tkwidgets import Floater

from .DNASerializer import DNASerializer
from .AutoSaver import AutoSaver
from .LevelStyleManager import *
from .LevelEditorGlobals import *
from .LESceneGraphExplorer import *

from toontown.fixes import VectorWidgets


class LevelEditorPanel(Pmw.MegaToplevel):
    """
    Class used to initialize the Tkinter GUI.
    """

    def __init__(self, levelEditor, parent = None, **kw):

        INITOPT = Pmw.INITOPT
        optiondefs = (
            ('title', 'Open Level Editor', None),
            )
        self.defineoptions(kw, optiondefs)

        Pmw.MegaToplevel.__init__(self, parent, title = self['title'])

        if sys.platform == 'win32':
            # FIXME: This doesn't work in other platforms for some reason...
            self.iconbitmap("resources/openttle_ico_temp.ico")

        self.levelEditor = levelEditor
        self.styleManager = self.levelEditor.styleManager
        self.fUpdateSelected = 1
        # Handle to the toplevels hull
        hull = self.component('hull')
        hull.geometry('650x625')

        balloon = self.balloon = Pmw.Balloon(hull)
        # Start with balloon help disabled
        self.balloon.configure(state = 'none')

        menuFrame = Frame(hull, relief = GROOVE, bd = 2)
        menuFrame.pack(fill = X)

        menuBar = Pmw.MenuBar(menuFrame, hotkeys = 1, balloon = balloon)
        menuBar.pack(side = LEFT, expand = 1, fill = X)
        menuBar.addmenu('Level Editor', 'Level Editor Operations')
        menuBar.addmenuitem('Level Editor', 'command',
                            'Load DNA from specified file',
                            label = 'Load DNA...',
                            command = DNASerializer.loadSpecifiedDNAFile)
        menuBar.addmenuitem('Level Editor', 'command',
                            'Save DNA data to specified file',
                            label = 'Save DNA As...',
                            command = DNASerializer.saveToSpecifiedDNAFile)
        menuBar.addmenuitem('Level Editor', 'command',
                            'Save DNA File',
                            label = 'Save DNA',
                            command = DNASerializer.outputDNADefaultFile)
        menuBar.addmenuitem('Level Editor', 'separator')
        menuBar.addmenuitem('Level Editor', 'command',
                            'Edit Visibility Groups',
                            label = 'Edit Vis Groups',
                            command = self.levelEditor.editDNAVisGroups)
        menuBar.addmenuitem('Level Editor', 'separator')
        menuBar.addmenuitem('Level Editor', 'command',
                            'Reset level',
                            label = 'Clear level',
                            command = self.levelEditor.reset)
        menuBar.addmenuitem('Level Editor', 'command',
                            'Make Long Street',
                            label = 'Make Long Street',
                            command = self.levelEditor.makeLongStreet)
        menuBar.addmenuitem('Level Editor', 'command',
                            'Make Street Along Curve',
                            label = 'Make Street Along Curve',
                            command = self.levelEditor.makeStreetAlongCurve)
        menuBar.addmenuitem('Level Editor', 'separator')
        menuBar.addmenuitem('Level Editor', 'command',
                            'Exit Level Editor Panel',
                            label = 'Exit',
                            command = self.levelEditor.destroy)

        menuBar.addmenu('Style', 'Style Operations')
        menuBar.addmenuitem('Style', 'command',
                            "Save Selected Object's Color",
                            label = 'Save Color',
                            command = DNASerializer.saveColor)
        menuBar.addmenuitem('Style', 'command',
                            "Save Selected Baseline's Style",
                            label = 'Save Baseline Style',
                            command = DNASerializer.saveBaselineStyle)
        menuBar.addmenuitem('Style', 'command',
                            "Save Selected Wall's Style",
                            label = 'Save Wall Style',
                            command = DNASerializer.saveWallStyle)
        menuBar.addmenuitem('Style', 'command',
                            "Save Selected Buildings's Style",
                            label = 'Save Bldg Style',
                            command = DNASerializer.saveBuildingStyle)
        menuBar.addmenuitem('Style', 'separator')
        menuBar.addmenuitem('Style', 'command',
                            'Reload Color Palettes',
                            label = 'Reload Colors',
                            command = self.styleManager.createColorAttributes)
        menuBar.addmenuitem('Style', 'command',
                            'Reload Baseline Style Palettes',
                            label = 'Reload Baseline Styles',
                            command = self.styleManager.createBaselineStyleAttributes)
        menuBar.addmenuitem('Style', 'command',
                            'Reload Wall Style Palettes',
                            label = 'Reload Wall Styles',
                            command = self.styleManager.createWallStyleAttributes)
        menuBar.addmenuitem('Style', 'command',
                            'Reload Building Style Palettes',
                            label = 'Reload Bldg Styles',
                            command = self.styleManager.createBuildingStyleAttributes)

        menuBar.addmenu('Advanced', 'Level Editor Advanced Options')
        menuBar.addmenuitem('Advanced', 'command',
                            'Open Injector',
                            label = 'Injector',
                            command = self.showInjector)
        menuBar.addmenuitem('Advanced', 'separator')
        menuBar.addmenuitem('Advanced', 'checkbutton',
                            'Toggle Auto-saver On/Off',
                            label =  'Toggle Auto Saver',
                            command = self.toggleAutoSaver)
        menuBar.addmenuitem('Advanced', 'command',
                            'User Set Auto Saver Options',
                            label = 'Auto Saver Options',
                            command = self.showAutoSaverDialog)

        # Corporate Clash Old Toontown-esque Filter
        if base.server == TOONTOWN_CORPORATE_CLASH:
            self.toggleOTVar = IntVar()
            self.toggleOTVar.set(0)
            menuBar.addmenuitem('Advanced', 'checkbutton',
                                'Enable Old Toontown filter preview',
                                label = 'Old Toontown Filter',
                                variable = self.toggleOTVar,
                                command = self.toggleOT)

        self.injectorDialog = Pmw.Dialog(parent, title = 'Injector',
                                         buttons = ('Run',),
                                         command = self.runInject)
        self.injectorDialog.withdraw()
        # self.injectorTextBox = Pmw.EntryField (parent = self.injectorDialog.interior())
        self.injectorTextBox = Text(self.injectorDialog.interior(), height = 30)
        self.injectorTextBox.pack(expand = 1, fill = BOTH)

        menuBar.addmenu('Help', 'Level Editor Help Operations')
        self.toggleBalloonVar = IntVar()
        self.toggleBalloonVar.set(0)
        menuBar.addmenuitem('Help', 'checkbutton',
                            'Toggle balloon help',
                            label = 'Balloon Help',
                            variable = self.toggleBalloonVar,
                            command = self.toggleBalloon)
        menuBar.addmenuitem('Help', 'command',
                            'Lists all the controls',
                            label = 'Controls...', command = self.showControls)
        menuBar.addmenuitem('Help', 'command',
                            'About the Open Level Editor',
                            label = 'About...', command = self.showAbout)
        # Create the HELP dialog
        Pmw.aboutversion(base.APP_VERSION)
        Pmw.aboutcopyright('Maintained by drewcification#5131')
        Pmw.aboutcontact(
                'For more information, check out the repo: http://github.com/OpenToontownTools/ToontownLevelEditor')
        self.aboutDialog = Pmw.AboutDialog(hull,
                                           applicationname = "OpenLevelEditor")

        self.aboutDialog.withdraw()

        # Create the CONTROLS dialog
        self.controlsDialog = Pmw.MessageDialog(parent,
                                                title = 'Controls',
                                                defaultbutton = 0,
                                                message_text = CONTROLS)
        self.controlsDialog.withdraw()

        self.autoSaverDialog = Pmw.Dialog(parent, title = 'Autosaver Options',
                                          buttons = ('Save Options',),
                                          command = self.setAutoSaverInterval)
        self.autoSaverDialog.withdraw()

        self.autoSaverDialogInterval = Pmw.Counter(self.autoSaverDialog.interior(),
                                                   labelpos = 'w',
                                                   label_text = 'Auto save interval in minutes:',
                                                   entry_width = 10,
                                                   entryfield_value = int(AutoSaver.autoSaverInterval),
                                                   entryfield_validate = {'validator': 'real',
                                                                        'min': 1, 'max': 60})

        self.autoSaverDialogMax = Pmw.Counter(self.autoSaverDialog.interior(),
                                              labelpos = 'w',
                                              label_text = 'Max auto save files:',
                                              entry_width = 10,
                                              entryfield_value = int(AutoSaver.maxAutoSaveCount),
                                              entryfield_validate = {'validator': 'numeric',
                                                                   'min': 0, 'max': 99})

        counters = (self.autoSaverDialogInterval, self.autoSaverDialogMax)
        Pmw.alignlabels(counters)
        for counter in counters:
            counter.pack(fill = 'both', expand = 1)

        self.editMenu = Pmw.ComboBox(
                menuFrame, labelpos = W,
                label_text = 'Edit Mode:', entry_width = 18,
                selectioncommand = self.levelEditor.setEditMode, history = 0,
                scrolledlist_items = NEIGHBORHOODS)
        self.editMenu.selectitem(NEIGHBORHOODS[0])
        self.editMenu.pack(side = LEFT, expand = 0)

        # Create the notebook pages
        self.notebook = Pmw.NoteBook(hull)
        self.notebook.pack(fill = BOTH, expand = 1)
        streetsPage = self.notebook.add('Streets')
        toonBuildingsPage = self.notebook.add('Toon Bldgs')
        landmarkBuildingsPage = self.notebook.add('Landmark Bldgs')
        # suitBuildingsPage = self.notebook.add('Suit Buildings')
        animBuildingsPage = self.notebook.add('Anim Bldgs')
        propsPage = self.notebook.add('Props')
        animPropsPage = self.notebook.add('Anim Props')
        interactivePropsPage = self.notebook.add('Interactive Props')
        signPage = self.notebook.add('Signs')
        suitPathPage = self.notebook.add('Paths')
        battleCellPage = self.notebook.add('Cells')
        sceneGraphPage = self.notebook.add('SceneGraph')
        self.notebook['raisecommand'] = self.updateInfo

        # STREETS
        Label(streetsPage, text = 'Streets',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        self.addStreetButton = ttk.Button(
                streetsPage,
                text = 'ADD STREET',
                command = self.addStreet)
        self.addStreetButton.pack(fill = X, padx = 20, pady = 10)
        streets = [s[7:] for s in self.styleManager.getCatalogCodes(
                'street')]
        streets.sort()
        self.streetSelector = Pmw.ComboBox(
                streetsPage,
                dropdown = 0,
                listheight = 200,
                labelpos = W,
                label_text = 'Street type:',
                label_width = 12,
                label_anchor = W,
                entry_width = 30,
                selectioncommand = self.setStreetModuleType,
                scrolledlist_items = streets
                )
        self.streetModuleType = self.styleManager.getCatalogCode('street', 0)
        self.streetSelector.selectitem(self.streetModuleType[7:])
        self.streetSelector.pack(expand = 1, fill = BOTH)

        # TOON BUILDINGS
        Label(toonBuildingsPage, text = 'Toon Buildings',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        self.addToonBuildingButton = ttk.Button(
                toonBuildingsPage,
                text = 'ADD TOON BUILDING',
                command = self.addFlatBuilding)
        self.addToonBuildingButton.pack(fill = X, padx = 20, pady = 10)
        self.toonBuildingSelector = Pmw.ComboBox(
                toonBuildingsPage,
                dropdown = 0,
                listheight = 200,
                labelpos = W,
                label_width = 12,
                label_anchor = W,
                label_text = 'Bldg type:',
                entry_width = 30,
                selectioncommand = self.setFlatBuildingType,
                scrolledlist_items = (['random'] + BUILDING_TYPES)
                )
        bf = Frame(toonBuildingsPage)
        Label(bf, text = 'Building Height:').pack(side = LEFT, expand = 0)
        self.heightMode = IntVar()
        self.heightMode.set(20)
        self.tenFootButton = ttk.Radiobutton(
                bf,
                text = '10 ft',
                value = 10,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.tenFootButton.pack(side = LEFT, expand = 1, fill = X)
        self.fourteenFootButton = ttk.Radiobutton(
                bf,
                text = '14 ft',
                value = 14,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.fourteenFootButton.pack(side = LEFT, expand = 1, fill = X)
        self.twentyFootButton = ttk.Radiobutton(
                bf,
                text = '20 ft',
                value = 20,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.twentyFootButton.pack(side = LEFT, expand = 1, fill = X)
        self.twentyFourFootButton = ttk.Radiobutton(
                bf,
                text = '24 ft',
                value = 24,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.twentyFourFootButton.pack(side = LEFT, expand = 1, fill = X)
        self.twentyFiveFootButton = ttk.Radiobutton(
                bf,
                text = '25 ft',
                value = 25,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.twentyFiveFootButton.pack(side = LEFT, expand = 1, fill = X)
        self.thirtyFootButton = ttk.Radiobutton(
                bf,
                text = '30 ft',
                value = 30,
                variable = self.heightMode,
                command = self.setFlatBuildingHeight)
        self.thirtyFootButton.pack(side = LEFT, expand = 1, fill = X)
        bf.pack(fill = X)

        self.toonBuildingType = 'random'
        self.toonBuildingSelector.selectitem(self.toonBuildingType)
        self.toonBuildingSelector.pack(expand = 1, fill = BOTH)

        # LANDMARK BUILDINGS
        Label(landmarkBuildingsPage, text = 'Landmark Buildings',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        # Don't try to load this stuff if there is none
        if self.styleManager.getCatalogCode('toon_landmark', 0) == "":
            Label(landmarkBuildingsPage, text = 'There are no landmark buildings in any of your loaded storages.').pack(
                    expand = 0)
        else:

            """
            self.landmarkHQIntVar = IntVar()
            self.landmarkHQIntVar.set(0)
            self.landmarkHQButton = ttk.Checkbutton(
                landmarkBuildingsPage,
                text = 'HQ',
                variable=self.landmarkHQIntVar,
                command=self.setLandmarkHQ)
            self.landmarkHQButton.pack(side = LEFT, expand = 1, fill = X)
            """

            self.addLandmarkBuildingButton = ttk.Button(
                    landmarkBuildingsPage,
                    text = 'ADD LANDMARK BUILDING',
                    command = self.addLandmark)
            self.addLandmarkBuildingButton.pack(fill = X, padx = 20, pady = 10)
            bldgs = [s[14:] for s in self.styleManager.getCatalogCodes(
                    'toon_landmark')]
            bldgs.sort()
            self.landmarkBuildingSelector = Pmw.ComboBox(
                    landmarkBuildingsPage,
                    dropdown = 0,
                    listheight = 200,
                    labelpos = W,
                    label_width = 12,
                    label_anchor = W,
                    label_text = 'Bldg type:',
                    entry_width = 30,
                    selectioncommand = self.setLandmarkType,
                    scrolledlist_items = bldgs
                    )
            self.landmarkType = self.styleManager.getCatalogCode(
                    'toon_landmark', 0)
            self.landmarkBuildingSelector.selectitem(
                    self.styleManager.getCatalogCode('toon_landmark', 0)[14:])
            self.landmarkBuildingSelector.pack(expand = 1, fill = BOTH)

            self.landmarkBuildingSpecialSelector = Pmw.ComboBox(
                    landmarkBuildingsPage,
                    dropdown = 0,
                    listheight = 100,
                    labelpos = W,
                    label_width = 12,
                    label_anchor = W,
                    label_text = 'Special type:',
                    entry_width = 30,
                    selectioncommand = self.setLandmarkSpecialType,
                    scrolledlist_items = LANDMARK_SPECIAL_TYPES
                    )
            self.landmarkSpecialType = LANDMARK_SPECIAL_TYPES[0]
            self.landmarkBuildingSpecialSelector.selectitem(
                    LANDMARK_SPECIAL_TYPES[0])
            self.landmarkBuildingSpecialSelector.pack(expand = 0)

            Label(landmarkBuildingsPage, text = 'Building Title:').pack(side = LEFT, expand = 0)

            self.renameSelectedLandmarkButton = ttk.Button(
                    landmarkBuildingsPage,
                    text = 'Rename Selected Bldg',
                    command = self.renameLandmark)
            self.renameSelectedLandmarkButton.pack(expand = 0, side = RIGHT)
            self.landmarkBuildingNameString = StringVar()
            self.landmarkBuildingNameBox = Entry(
                    landmarkBuildingsPage, width = 24,
                    textvariable = self.landmarkBuildingNameString)
            self.landmarkBuildingNameBox.pack(expand = 0, fill = X)
            
        self.bldgLabels = IntVar()
        self.bldgLabels.set(0)
        self.bldgLabelsButton = ttk.Checkbutton(
                landmarkBuildingsPage,
                text = 'Show Bldg Labels', width = 20,
                variable = self.bldgLabels,
                command = self.toggleBldgLabels)
        self.bldgLabelsButton.pack(side = LEFT, expand = 1, fill = X)

        # ANIMATED BUILDINGS
        Label(animBuildingsPage, text = 'Animated Buildings',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        # Don't try to load this stuff if there is none
        if self.styleManager.getCatalogCode('anim_building', 0) == "":
            Label(animBuildingsPage, text = 'There are no animated buildings in any of your loaded storages.').pack(
                    expand = 0)
        else:
            self.addAnimBuildingsButton = ttk.Button(
                    animBuildingsPage,
                    text = 'ADD ANIMATED BUILDING',
                    command = self.addAnimBuilding)
            self.addAnimBuildingsButton.pack(fill = X, padx = 20, pady = 10)
            codes = (self.styleManager.getCatalogCodes('anim_building'))
            codes.sort()
            self.animBuildingSelector = Pmw.ComboBox(
                    animBuildingsPage,
                    dropdown = 0,
                    listheight = 200,
                    labelpos = W,
                    label_width = 12,
                    label_anchor = W,
                    label_text = 'Animated Building type:',
                    entry_width = 30,
                    selectioncommand = self.setAnimBuildingType,
                    scrolledlist_items = codes
                    )
            self.animBuildingType = self.styleManager.getCatalogCode('anim_building', 0)
            self.animBuildingSelector.selectitem(
                    self.styleManager.getCatalogCode('anim_building', 0))
            self.animBuildingSelector.pack(expand = 1, fill = BOTH)

        # SIGNS
        Label(signPage, text = 'Signs',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        self.currentSignDNA = None
        self.currentBaselineDNA = None
        self.levelEditor.selectedNodePathHookHooks.append(self.updateSignPage)

        gridFrame = Frame(signPage)
        signSelectedFrame = Frame(gridFrame)

        self.currentBaselineIndex = 0
        self.baselineMenu = Pmw.ComboBox(
                signSelectedFrame,
                labelpos = W,
                label_text = 'Selected:', entry_width = 24,
                selectioncommand = self.selectSignBaseline,
                history = 0,  # unique = 0,
                scrolledlist_items = ['<the sign>'])
        self.baselineMenu.selectitem(self.currentBaselineIndex)
        self.baselineMenu.pack(side = LEFT, expand = 1, fill = X)

        self.baselineAddButton = ttk.Button(
                signSelectedFrame,
                text = "Add Baseline", command = self.addBaseline)
        self.baselineAddButton.pack(side = LEFT, expand = 1, fill = X)

        self.baselineDeleteButton = ttk.Button(
                signSelectedFrame,
                text = "Del", command = self.deleteSignItem)
        self.baselineDeleteButton.pack(side = LEFT, expand = 1, fill = X)

        signSelectedFrame.grid(row = 0, column = 0, columnspan = 6)

        self.baselineString = StringVar()
        self.baselineString.trace("wu", self.signBaselineTrace)
        self.baselineTextBox = Entry(
                gridFrame, width = 24,
                textvariable = self.baselineString)
        self.baselineTextBox.grid(row = 1, column = 0, columnspan = 3)

        fontList = [""] + self.styleManager.getCatalogCodes('font')
        self.fontMenu = Pmw.ComboBox(
                gridFrame, labelpos = W,
                label_text = 'Font:', entry_width = 12,
                selectioncommand = self.setSignBaslineFont, history = 0,
                scrolledlist_items = fontList)
        self.fontMenu.selectitem(0)
        self.fontMenu.grid(row = 1, column = 3, columnspan = 3)

        graphicList = self.styleManager.getCatalogCodes('graphic')
        self.graphicMenu = Pmw.ComboBox(
                gridFrame, labelpos = W,
                label_text = 'Add Graphic:', entry_width = 24,
                selectioncommand = self.addSignGraphic, history = 0,
                scrolledlist_items = graphicList)
        # self.graphicMenu.selectitem(0)
        self.graphicMenu.grid(row = 2, column = 0, columnspan = 4)

        signButtonFrame = Frame(gridFrame)

        self.bigFirstLetterIntVar = IntVar()
        self.bigFirstLetterCheckbutton = ttk.Checkbutton(
                signButtonFrame,
                text = 'Big First Letter',
                variable = self.bigFirstLetterIntVar, command = self.setBigFirstLetter)
        self.bigFirstLetterCheckbutton.pack(
                side = LEFT, expand = 1, fill = X)

        self.allCapsIntVar = IntVar()
        self.allCapsCheckbutton = ttk.Checkbutton(
                signButtonFrame,
                text = 'All Caps',
                variable = self.allCapsIntVar, command = self.setAllCaps)
        self.allCapsCheckbutton.pack(side = LEFT, expand = 1, fill = X)

        self.dropShadowIntVar = IntVar()
        self.dropShadowCheckbutton = ttk.Checkbutton(
                signButtonFrame,
                text = 'Drop Shadow',
                variable = self.dropShadowIntVar, command = self.setDropShadow)
        self.dropShadowCheckbutton.pack(side = LEFT, expand = 1, fill = X)

        signButtonFrame.grid(row = 3, column = 0, columnspan = 6)

        self.addKernFloater = Floater.Floater(
                gridFrame,
                text = 'Kern',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setSignBaselineKern)
        self.addKernFloater.grid(row = 4, column = 0, rowspan = 2, columnspan = 3,
                                 sticky = EW)
        self.addWiggleFloater = Floater.Floater(
                gridFrame,
                text = 'Wiggle',
                numDigits = 4,
                # maxVelocity=10.0,
                command = self.setSignBaselineWiggle)
        self.addWiggleFloater.grid(row = 6, column = 0, rowspan = 2, columnspan = 3,
                                   sticky = EW)
        self.addStumbleFloater = Floater.Floater(
                gridFrame,
                text = 'Stumble',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setSignBaselineStumble)
        self.addStumbleFloater.grid(row = 8, column = 0, rowspan = 2, columnspan = 3,
                                    sticky = EW)
        self.addStompFloater = Floater.Floater(
                gridFrame,
                text = 'Stomp',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setSignBaselineStomp)
        self.addStompFloater.grid(row = 10, column = 0, rowspan = 2, columnspan = 3,
                                  sticky = EW)
        self.addCurveFloater = Floater.Floater(
                gridFrame,
                text = 'Curve',
                numDigits = 4,
                # maxVelocity = 1.0,
                command = self.setSignBaselineCurve)
        self.addCurveFloater.grid(row = 12, column = 0, rowspan = 2, columnspan = 3,
                                  sticky = EW)
        self.addXFloater = Floater.Floater(
                gridFrame,
                text = 'X',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setDNATargetX)
        self.addXFloater.grid(row = 4, column = 3, rowspan = 2, columnspan = 3,
                              sticky = EW)
        self.addZFloater = Floater.Floater(
                gridFrame,
                text = 'Z',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setDNATargetZ)
        self.addZFloater.grid(row = 6, column = 3, rowspan = 2, columnspan = 3,
                              sticky = EW)
        self.addScaleXFloater = Floater.Floater(
                gridFrame,
                text = 'Scale X',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setDNATargetScaleX)
        self.addScaleXFloater.grid(row = 8, column = 3, rowspan = 2, columnspan = 3,
                                   sticky = EW)
        self.addScaleZFloater = Floater.Floater(
                gridFrame,
                text = 'Scale Z',
                numDigits = 4,
                # maxVelocity=1.0,
                command = self.setDNATargetScaleZ)
        self.addScaleZFloater.grid(row = 10, column = 3, rowspan = 2, columnspan = 3,
                                   sticky = EW)
        self.addRollFloater = Floater.Floater(
                gridFrame,
                text = 'Roll',
                numDigits = 4,
                # maxVelocity=10.0,
                command = self.setDNATargetRoll)
        self.addRollFloater.grid(row = 12, column = 3, rowspan = 2, columnspan = 3,
                                 sticky = EW)

        gridFrame.pack(fill = BOTH)

        # PROPS
        Label(propsPage, text = 'Props',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        self.addPropsButton = ttk.Button(
                propsPage,
                text = 'ADD PROP',
                command = self.addProp)
        self.addPropsButton.pack(fill = X, padx = 20, pady = 10)
        codes = (self.styleManager.getCatalogCodes('prop') +
                 self.styleManager.getCatalogCodes('holiday_prop'))
        codes.sort()
        self.propSelector = Pmw.ComboBox(
                propsPage,
                dropdown = 0,
                listheight = 200,
                labelpos = W,
                label_width = 12,
                label_anchor = W,
                label_text = 'Prop type:',
                entry_width = 30,
                selectioncommand = self.setPropType,
                scrolledlist_items = codes
                )
        self.propType = self.styleManager.getCatalogCode('prop', 0)
        self.propSelector.selectitem(
                self.styleManager.getCatalogCode('prop', 0))
        self.propSelector.pack(expand = 1, fill = BOTH)

        # ANIMATED PROPS
        Label(animPropsPage, text = 'Animated Props',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        # Don't try to load this stuff if there is none
        if self.styleManager.getCatalogCode('anim_prop', 0) == "":
            Label(animPropsPage, text = 'There are no animated props in any of your loaded storages.').pack(expand = 0)
        else:
            self.addAnimPropsButton = ttk.Button(
                    animPropsPage,
                    text = 'ADD ANIMATED PROP',
                    command = self.addAnimProp)
            self.addAnimPropsButton.pack(fill = X, padx = 20, pady = 10)
            codes = (self.styleManager.getCatalogCodes('anim_prop'))
            codes.sort()
            self.animPropSelector = Pmw.ComboBox(
                    animPropsPage,
                    dropdown = 0,
                    listheight = 200,
                    labelpos = W,
                    label_width = 12,
                    label_anchor = W,
                    label_text = 'Animated Prop type:',
                    entry_width = 30,
                    selectioncommand = self.setAnimPropType,
                    scrolledlist_items = codes
                    )
            self.animPropType = self.styleManager.getCatalogCode('anim_prop', 0)
            self.animPropSelector.selectitem(
                    self.styleManager.getCatalogCode('anim_prop', 0))
            self.animPropSelector.pack(expand = 1, fill = BOTH)

        # ITERACTIVE PROPS
        Label(interactivePropsPage, text = 'Interactive Props',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        # Don't try to load this stuff if there is none
        if self.styleManager.getCatalogCode('interactive_prop', 0) == "":
            Label(interactivePropsPage, text = 'There are no interactive props in any of your loaded storages.').pack(
                    expand = 0)
        else:
            self.addInteractivePropsButton = ttk.Button(
                    interactivePropsPage,
                    text = 'ADD INTERACTIVE PROP',
                    command = self.addInteractiveProp)
            self.addInteractivePropsButton.pack(fill = X, padx = 20, pady = 10)
            codes = (self.styleManager.getCatalogCodes('interactive_prop'))
            codes.sort()
            self.interactivePropSelector = Pmw.ComboBox(
                    interactivePropsPage,
                    dropdown = 0,
                    listheight = 200,
                    labelpos = W,
                    label_width = 12,
                    label_anchor = W,
                    label_text = 'Interactive Prop type:',
                    entry_width = 30,
                    selectioncommand = self.setInteractivePropType,
                    scrolledlist_items = codes
                    )
            self.interactivePropType = self.styleManager.getCatalogCode('interactive_prop', 0)
            self.interactivePropSelector.selectitem(
                    self.styleManager.getCatalogCode('interactive_prop', 0))
            self.interactivePropSelector.pack(expand = 1, fill = BOTH)

        # SUIT PATHS
        Label(suitPathPage, text = 'Suit Paths',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)

        spButtons = Frame(suitPathPage)
        self.fPaths = IntVar()
        self.fPaths.set(0)
        self.pathButton = ttk.Checkbutton(spButtons,
                                          text = 'Show Paths',
                                          width = 12,
                                          variable = self.fPaths,
                                          command = self.toggleSuitPaths)
        self.pathButton.pack(side = LEFT, expand = 1, fill = X)

        self.zoneColor = IntVar()
        self.zoneColor.set(0)
        self.colorZoneButton1 = ttk.Checkbutton(
                spButtons,
                text = 'Color Zones', width = 12,
                variable = self.zoneColor,
                command = self.levelEditor.toggleZoneColors)
        self.colorZoneButton1.pack(side = LEFT, expand = 1, fill = X)

        self.pathLabels = IntVar()
        self.pathLabels.set(0)
        self.pathLabelsButton = ttk.Checkbutton(
                spButtons,
                text = 'Show Point Labels', width = 20,
                variable = self.pathLabels,
                command = self.togglePathLabels)
        self.pathLabelsButton.pack(side = LEFT, expand = 1, fill = X)

        spButtons.pack(fill = X)

        spButtons = Frame(suitPathPage)
        Label(spButtons, text = 'Highlight:').pack(side = LEFT, fill = X)
        self.highlightConnectedButton = ttk.Button(
                spButtons,
                text = 'Forward',
                width = 6,
                command = self.levelEditor.highlightConnected)
        self.highlightConnectedButton.pack(side = LEFT, expand = 1, fill = X)

        self.highlightConnectedButton2 = ttk.Button(
                spButtons,
                text = 'Connected',
                width = 6,
                command = lambda s = self: s.levelEditor.highlightConnected(fReversePath = 1))
        self.highlightConnectedButton2.pack(side = LEFT, expand = 1, fill = X)

        self.clearHighlightButton = ttk.Button(
                spButtons,
                text = 'Clear',
                width = 6,
                command = self.levelEditor.clearPathHighlights)
        self.clearHighlightButton.pack(side = LEFT, expand = 1, fill = X)
        spButtons.pack(fill = X, pady = 4)

        self.suitPointSelector = Pmw.ComboBox(
                suitPathPage,
                dropdown = 0,
                listheight = 200,
                labelpos = W,
                label_text = 'Point type:',
                label_width = 12,
                label_anchor = W,
                entry_width = 30,
                selectioncommand = self.setSuitPointType,
                scrolledlist_items = ['street', 'front door', 'side door']
                )
        self.suitPointSelector.selectitem('street')
        self.suitPointSelector.pack(expand = 1, fill = BOTH)

        # BATTLE CELLS
        Label(battleCellPage, text = 'Battle Cells',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        bcButtons = Frame(battleCellPage)
        self.fCells = IntVar()
        self.fCells.set(0)
        self.cellButton = ttk.Checkbutton(bcButtons,
                                          text = 'Show Cells',
                                          width = 12,
                                          variable = self.fCells,
                                          command = self.toggleBattleCells)
        self.cellButton.pack(side = LEFT, expand = 1, fill = X)

        self.colorZoneButton2 = ttk.Checkbutton(
                bcButtons,
                text = 'Color Zones', width = 12,
                variable = self.zoneColor,
                command = self.levelEditor.toggleZoneColors)
        self.colorZoneButton2.pack(side = LEFT, expand = 1, fill = X)

        ttk.Button(bcButtons,
                   text = 'Connect prop to cell',
                   command = self.levelEditor.connectToCell).pack(side = LEFT, expand = 1, fill = X)

        ttk.Button(bcButtons,
                   text = 'Disconnect prop',
                   command = lambda p0 = True: self.levelEditor.connectToCell(p0)).pack(side = LEFT, expand = 1,
                                                                                        fill = X)

        bcButtons.pack(fill = X)

        self.battleCellSelector = Pmw.ComboBox(
                battleCellPage,
                dropdown = 0,
                listheight = 200,
                labelpos = W,
                label_text = 'Cell type:',
                label_width = 12,
                label_anchor = W,
                entry_width = 30,
                selectioncommand = self.setBattleCellType,
                scrolledlist_items = ['20w 20l', '20w 30l', '30w 20l', '30w 30l']
                )
        self.battleCellSelector.selectitem('20w 20l')
        self.battleCellSelector.pack(expand = 1, fill = BOTH)

        # SCENE GRAPH EXPLORER
        Label(sceneGraphPage, text = 'Level Scene Graph',
              font = ('Calibri', 14, 'bold')).pack(expand = 0)
        self.sceneGraphExplorer = SceneGraphExplorer(
                parent = sceneGraphPage,
                nodePath = self.levelEditor,
                menuItems = ['Add Group', 'Add Vis Group'])
        self.sceneGraphExplorer.pack(expand = 1, fill = BOTH)

        # Compact down notebook
        self.notebook.setnaturalsize()

        # Snapping Options
        snapFrame = Frame(hull)
        self.fMapVis = IntVar()
        self.fMapVis.set(0)
        # self.mapSnapButton = ttk.Checkbutton(snapFrame,
        # text = 'Map Vis',
        # width = 12,
        # variable = self.fMapVis,
        # command = self.toggleMapVis)
        # self.mapSnapButton.pack(side = LEFT, expand = 1, fill = X)

        Label(snapFrame, text = 'Snapping', width = 8, anchor = 'nw',
              font = ('Calibri', 10, 'bold')).pack(padx = 5, side = LEFT, expand = 1, fill = X)

        self.fXyzSnap = IntVar()
        self.fXyzSnap.set(0)
        self.xyzSnapButton = ttk.Checkbutton(snapFrame,
                                             text = 'Position Snapping',
                                             width = 18,
                                             variable = self.fXyzSnap,
                                             command = self.toggleXyzSnap)
        self.xyzSnapButton.pack(side = LEFT, expand = 1, fill = X)

        self.fHprSnap = IntVar()
        self.fHprSnap.set(0)
        self.hprSnapButton = ttk.Checkbutton(snapFrame,
                                             text = 'Rotation Snapping',
                                             width = 18,
                                             variable = self.fHprSnap,
                                             command = self.toggleHprSnap)
        self.hprSnapButton.pack(side = LEFT, expand = 1, fill = X)

        def toggleWidgetHandles(s = self):
            if s.fPlaneSnap.get():
                base.direct.widget.disableHandles(['x-ring', 'x-disc',
                                                   'y-ring', 'y-disc',
                                                   'z-disc', 'z-post'])
            else:
                base.direct.widget.enableHandles('all')

        self.fPlaneSnap = IntVar()
        self.fPlaneSnap.set(0)
        self.planeSnapButton = ttk.Checkbutton(snapFrame,
                                               text = 'Plane Snapping',
                                               width = 18,
                                               variable = self.fPlaneSnap,
                                               command = toggleWidgetHandles)
        self.planeSnapButton.pack(side = LEFT, expand = 1, fill = X)

        snapFrame.pack(fill = X)

        # Visual Options
        visualFrame = Frame(hull)
        Label(visualFrame, text = 'Visual', width = 8, anchor = 'nw',
              font = ('Calibri', 10, 'bold')).pack(padx = 5, side = LEFT, expand = 1, fill = X)

        self.fLabel = IntVar()
        self.fLabel.set(0)
        self.labelButton = ttk.Checkbutton(visualFrame,
                                           text = 'Show Zone Labels',
                                           width = 18,
                                           variable = self.fLabel,
                                           command = self.toggleZoneLabels)
        self.labelButton.pack(side = LEFT, expand = 1, fill = X)

        self.fLabelOnTop = IntVar()
        self.fLabelOnTop.set(0)
        self.labelOnTopButton = ttk.Checkbutton(visualFrame,
                                                text = 'Labels Always On Top',
                                                width = 20,
                                                variable = self.fLabelOnTop,
                                                command = self.toggleZoneLabelsOnTop)
        self.labelOnTopButton.pack(side = LEFT, expand = 1, fill = X)

        self.fGrid = IntVar()
        self.fGrid.set(0)
        base.direct.gridButton = ttk.Checkbutton(visualFrame,
                                                 text = 'Show Grid',
                                                 width = 18,
                                                 variable = self.fGrid,
                                                 command = self.toggleGrid)
        base.direct.gridButton.pack(side = LEFT, expand = 1, fill = X)

        self.fMaya = IntVar()
        self.fMaya.set(1)
        self.mayaButton = ttk.Checkbutton(visualFrame,
                                          text = 'Maya Cam',
                                          width = 18,
                                          variable = self.fMaya,
                                          command = self.toggleMaya)
        self.mayaButton.pack(side = LEFT, expand = 1, fill = X)

        # Make maya mode on by default
        self.toggleMaya()

        visualFrame.pack(fill = X)

        # experimental stuff

        if ConfigVariableBool("want-experimental", False):
            buttonFrame4 = Frame(hull)
            Label(buttonFrame4, text = 'Experimental', width = 8, anchor = 'nw',
                  font = ('Calibri', 10, 'bold')).pack(padx = 5, side = LEFT, expand = 1, fill = X)
            self.driveMode = IntVar()
            self.driveMode.set(0)
            self.driveModeButton = ttk.Checkbutton(
                    buttonFrame4,
                    text = 'Drive',
                    width = 18,
                    variable = self.driveMode,
                    command = self.toggleDrive)
            self.driveModeButton.pack(side = LEFT, fill = X, expand = 1)

            self.fColl = IntVar()
            self.fColl.set(1)
            base.direct.collButton = ttk.Checkbutton(
                    buttonFrame4,
                    text = 'Collide',
                    variable = self.fColl, width = 18,
                    command = self.levelEditor.toggleCollisions)
            base.direct.collButton.pack(side = LEFT, expand = 1, fill = X)

            self.fVis = IntVar()
            self.fVis.set(1)
            base.direct.visButton = ttk.Checkbutton(
                    buttonFrame4,
                    text = 'Visibility',
                    variable = self.fVis, width = 18,
                    command = self.levelEditor.toggleVisibility)
            base.direct.visButton.pack(side = LEFT, expand = 1, fill = X)

            buttonFrame4.pack(fill = X)

        # Object Functions
        objectFrame = Frame(hull)
        ttk.Label(objectFrame, text = 'Object', width = 8, anchor = 'nw',
                  font = ('Calibri', 10, 'bold')).pack(padx = 5, side = LEFT, expand = 1, fill = X)

        self.colorEntry = VectorWidgets.ColorEntry(
                objectFrame, text = 'Select Color', value = (0, 0, 0, 255),
                relief = FLAT, command = self.updateSelectedObjColor)
        self.colorEntry.menu.add_command(
                label = 'Save Color', command = DNASerializer.saveColor)
        self.colorEntry.pack(side = LEFT, expand = 1, fill = X)

        self.selectButton = ttk.Button(objectFrame,
                                       text = 'Place Selected',
                                       width = 18,
                                       command = lambda: last.place()
                                       )
        self.selectButton.pack(side = LEFT, expand = 1, fill = X)
        objectFrame.pack(fill = X)

        # Make sure input variables processed
        self.initialiseoptions(LevelEditorPanel)

        # Initializes auto saver for use
        AutoSaver.initializeAutoSaver()

    def updateInfo(self, page):
        if page == 'Signs':
            self.updateSignPage()

    # [gjeon] to toggle maya cam mode
    def toggleMaya(self):
        base.direct.cameraControl.lockRoll = self.fMaya.get()
        direct.cameraControl.useMayaCamControls = self.fMaya.get()

    def toggleGrid(self):
        if self.fGrid.get():
            base.direct.grid.enable()
        else:
            base.direct.grid.disable()

    def toggleSuitPaths(self):
        if self.fPaths.get():
            self.levelEditor.showSuitPaths()
        else:
            self.levelEditor.hideSuitPaths()

    def toggleBattleCells(self):
        if self.fCells.get():
            self.levelEditor.showBattleCells()
        else:
            self.levelEditor.hideBattleCells()

    def toggleZoneLabels(self):
        if self.fLabel.get():
            self.levelEditor.labelZones()
        else:
            self.levelEditor.clearZoneLabels()

    def toggleZoneLabelsOnTop(self):
        self.levelEditor.labelsOnTop = self.fLabelOnTop.get()
        for lbl in self.levelEditor.zoneLabels + self.levelEditor.bldgLabels:
            lbl.setDepthTest(not self.fLabelOnTop.get())
        for lbl in self.levelEditor.NPToplevel.findAllMatches('**/suit_point_label_*'):
            lbl.setDepthTest(not self.fLabelOnTop.get())

    def togglePathLabels(self):
        if self.pathLabels.get():
            for lbl in self.levelEditor.NPToplevel.findAllMatches('**/suit_point_label_*'):
                lbl.show()
        else:
            for lbl in self.levelEditor.NPToplevel.findAllMatches('**/suit_point_label_*'):
                lbl.hide()

    def toggleBldgLabels(self):
        if self.bldgLabels.get():
            self.levelEditor.labelBldgs()
        else:
            self.levelEditor.clearBldgLabels()

    def toggleXyzSnap(self):
        base.direct.grid.setXyzSnap(self.fXyzSnap.get())

    def toggleHprSnap(self):
        base.direct.grid.setHprSnap(self.fXyzSnap.get())

    def toggleMapVis(self):
        self.levelEditor.toggleMapVis(self.fMapVis.get())

    def setStreetModuleType(self, name):
        self.streetModuleType = 'street_' + name
        self.levelEditor.setCurrent('street_texture', self.streetModuleType)

    def addStreet(self):
        self.levelEditor.addStreet(self.streetModuleType)

    def setFlatBuildingType(self, name):
        self.toonBuildingType = name
        self.levelEditor.setCurrent('building_type', self.toonBuildingType)

    def setFlatBuildingHeight(self):
        height = self.heightMode.get()
        self.levelEditor.setCurrent('building_height', height)
        self.updateHeightList(height)

    def updateHeightList(self, height):
        # Update combo box
        heightList = self.levelEditor.getList(repr(height) + '_ft_wall_heights')
        self.toonBuildingSelector.setlist(
                ['random'] + list(map(createHeightCode, heightList)))
        self.toonBuildingSelector.selectitem(0)
        self.toonBuildingSelector.invoke()

    def addFlatBuilding(self):
        self.levelEditor.addFlatBuilding(self.toonBuildingType)

    def setLandmarkType(self, name):
        self.landmarkType = 'toon_landmark_' + name
        self.levelEditor.setCurrent('toon_landmark_texture', self.landmarkType)

    def signPanelSync(self):
        self.baselineMenu.delete(1, END)
        sign = self.findSignFromDNARoot()
        if not sign:
            return
        baselineList = DNAGetChildren(sign, DNA_SIGN_BASELINE)
        for baseline in baselineList:
            s = DNAGetBaselineString(baseline)
            self.baselineMenu.insert(END, s)
        self.baselineMenu.selectitem(0)
        self.selectSignBaseline(0)

    def updateSignPage(self):
        if self.notebook.getcurselection() == 'Signs':
            sign = self.findSignFromDNARoot()
            # Only update if it's not the current sign:
            if self.currentSignDNA != sign:
                self.currentSignDNA = sign
                self.signPanelSync()

    def findSignFromDNARoot(self):
        dnaRoot = self.levelEditor.selectedDNARoot
        if not dnaRoot:
            return
        objClass = DNAGetClassType(dnaRoot)
        if (objClass == DNA_LANDMARK_BUILDING
                or objClass == DNA_PROP \
                or objClass == DNA_ANIM_BUILDING):
            target = DNAGetChildRecursive(dnaRoot, DNA_SIGN)
            return target

    def selectSignBaseline(self, val):
        if not self.currentSignDNA:
            return
        # Temporarily undefine DNATarget (this will speed
        # up setting the values, because the callbacks won't
        # call self.levelEditor.replaceSelected() with each
        # setting):
        self.levelEditor.DNATarget = None
        self.currentBaselineDNA = None
        target = None
        index = self.currentBaselineIndex = int((self.baselineMenu.curselection())[0])
        if index == 0:
            target = self.currentSignDNA
            # Unset some ui elements:
            self.baselineString.set('')
            self.fontMenu.selectitem(0)
            self.addCurveFloater.set(0)
            self.addKernFloater.set(0)
            self.addWiggleFloater.set(0)
            self.addStumbleFloater.set(0)
            self.addStompFloater.set(0)
            self.bigFirstLetterIntVar.set(0)
            self.allCapsIntVar.set(0)
            self.dropShadowIntVar.set(0)
        else:
            target = DNAGetChild(self.currentSignDNA, DNA_SIGN_BASELINE, index - 1)
            if target:
                # Update panel info:
                s = DNAGetBaselineString(target)
                self.baselineString.set(s)
                self.fontMenu.selectitem(target.getCode())
                try:
                    val = 1.0 / target.getWidth()
                except ZeroDivisionError:
                    val = 0.0
                self.addCurveFloater.set(val)
                self.addKernFloater.set(target.getKern())
                self.addWiggleFloater.set(target.getWiggle())
                self.addStumbleFloater.set(target.getStumble())
                self.addStompFloater.set(target.getStomp())
                flags = target.getFlags()
                self.bigFirstLetterIntVar.set('b' in flags)
                self.allCapsIntVar.set('c' in flags)
                self.dropShadowIntVar.set('d' in flags)

                self.currentBaselineDNA = target
        if target:
            pos = target.getPos()
            self.addXFloater.set(pos[0])
            self.addZFloater.set(pos[2])
            scale = target.getScale()
            self.addScaleXFloater.set(scale[0])
            self.addScaleZFloater.set(scale[2])
            hpr = target.getHpr()
            self.addRollFloater.set(hpr[2])

            self.levelEditor.DNATarget = target

    def deleteSignItem(self):
        """Delete the selected sign or sign baseline"""
        if self.currentBaselineDNA:
            # Remove the baseline:
            assert int((self.baselineMenu.curselection())[0]) == self.currentBaselineIndex
            DNARemoveChildOfClass(self.currentSignDNA, DNA_SIGN_BASELINE,
                                  self.currentBaselineIndex - 1)
            self.baselineMenu.delete(self.currentBaselineIndex)
            self.baselineMenu.selectitem(0)
            self.currentBaselineIndex = 0
            self.currentBaselineDNA = None
            self.selectSignBaseline(0)
            self.levelEditor.replaceSelected()
        elif self.currentSignDNA:
            # Remove the sign:
            assert int((self.baselineMenu.curselection())[0]) == 0
            le = self.levelEditor
            le.removeSign(le.DNATarget, le.DNATargetParent)
            self.currentBaselineDNA = None
            self.currentSignDNA = None
            self.levelEditor.replaceSelected()

    def signBaselineTrace(self, a, b, mode):
        # print self, a, b, mode, self.baselineString.get()
        baseline = self.currentBaselineDNA
        if baseline:
            s = self.baselineString.get()
            self.setBaselineString(s)

    def addSignGraphic(self, code):
        """
        Create a new baseline with a graphic and
        add it to the current sign
        """
        sign = self.findSignFromDNARoot()
        if sign:
            graphic = DNASignGraphic()
            graphic.setCode(code)
            baseline = DNASignBaseline()
            baseline.add(graphic)
            sign.add(baseline)
            # Show the UI to the new baseline:
            self.levelEditor.DNATarget = baseline
            self.baselineMenu.insert(END, '[' + code + ']')
            current = self.baselineMenu.size() - 1
            self.baselineMenu.selectitem(current)
            self.selectSignBaseline(current)
            self.levelEditor.replaceSelected()

    def addBaseline(self):
        sign = self.findSignFromDNARoot()
        if sign:
            baseline = DNASignBaseline()
            text = "Zoo"
            DNASetBaselineString(baseline, text)
            sign.add(baseline)
            # Show the UI to the new baseline:
            self.levelEditor.DNATarget = baseline
            self.baselineMenu.insert(END, text)
            current = self.baselineMenu.size() - 1
            self.baselineMenu.selectitem(current)
            self.selectSignBaseline(current)
            self.levelEditor.replaceSelected()

    def addBaselineItem(self):
        pass

    def selectSignBaselineItem(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            baseline.setCode(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineStyle(self, val):
        baseline = self.currentBaselineDNA
        if baseline == None:
            print("\n\nbaseline == None")
            return  # skyler: This isn't working yet.
            #               As a workaround, select the baseline from the tk panel.
            # Try to find the first baseline in the sign:
            sign = self.findSignFromDNARoot()
            if sign:
                self.currentSignDNA = sign
                baseline = DNAGetChild(sign, DNA_SIGN_BASELINE)
        if baseline and val:
            self.levelEditor.DNATarget = baseline
            self.currentBaselineDNA = baseline
            settings = val
            self.levelEditor.replaceSelectedEnabled = 0

            # Don't set string: self.baselineString.set('')
            if settings['curve'] != None:
                self.addCurveFloater.set(settings['curve'])
            if settings['kern'] != None:
                self.addKernFloater.set(settings['kern'])
            if settings['wiggle'] != None:
                self.addWiggleFloater.set(settings['wiggle'])
            if settings['stumble'] != None:
                self.addStumbleFloater.set(settings['stumble'])
            if settings['stomp'] != None:
                self.addStompFloater.set(settings['stomp'])

            flags = settings['flags']
            if flags != None:
                self.bigFirstLetterIntVar.set('b' in flags)
                self.setBigFirstLetter()

                self.allCapsIntVar.set('c' in flags)
                self.setAllCaps()

                self.dropShadowIntVar.set('d' in flags)
                self.setDropShadow()

            code = settings['code']
            if code != None:
                self.fontMenu.selectitem(code)
                self.setSignBaslineFont(code)

            if settings['x'] != None:
                self.addXFloater.set(settings['x'])
            if settings['z'] != None:
                self.addZFloater.set(settings['z'])
            if settings['scaleX'] != None:
                self.addScaleXFloater.set(settings['scaleX'])
            if settings['scaleZ'] != None:
                self.addScaleZFloater.set(settings['scaleZ'])
            if settings['roll'] != None:
                self.addRollFloater.set(settings['roll'])

            color = settings['color']
            if color != None:
                # self.updateSelectedObjColor(settings['color'])
                self.setCurrentColor(color)
                self.setResetColor(color)
                baseline.setColor(color)

            self.levelEditor.replaceSelectedEnabled = 1
            self.levelEditor.replaceSelected()

    def setBaselineString(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            DNASetBaselineString(baseline, val)
            self.baselineMenu.delete(self.currentBaselineIndex)
            self.baselineMenu.insert(self.currentBaselineIndex, val)
            self.baselineMenu.selectitem(self.currentBaselineIndex)
            self.levelEditor.replaceSelected()

    def adjustBaselineFlag(self, newValue, flagChar):
        baseline = self.currentBaselineDNA
        if baseline:
            flags = baseline.getFlags()
            if newValue:
                if not flagChar in flags:
                    # Add the flag:
                    baseline.setFlags(flags + flagChar)
            elif flagChar in flags:
                # Remove the flag:
                flags = ''.join(flags.split(flagChar))
                baseline.setFlags(flags)
            self.levelEditor.replaceSelected()

    def setLandmarkSpecialType(self, type):
        self.landmarkSpecialType = type
        if self.levelEditor.lastLandmarkBuildingDNA:
            self.levelEditor.lastLandmarkBuildingDNA.setBuildingType(self.landmarkSpecialType)

    def setBigFirstLetter(self):
        self.adjustBaselineFlag(self.bigFirstLetterIntVar.get(), 'b')

    def setAllCaps(self):
        self.adjustBaselineFlag(self.allCapsIntVar.get(), 'c')

    def setDropShadow(self):
        self.adjustBaselineFlag(self.dropShadowIntVar.get(), 'd')

    def setSignBaslineFont(self, val):
        target = self.levelEditor.DNATarget
        if target and (DNAGetClassType(target) == DNA_SIGN_BASELINE
                       or DNAGetClassType(target) == DNA_SIGN_TEXT):
            target.setCode(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineCurve(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            try:
                val = 1.0 / val
            except ZeroDivisionError:
                val = 0.0
            baseline.setWidth(val)
            baseline.setHeight(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineKern(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            baseline.setKern(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineWiggle(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            baseline.setWiggle(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineStumble(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            baseline.setStumble(val)
            self.levelEditor.replaceSelected()

    def setSignBaselineStomp(self, val):
        baseline = self.currentBaselineDNA
        if baseline:
            baseline.setStomp(val)
            self.levelEditor.replaceSelected()

    def setDNATargetX(self, val):
        target = self.levelEditor.DNATarget
        if target:
            pos = target.getPos()
            pos = VBase3(val, pos[1], pos[2])
            target.setPos(pos)
            self.levelEditor.replaceSelected()

    def setDNATargetZ(self, val):
        target = self.levelEditor.DNATarget
        if target:
            pos = target.getPos()
            pos = VBase3(pos[0], pos[1], val)
            target.setPos(pos)
            self.levelEditor.replaceSelected()

    def setDNATargetScaleX(self, val):
        target = self.levelEditor.DNATarget
        if target:
            scale = target.getScale()
            scale = VBase3(val, scale[1], scale[2])
            target.setScale(scale)
            self.levelEditor.replaceSelected()

    def setDNATargetScaleZ(self, val):
        target = self.levelEditor.DNATarget
        if target:
            scale = target.getScale()
            scale = VBase3(scale[0], scale[1], val)
            target.setScale(scale)
            self.levelEditor.replaceSelected()

    def setDNATargetRoll(self, val):
        target = self.levelEditor.DNATarget
        if target:
            hpr = target.getHpr()
            hpr = VBase3(hpr[0], hpr[1], val)
            target.setHpr(hpr)
            self.levelEditor.replaceSelected()

    def addLandmark(self):
        self.levelEditor.addLandmark(self.landmarkType, self.landmarkSpecialType, self.landmarkBuildingNameString.get())

    def renameLandmark(self):
        self.levelEditor.renameLandmark(self.landmarkBuildingNameString.get())

    def addAnimBuilding(self):
        self.levelEditor.addAnimBuilding(self.animBuildingType)

    def setAnimBuildingType(self, name):
        print(name)

    def setPropType(self, name):
        self.propType = name
        self.levelEditor.setCurrent('prop_texture', self.propType)

    def addProp(self):
        self.levelEditor.addProp(self.propType)

    def setAnimPropType(self, name):
        self.animPropType = name
        self.levelEditor.setCurrent('anim_prop_texture', self.animPropType)

    def addAnimProp(self):
        self.levelEditor.addAnimProp(self.animPropType)

    def setInteractivePropType(self, name):
        self.interactivePropType = name
        self.levelEditor.setCurrent('interactive_prop_texture', self.interactivePropType)

    def addInteractiveProp(self):
        self.levelEditor.addInteractiveProp(self.interactivePropType)

    def updateSelectedWallWidth(self, strVal):
        self.levelEditor.updateSelectedWallWidth(atof(strVal))

    def setCurrentColor(self, colorVec, fUpdate = 0):
        # Turn on/off update of selected before updating entry
        self.fUpdateSelected = fUpdate
        self.colorEntry.set([int(colorVec[0] * 255.0),
                             int(colorVec[1] * 255.0),
                             int(colorVec[2] * 255.0),
                             255])

    def setResetColor(self, colorVec):
        self.colorEntry['resetValue'] = (
            [int(colorVec[0] * 255.0),
             int(colorVec[1] * 255.0),
             int(colorVec[2] * 255.0),
             255])

    def setSuitPointType(self, name):
        if name == "street":
            self.levelEditor.currentSuitPointType = DNASuitPoint.STREETPOINT
        elif name == "front door":
            self.levelEditor.currentSuitPointType = DNASuitPoint.FRONTDOORPOINT
        elif name == "side door":
            self.levelEditor.currentSuitPointType = DNASuitPoint.SIDEDOORPOINT
        print(self.levelEditor.currentSuitPointType)

    def setBattleCellType(self, name):
        self.levelEditor.currentBattleCellType = name

    def setAutoSaverInterval(self, i):
        if i == 'Save Options':
            try:
                AutoSaver.autoSaverInterval = float(self.autoSaverDialogInterval.get())
                AutoSaver.maxAutoSaveCount = float(self.autoSaverDialogMax.get())
            except ValueError as e:
                # Non-float was passed
                raise e
        self.autoSaverDialog.withdraw()

    def updateSelectedObjColor(self, color):
        try:
            obj = self.levelEditor.DNATarget
            if self.fUpdateSelected and (obj != None):
                objClass = DNAGetClassType(obj)
                if ((objClass == DNA_WALL) or
                        (objClass == DNA_WINDOWS) or
                        (objClass == DNA_DOOR) or
                        (objClass == DNA_FLAT_DOOR) or
                        (objClass == DNA_CORNICE) or
                        (objClass == DNA_PROP) or
                        (objClass == DNA_SIGN) or
                        (objClass == DNA_SIGN_BASELINE) or
                        (objClass == DNA_SIGN_TEXT) or
                        (objClass == DNA_SIGN_GRAPHIC)
                ):
                    self.levelEditor.setDNATargetColor(
                            VBase4((color[0] / 255.0),
                                   (color[1] / 255.0),
                                   (color[2] / 255.0),
                                   1.0))
        except AttributeError:
            pass
        # Default is to update selected
        self.fUpdateSelected = 1

    def toggleBalloon(self):
        if self.toggleBalloonVar.get():
            self.balloon.configure(state = 'balloon')
        else:
            self.balloon.configure(state = 'none')

    def showAbout(self):
        self.aboutDialog.show()
        self.aboutDialog.focus_set()

    def showControls(self):
        self.controlsDialog.show()
        self.controlsDialog.focus_set()

    def showAutoSaverDialog(self):
        self.autoSaverDialog.show()
        self.autoSaverDialog.focus_set()

    def showInjector(self):
        self.injectorDialog.show()
        self.injectorDialog.focus_set()

    def runInject(self, e):
        if e == None:
            self.injectorDialog.withdraw()
        if e == 'Run':
            exec(self.injectorTextBox.get('1.0', 'end'), globals())
        pass

    def toggleOT(self):
        if self.toggleOTVar.get():
            self.levelEditor.getNPToplevel().setShader(
                    Shader.load(Shader.SL_GLSL,
                                vertex = 'resources/shaders/tt_sha_render_bandw.vert',
                                fragment = 'resources/shaders/tt_sha_render_bandw.frag'))
        else:
            self.levelEditor.getNPToplevel().clearShader()

    def toggleDrive(self):
        if self.driveMode:
            self.levelEditor.useDriveMode()
        else:
            self.levelEditor.useDirectFly()

    def toggleAutoSaver(self):
        if AutoSaver.autoSaverToggled is False:
            # If no working DNA outputFile is selected, one is chosen here
            if DNASerializer.outputFile is None:
                DNASerializer.saveToSpecifiedDNAFile()
            print(f'Starting auto saver on an interval of {AutoSaver.autoSaverInterval} minutes')
            # Toggles auto saver to begin auto saving loop
            AutoSaver.autoSaverToggled = True
        else:
            print('Stopping auto saver')
            # Stops auto saving loop
            AutoSaver.autoSaverToggled = False
