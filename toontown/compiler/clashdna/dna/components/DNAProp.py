from toontown.compiler.clashdna.dna.components.DNANode import DNANode
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNAProp(DNANode):
    COMPONENT_CODE = 4

    def __init__(self, name):
        DNANode.__init__(self, name)
        self.code = ''
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAProp'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('color', *self.color)
        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
