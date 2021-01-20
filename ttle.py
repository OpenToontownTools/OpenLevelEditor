""" OpenLevelEditor Base Class - Drewcification 091420 """

import argparse
import asyncio
import builtins
import os
import pathlib
import sys
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, loadPrcFileData
from tkinter import Tk, messagebox

from ott.Settings import Settings
from toontown.toonbase import ToontownGlobals

TOONTOWN_ONLINE = 0
TOONTOWN_REWRITTEN = 1
TOONTOWN_CORPORATE_CLASH = 2
TOONTOWN_OFFLINE = 3

SERVER_TO_ID = {'online':    TOONTOWN_ONLINE,
                'rewritten': TOONTOWN_REWRITTEN,
                'clash':     TOONTOWN_CORPORATE_CLASH,
                'offline':   TOONTOWN_OFFLINE
                }

DEFAULT_SERVER = TOONTOWN_ONLINE

DEFAULT_SETTINGS = {
    'autosave-enabled':   True,
    'autosave-interval':  15,
    'autosave-max-files': 10,
    'fps-meter-update-rate': 0
    }

class ToontownLevelEditor(ShowBase):
    notify = directNotify.newCategory("Open Level Editor")
    APP_VERSION = open('ver', 'r').read()

    def __init__(self):

        # Load the prc file prior to launching showbase in order
        # to have it affect window related stuff
        loadPrcFile('editor.prc')

        builtins.userfiles = self.config.GetString('userfiles-directory')

        if not os.path.exists(userfiles):
            pathlib.Path(userfiles).mkdir(parents = True, exist_ok = True)

        builtins.settings = Settings(f'{userfiles}/settings.json')

        for setting in DEFAULT_SETTINGS:
            if setting not in settings:
                settings[setting] = DEFAULT_SETTINGS[setting]

        # Check for -e or -d launch options
        parser = argparse.ArgumentParser(description = "Modes")
        parser.add_argument("--experimental", action = 'store_true', help = "Enables experimental features")
        parser.add_argument("--debug", action = 'store_true', help = "Enables debugging features")
        parser.add_argument("--noupdate", action = 'store_true', help = "Disables Auto Updating")
        parser.add_argument("--png", action = 'store_true', help = "Forces PNG resources mode, if this is not "
                                                                   "specified, it will automatically determine the "
                                                                   "format")
        parser.add_argument("--compiler", nargs = "*",
                            help = "Specify which compiler to use (Only useful if your game uses a form of "
                                   "libpandadna.) Valid options are 'libpandadna', for games which use the "
                                   "modern c++ version of libpandadna, and 'clash', for Corporate Clash")

        parser.add_argument("--server", nargs = "*", help = "Enables features exclusive to various Toontown projects",
                            default = 'online')
        parser.add_argument("--holiday", nargs = "*", help = "Enables holiday modes. [halloween or winter]")
        parser.add_argument("--hoods", nargs = "*", help = "Only loads the storage files of the specified hoods",
                            default = ['TT', 'DD', 'BR', 'DG',
                                       'DL', 'MM', 'GS', 'GZ',
                                       'SBHQ', 'LBHQ', 'CBHQ', 'BBHQ',
                                       'OZ', 'PA', 'ES', 'TUT'])
        parser.add_argument("dnaPath", nargs = "?", help = "Load the DNA file through the specified path")

        args = parser.parse_args()
        if args.experimental:
            loadPrcFileData("", "want-experimental true")
        if args.debug:
            loadPrcFileData("", "want-debug true")
        if args.compiler:
            loadPrcFileData("", f"compiler {args.compiler[0]}")
        if args.holiday:
            loadPrcFileData("", f"holiday {args.holiday[0]}")
        if args.png:
            loadPrcFileData("", "png-textures true")
        else:
            # If we don't specify png, we can search
            # we can use the eyes texture
            if os.path.exists("phase_3/maps/eyes.jpg"):
                loadPrcFileData("", "png-textures false")
            elif os.path.exists("phase_3/maps/eyes.png"):
                loadPrcFileData("", "png-textures true")
            else:
                messagebox.showerror(
                    message = "There was an error located resources!\n"
                              "Make sure you put the phase folders in the root folder!")

        server = SERVER_TO_ID.get(args.server[0].lower(), DEFAULT_SERVER)
        self.server = server

        self.hoods = args.hoods
        # HACK: Check for dnaPath in args.hoods
        for hood in self.hoods[:]:
            if hood.endswith('.dna'):
                args.dnaPath = hood
                args.hoods.remove(hood)
                break

        # Check for any files we need and such
        self.__checkForFiles()

        # Import the main dlls so we don't have to repeatedly import them everywhere
        self.__importMainLibs()

        # Setup the root for Tkinter!
        self.__createTk()

        if not args.noupdate:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.__checkUpdates())

        self.__addCullBins()

        # Now we actually start the editor
        ShowBase.__init__(self)
        aspect2d.setAntialias(AntialiasAttrib.MAuto)

        # Create the framerate meter
        flag = self.config.GetBool('show-frame-rate-meter', False)
        if flag:
            self.toggleFrameRateMeter(flag)

        from toontown.leveleditor import LevelEditor
        self.le = LevelEditor.LevelEditor()
        self.le.startUp(args.dnaPath)

    def setFrameRateMeter(self, flag):
        return

    def toggleFrameRateMeter(self, flag):
        if flag:
            if not self.frameRateMeter:
                self.frameRateMeter = OnscreenText(parent = base.a2dTopRight, text = '', pos = (-0.01, -0.05, 0.0),
                                                   scale = 0.05, style = 3, bg = (0, 0, 0, 0.4), align = TextNode.ARight,
                                                   font = ToontownGlobals.getToonFont())
                taskMgr.add(self.updateFrameRateMeter, 'fps')
        else:
            if self.frameRateMeter:
                self.frameRateMeter.destroy()
                self.frameRateMeter = None

    def updateFrameRateMeter(self, task):
        """
        Base code inspired from
        https://discourse.panda3d.org/t/trying-to-create-custom-fps-counter/25328/15
        """
        fps = globalClock.getAverageFrameRate()

        if fps <= 45:
            # At or below 45 fps is yellow
            color = (1, 0.9, 0, 1)
        elif fps <= 30:
            # At or below 30 fps is red
            color = (1, 0, 0, 1)
        else:
            # Color is green by default
            color = (0, 0.9, 0, 1)

        text = f'{round(fps, 1)} FPS'
        self.frameRateMeter.setText(text)
        self.frameRateMeter.setFg(color)
        task.delayTime = settings['fps-meter-update-rate']/1000
        return task.again

    def __checkForFiles(self):
        # Make custom hood directory if it doesn't exist
        if not os.path.exists(f'{userfiles}/hoods/'):
            os.mkdir(f'{userfiles}/hoods/')
        # Make a maps directory if we don't have one
        if not os.path.isdir("maps"):
            os.mkdir("maps")
        # Make a Screenshots directory if we don't have one
        if not os.path.isdir("screenshots"):
            os.mkdir("screenshots")

    def __importMainLibs(self):
        builtin_dict = builtins.__dict__
        builtin_dict.update(__import__('panda3d.core', fromlist = ['*']).__dict__)
        builtin_dict.update(__import__('libotp', fromlist = ['*']).__dict__)
        builtin_dict.update(__import__('libtoontown', fromlist = ['*']).__dict__)

    def __createTk(self):
        tkroot = Tk()
        tkroot.withdraw()
        tkroot.title("Open Level Editor")
        if sys.platform == 'win32':
            # FIXME: This doesn't work in other platforms for some reason...
            tkroot.iconbitmap("resources/openttle_ico_temp.ico")

        self.tkRoot = tkroot

    @staticmethod
    def __addCullBins():
        cbm = CullBinManager.getGlobalPtr()
        cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
        cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)

    async def __checkUpdates(self):
        import aiohttp, webbrowser
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                        "https://raw.githubusercontent.com/OpenToontownTools/OpenLevelEditor/master/ver") as resp:
                    ver = await resp.text()
                    ver = ver.splitlines()[0]
                    if ver != self.APP_VERSION:
                        self.notify.info(f"Client is out of date! Latest: {ver} | Client: {self.APP_VERSION}")
                        if messagebox.askokcancel("Error",
                                                  f"Client is out of date!\nLatest: {ver} | Client: {self.APP_VERSION}. "
                                                  f"Press OK to be taken to the download page."):
                            webbrowser.open("https://github.com/OpenToontownTools/OpenLevelEditor/releases/latest")
                    else:
                        self.notify.info("Client is up to date!")
            except:
                messagebox.showerror(
                    message = "There was an error checking for updates! This is likely an issue with your connection. "
                              "Press OK to continue using the application.")


# Run it
ToontownLevelEditor().run()
