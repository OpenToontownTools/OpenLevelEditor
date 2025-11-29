from panda3d.core import Mat4
from imgui_bundle import imgui, imguizmo

from direct.showbase.DirectObject import DirectObject

gizmo = imguizmo.im_guizmo

def convertPandaMatrixToGizmo(matrix):
    # Create a new matrix in case it's a constant variable.
    matrix = Mat4(matrix)

    mat = gizmo.Matrix16([
        matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
        matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
        matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
        matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]
    ])

    return mat

def convertGizmoMatrixToPanda(matrix: gizmo.Matrix16):
    pandaMat = Mat4(*matrix.values.tolist())
    return pandaMat

class Gizmo(DirectObject):
    def __init__(self, editor):
        DirectObject.__init__(self)

        self.editor = editor
        self.operation: gizmo.OPERATION = gizmo.OPERATION.translate
        self.using = False

    def draw(self):
        if not base.direct.selected.last:
            return

        gizmo.begin_frame()
        size = imgui.get_io().display_size
        gizmo.set_rect(0, 0, size.x, size.y)
        gizmo.set_drawlist(imgui.get_background_draw_list())

        objMat = convertPandaMatrixToGizmo(base.direct.selected.last.getNetTransform().getMat())
        delta = gizmo.Matrix16()
        # TODO: Snapping toggle.
        snapping = gizmo.Matrix3([base.direct.grid.gridSpacing] * 3)
        if gizmo.is_using_any():
            if not self.using:
                self.using = True
                # Record undo point
                base.direct.pushUndo([base.direct.selected.last])
        else:
            self.using = False
        if gizmo.manipulate(convertPandaMatrixToGizmo(base.camLens.getViewMat() * base.cam.getNetTransform().getInverse().getMat()),
                            convertPandaMatrixToGizmo(base.camLens.getProjectionMat()),
                            self.operation, gizmo.MODE.local,
                            objMat, delta, snapping):
            if not convertGizmoMatrixToPanda(delta).isNan():
                base.direct.selected.last.setMat(base.direct.selected.last.getMat() * convertGizmoMatrixToPanda(delta))
