import enum

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath, VBase3, Point3
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, ImVec2

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.leveleditor.LevelEditor import LevelEditor

class PropType(enum.Enum):
    STREET = 0
    LANDMARK = 1
    PROP = 2

class PropPreviewPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor: LevelEditor = editor

        # This is required so that ImGui won't render the texture
        # upside down. (Sure hope this doesn't break anything else...)
        loadPrcFileData('','copy-texture-inverted 1')

        self.buffer = base.win.makeTextureBuffer("PreviewBuffer", 256, 256)
        self.texture = self.buffer.getTexture()
        self.texref = base.imgui.loadTexture(self.texture)

        self.buffer.setSort(-100)

        self.camera = base.makeCamera(self.buffer)
        self.render = NodePath("PreviewRender")
        self.camera.reparentTo(self.render)
        self.nodeHolder: NodePath = self.render.attachNewNode('nodeHolder')
        self.nodeHolder.setPosHpr((0.00, 31.50, -6.15), (0.00, 0.00, 0.00))
        self.propType: PropType = PropType.STREET
        self.node: NodePath | None = None

    def cleanupRender(self):
        for node in self.render.children:
            if node in (self.camera, self.nodeHolder):
                continue
            node.removeNode()
        if self.node:
            self.node.removeNode()
            self.node = None

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

        node = newDNAStreet.traverse(self.render, DNASTORE, 1)
        node.setP(90.00)
        self.propType = PropType.STREET
        self.centerAndReparentNode(node)

    def previewProp(self, propType: str):
        self.cleanupRender()
        newDNAProp = DNAProp(f"{propType}_DNARoot")
        newDNAProp.setCode(propType)
        newDNAProp.setPos(VBase3(0))
        newDNAProp.setHpr(VBase3(0))
        node = newDNAProp.traverse(self.render, DNASTORE, 1)
        self.propType = PropType.PROP
        self.centerAndReparentNode(node)

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
       # # Headquarters do not have doors
       # if specialType not in ['hq', 'kartshop']:
       #     newDNADoor = self.levelEditor.createDoor('landmark_door')
       #     newDNALandmarkBuilding.add(newDNADoor)

        node = newDNALandmarkBuilding.traverse(self.render, DNASTORE, 1)
        self.propType = PropType.LANDMARK
        self.centerAndReparentNode(node)

    def centerAndReparentNode(self, node: NodePath):
        self.node = node
        p1, p2 = Point3(), Point3()
        self.node.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = 12 / biggest
        mid = (p1 + d / 2.0) * s
        self.node.setPos(-mid[0], -mid[1] + 1, -mid[2] + 5)
        self.node.setScale(Vec3(s))
        self.node.reparentTo(self.nodeHolder)

    def draw(self):
        if self.propType == PropType.STREET:
            self.nodeHolder.setH(0)
        else:
            self.nodeHolder.setH(self.nodeHolder, 30 * globalClock.getDt())
        imgui.image(self.texref, ImVec2(256, 256))
