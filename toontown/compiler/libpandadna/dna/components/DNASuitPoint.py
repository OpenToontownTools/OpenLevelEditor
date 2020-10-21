class DNASuitPoint:
    COMPONENT_CODE = 20
    pointTypeMap = {
        'STREET_POINT': 0,
        'FRONT_DOOR_POINT': 1,
        'SIDE_DOOR_POINT': 2,
        'COGHQ_IN_POINT': 3,
        'COGHQ_OUT_POINT': 4
    }
    ivPointTypeMap = {v: k for k, v in pointTypeMap.items()}

    def __init__(self, index, pointType, pos, landmarkBuildingIndex=-1):
        self.index = index
        self.pointType = pointType
        self.pos = pos
        self.landmarkBuildingIndex = landmarkBuildingIndex
        self.graphId = 0

    def setIndex(self, index):
        self.index = index

    def setGraphId(self, graphId):
        self.graphId = graphId

    def setLandmarkBuildingIndex(self, index):
        self.landmarkBuildingIndex = index

    def setPos(self, pos):
        self.pos = pos

    def setPointType(self, pointType):
        if isinstance(pointType, int):
            if pointType in DNASuitPoint.ivPointTypeMap:
                self.pointType = pointType
                return
        elif isinstance(pointType, str):
            if pointType in DNASuitPoint.pointTypeMap:
                self.pointType = DNASuitPoint.pointTypeMap[pointType]
                return
        error = '%s is not a valid DNASuitPointType'
        raise TypeError(error % str(pointType))
