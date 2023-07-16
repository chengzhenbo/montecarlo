from dataclasses import dataclass


class FloorIdError(Exception):
    def __init__(self,
                 floor_id:int,
                 message=f'楼层编号错误'):
        self.floor_id = floor_id
        self.message = message
        super().__init__(self.message)



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


