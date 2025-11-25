from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath


from direct.extensions_native.extension_native_helpers import Dtool_funcToMethod

from toontown.panels.SceneGraphExplorer import SceneGraphExplorer


class ExplorerManager(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)

        self.nodesToExplorers: dict[NodePath, SceneGraphExplorer] = {}

        # Replace the explore() extension method for NodePath
        def explore(nodePath):
            self.nodesToExplorers[nodePath] = SceneGraphExplorer(nodePath)

        Dtool_funcToMethod(explore, NodePath)
        self.accept('imgui-new-frame', self.__checkActive)

    def __checkActive(self):
        for node in list(self.nodesToExplorers.keys()):
            placer = self.nodesToExplorers[node]
            if not placer.active:
                del self.nodesToExplorers[node]

