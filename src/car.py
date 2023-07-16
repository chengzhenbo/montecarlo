from dataclasses import dataclass, field
from enum import StrEnum, auto

from src.floor import Floor

class CarType(StrEnum):
    SINGLE = auto()
    DOUBLE = auto()

@dataclass
class Car():
    id: int = 0
    v:float = 0.0
    a:float = 0.0
    jerk:float  = 0.0
    capacity:int  = 0
    capacity_ratio:float = 0.8
    t_open_door:float = 3.2
    t_close_door:float = 3.2
    t_p:float  = 1.2 # 乘客进/出时间
    car_type:CarType = CarType.SINGLE
    stop_floor_ids:list[int] = field(default_factory=list) 
    _current_floor:Floor = field(default_factory=Floor) 

    def set_current_floor(self, c_floor:Floor)->None:
        """将c_floor设为当前轿厢所处的楼层"""
        self._current_floor = c_floor
    
    @property
    def serve_floor_ids(self)->list[Floor]:
        if self.car_type == CarType.SINGLE:
            return self.stop_floor_ids
        if self.car_type == CarType.DOUBLE:
            up_car_serve_floors =  []
            for f_id in self.stop_floor_ids:
                if f_id == -1:
                    up_car_serve_floors.append(1) # 0不作为楼层编号
                else:
                    up_car_serve_floors.append(f_id+1)
            floor_ids = list(set(self.stop_floor_ids+up_car_serve_floors))
            floor_ids.sort()
            return floor_ids

    @property
    def current_floor(self)->Floor:
        return self._current_floor