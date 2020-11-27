from panda3d.core import Filename
import os
from tkinter import *
from tkinter.filedialog import *
from direct.directnotify import DirectNotifyGlobal

dnaDirectory = Filename.expandFrom(userfiles)

class DNASerializer:
    notify = DirectNotifyGlobal.directNotify.newCategory('LevelEditor')

    def __init__(self, editor):
        self.editor = editor

    # STYLE/DNA FILE FUNCTIONS
    def loadSpecifiedDNAFile(self):
        path = dnaDirectory.toOsSpecific()
        if not os.path.isdir(path):
            print('LevelEditor Warning: Invalid default DNA directory!')
            print('Using current directory')
            path = '.'
        dnaFilename = askopenfilename(
                defaultextension = '.dna',
                filetypes = (('DNA Files', '*.dna'), ('All files', '*')),
                initialdir = path,
                title = 'Load DNA File',
                parent = self.editor.panel.component('hull'))
        if dnaFilename:
            self.loadDNAFromFile(dnaFilename)
            self.outputFile = dnaFilename
        print("Finished Load: ", dnaFilename)

    def saveToSpecifiedDNAFile(self):
        path = dnaDirectory.toOsSpecific()
        if not os.path.isdir(path):
            print('LevelEditor Warning: Invalid DNA save directory!')
            print('Using current directory')
            path = '.'
        dnaFilename = asksaveasfilename(
                defaultextension = '.dna',
                filetypes = (('DNA Files', '*.dna'), ('All files', '*')),
                initialdir = path,
                title = 'Save DNA File as',
                parent = self.editor.panel.component('hull'))
        if dnaFilename:
            self.outputDNA(dnaFilename)
            self.outputFile = dnaFilename

    def loadDNAFromFile(self, filename):
        self.notify.debug("Filename: %s" % filename)
        # Reset level, destroying existing scene/DNA hierarcy
        self.editor.reset(fDeleteToplevel = 1, fCreateToplevel = 0,
                   fUpdateExplorer = 0)
        # Now load in new file
        try:
            self.notify.debug("Trying to load file")
            node = loadDNAFile(DNASTORE, Filename.fromOsSpecific(filename).cStr(), CSDefault, 1)
        except Exception:
            self.notify.debug(
                    "Couldn't load specified DNA file. Please make sure storage code has been specified in Config.prc file")
            return
        if node.getNumParents() == 1:
            # If the node already has a parent arc when it's loaded, we must
            # be using the level editor and we want to preserve that arc.
            newNPToplevel = NodePath(node)
            newNPToplevel.reparentTo(hidden)
        else:
            # Otherwise, we should create a new arc for the node.
            newNPToplevel = hidden.attachNewNode(node)

        # Make sure the topmost file DNA object gets put under DNARoot
        newDNAToplevel = self.editor.findDNANode(newNPToplevel)

        # reset the landmark block number:
        (self.landmarkBlock, needTraverse) = self.editor.findHighestLandmarkBlock(newDNAToplevel, newNPToplevel)

        # Update toplevel variables
        if needTraverse:
            self.editor.createToplevel(newDNAToplevel)
        else:
            self.editor.createToplevel(newDNAToplevel, newNPToplevel)
        # Create visible representations of all the paths and battle cells
        self.editor.createSuitPaths()
        self.editor.hideSuitPaths()
        self.editor.createBattleCells()
        self.editor.hideBattleCells()

        self.editor.loadAnimatedProps(newNPToplevel)

        # Set the title bar to have the filename to make it easier
        # to remember what file you are working on
        self.editor.panel["title"] = 'Open Level Editor: ' + os.path.basename(filename)
        self.editor.panel.sceneGraphExplorer.update()
        self.editor.popupNotification(f"Loaded {os.path.basename(filename)}")

    def outputDNADefaultFile(self):
        outputFile = self.outputFile
        if outputFile == None:
            self.saveToSpecifiedDNAFile()
            return
        file = os.path.join(dnaDirectory.toOsSpecific(), outputFile)
        self.outputDNA(file)

    def outputDNA(self, filename):
        print('Saving DNA to: ', filename)
        binaryFilename = Filename(filename)
        binaryFilename.setBinary()
        self.editor.DNAData.writeDna(binaryFilename, Notify.out(), DNASTORE)
        self.editor.popupNotification(f"Saved to {os.path.basename(binaryFilename)}")
        if ConfigVariableString("compiler") in ['libpandadna', 'clash']:
            print(f"Compiling PDNA for {ConfigVariableString('compiler')}")
            self.compileDNA(binaryFilename)

    def compileDNA(self, filename):
        from toontown.compiler.compile import process_single_file
        process_single_file(filename)

    def saveColor(self):
        self.appendColorToColorPaletteFile(self.editor.panel.colorEntry.get())

    def appendColorToColorPaletteFile(self, color):
        obj = self.DNATarget
        if obj:
            classType = DNAGetClassType(obj)
            if classType == DNA_WALL:
                tag = 'wall_color:'
            elif classType == DNA_WINDOWS:
                tag = 'window_color:'
            elif classType == DNA_DOOR:
                tag = 'door_color:'
            elif classType == DNA_FLAT_DOOR:
                tag = 'door_color:'
            elif classType == DNA_CORNICE:
                tag = 'cornice_color:'
            elif classType == DNA_PROP:
                tag = 'prop_color:'
            else:
                return
            # Valid type, add color to file
            filename = self.neighborhood + '_colors.txt'
            fname = Filename(dnaDirectory.getFullpath() +
                             '/stylefiles/' + filename)
            f = open(fname.toOsSpecific(), 'ab')
            f.write('%s Vec4(%.2f, %.2f, %.2f, 1.0)\n' %
                    (tag,
                     color[0] / 255.0,
                     color[1] / 255.0,
                     color[2] / 255.0))
            f.close()

    def saveStyle(self, filename, style):
        # A generic routine to append a new style definition to one of
        # the style files.

        fname = Filename(dnaDirectory.getFullpath() +
                         '/stylefiles/' + filename)
        # We use binary mode to avoid Windows' end-of-line convention
        f = open(fname.toOsSpecific(), 'a')
        # Add a blank line
        f.write('\n')
        # Now output style details to file
        style.output(f)
        # Close the file
        f.close()

    def saveBaselineStyle(self):
        if self.editor.panel.currentBaselineDNA:
            # Valid baseline, add style to file
            filename = self.neighborhood + '/baseline_styles.txt'
            style = DNABaselineStyle(self.editor.panel.currentBaselineDNA)
            self.saveStyle(filename, style)

    def saveWallStyle(self):
        if self.lastWall:
            # Valid wall, add style to file
            filename = self.neighborhood + '/wall_styles.txt'
            style = DNAWallStyle(self.lastWall)
            self.saveStyle(filename, style)

    def saveBuildingStyle(self):
        dnaObject = self.selectedDNARoot
        if dnaObject:
            if DNAClassEqual(dnaObject, DNA_FLAT_BUILDING):
                # Valid wall, add style to file
                filename = self.neighborhood + '/building_styles.txt'
                style = DNAFlatBuildingStyle(dnaObject)
                self.saveStyle(filename, style)
                return
        print('Must select building before saving building style')

    def loadStreetCurve(self):
        path = '.'
        streetCurveFilename = askopenfilename(
                defaultextension = '.egg',
                filetypes = (('Egg files', '*.egg'),
                             ('Bam files', '*.bam'),
                             ('Maya files', '*.mb'),
                             ('All files', '*')),
                initialdir = path,
                title = 'Load Curve File',
                parent = self.editor.panel.component('hull'))
        if streetCurveFilename:
            modelFile = loader.loadModel(Filename.fromOsSpecific(streetCurveFilename))
            # curves = modelFile.findAllMatches('**/+ClassicNurbsCurve')
            curves = {'inner': [], 'outer': [], 'innersidest': [], 'outersidest': []}
            curvesInner = modelFile.findAllMatches('**/*curve_inner*')
            print("-------------- curvesInner-----------------")
            print(curvesInner)
            curvesOuter = modelFile.findAllMatches('**/*curve_outer*')
            print("---------------- curvesOuter---------------")
            print(curvesOuter)
            curveInnerSideSts = modelFile.findAllMatches('**/*curveside_inner*')
            print("--------- curveInnerSideSts----------")
            print(curveInnerSideSts)

            curveOuterSideSts = modelFile.findAllMatches('**/*curveside_outer*')
            print("----------- curveOuterSideSits ----------")
            print(curveOuterSideSts)

            # return an ordered list
            for i in range(len(curvesInner) + 1):  # RAU don't forget, these curves are 1 based
                curve = modelFile.find('**/*curve_inner_' + str(i))
                if not curve.isEmpty():
                    # Mark whether it is a section of buildings or trees
                    curveType = curve.getName().split("_")[0]
                    curves['inner'].append([curve.node(), curveType])

            for i in range(len(curvesOuter) + 1):
                curve = modelFile.find('**/*curve_outer_' + str(i))
                if not curve.isEmpty():
                    # Mark whether it is a section of buildings or trees
                    curveType = curve.getName().split("_")[0]
                    curves['outer'].append([curve.node(), curveType])

            maxNum = len(curvesInner)
            if len(curvesOuter) > maxNum:
                maxNum = len(curvesOuter)

            maxNum += 2  # track ends in a barricade, and add 1 since 1 based
            # RAU also do special processing for the side streets
            # side streets are numbered differently and could be non consecutive
            # curveside_inner_28_1, curveside_outer_28_1, curveside_inner_28_2,
            # curveside_outer_28_2 (two side streets closest to main building track 28)
            for i in range(maxNum):
                for barricade in ['innerbarricade', 'outerbarricade']:
                    curve = modelFile.find('**/*curveside_inner_' + barricade + '_' + str(i))
                    if not curve.isEmpty():
                        # Mark whether it is a section of buildings or trees
                        curveType = curve.getName().split("_")[0]
                        curves['innersidest'].append([curve.node(), curveType])
                        print("adding innersidest %s" % curve.getName())

            for i in range(maxNum):
                for barricade in ['innerbarricade', 'outerbarricade']:
                    curve = modelFile.find('**/*curveside_outer_' + barricade + '_' + str(i))
                    if not curve.isEmpty():
                        # Mark whether it is a section of buildings or trees
                        curveType = curve.getName().split("_")[0]
                        curves['outersidest'].append([curve.node(), curveType])
                        print("adding outersidest %s" % curve.getName())

            print("loaded curves: %s" % curves)
            return curves
        else:
            return None
