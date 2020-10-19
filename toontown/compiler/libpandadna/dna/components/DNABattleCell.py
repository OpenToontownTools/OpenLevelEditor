class DNABattleCell:
    COMPONENT_CODE = 21

    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = pos

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def setWidthHeight(self, width, height):
        self.setWidth(width)
        self.setHeight(height)

    def setPos(self, pos):
        self.pos = pos
