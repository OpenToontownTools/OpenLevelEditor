from toontown.compiler.libpandadna.dna.components.DNANode import DNANode
from toontown.compiler.libpandadna.dna.base.DNAPacker import *


class DNALandmarkBuilding(DNANode):
    COMPONENT_CODE = 13

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.code = ''
        self.wallColor = (1, 1, 1, 1)
        self.title = ''
        self.article = ''
        self.buildingType = ''

    def setCode(self, code):
        self.code = code

    def setWallColor(self, color):
        self.wallColor = color
    
    def setTitle(self, title):
        self.title = title
    
    def setArticle(self, article):
        self.article = article
    
    def setBuildingType(self, buildingType):
        self.buildingType = buildingType

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNALandmarkBuilding'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('wall color', *self.wallColor)
        packer.pack('title', self.title, STRING)
        packer.pack('article', self.article, STRING)
        packer.pack('building type', self.buildingType, STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
