import math
import sys
from toontown.compiler.clashdna.dna.base.DNAPacker import *
from .DNANode import DNANode


class DNASignBaseline(DNANode):
    COMPONENT_CODE = 6

    def __init__(self):
        DNANode.__init__(self, '')

        self.code = ''
        self.color = (1, 1, 1, 1)
        self.flags = ''
        self.indent = 0.0
        self.kern = 0.0
        self.wiggle = 0.0
        self.stumble = 0.0
        self.stomp = 0.0
        self.width = 0.0
        self.height = 0.0

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def setHeight(self, height):
        self.height = height

    def setIndent(self, indent):
        self.indent = indent

    def setKern(self, kern):
        self.kern = kern

    def setStomp(self, stomp):
        self.stomp = stomp

    def setStumble(self, stumble):
        self.stumble = stumble

    def setWiggle(self, wiggle):
        self.wiggle = wiggle

    def setWidth(self, width):
        self.width = width

    def setFlags(self, flags):
        self.flags = flags

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASignBaseline'  # Override the name for debugging.

        traversed_data = DNAPacker()
        text = ''

        for child in self.children:
            if child.__class__.__name__ == 'DNASignText':
                text += child.letters
            else:
                if recursive:
                    traversed_data += child.traverse(recursive=recursive, verbose=verbose)

        packer.pack('sign node text', text, STRING)
        packer.pack('sign node code', self.code, STRING)
        packer.packColor('sign node color', *self.color)
        packer.pack('sign node flags', self.flags, STRING)
        packer.pack('sign node indent', self.indent, FLOAT32)
        packer.pack('sign node kern', self.kern, FLOAT32)
        packer.pack('sign node wiggle', self.wiggle, FLOAT32)
        packer.pack('sign node stumble', self.stumble, FLOAT32)
        packer.pack('sign node stomp', self.stomp, FLOAT32)
        packer.pack('sign node width', self.width, FLOAT32)
        packer.pack('sign node height', self.height, FLOAT32)

        if recursive:
            packer += traversed_data
            packer += b'\xFF'

        return packer
