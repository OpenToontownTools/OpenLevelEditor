import DNAAnimProp
from dna.base.DNAPacker import *


class DNAInteractiveProp(DNAAnimProp.DNAAnimProp):
    COMPONENT_CODE = 15

    def __init__(self, name):
        DNAAnimProp.DNAAnimProp.__init__(self, name)

        self.cellId = -1

    def setCellId(self, cellId):
        self.cellId = cellId

    def traverse(self, recursive=True, verbose=False):
        packer = DNAAnimProp.DNAAnimProp.traverse(
            self, recursive=False, verbose=verbose)
        packer.name = 'DNAInteractiveProp'  # Override the name for debugging.

        packer.pack('cell ID', self.cellId, INT16)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
