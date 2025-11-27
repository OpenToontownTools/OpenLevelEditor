# FlatBuildingPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

class FlatBuildingPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.selectedProp = ""

    def draw(self):
        avail_w, avail_h = imgui.get_content_region_avail()

        imgui.separator_text("Common Sizes")
        if imgui.button("Place 10ft (Fences)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 10)
            self.levelEditor.addFlatBuilding('random')

        if imgui.button("Place 20ft (Normal)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 20)
            self.levelEditor.addFlatBuilding('random')

        if imgui.button("Place 30ft (Tall)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 30)
            self.levelEditor.addFlatBuilding('random')


        imgui.separator_text("With Foundations")
        if imgui.button("Place 14ft (Fence w/ Foundation)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 14)
            self.levelEditor.addFlatBuilding('random')

        if imgui.button("Place 24ft (Normal w/ Foundation)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 24)
            self.levelEditor.addFlatBuilding('random')

        if imgui.button("Place 25ft (Slightly Taller w/ Shorter Foundation)", ImVec2(avail_w, 0)):
            self.levelEditor.setCurrent('building_height', 25)
            self.levelEditor.addFlatBuilding('random')
