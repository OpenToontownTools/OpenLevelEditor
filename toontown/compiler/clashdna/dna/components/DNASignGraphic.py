from .DNANode import DNANode
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNASignGraphic(DNANode):
    COMPONENT_CODE = 8

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.code = ''
        self.color = (1, 1, 1, 1)
        self.width = 0
        self.height = 0
        self.bDefaultColor = True

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color
        self.bDefaultColor = False

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASignGraphic'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('color', *self.color)
        packer.pack('width', int(self.width * 100), INT16)
        packer.pack('height', int(self.height * 100), INT16)
        packer.pack('bDefaultColor', self.bDefaultColor, BOOLEAN)
        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
