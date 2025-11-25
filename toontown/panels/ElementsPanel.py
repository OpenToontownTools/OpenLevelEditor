# ElementsPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui_ctx
from imgui_bundle._imgui_bundle import imgui
from imgui_bundle.demos_python.demos_immvision.demo_immvision_no_opencv import ImVec2

from toontown.panels.PropSelectionPanel import PropSelectionPanel
from toontown.panels.StreetSelectionPanel import StreetSelectionPanel


class ElementsPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.isOpen = True
        self.streetPanel = StreetSelectionPanel(editor)
        self.propPanel = PropSelectionPanel(editor)


    def draw(self):
        if not self.isOpen:
            return
        with imgui_ctx.begin("Elements"):  # the panel containing your tabs

            if imgui.begin_tab_bar("##tabs"):

                # Streets Tab
                if imgui.begin_tab_item("Streets")[0]:
                    self.streetPanel.draw()

                    imgui.end_tab_item()

                # Props Tab
                if imgui.begin_tab_item("Props")[0]:
                    self.propPanel.draw()

                    imgui.end_tab_item()

                imgui.end_tab_bar()
