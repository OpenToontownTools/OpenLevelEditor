from .DNAGroup import DNAGroup
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNAWindows(DNAGroup):
    COMPONENT_CODE = 11

    def __init__(self, name):
        DNAGroup.__init__(self, name)
        self.code = ''
        self.color = (1, 1, 1, 1)
        self.windowCount = 1

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def setWindowCount(self, count):
        self.windowCount = count

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAWindows'  # Override the name for debugging.
        packer.pack('code', self.code, STRING)
        packer.packColor('color', *self.color)
        packer.pack('window count', self.windowCount, UINT8)
        return packer
