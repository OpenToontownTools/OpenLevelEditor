from toontown.compiler.libpandadna.dna.components.DNAGroup import DNAGroup
from toontown.compiler.libpandadna.dna.base.DNAPacker import *


class DNACornice(DNAGroup):
    COMPONENT_CODE = 12

    def __init__(self, name):
        DNAGroup.__init__(self, name)
        self.code = ''
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNACornice'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('color', *self.color)

        return packer
