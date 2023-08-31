import os
from tkinter.filedialog import asksaveasfilename
from typing import Dict, Callable, List, Optional, Tuple

from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath, Filename
from panda3d.toontown import DNAVisGroup

from toontown.leveleditor import LevelEditorGlobals
from toontown.leveleditor.DNASerializer import DNASerializer
from toontown.toonbase.CEFPanda import CEFPanda


class CEFLevelEditorPanel(DirectObject):
    def __init__(self, levelEditor):
        DirectObject.__init__(self)
        self.levelEditor = levelEditor

        self.htmlUi = CEFPanda()
        self.htmlUi.load_file('resources/ui/ui.html')

        self.visNumToNP: Dict[str, NodePath] = {}

        self.accept('SGE_Update Explorer', lambda np, s = self: s.repopulateVisgroupList())

    def setupLists(self):
        # streets
        self.htmlUi.exec_js_func('populate_list', 'street-module-list', [s for s in self.levelEditor.styleManager.getCatalogCodes('street')])

        # static props
        propList: List[str] = self.levelEditor.styleManager.getCatalogCodes('prop') + self.levelEditor.styleManager.getCatalogCodes('holiday_prop')
        # make it alphabetical
        propList.sort()
        self.htmlUi.exec_js_func('populate_list', 'prop-list', propList)
        del propList

        # Landmark buildings
        landmarks: List[str] = [s[14:] for s in self.levelEditor.styleManager.getCatalogCodes('toon_landmark')]
        landmarks.sort()
        self.htmlUi.exec_js_func('populate_list', 'landmark-list', landmarks)
        del landmarks

        # Landmark building types
        self.htmlUi.exec_js_func('populate_list', 'landmark-type-list', LevelEditorGlobals.LANDMARK_SPECIAL_TYPES[1:])

        # Interactive Props
        interPropList: List[str] = self.levelEditor.styleManager.getCatalogCodes('interactive_prop')
        self.htmlUi.exec_js_func('populate_list', 'interactive-prop-list', interPropList)

        # vis
        self.repopulateVisgroupList()

    def bindFunctions(self):
        """
        Binds functions called from the javascript to their python counterparts
        """
        binds: Dict[str, Callable] = {
            # generic events
            'le_set_input_focus': self.__toggleInputFocus,
            'le_set_mouse_events': self.__toggleMouseEvents,

            # save/load events
            'le_load_dna': DNASerializer.loadSpecifiedDNAFile,
            'le_save_dna': DNASerializer.outputDNADefaultFile,
            'le_save_as_dna': DNASerializer.saveToSpecifiedDNAFile,
            'le_export_bam': self.__exportToBam,

            # spawn events
            'le_spawn_street': self.__spawnStreet,
            'le_spawn_prop': self.__spawnProp,
            'le_spawn_landmark': self.__spawnLandmark,
            'le_spawn_interactive_prop': self.__spawnInteractiveProp,

            # edit events
            'le_rename_landmark': self.__renameLandmark,

            # visgroup events
            'le_select_visgroup': self.__selectVisGroup,
            'le_flash_visgroup': self.__flashVisGroup,
            'le_new_visgroup': self.__newVisGroup,

        }

        for js, py in binds.items():
            self.htmlUi.set_js_function(js, py)

    def popupError(self, message: str):
        self.htmlUi.exec_js_func('show_error_popup', message)

    def __toggleInputFocus(self, state: bool):
        if state:
            self.levelEditor.disallowInput()
        else:
            self.levelEditor.allowInput()

    def __toggleMouseEvents(self, state: bool):
        self.levelEditor.toggleMouseInputs(state)

    ''' Save / Load events'''

    def __exportToBam(self):
        """
        Export level geometry as .bam
        """
        path = Filename.expandFrom(userfiles).toOsSpecific()
        if not os.path.isdir(path):
            path = '.'
        fileName = asksaveasfilename(defaultextension = '.dna',
                                     filetypes = (('Panda3D Model Files', '*.bam'), ('All files', '*')),
                                     initialdir = path,
                                     title = 'Export as .BAM')
        if fileName:
            self.levelEditor.getNPToplevel().findAllMatches('**/+CollisionNode').stash()
            self.levelEditor.getNPToplevel().writeBamFile(Filename.expandFrom(fileName))
            self.levelEditor.getNPToplevel().findAllMatches('**/+CollisionNode').unstash()

            self.popupError(f'Exported level as {fileName}')
        else:
            self.popupError('Export cancelled.')

    ''' Spawn Events '''

    def __spawnStreet(self, code: str):
        if code == '':
            self.popupError("Unable to spawn street module!<br/>You must select a module before spawning.")
            return
        self.levelEditor.addStreet(code)

    def __spawnProp(self, code: str):
        if code == '':
            self.popupError("Unable to spawn prop!<br/>You must select a prop before spawning.")
            return
        self.levelEditor.addProp(code)

    def __spawnLandmark(self, code: str, extraType: str, isSz: bool, bldgName: str):
        if code == '':
            self.popupError("Unable to spawn building!<br/>You must select a building model before spawning.")
            return
        self.levelEditor.addLandmark('toon_landmark_' + code, extraType, bldgName, isSz)

    def __spawnInteractiveProp(self, code: str):
        if code == '':
            self.popupError("Unable to spawn interactive prop!<br/>You must select a prop type before spawning.")
            return
        self.levelEditor.addInteractiveProp(code)

    ''' Edit Events '''

    def selectLandmark(self, title: str):
        self.htmlUi.exec_js_func('select_landmark', title)

    def __renameLandmark(self, title: str):
        self.levelEditor.renameLandmark(title)

    def deselectLandmark(self):
        self.htmlUi.exec_js_func('deselect_landmark')

    ''' Visgroups '''

    def __selectVisGroup(self, visGroup: str):
        if visGroup == '':
            self.popupError('Select a Vis Group in the list first!')
            return
        visNP: Optional[NodePath] = self.visNumToNP.get(visGroup, None)
        if not visNP:
            self.popupError(f'Error selecting Vis Group.<br/><b>{visGroup}</b> not in dict.')
            return
        messenger.send('SGE_Set Reparent Target', [visNP])
        messenger.send('SGE_Flash', [visNP])

        visNP: DNAVisGroup = self.levelEditor.findDNANode(visNP)
        self.repopulateVisgroupVisiblesList(visNP)

    def __flashVisGroup(self, visGroup: str):
        visNP: Optional[NodePath] = self.visNumToNP.get(visGroup, None)
        if not visNP:
            self.popupError(f'Error selecting Vis Group.<br/><b>{visGroup}</b> not in dict.')
            return
        messenger.send('SGE_Flash', [visNP])

    def __newVisGroup(self, visName: str):
        if visName == '':
            self.popupError('Unable to create Vis Group!<br/>You must set an ID for the Vis Group!')
            return
        self.levelEditor.newVisGroup(visName)
        self.repopulateVisgroupList()

    def repopulateVisgroupList(self):
        vis = self.levelEditor.getDNAVisGroups(self.levelEditor.NPToplevel)
        self.visNumToNP = {}
        for group in vis:
            self.visNumToNP[group[1].getName()] = group[0]
        # vis
        visNames = [x[1].getName() for x in vis]
        visNames.sort()
        if len(visNames) != 0:
            lastVisNum = int(visNames[-1])
            self.htmlUi.exec_js_func('set_new_visgroup_id', lastVisNum + 1)

        self.htmlUi.exec_js_func('populate_visgroup_list', visNames)

    def repopulateVisgroupVisiblesList(self, visGroup: DNAVisGroup):
        visState: Dict[str, bool] = {}
        for vis in self.visNumToNP:
            visState[vis] = False
        for i in range(visGroup.getNumVisibles()):
            name = visGroup.getVisibleName(i)
            if name in visState:
                visState[name] = True

        asList: List[Tuple[str, bool]] = [(k, v) for k, v in visState.items()]
        asList.sort()
        self.htmlUi.exec_js_func('populate_visgroup_visibles_list', asList)
