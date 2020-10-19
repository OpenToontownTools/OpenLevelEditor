from .DNANode import DNANode
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNAWall(DNANode):
    COMPONENT_CODE = 10

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.code = ''
        self.height = 10
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def setHeight(self, height):
        self.height = height

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAWall'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.pack('height', int(self.height * 100), INT16)
        packer.packColor('color', *self.color)
        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
