import os
import shutil
import time
import threading


class AutoSaver:
    autoSaverInterval = 15  # Default auto saver interval
    autoSaveCount = 0  # Number of saving iterations for one ouputFile
    autoSaverMgrRunning = False
    autoSaverToggled = False

    def __init__(self, DNASerializer = None):
        AutoSaver.DNASerializer = DNASerializer

    @staticmethod
    def initializeAutoSaver():
        threading.Thread(target=AutoSaver.autoSaverProcess, daemon=True).start()

    @staticmethod
    def autoSaverProcess():
        while True:
            autoSaverInterval = AutoSaver.autoSaverInterval * 60  # Converts global autoSaverInterval to minutes
            # Loops without doing anything if auto saver isn't toggled
            if AutoSaver.autoSaverToggled is False:
                time.sleep(0.1)
            while AutoSaver.autoSaverToggled is True:
                endTime = time.time() + autoSaverInterval  # Epoch time of next auto save
                # Loops until endTime is reached or the auto saver is un-toggled by user.
                while time.time() <= endTime and AutoSaver.autoSaverToggled is True:
                    time.sleep(0.1)
                if AutoSaver.autoSaverToggled is True:
                    AutoSaver.manageAutoSaveFiles()
                    AutoSaver.autoSaveCount += 1

    @staticmethod
    def manageAutoSaveFiles():
        AutoSaver.autoSaverRunning = True
        DNASerializer = AutoSaver.DNASerializer
        autoSaveCount = AutoSaver.autoSaveCount

        # Sets max number of auto save files
        if AutoSaver.autoSaveCount >= 10:
            autoSaveCount = 10

        # Defining outputFile name properties
        base = os.path.basename(DNASerializer.outputFile)
        dir = os.path.dirname(DNASerializer.outputFile)
        basename, extension = os.path.splitext(base)

        # Renames output file to auto save file naming convention
        if autoSaveCount == 0:
            DNASerializer.outputFile = os.path.join(dir, basename + '_autosave-latest' + extension).replace('\\', '/')
        basename = basename[:-6]  # Deletes 'latest' from filename
        # Incrementally copies each auto save file (i.e. 3400_autosave-1.dna -> 3400_autosave-2.dna)
        while autoSaveCount != 0:
            filename = os.path.join(dir, basename + str(autoSaveCount) + extension)
            oldFilename = os.path.join(dir, basename + str(autoSaveCount - 1) + extension)
            # Copies working auto save file
            if autoSaveCount == 1:
                shutil.copy2(DNASerializer.outputFile, filename)
                print()
            # Copies each numbered auto save file
            if autoSaveCount > 1:
                shutil.copy2(oldFilename, filename)
            autoSaveCount -= 1
        DNASerializer.outputDNADefaultFile()  # Saves working DNA file
        AutoSaver.autoSaverRunning = False
