from toontown.compiler.clashdna.dna.components.DNAGroup import DNAGroup
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNANode(DNAGroup):
    COMPONENT_CODE = 3

    def __init__(self, name):
        DNAGroup.__init__(self, name)
        self.pos = (0, 0, 0)
        self.hpr = (0, 0, 0)
        self.scale = (1, 1, 1)

    def setPos(self, pos):
        self.pos = pos

    def setHpr(self, hpr):
        self.hpr = hpr

    def setScale(self, scale):
        self.scale = scale

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNANode'  # Override the name for debugging.
        for component in self.pos:
            packer.pack('position', int(component * 100), FLOAT64)
        for component in self.hpr:
            packer.pack('rotation', int(component * 100), FLOAT64)
        for component in self.scale:
            packer.pack('scale', int(component * 100), UINT16)
        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
