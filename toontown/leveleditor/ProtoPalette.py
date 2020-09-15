"""
Palette for Prototyping
"""

from direct.leveleditor.ProtoPaletteBase import *
import os

class ProtoPalette(ProtoPaletteBase):
    def __init__(self):
        self.dirname = os.path.dirname(__file__)
        ProtoPaletteBase.__init__(self)
