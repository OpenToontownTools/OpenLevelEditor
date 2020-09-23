""" ToontownLevelEditor 2.0 Base Class  - Drewcification 091420 """

import asyncio
import argparse
import builtins
import webbrowser
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, loadPrcFileData
from tkinter import Tk, messagebox

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
        parser.add_argument("--clash", action='store_true', help="Enables Corporate Clash features")
        parser.add_argument("--noupdate", action='store_true', help="Disables Auto Updating")
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

        
        tkroot = Tk()
        tkroot.withdraw()
        tkroot.title("Open Level Editor")
        #tkroot.iconbitmap("resources/icon.ico")
        self.tkRoot = tkroot
        
        if not args.noupdate:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.checkUpdates())

        # Now we actually start the editor
        ShowBase.__init__(self)
        from toontown.leveleditor import LevelEditor
        self.le = LevelEditor.LevelEditor()

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
