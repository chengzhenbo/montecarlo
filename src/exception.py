from dataclasses import dataclass

@dataclass
class FloorIdError(Exception):
    floor_id:int 
    def __str__(self) -> str:
        return f"楼层编号{self.floor_id}不在楼层编号范围内."

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


