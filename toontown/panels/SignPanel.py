# SignPanel
# Created by drewc Nov 27, 2025
from direct.showbase.DirectObject import DirectObject
from imgui_bundle import imgui, imgui_ctx

from toontown.leveleditor.EditorUtil import DNAGetClassType, DNAGetChildRecursive, DNAGetChildren, DNAGetBaselineString
from toontown.leveleditor.LevelEditorGlobals import DNA_ANIM_BUILDING, DNA_PROP, DNA_LANDMARK_BUILDING, DNA_SIGN, DNA_SIGN_BASELINE
from toontown.panels.FlatBuildingPanel import FlatBuildingPanel
from toontown.panels.LandmarkPanel import LandmarkPanel
from toontown.panels.PropSelectionPanel import PropSelectionPanel
from toontown.panels.StreetSelectionPanel import StreetSelectionPanel
from toontown.panels.PropPreviewPanel import PropPreviewPanel


class SignPanel(DirectObject):

    def __init__(self, editor):
        DirectObject.__init__(self)
        self.levelEditor = editor
        self.isOpen = False

    def findSignFromDNARoot(self):
        dnaRoot = self.levelEditor.selectedDNARoot
        if not dnaRoot:
            return
        objClass = DNAGetClassType(dnaRoot)
        if (objClass == DNA_LANDMARK_BUILDING
                or objClass == DNA_PROP
                or objClass == DNA_ANIM_BUILDING):
            target = DNAGetChildRecursive(dnaRoot, DNA_SIGN)
            return target

    def draw(self):
        if not self.isOpen:
            return
        with imgui_ctx.begin("Sign"):  # the panel containing your tabs
            if imgui.begin_combo("Baseline", "<the sign>"):
                imgui.selectable("<the sign>", True)
                sign = self.findSignFromDNARoot()
                if sign:

                    baselineList = DNAGetChildren(sign, DNA_SIGN_BASELINE)
                    for baseline in baselineList:
                        s = DNAGetBaselineString(baseline)
                        imgui.selectable(s, False)
                imgui.end_combo()
            imgui.input_text("Text", "")
            if imgui.begin_combo("Font", "humanist"):
                for font in self.levelEditor.styleManager.getCatalogCodes('font'):
                    imgui.selectable(font, False)
                imgui.end_combo()