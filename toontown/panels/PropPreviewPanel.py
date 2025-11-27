from panda3d.core import NodePath, VBase3
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.leveleditor.LevelEditor import LevelEditor

class PropPreviewPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor: LevelEditor = editor

        self.buffer = base.win.makeTextureBuffer("PreviewBuffer", 256, 256)
        self.texture = self.buffer.getTexture()
        self.texref = base.imgui.loadTexture(self.texture)

        self.buffer.setSort(-100)

        self.camera = base.makeCamera(self.buffer)
        self.render = NodePath("PreviewRender")
        self.camera.reparentTo(self.render)

        self.node = None

    def cleanupRender(self):
        for node in self.render.children:
            if node == self.camera:
                continue
            node.removeNode()

    def previewStreet(self, streetType: str):
        self.cleanupRender()
        newDNAStreet = DNAStreet(f"{streetType}_DNARoot")
        newDNAStreet.setCode(streetType)
        newDNAStreet.setPos(VBase3(0))
        newDNAStreet.setHpr(VBase3(0))
        newDNAStreet.setStreetTexture(
                'street_street_' + self.levelEditor.neighborhoodCode.replace("TTOFF_", '') + '_tex')
        newDNAStreet.setSidewalkTexture(
                'street_sidewalk_' + self.levelEditor.neighborhoodCode.replace("TTOFF_", '') + '_tex')
        newDNAStreet.setCurbTexture(
                'street_curb_' + self.levelEditor.neighborhoodCode.replace("TTOFF_", '') + '_tex')

        self.node = newDNAStreet.traverse(self.render, DNASTORE, 1)
        self.node.setPosHpr(self.camera, (0.00, 203.10, -2.20), (1.00, 90.00, 0.00))

    def previewProp(self, propType: str):
        self.cleanupRender()
        newDNAProp = DNAProp(f"{propType}_DNARoot")
        newDNAProp.setCode(propType)
        newDNAProp.setPos(VBase3(0))
        newDNAProp.setHpr(VBase3(0))
        self.node = newDNAProp.traverse(self.render, DNASTORE, 1)
        self.node.setPosHpr((0.00, 31.50, -6.15), (0.00, 0.00, 0.00))

    def previewLandmark(self, landmarkType: str, specialType: str):
        self.cleanupRender()
        if self.node:
            self.node.removeNode()
        block = self.levelEditor.getCurrentLandmarkBlock()
        newDNALandmarkBuilding = DNALandmarkBuilding(
                f"tb{block}:{landmarkType}_DNARoot")
        newDNALandmarkBuilding.setCode(landmarkType)
        newDNALandmarkBuilding.setTitle("")
        newDNALandmarkBuilding.setBuildingType(specialType)
        newDNALandmarkBuilding.setPos(VBase3(0))
        newDNALandmarkBuilding.setHpr(VBase3(0))
        # Headquarters do not have doors
        if specialType not in ['hq', 'kartshop']:
            newDNADoor = self.levelEditor.createDoor('landmark_door')
            newDNALandmarkBuilding.add(newDNADoor)

        self.node = newDNALandmarkBuilding.traverse(self.render, DNASTORE, 1)
        self.node.setPosHpr((-13.20, 70.70, -14.95), (0.00, 0.00, 0.00))

    def draw(self):
        # Panda3D renders textures upside down, so we tell ImGui to render
        # it the same way. (uv0 : (0, 1), uv1: (1, 0))
        imgui.image(self.texref, ImVec2(256, 256), ImVec2(0, 1), ImVec2(1, 0))
