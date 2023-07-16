from dataclasses import dataclass
from pydantic import BaseModel,validator
import itertools
from math import sqrt, pow, ceil
import random 
from typing import Dict,List,Set
from enum import Enum
import numpy as np


class CarType(Enum):
    SINGLE = 1
    DOUBLE = 2


@dataclass
class BaseFloorError(Exception):
    num_basefloors:int 

@dataclass
class FloorsError(Exception):
    num_floors:int

@dataclass
class BuildingDistanceIndexError(Exception):
    pass

@dataclass
class OriginFloorError(Exception):
    pass

@dataclass 
class Passenger():
    id_iter = itertools.count()
    id:int 
    origin_floor:int 
    destination_floor:int 

    def __init__(self, 
                 origin_floor:int, 
                 destination_floor:int):
        self.id = next(self.id_iter)
        self.origin_floor = origin_floor
        self.destination_floor = destination_floor

class Building:
    def __init__(self, 
                 N:int=0, 
                 NB:int=0, 
                 car_type:CarType = CarType.DOUBLE,
                 ratio_from_NB:float = 0.0, #从底层出发相对于从大堂出发的比率(0~1)
                 avg_height:float=0.0, 
                 avg_num_passengers_every_floor:int=0):
        self.N = N 
        self.NB = NB
        self.car_type = car_type
        self.ratio_from_NB = ratio_from_NB
        self.avg_height = avg_height
        self.avg_num_passengers_every_floor = avg_num_passengers_every_floor

        self._floor_heights = {}
        self._floor_distances = {}
        self._floor_num_passengers = {}
        self._origin_floor_weights:List[Set] = [()]
        self._bottom_car_stops:List = []
        self._up_car_stops:List = []

        assert self.NB >= 0, "地下出发的可能性"
        assert self.N > 0, "楼层值必须大于0"

        self.init_floor_heights()
        self.init_floor_distances()
        self.init_floor_num_passengers()
        self.init_origin_floor_weights()
        
    def init_floor_heights(self)->None:
        if self.NB < 0:
            raise BaseFloorError(num_basefloors = self.NB)
        if self.N < 0:
            raise FloorsError(num_floors = self.N)
        
        for i in range(self.NB, 0, -1):
            ind_NB = -1*i
            self._floor_heights[ind_NB] = self.avg_height
        
        for i in range(1, self.N+1):
            self._floor_heights[i] = self.avg_height
    
    def init_floor_distances(self)->None:
        ind_floors = list(self._floor_heights.keys())
        num_floors = len(ind_floors)
        for i in range(num_floors-1):
            for j in range(i+1, num_floors):
                self._floor_distances[(ind_floors[i], 
                                      ind_floors[j])] = sum([self.floor_heights[k] 
                                                                for k in range(ind_floors[i], 
                                                                               ind_floors[j]) 
                                                                if k in self.floor_heights])
    def init_floor_num_passengers(self)->None:
        if self.N < 0:
            raise FloorsError(num_floors = self.N)
        
        for i in range(2, self.N+1):
            self._floor_num_passengers[i] = self.avg_num_passengers_every_floor

    def init_origin_floor_weights(self)->None:
        assert 0 <= self.ratio_from_NB and self.ratio_from_NB <= 1, "ratio_from_NB 取值范围[0, 1]"
        
        if self.car_type == CarType.SINGLE:
            self._origin_floor_weights = [(1, 1-self.ratio_from_NB)] # 表示第1层，(1-ratio_from_NB)比重从该层出发
            # 设置从地下各层出发的比率
            for i in range(self.NB, 0, -1):
                    ind_NB = -1*i
                    assert self.ratio_from_NB >= 0, "考虑从地下出发的可能性"
                    self._origin_floor_weights.insert(0, (ind_NB, self.ratio_from_NB/self.NB))
            return 
        elif self.car_type == CarType.DOUBLE:
            all_floors = [i for i in range(self.NB*-1, self.N+1, 1) if i != 0 ]
            for i, floor in enumerate(all_floors):
                if (i%2) == 0:
                    self._bottom_car_stops.append(floor)
                else:
                    self._up_car_stops.append(floor)
            if self._bottom_car_stops[-1] == self.N:
                self._up_car_stops.pop()
                self._up_car_stops.append(self.N)
                self._bottom_car_stops.pop()
                self._bottom_car_stops.append(self.N-1)
            if 1 in self._bottom_car_stops:
                index_1 = self._bottom_car_stops.index(1)
                origin_floor = self._up_car_stops[index_1]
            if 1 in self._up_car_stops:
                index_1 = self._up_car_stops.index(1)
                origin_floor = self._bottom_car_stops[index_1]
            if origin_floor < 0:
                self._origin_floor_weights = [(1, 1-self.ratio_from_NB)]
            else:
                self._origin_floor_weights = [(1, 1-self.ratio_from_NB), (origin_floor, 1-self.ratio_from_NB)]
            for i in range(self.NB, 0, -1):
                    ind_NB = -1*i
                    assert self.ratio_from_NB >= 0, "考虑从地下出发的可能性"
                    self._origin_floor_weights.insert(0, (ind_NB, self.ratio_from_NB/self.NB))
        else:
            return None
        

    def set_floor_num_passengers(self, 
                                 floor:int, 
                                 n_passengers:int)->None:
        assert n_passengers >= 0, "楼层的人数必须大于0"
        if floor in self.floor_heights:
            self._floor_num_passengers[floor] = n_passengers 
        else:
            print('楼层输入错误.') 

    def set_floor_distance(self, 
                           floor:int, 
                           distance:float)->None:
        if floor in self.floor_heights:
            self._floor_distances[floor] = distance 
        else:
            print('楼层输入错误.')

    def set_floor_height(self, 
                         floor:int, 
                         height:float)->None:
        if floor in self.floor_heights:
            self._floor_heights[floor] = height 
        else:
            print('楼层输入错误.')

    @property
    def num_passengers(self)->int:
        return sum(self._floor_num_passengers.values())

    @property
    def origin_floor_weights(self):
        return self._origin_floor_weights
    
    @property 
    def floor_heights(self):
        return self._floor_heights
    
    @property 
    def floor_distances(self):
        return self._floor_distances
    
    @property 
    def floor_num_passengers(self):
        return self._floor_num_passengers
    
    @property 
    def floors(self):
        return self.floor_heights.keys()
    
    @property
    def bottom_car_stops(self):
        return self._bottom_car_stops

    @property
    def up_car_stops(self):
        return self._up_car_stops
    
      
class Car(BaseModel):
    id: int
    v:float = 0.0
    a:float = 0.0
    jerk:float  = 0.0
    capacity:int  = 0
    ratio_load_a_travel = 0.8
    t_open_door:float = 3.2
    t_close_door:float = 3.2
    t_p:float  = 1.2 # 乘客进出时间
    current_floor:int = 1
    inner_passengers:List[Passenger] = []
    inner_bottom_car_passengers:List[Passenger] = []
    inner_up_car_passengers:List[Passenger] = []
    

    @validator('capacity')
    def capacity_must_greater_zero(cls, v):
        if v < 0:
            raise ValueError('capacity must greater than zero')
        return v
    
    def __hash__(self) -> int:
        return self.id.__hash__()
    
    @classmethod
    def get_floors_outer_passengers(self,passengers:List[Passenger])->List:
        return [p.origin_floor for p in passengers]

def car_transition_matrix_for_building(car:Car, 
                                       building:Building)->dict:
    ttm = {}
    ind_floors = list(building.floor_heights.keys())
    num_floors = len(ind_floors)

    def bound_1()->float:
        return 2*pow(car.a, 3)/pow(car.jerk, 2)
    
    def bound_2()->float:
        return (pow(car.a, 2)*car.v + pow(car.v, 2)*car.jerk)/(car.a*car.jerk)
    
    def distance_time(d:float, b1:float, b2:float)->float:
        if d >= b2:
            return d/car.v + car.v/car.a + car.a/car.jerk 
        elif d < b1:
            return pow(32*d/car.jerk, 1/3)
        else:
            return car.a/car.jerk + sqrt(4*d/car.a + pow(car.a/car.jerk, 2))
    
    b1 = bound_1()
    b2 = bound_2()
    assert(b2>=b1), '轿厢参数设置有误'

    for i in range(num_floors-1):
        for j in range(i+1, num_floors):
            if (ind_floors[i], ind_floors[j]) in building.floor_distances:
                d = building.floor_distances[(ind_floors[i], ind_floors[j])]
            else:
                raise BuildingDistanceIndexError
            ttm[ind_floors[i], ind_floors[j]] = distance_time(d=d, b1=b1, b2=b2)
    return ttm

def waiting_passengers_in_building(building:Building)->List[Passenger]:
    """根据建筑每一层人数产生侯梯的乘客，需要根据建筑出发楼层设置，将乘客分布在各个出发楼层。
       乘客到各个目的楼层等可能
    Args:
        building (Building): Building对象

    Raises:
        OriginFloorError: 楼层异常

    Returns:
        List[Passenger]: 侯梯乘客列表，每个乘客确定了其出发和目的楼层
    """
    Passenger.id_iter = itertools.count(0) # 每次调用都初始化passenger的ID为0
    waiting_passengers = []
    for destination_floor, num_passengers in building.floor_num_passengers.items():
        for _ in range(num_passengers):
             # 建筑只有一个出发楼层1
            origin_floor = building.origin_floor_weights[-1][0] 
            # 建筑有多个入口情况下，出发楼层按Building对象设定的出发楼层比率分布确定
            if len(building.origin_floor_weights) > 1:
                floors = [fw[0] for fw in building.origin_floor_weights]
                weights = [fw[1] for fw in building.origin_floor_weights]
                origin_floor = random.choices(floors, weights=weights, k=1)[-1] 
            if origin_floor not in building.floors:
                raise OriginFloorError
            if building.car_type == CarType.SINGLE:
                if origin_floor != destination_floor:
                    waiting_passengers.append(Passenger(origin_floor = origin_floor, 
                                                    destination_floor = destination_floor))
            else:
                if (origin_floor in building.bottom_car_stops and destination_floor in building.bottom_car_stops)\
                    or (origin_floor in building.up_car_stops and destination_floor in building.up_car_stops):
                    if origin_floor != destination_floor:
                        waiting_passengers.append(Passenger(origin_floor = origin_floor, 
                                                    destination_floor = destination_floor))
                else:
                    for f in floors:
                        if destination_floor in building.bottom_car_stops:
                            if f in building.bottom_car_stops:
                                origin_floor = f
                                break 
                        else:
                            if f in building.up_car_stops:
                                origin_floor = f
                                break 
                    if origin_floor != destination_floor:
                        waiting_passengers.append(Passenger(origin_floor = origin_floor, 
                                                    destination_floor = destination_floor))

    # 产生的乘客随机排列
    random.shuffle(waiting_passengers)
    return waiting_passengers

def get_round_trip_time_one_car(passengers:List[Passenger], 
                        transition_matrix:Dict, 
                        car:Car,
                        back_floor:int)->float:
    rtt = 0.0
    num_passengers = len(passengers)
    if  num_passengers > 0:
        destination_floors = [p.destination_floor for p in passengers]
        destination_floors.sort()
        stops = list(set(destination_floors))
        stops.insert(0, car.current_floor)
        num_up_stops = len(stops)

        for i in range(num_up_stops-1):
            if (stops[i], stops[i+1]) in transition_matrix:
                rtt += transition_matrix[(stops[i], stops[i+1])] # 上行时间

        rtt += transition_matrix[(back_floor, stops[-1])] # 空载回程时间
        rtt += num_passengers*car.t_p # 乘客进出时间
        rtt += (car.t_open_door+car.t_close_door)*num_up_stops

    return rtt

def get_round_trip_time_double_car(bottom_passengers:List[Passenger], 
                                   up_passengers:List[Passenger],
                                    transition_matrix:Dict, 
                                    car:Car,
                                    back_floor:int, 
                                    building:Building)->float:
    rtt = 0.0
    num_passengers = len(bottom_passengers)+len(up_passengers)
    if  num_passengers > 0:
        b_destination_floors = [bp.destination_floor for bp in bottom_passengers]
        u_destination_floors = [up.destination_floor for up in up_passengers]
        destination_floors = b_destination_floors+u_destination_floors
        
        stops = list(set(destination_floors))
        stops.insert(0, car.current_floor)
        stops.sort()
        num_up_stops = len(stops)
        for i, fs in enumerate(stops):
            if fs in building.up_car_stops:
                if fs-1 in stops:
                    num_up_stops -= 1
                    stops.pop(i)

        for i in range(num_up_stops-1):
            if (stops[i], stops[i+1]) in transition_matrix:
                rtt += transition_matrix[(stops[i], stops[i+1])] # 上行时间

        rtt += transition_matrix[(back_floor, stops[-1])] # 空载回程时间
        rtt += max([len(bottom_passengers),len(up_passengers)])*car.t_p # 乘客进出时间
        rtt += (car.t_open_door+car.t_close_door)*num_up_stops

    return rtt

def main():
    b1 = Building(N=21, 
                  NB=2, 
                  car_type=CarType.DOUBLE,
                  ratio_from_NB=0.5,
                  avg_height=4.2, 
                  avg_num_passengers_every_floor=130)
    b1.set_floor_num_passengers(floor=44, n_passengers=0)
    b1.set_floor_num_passengers(floor=43, n_passengers=0)
    b1.set_floor_num_passengers(floor=23, n_passengers=0)
    b1.set_floor_num_passengers(floor=2, n_passengers=0)
    
    car = Car(id=1,
              v=8, 
              a=1, 
              jerk=0.6, 
              capacity=13) 
    
    car_transition_matrix = car_transition_matrix_for_building(car=car, building=b1) 

    num_trials = 10
    round_trip_time = []
    permited_num_in_car = ceil(car.capacity*car.ratio_load_a_travel)
    if b1.car_type == CarType.DOUBLE:
        permited_num_in_car = permited_num_in_car*2

    for _ in range(num_trials):
        waiting_passengers_b1 = waiting_passengers_in_building(b1)
        
        while len(waiting_passengers_b1) > 0:
            # 根据电梯当前所在的楼层，把侯梯乘客中在该楼层的乘客加到电梯内招
            num_inner_passengers = 0
            for i_p, passenger in reversed(list(enumerate(waiting_passengers_b1))):

                if num_inner_passengers > permited_num_in_car:
                    break
                if b1.car_type == CarType.SINGLE:
                    if passenger.origin_floor == car.current_floor:
                        car.inner_passengers.append(passenger)
                        num_inner_passengers += 1
                        waiting_passengers_b1.pop(i_p) # 乘客列表中删除已经进入电梯的乘客
                if b1.car_type == CarType.DOUBLE:
                    if passenger.origin_floor == car.current_floor:
                        car.inner_bottom_car_passengers.append(passenger)
                        num_inner_passengers += 1
                        waiting_passengers_b1.pop(i_p) # 乘客列表中删除已经进入电梯的乘客
                    if car.current_floor+1 in b1.up_car_stops:
                        if passenger.origin_floor == car.current_floor+1:
                            car.inner_up_car_passengers.append(passenger)
                            num_inner_passengers += 1
                            waiting_passengers_b1.pop(i_p) # 乘客列表中删除已经进入电梯的乘客
            if len(car.inner_passengers)>0 or \
                len(car.inner_bottom_car_passengers)>0 or\
                len(car.inner_up_car_passengers)>0: #电梯内招中有乘客
                # 还剩下的侯梯乘客
                floors_outer_passengers = Car.get_floors_outer_passengers(waiting_passengers_b1)
                # 从还剩下的侯梯乘客中，选择其中楼层最低的作为返回楼层
                if len(floors_outer_passengers) > permited_num_in_car:
                    back_floor = min(floors_outer_passengers[permited_num_in_car:])
                elif len(floors_outer_passengers)>0 and len(floors_outer_passengers) <= permited_num_in_car:
                    back_floor = min(floors_outer_passengers)
                else:
                    break
                # 计算RTT
                if b1.car_type == CarType.SINGLE:
                    rtt = get_round_trip_time_one_car(passengers=car.inner_passengers,
                                                            transition_matrix=car_transition_matrix,
                                                            car=car,
                                                            back_floor = back_floor)
                else:
                    rtt = get_round_trip_time_double_car(bottom_passengers=car.inner_bottom_car_passengers, 
                                                                up_passengers=car.inner_up_car_passengers,
                                                            transition_matrix=car_transition_matrix,
                                                            car=car,
                                                            back_floor = back_floor,
                                                            building = b1)
                round_trip_time.append(rtt)
                # 更新电梯所返回的楼层
                car.current_floor = back_floor
                # 清空电梯内招乘客
                car.inner_passengers = []
                car.inner_bottom_car_passengers = []
                car.inner_up_car_passengers = []
                # 内招乘客计数器再初始化
                num_inner_passengers = 0
    RTT = np.average(round_trip_time)
    E = RTT/20
    int_act = RTT/E 
    if b1.car_type == CarType.SINGLE:
        HC = (300*E*car.capacity*car.ratio_load_a_travel)/(RTT*b1.num_passengers)
    else:
        HC = (300*E*car.capacity*2*car.ratio_load_a_travel)/(RTT*b1.num_passengers)
    print(f'car type is {b1.car_type.name}')
    print(f'num of passengers {b1.num_passengers}')
    print(f'round_trip_time = {RTT}')
    print(f'num of cars = {round(E)}')
    print(f'int = {int_act}')
    print(f'HC% = {HC:.0%}')
if __name__ == "__main__":
    main()