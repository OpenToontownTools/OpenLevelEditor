from .DNAGroup import DNAGroup
from toontown.compiler.clashdna.dna.base.DNAPacker import *


class DNAVisGroup(DNAGroup):
    COMPONENT_CODE = 2

    def __init__(self, name):
        DNAGroup.__init__(self, name)

        self.visibles = []
        self.suitEdges = []
        self.battleCells = []

    def getVisGroup(self):
        return self

    def addVisible(self, visible):
        self.visibles.append(visible)

    def addSuitEdge(self, suitEdge):
        self.suitEdges.append(suitEdge)

    def addBattleCell(self, battleCell):
        self.battleCells.append(battleCell)

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAVisGroup'  # Override the name for debugging.
        packer.pack('suit edge count', len(self.suitEdges), UINT16)
        for edge in self.suitEdges:
            startPointIndex = edge.startPoint.index
            packer.pack('start point index', startPointIndex, UINT16)
            endPointIndex = edge.endPoint.index
            packer.pack('end point index', endPointIndex, UINT16)
        packer.pack('visible count', len(self.visibles), UINT16)
        for visible in self.visibles:
            packer.pack('visible', visible, STRING)
        packer.pack('battle cell count', len(self.battleCells), UINT16)
        for cell in self.battleCells:
            packer.pack('width', cell.width, UINT8)
            packer.pack('height', cell.height, UINT8)
            for component in cell.pos:
                packer.pack('position', int(component * 100), FLOAT64)
        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
