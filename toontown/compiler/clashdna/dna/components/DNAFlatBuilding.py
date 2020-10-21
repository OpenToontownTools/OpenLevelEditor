from toontown.compiler.libpandadna.dna.components.DNANode import DNANode
from toontown.compiler.libpandadna.dna.base.DNAPacker import *


class DNAFlatBuilding(DNANode):
    COMPONENT_CODE = 9

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.width = 0
        self.hasDoor = False

    def setWidth(self, width):
        self.width = width

    def setHasDoor(self, hasDoor):
        self.hasDoor = True

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAFlatBuilding'  # Override the name for debugging.
        packer.pack('width', self.width * 10, UINT16)
        packer.pack('has door', self.hasDoor, BOOLEAN)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
