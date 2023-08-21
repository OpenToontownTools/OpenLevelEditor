from typing import Dict, Callable

from toontown.leveleditor import LevelEditorGlobals
from toontown.toonbase.CEFPanda import CEFPanda


class CEFLevelEditorPanel:
    def __init__(self, levelEditor):
        self.levelEditor = levelEditor

        self.htmlUi = CEFPanda()
        self.htmlUi.load_file('resources/ui/ui.html')

    def setupLists(self):
        # streets
        self.htmlUi.exec_js_func('populate_list', 'street-module-list', [s for s in self.levelEditor.styleManager.getCatalogCodes('street')])

        # static props
        propList = self.levelEditor.styleManager.getCatalogCodes('prop') + self.levelEditor.styleManager.getCatalogCodes('holiday_prop')
        # make it alphabetical
        propList.sort()
        self.htmlUi.exec_js_func('populate_list', 'prop-list', propList)
        del propList

        # Landmark buildings
        landmarks = [s[14:] for s in self.levelEditor.styleManager.getCatalogCodes('toon_landmark')]
        landmarks.sort()
        self.htmlUi.exec_js_func('populate_list', 'landmark-list', landmarks)
        del landmarks

        # Landmark building types
        self.htmlUi.exec_js_func('populate_list', 'landmark-type-list', LevelEditorGlobals.LANDMARK_SPECIAL_TYPES[1:])

    def bindFunctions(self):
        """
        Binds functions called from the javascript to their python counterparts
        """
        binds: Dict[str, Callable] = {
            # generic events
            'le_set_input_focus': self.__toggleInputFocus,
            'le_set_mouse_events': self.__toggleMouseEvents,

            # spawn events
            'le_spawn_street': self.__spawnStreet,
            'le_spawn_prop': self.__spawnProp,
            'le_spawn_landmark': self.__spawnLandmark,

            # edit events
            'le_rename_landmark': self.__renameLandmark

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
        print(f"Requested landmark spawn: \n"
              f"    Code {code}\n"
              f"    Type {extraType}\n"
              f"    is Safezone {isSz}\n"
              f"    name '{bldgName}'")

        self.levelEditor.addLandmark('toon_landmark_'+code, extraType, bldgName, isSz)

    def selectLandmark(self, title: str):
        self.htmlUi.exec_js_func('select_landmark', title)

    def __renameLandmark(self, title: str):
        self.levelEditor.renameLandmark(title)

    def deselectLandmark(self):
        self.htmlUi.exec_js_func('deselect_landmark')
