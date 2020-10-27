""" ToontownLevelEditor 2.0 Base Class  - Drewcification 091420 """

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.ShowBase import ShowBase

from panda3d.core import loadPrcFile, loadPrcFileData

from tkinter import Tk, messagebox

import asyncio
import argparse
import builtins
import json
import os
import sys
import webbrowser

TOONTOWN_ONLINE = 0
TOONTOWN_REWRITTEN = 1
TOONTOWN_CORPORATE_CLASH = 2
TOONTOWN_OFFLINE = 3

SERVER_TO_ID = {'online': TOONTOWN_ONLINE,
                'rewritten': TOONTOWN_REWRITTEN,
                'clash': TOONTOWN_CORPORATE_CLASH,
                'offline': TOONTOWN_OFFLINE}

# Make custom hood directory if it doesn't exist
if not os.path.exists('leveleditor/hoods/'):
    os.mkdir('leveleditor/hoods/')

class ToontownLevelEditor(ShowBase):
    notify = directNotify.newCategory("Open Level Editor")
    APP_VERSION = open('ver', 'r').read()

    def __init__(self):

        # Load the prc file prior to launching showbase in order
        # to have it affect window related stuff
        loadPrcFile('editor.prc')

        # Check for -e or -d launch options
        parser = argparse.ArgumentParser(description="Modes")
        parser.add_argument("--experimental", action='store_true', help="Enables experimental features")
        parser.add_argument("--debug", action='store_true', help="Enables debugging features")
        parser.add_argument("--noupdate", action='store_true', help="Disables Auto Updating")
        parser.add_argument("--compiler", nargs = "*", help="Specify which compiler to use (Only useful if your game uses a form of "
                                                            "libpandadna.) Valid options are 'libpandadna', for games which use the "
                                                            "modern c++ version of libpandadna (like Toontown Offline), and 'clash', "
                                                            "for games that use the legacy python version of libpandadna, mainly Corporate Clash")

        parser.add_argument("--server", nargs="*", help="Enables features exclusive to various Toontown projects", default='online')
        parser.add_argument("--holiday", nargs="*", help="Enables holiday modes. [halloween or winter]")
        parser.add_argument("--hoods", nargs="*", help="Only loads the storage files of the specified hoods",
                            default=['TT', 'DD', 'BR', 'DG',
                                     'DL', 'MM', 'GS', 'GZ',
                                     'SBHQ', 'LBHQ', 'CBHQ', 'BBHQ',
                                     'OZ', 'PA', 'ES', 'TUT'])
        parser.add_argument("dnaPath", nargs="?", help="Load the DNA file through the specified path")

        args = parser.parse_args()
        if args.experimental:
            loadPrcFileData("", "want-experimental true")
        if args.debug:
            loadPrcFileData("", "want-debug true")
        if args.compiler:
            loadPrcFileData("", f"compiler {args.compiler[0]}")
        if args.holiday:
            loadPrcFileData("", f"holiday {args.holiday[0]}")


        server = SERVER_TO_ID.get(args.server[0].lower(), TOONTOWN_ONLINE)
        self.server = server

        self.hoods = args.hoods
        # HACK: Check for dnaPath in args.hoods
        for hood in self.hoods[:]:
            if hood.endswith('.dna'):
                args.dnaPath = hood
                args.hoods.remove(hood)
                break

        # Import the main dlls so we don't have to repeatedly import them everywhere
        builtins.__dict__.update(__import__('panda3d.core', fromlist=['*']).__dict__)
        builtins.__dict__.update(__import__('libotp', fromlist=['*']).__dict__)
        builtins.__dict__.update(__import__('libtoontown', fromlist=['*']).__dict__)

        tkroot = Tk()
        tkroot.withdraw()
        tkroot.title("Open Level Editor")
        if sys.platform == 'win32':
            # FIXME: This doesn't work in other platforms for some reason...
            tkroot.iconbitmap("resources/openttle_ico_temp.ico")

        self.tkRoot = tkroot

        if not args.noupdate:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.checkUpdates())

        # Now we actually start the editor
        ShowBase.__init__(self)
        aspect2d.setAntialias(AntialiasAttrib.MAuto)
        from toontown.leveleditor import LevelEditor
        self.le = LevelEditor.LevelEditor()
        self.le.startUp(args.dnaPath)

    async def checkUpdates(self):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://raw.githubusercontent.com/OpenToontownTools/TTOpenLevelEditor/master/ver") as resp:
                ver = await resp.text()
                ver = ver.splitlines()[0]
                if ver != self.APP_VERSION:
                    self.notify.info(f"Client is out of date! Latest: {ver} | Client: {self.APP_VERSION}")
                    if messagebox.askokcancel("Error", f"Client is out of date!\nLatest: {ver} | Client: {self.APP_VERSION}. Press OK to be taken to the download page."):
                        webbrowser.open("https://github.com/OpenToontownTools/TTOpenLevelEditor/releases/latest")
                else:
                    self.notify.info("Client is up to date!")

# Run it
ToontownLevelEditor().run()
