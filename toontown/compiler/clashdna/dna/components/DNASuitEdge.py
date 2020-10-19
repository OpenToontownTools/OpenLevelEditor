class DNASuitEdge:
    COMPONENT_CODE = 22

    def __init__(self, startPoint, endPoint, zoneId):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.zoneId = zoneId

    def setStartPoint(self, startPoint):
        self.startPoint = startPoint

    def setEndPoint(self, endPoint):
        self.endPoint = endPoint

    def setZoneId(self, zoneId):
        self.zoneId = zoneId
