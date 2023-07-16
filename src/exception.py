from dataclasses import dataclass

class FloorIdError(Exception):
    floor_id:int

class OriginFloorIdError(Exception):
    floor_id:int

class CarNotInBuildingError(Exception):
    pass

class FloorError(Exception):
    pass

class CarOverflowError(Exception):
    pass

class NoCarInBuildingError(Exception):
    pass

class DoubleCarRTTError(Exception):
    pass


