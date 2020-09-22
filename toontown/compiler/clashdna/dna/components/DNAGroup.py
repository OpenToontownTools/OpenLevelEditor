from dna.base.DNAPacker import *


class DNAGroup:
    COMPONENT_CODE = 1

    def __init__(self, name):
        self.name = name
        self.children = []
        self.parent = None
        self.visGroup = None

    def setName(self, name):
        self.name = name

    def add(self, child):
        self.children.append(child)

    def setVisGroup(self, visGroup):
        self.visGroup = visGroup

    def getVisGroup(self):
        return self.visGroup

    def setParent(self, parent):
        self.parent = parent
        self.visGroup = parent.getVisGroup()

    def getParent(self):
        return self.parent

    def clearParent(self):
        self.parent = None
        self.visGroup = None

    def traverse(self, recursive=True, verbose=False):
        packer = DNAPacker(name='DNAGroup', verbose=verbose)

        packer.pack('component code', self.COMPONENT_CODE, UINT8)
        packer.pack('name', self.name, STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer

    def traverseChildren(self, verbose=False):
        packer = DNAPacker(verbose=verbose)
        for child in self.children:
            packer += child.traverse(recursive=True, verbose=verbose)

        packer.pack('increment parent', 255, UINT8)
        return packer
