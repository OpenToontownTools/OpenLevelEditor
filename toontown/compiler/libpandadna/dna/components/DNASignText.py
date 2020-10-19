from toontown.compiler.libpandadna.dna.components.DNANode import DNANode
from toontown.compiler.libpandadna.dna.base.DNAPacker import *


class DNASignText(DNANode):
    COMPONENT_CODE = 7

    def __init__(self):
        DNANode.__init__(self, '')

        self.code = ''
        self.color = (1, 1, 1, 1)
        self.letters = ''

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def setLetters(self, letters):
        self.letters = letters

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASignText'  # Override the name for debugging.
        packer.pack('sign text letters', self.letters, STRING)
        packer.pack('sign text code', self.code, STRING)
        packer.packColor('sign text color', *self.color)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
