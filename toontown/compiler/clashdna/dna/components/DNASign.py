from toontown.compiler.clashdna.dna.base.DNAPacker import *
from .DNANode import DNANode


class DNASign(DNANode):
    COMPONENT_CODE = 5

    def __init__(self):
        DNANode.__init__(self, '')

        self.code = ''
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASign'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('color', *self.color)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
