import os
import shutil
import time
import threading
from datetime import datetime

from .DNASerializer import DNASerializer


class AutoSaver:

    @staticmethod
    def initializeAutoSaver():
        # Remove any existing autosaver tasks (used if we change settings)
        taskMgr.remove('autosaver-task')

        # Create 'autosaves' directory in user data directory
        if not os.path.isdir(f'{userfiles}/autosaves'):
            os.mkdir(f'{userfiles}/autosaves')
            print('Created "autosaves" dir')
        taskMgr.doMethodLater(settings.get('autosave-interval', 15) * 60, AutoSaver.autoSaverProcess, 'autosaver-task')

    @staticmethod
    def autoSaverProcess(task):
        autosaveEnabled = settings.get('autosave-enabled', True)
        # Loops without doing anything if auto saver isn't toggled
        if not autosaveEnabled:
            return task.again

        # Only auto save if auto save is toggled
        if autosaveEnabled:
            AutoSaver.manageAutoSaveFiles()
            return task.again

    @staticmethod
    def manageAutoSaveFiles():
        DNASerializer.autoSaverMgrRunning = True
        autoSaveCount = int(DNASerializer.autoSaveCount)
        outputFile = DNASerializer.outputFile
        newout = outputFile
        if not outputFile:
            newout = os.path.join(userfiles, 'unsaved.dna')

        # Defining outputFile name properties
        bn = os.path.basename(newout)
        basename, extension = os.path.splitext(bn)

        DNASerializer.outputDNA(
                f'{userfiles}/autosaves/auto_{basename}_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.dna',
                True)
        DNASerializer.autoSaverMgrRunning = False
