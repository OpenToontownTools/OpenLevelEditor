# InteractivePropPanel
# Created by drewc Nov 27, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

from toontown.panels.PropPreviewPanel import PropPreviewPanel

class InteractivePropPanel(DirectObject):

    def __init__(self, editor, preview: PropPreviewPanel):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.selectedProp = ""
        self.preview: PropPreviewPanel = preview

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()
        imgui.dummy((avail_w / 5, 0)) ; imgui.same_line()
        self.preview.draw()
        if imgui.button("Place", ImVec2(avail_w, 0)):
            self.levelEditor.addInteractiveProp(self.selectedProp)

        imgui.separator_text("Select Prop")
        avail_w, avail_h = imgui.get_content_region_avail()

        if imgui.begin_list_box("##interSelectionBox", ImVec2(avail_w, avail_h)):
            for prop in self.levelEditor.styleManager.getCatalogCodes('interactive_prop'):
                isSelected = self.selectedProp == prop
                clicked, _ = imgui.selectable(prop, isSelected)
                if clicked:
                    self.selectedProp = prop
                    self.preview.previewProp(prop)
            imgui.end_list_box()
