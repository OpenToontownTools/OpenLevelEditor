# StreetSelectionPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

from toontown.panels.PropPreviewPanel import PropPreviewPanel

class StreetSelectionPanel(DirectObject):

    def __init__(self, editor, preview: PropPreviewPanel):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.preview: PropPreviewPanel = preview
        self.selectedStreet = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        imgui.dummy((avail_w / 5, 0)) ; imgui.same_line()
        self.preview.draw()
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
                    self.preview.previewStreet(street)
            imgui.end_list_box()
