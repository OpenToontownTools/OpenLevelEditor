from toontown.compiler.libpandadna.dna.components import DNALandmarkBuilding
from toontown.compiler.libpandadna.dna.base.DNAPacker import *


class DNAAnimBuilding(DNALandmarkBuilding.DNALandmarkBuilding):
    COMPONENT_CODE = 16

    def __init__(self, name):
        DNALandmarkBuilding.DNALandmarkBuilding.__init__(self, name)

        self.animName = ''

    def setAnim(self, anim):
        self.animName = anim

    def traverse(self, recursive=True, verbose=False):
        packer = DNALandmarkBuilding.DNALandmarkBuilding.traverse(
            self, recursive=False, verbose=verbose)
        packer.name = 'DNAAnimBuilding'  # Override the name for debugging.

        packer.pack('anim name', self.animName, STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
