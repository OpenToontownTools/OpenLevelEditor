from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Func, Wait

from imgui_bundle import imgui, imgui_ctx

class SceneGraphExplorer(DirectObject):
    def __init__(self, nodePath = None, active = True):
        DirectObject.__init__(self)
        self.nodePath: NodePath = nodePath
        self.active = active
        if not nodePath:
            self.nodePath = base.render

        self.__currentNodePath = self.nodePath

        self.windowPos = None

        self.reparentTarget: NodePath | None = None

        self.flashOnClick = False
        self.highlightSeq: Sequence | None = None

        self.rename = ''
        self.showSetNamePopupForNode: NodePath = None
        self.focusSetNameInput = False

        self.__firstDraw = True
        self.accept('imgui-new-frame', self.__draw)

    def __del__(self):
        self.ignoreAll()

    def __draw(self):
        if not self.active:
            return

        id = 0
        def drawTreeForNode(nodePath):
            nonlocal id
            flags = 0
            if nodePath.getNumChildren() == 0:
                flags = imgui.TreeNodeFlags_.leaf.value
            elif nodePath == self.nodePath:
                flags = imgui.TreeNodeFlags_.default_open.value

            typeName = nodePath.node().getType().getName()
            name = nodePath.getName()

            dnaNode = None
            if hasattr(base, 'le'):
                dnaNode = base.le.findDNANode(nodePath)
            if dnaNode is not None:
                typeName = dnaNode.getType().getName()
                name = dnaNode.getName()

            tree = imgui.tree_node_ex(f"{self.nodePath.getName()}-{id}", flags, f"{typeName} {name}")

            if self.flashOnClick and imgui.is_item_clicked():
                base.messenger.send('SGE_Flash', [nodePath])

            if imgui.begin_popup_context_item():
                clickedFlash, _ = imgui.menu_item("Flash", "", False)
                if clickedFlash:
                    base.messenger.send('SGE_Flash', [nodePath])

                imgui.separator()

                clickedSetName, _ = imgui.menu_item("Set Name", "", False)
                if clickedSetName:
                    self.rename = nodePath.getName()
                    # HACK: Calling imgui.begin_popup wouldn't work here for some reason.
                    # Do this to call it outside the context popup statement.
                    self.showSetNamePopupForNode = nodePath
                    self.focusSetNameInput = True

                imgui.separator()

                clickedSetTarget, _ = imgui.menu_item("Set Reparent Target", "", False)
                if clickedSetTarget:
                    self.reparentTarget = nodePath
                    messenger.send('SGE_Set Reparent Target', [nodePath])

                clickedReparent, _ = imgui.menu_item("Reparent to Target", "", False, self.reparentTarget is not None)
                if clickedReparent:
                    messenger.send('SGE_Reparent', [nodePath])

                clickedWrtReparent, _ = imgui.menu_item("WRT Reparent To Target", "", False, self.reparentTarget is not None)
                if clickedWrtReparent:
                    messenger.send('SGE_WRT Reparent', [nodePath])

                imgui.separator()

                clickedPlace, _ = imgui.menu_item("Place", "", False)
                if clickedPlace:
                    nodePath.place()
                if nodePath != self.nodePath:
                    clickedExplore, _ = imgui.menu_item("Explore Seperately", "", False)
                    if clickedExplore:
                        nodePath.explore()
                imgui.end_popup()

            if self.showSetNamePopupForNode == nodePath:
                self.showSetNamePopupForNode = None
                imgui.open_popup(f"{nodePath}-namePopup")

            with imgui_ctx.begin_popup(f"{nodePath}-namePopup") as namePopup:
                if namePopup:
                    imgui.text("Set Name:")
                    imgui.same_line()

                    if self.focusSetNameInput:
                        imgui.set_keyboard_focus_here()
                        self.focusSetNameInput = False

                    nameChanged, newName = imgui.input_text("##input", self.rename, imgui.InputTextFlags_.chars_no_blank.value)
                    if nameChanged:
                        self.rename = newName

                    if imgui.button("OK") or imgui.is_key_pressed(imgui.Key.enter):
                        nodePath.setName(self.rename)
                        messenger.send('DIRECT_nodePathSetName', [nodePath, self.rename])
                        self.rename = ''
                        imgui.close_current_popup()

                    imgui.same_line()

                    if imgui.button("Cancel") or imgui.is_key_pressed(imgui.Key.escape):
                        self.rename = ''
                        imgui.close_current_popup()

            if tree:
                for child in nodePath.children:
                    id += 1
                    drawTreeForNode(child)
                imgui.tree_pop()

        if self.__firstDraw:
            imgui.set_next_window_size((410,761))
            self.__firstDraw = False

        if self.windowPos and (self.nodePath != self.__currentNodePath):
            imgui.set_next_window_pos(self.windowPos)
            self.__currentNodePath = self.nodePath

        with imgui_ctx.begin(f"Explore: {self.nodePath.getName()}", True, imgui.WindowFlags_.menu_bar) as (_, windowOpen):
            if not windowOpen:
                self.active = False
                return

            self.windowPos = imgui.get_window_pos()

            with imgui_ctx.begin_menu_bar() as menuBar:
                if menuBar:
                    with imgui_ctx.begin_menu("Options") as optionsMenu:
                        if optionsMenu:
                            clickedFlashToggle, _ = imgui.menu_item("Flash on Click", "", self.flashOnClick)
                            if clickedFlashToggle:
                                self.flashOnClick = not self.flashOnClick

            imgui.text(f"Active Reparent Target: {self.reparentTarget}")
            drawTreeForNode(self.nodePath)






