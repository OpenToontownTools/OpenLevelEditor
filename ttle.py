""" ToontownLevelEditor 2.0 Base Class  - Drewcification 091420 """
from direct.showbase.ShowBase import ShowBase
import builtins
import argparse
from panda3d.core import loadPrcFile, loadPrcFileData


class ToontownLevelEditor(ShowBase):
    def __init__(self):
        # Check for -e or -d launch options
        ShowBase.__init__(self)
        parser = argparse.ArgumentParser(description="Modes")
        parser.add_argument("--experimental", action='store_true', help="Enables experimental features")
        parser.add_argument("--debug", action='store_true', help="Enables debugging features")
        parser.add_argument("--clash", action='store_true', help="Enables Corporate Clash features")
        parser.add_argument("--hoods", nargs="*", help="Only loads the storage files of the specified hoods",
                            default=['TT', 'DD', 'BR', 'DG',
                                     'DL', 'MM', 'CC', 'CL',
                                     'CM', 'CS', 'GS', 'GZ',
                                     'OZ', 'PA', 'ES', 'TUT'])
        args = parser.parse_args()
        if args.experimental:
            loadPrcFileData("", "want-experimental true")
        if args.debug:
            loadPrcFileData("", "want-debug true")
        if args.clash:
            loadPrcFileData("", "want-clash-specific-options true")
        self.hoods = args.hoods

        # Import the main dlls so we don't have to repeatedly import them everywhere
        builtins.__dict__.update(__import__('panda3d.core', fromlist=['*']).__dict__)
        builtins.__dict__.update(__import__('libotp', fromlist=['*']).__dict__)
        builtins.__dict__.update(__import__('libtoontown', fromlist=['*']).__dict__)

        # Load the prc file
        loadPrcFile('editor.prc')

        # Now we actually start the editor
        from toontown.leveleditor import LevelEditor
        self.le = LevelEditor.LevelEditor()


ToontownLevelEditor().run()
