# LandmarkPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui_ctx
from imgui_bundle._imgui_bundle import imgui
from imgui_bundle.demos_python.demos_immvision.demo_immvision_no_opencv import ImVec2

from toontown.leveleditor import LevelEditorGlobals


class LandmarkPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.selectedProp = ""
        self.selectedSpecial = ""
        self.buildingName = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        if imgui.button("Place", ImVec2(avail_w, 0)):
            self.levelEditor.addLandmark(self.selectedProp, self.selectedSpecial)

        imgui.separator_text("Bldg Type")
        if imgui.begin_combo("##lmType", "generic"):
            for _type in LevelEditorGlobals.LANDMARK_SPECIAL_TYPES:
                imgui.selectable(_type if _type != "" else "generic", False)
            imgui.end_combo()
        imgui.separator_text("Select Prop")
        avail_w, avail_h = imgui.get_content_region_avail()

        if imgui.begin_list_box("##lmSelectionBox", ImVec2(avail_w, avail_h)):
            for prop in self.levelEditor.styleManager.getCatalogCodes('toon_landmark'):
                isSelected = self.selectedProp == prop
                clicked, _ = imgui.selectable(prop, isSelected)
                if clicked:
                    self.selectedProp = prop
            imgui.end_list_box()