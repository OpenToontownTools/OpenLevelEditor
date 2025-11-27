# ElementsPanel
# Created by drewc Nov 25, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, imgui_ctx

from toontown.panels.FlatBuildingPanel import FlatBuildingPanel
from toontown.panels.LandmarkPanel import LandmarkPanel
from toontown.panels.PropSelectionPanel import PropSelectionPanel
from toontown.panels.StreetSelectionPanel import StreetSelectionPanel
from toontown.panels.PropPreviewPanel import PropPreviewPanel


class ElementsPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.isOpen = True
        self.previewPanel = PropPreviewPanel(editor)
        self.streetPanel = StreetSelectionPanel(editor, self.previewPanel)
        self.propPanel = PropSelectionPanel(editor, self.previewPanel)
        self.flatBuildingPanel = FlatBuildingPanel(editor)
        self.landmarkPanel = LandmarkPanel(editor, self.previewPanel)


    def draw(self):
        if not self.isOpen:
            return
        with imgui_ctx.begin("Elements"):  # the panel containing your tabs

            if imgui.begin_tab_bar("##tabs"):

                # Streets Tab
                if imgui.begin_tab_item("Streets")[0]:
                    self.streetPanel.draw()

                    imgui.end_tab_item()

                if imgui.begin_tab_item("Flat Bldgs")[0]:
                    self.flatBuildingPanel.draw()
                    imgui.end_tab_item()

                if imgui.begin_tab_item("Landmark Bldgs")[0]:
                    self.landmarkPanel.draw()
                    imgui.end_tab_item()

                # Props Tab
                if imgui.begin_tab_item("Props")[0]:
                    self.propPanel.draw()

                    imgui.end_tab_item()

                imgui.end_tab_bar()
