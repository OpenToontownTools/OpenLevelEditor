# LandmarkPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

from toontown.leveleditor import LevelEditorGlobals
from toontown.panels.PropPreviewPanel import PropPreviewPanel

class LandmarkPanel(DirectObject):

    def __init__(self, editor, preview: PropPreviewPanel):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.preview: PropPreviewPanel = preview
        self.selectedProp = ""
        self.selectedSpecial = ""
        self.buildingName = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        imgui.dummy((avail_w / 5, 0)) ; imgui.same_line()
        self.preview.draw()
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
                    self.preview.previewLandmark(self.selectedProp, self.selectedSpecial)
            imgui.end_list_box()
