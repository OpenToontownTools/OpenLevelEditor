import Pmw
import sys
from direct.showbase.TkGlobal import *
from direct.tkwidgets.Tree import *


class VisGroupsEditor(Pmw.MegaToplevel):
    def __init__(self, levelEditor, visGroups = ['None'],
                 parent = None, **kw):

        INITOPT = Pmw.INITOPT
        optiondefs = (
            ('title', 'Visability Groups Editor', None),
            )
        self.defineoptions(kw, optiondefs)

        Pmw.MegaToplevel.__init__(self, parent, title = self['title'])
        if sys.platform == 'win32':
            # FIXME: This doesn't work in other platforms for some reason...
            self.iconbitmap("resources/openttle_ico_temp.ico")
        self.levelEditor = levelEditor
        self.visGroups = visGroups
        self.visGroupNames = [pair[1].getName() for pair in self.visGroups]
        # Initialize dictionary of visibility relationships
        self.visDict = {}
        # Group we are currently setting visGroups for
        self.target = None
        # Flag to enable/disable toggleVisGroup command
        self.fCommand = 1

        # Handle to the toplevels hull
        hull = self.component('hull')

        balloon = self.balloon = Pmw.Balloon(hull)
        # Start with balloon help disabled
        self.balloon.configure(state = 'none')

        menuFrame = Frame(hull, relief = GROOVE, bd = 2)
        menuFrame.pack(fill = X, expand = 1)

        menuBar = Pmw.MenuBar(menuFrame, hotkeys = 1, balloon = balloon)
        menuBar.pack(side = LEFT, expand = 1, fill = X)
        menuBar.addmenu('Vis Groups Editor',
                        'Visability Groups Editor Operations')
        menuBar.addmenuitem('Vis Groups Editor', 'command',
                            'Exit Visability Groups Editor',
                            label = 'Exit',
                            command = self.preDestroy)

        menuBar.addmenu('Help', 'Visability Groups Editor Help Operations')
        self.toggleBalloonVar = IntVar()
        self.toggleBalloonVar.set(0)
        menuBar.addmenuitem('Help', 'checkbutton',
                            'Toggle balloon help',
                            label = 'Balloon Help',
                            variable = self.toggleBalloonVar,
                            command = self.toggleBalloon)

        # Create a combo box to choose target vis group
        self.targetSelector = Pmw.ComboBox(
                hull, labelpos = W, label_text = 'Target Vis Group:',
                entry_width = 12, selectioncommand = self.selectVisGroup,
                scrolledlist_items = self.visGroupNames)
        self.targetSelector.selectitem(self.visGroupNames[0])
        self.targetSelector.pack(expand = 1, fill = X)

        # Scrolled frame to hold radio selector
        sf = Pmw.ScrolledFrame(hull, horizflex = 'elastic',
                               usehullsize = 1, hull_width = 200,
                               hull_height = 400)
        frame = sf.interior()
        sf.pack(padx = 5, pady = 3, fill = BOTH, expand = 1)

        # Add vis groups selector
        self.selected = Pmw.RadioSelect(frame, selectmode = MULTIPLE,
                                        orient = VERTICAL,
                                        pady = 0,
                                        command = self.toggleVisGroup)
        for groupInfo in self.visGroups:
            nodePath = groupInfo[0]
            group = groupInfo[1]
            name = group.getName()
            self.selected.add(name, width = 12)
            # Assemble list of groups visible from this group
            visible = []
            for i in range(group.getNumVisibles()):
                visible.append(group.getVisibleName(i))
            visible.sort()
            self.visDict[name] = [nodePath, group, visible]
        # Pack the widget
        self.selected.pack(expand = 1, fill = X)
        # And make sure scrolled frame is happy
        sf.reposition()

        buttonFrame = Frame(hull)
        buttonFrame.pack(fill = X, expand = 1)

        self.showMode = IntVar()
        self.showMode.set(0)
        self.showAllButton = Radiobutton(buttonFrame, text = 'Show All',
                                         value = 0, indicatoron = 1,
                                         variable = self.showMode,
                                         command = self.refreshVisibility)
        self.showAllButton.pack(side = LEFT, fill = X, expand = 1)
        self.showActiveButton = Radiobutton(buttonFrame, text = 'Show Target',
                                            value = 1, indicatoron = 1,
                                            variable = self.showMode,
                                            command = self.refreshVisibility)
        self.showActiveButton.pack(side = LEFT, fill = X, expand = 1)

        # Make sure input variables processed
        self.initialiseoptions(VisGroupsEditor)

        # Switch to current target's list
        self.selectVisGroup(self.visGroupNames[0])

    def selectVisGroup(self, target):
        print('Setting vis options for group:', target)
        # Record current target
        oldTarget = self.target
        # Record new target
        self.target = target
        # Deselect buttons from old target (first deactivating command)
        self.fCommand = 0
        if oldTarget:
            visList = self.visDict[oldTarget][2]
            for group in visList:
                self.selected.invoke(self.selected.index(group))
        # Now set buttons to reflect state of new target
        visList = self.visDict[target][2]
        for group in visList:
            self.selected.invoke(self.selected.index(group))
        # Reactivate command
        self.fCommand = 1
        # Update scene
        self.refreshVisibility()

    def toggleVisGroup(self, groupName, state):
        if self.fCommand:
            targetInfo = self.visDict[self.target]
            target = targetInfo[1]
            visList = targetInfo[2]
            groupNP = self.visDict[groupName][0]
            group = self.visDict[groupName][1]
            # MRM: Add change in visibility here
            # Show all vs. show active
            if state == 1:
                print('Vis Group:', self.target, 'adding group:', groupName)
                if groupName not in visList:
                    visList.append(groupName)
                    target.addVisible(groupName)
                    # Update vis and color
                    groupNP.show()
                    groupNP.setColorScale(0, .8, .5, 1)
            else:
                print('Vis Group:', self.target, 'removing group:', groupName)
                if groupName in visList:
                    visList.remove(groupName)
                    target.removeVisible(groupName)
                    # Update vis and color
                    if self.showMode.get() == 1:
                        groupNP.hide()
                    groupNP.clearColorScale()
        # Update scene
        self.refreshVisibility()

    def refreshVisibility(self):
        # Get current visibility list for target
        targetInfo = self.visDict[self.target]
        visList = targetInfo[2]
        for key in list(self.visDict.keys()):
            groupNP = self.visDict[key][0]
            if key in visList:
                groupNP.show()
                if key == self.target:
                    groupNP.setColorScale(0, 1, 0, 1)
                else:
                    groupNP.setColorScale(0, .8, .5, 1)
            else:
                if self.showMode.get() == 0:
                    groupNP.show()
                else:
                    groupNP.hide()
                groupNP.clearColorScale()

    def preDestroy(self):
        # First clear level editor variable
        self.levelEditor.vgpanel = None
        self.destroy()

    def toggleBalloon(self):
        if self.toggleBalloonVar.get():
            self.balloon.configure(state = 'balloon')
        else:
            self.balloon.configure(state = 'none')
