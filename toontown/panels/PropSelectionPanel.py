# PropSelectionPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui_ctx
from imgui_bundle._imgui_bundle import imgui
from imgui_bundle.demos_python.demos_immvision.demo_immvision_no_opencv import ImVec2


class PropSelectionPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.selectedProp = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        imgui.button("Place", ImVec2(avail_w, 0))

        imgui.separator_text("Select Prop")
        avail_w, avail_h = imgui.get_content_region_avail()

        if imgui.begin_list_box("##propSelectionBox", ImVec2(avail_w, avail_h)):
            for prop in self.levelEditor.styleManager.getCatalogCodes('prop'):
                isSelected = self.selectedProp == prop
                clicked, _ = imgui.selectable(prop, isSelected)
                if clicked:
                    self.selectedProp = prop
            imgui.end_list_box()