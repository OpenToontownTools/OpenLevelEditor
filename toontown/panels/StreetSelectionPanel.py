# StreetSelectionPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

class StreetSelectionPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.selectedStreet = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        if imgui.button("Place", ImVec2(avail_w, 0)):
            self.levelEditor.addStreet(self.selectedStreet)

        imgui.separator_text("Select Prop")
        avail_w, avail_h = imgui.get_content_region_avail()

        if imgui.begin_list_box("##streetSelectionBox", ImVec2(avail_w, avail_h)):
            for street in self.levelEditor.styleManager.getCatalogCodes('street'):
                isSelected = self.selectedStreet == street
                clicked, _ = imgui.selectable(street, isSelected)
                if clicked:
                    self.selectedStreet = street
            imgui.end_list_box()
