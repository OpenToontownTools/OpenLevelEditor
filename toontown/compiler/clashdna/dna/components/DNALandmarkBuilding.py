from .DNANode import DNANode
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNALandmarkBuilding(DNANode):
    COMPONENT_CODE = 13

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.code = ''
        self.wallColor = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setWallColor(self, color):
        self.wallColor = color

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNALandmarkBuilding'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('wall color', *self.wallColor)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
