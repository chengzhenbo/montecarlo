from dataclasses import dataclass,field
from math import sqrt, pow, fsum
from collections import OrderedDict

from src.exception import (FloorIdError,
                           OriginFloorIdError,
                           CarNotInBuildingError,
                           FloorError,
                           CarOverflowError,
                           NoCarInBuildingError,
                           DoubleCarRTTError)
from src.car import Car, CarType
from src.floor import Floor
from src.passenger import Passenger

@dataclass
class Building():
    a_num_floors:int = 1
    b_num_floors:int = 0
    avg_floor_height:float = 0.0
    avg_floor_num_passengers:float = 0.0
    _floors:dict[int:Floor] = field(default_factory=dict) 
    _cars:list[Car] = field(default_factory=list) 
    _car_transition_matrixs:dict[int:dict] = field(default_factory=dict) 
    
    def __post_init__(self)->None:
        if self.a_num_floors < 1:
            raise ValueError('地上楼层数必须大于1')
        if self.b_num_floors < 0:
            raise ValueError('地下楼层数必须大于等于0')
        if self.avg_floor_height <= 0.0:
            raise ValueError('平均层高必须大于0')
        if self.avg_floor_num_passengers < 0.0:
            raise ValueError('各楼层平均人数必须大于等于0')
        self._init__floors()

    
    def _init__floors(self)->None:
        # 初始化地下楼层，同时将地下楼层初始化为出发楼层
        for i in range(self.b_num_floors, 0, -1):
            b_floor_id = -1*i #地下楼层用负数编号
            self._floors[b_floor_id] = Floor(id = b_floor_id, 
                                       height = self.avg_floor_height,
                                       num_passengers = 0,
                                       is_origin=True)
            
        # 初始化地上楼层，将建筑地面第1层初始化为出发楼层
        for i in range(1, self.a_num_floors+1):
            is_origin = False
            num_passenger = self.avg_floor_num_passengers
            if i == 1:
                is_origin = True
                num_passenger = 0
            self._floors[i] = Floor(id = i, 
                                    height = self.avg_floor_height,
                                    num_passengers = num_passenger,
                                    is_origin = is_origin)

    def register_car(self, car:Car)->None:
        # 将新添加的轿厢置于建筑的第1层
        car.set_current_floor(self.floors[1]) 
        self._cars.append(car)
        # 对新添加的轿厢，求出其运行时间矩阵
        self._car_transition_matrixs[car.id] = self._set_transition_matrix(car)
        # 根据新添加轿厢的类型，确定停机楼层
        self._set_car_stop_floors(car)
        # 对于双轿厢，根据停机楼层更新其出发楼层
        self.__update_origin_floors(car)
        # 初始化各个出发楼层乘客占比 
        self.__init_origin_floor_percentages()

    def  get_round_trip_time(self, passengers:list[Passenger], 
                            car:Car, 
                            back_floor:Floor,
                            num_passengers_set:tuple[int, int])->float:
        """计算乘客序列对某个轿厢的往返时间"""
        if num_passengers_set[0] > car.capacity or num_passengers_set[1] > car.capacity:
            raise CarOverflowError("乘客数不能超过轿厢容量")
        
        min_floor_id = min([p.floor_from.id for p in passengers]) 
        if car.car_type == CarType.SINGLE: 
            if min_floor_id in car.stop_floor_ids: # 乘客最小楼层是轿厢的停机楼层
                to_floor = self.floors[min_floor_id]
            else:
                raise DoubleCarRTTError('最小楼层错误')
        if car.car_type == CarType.DOUBLE:
            # 将轿厢运行到乘客中最小层时间
            if min_floor_id in car.stop_floor_ids: # 乘客最小楼层是轿厢的停机楼层
                to_floor = self.floors[min_floor_id]
            elif self.get_below_floor(self.floors[min_floor_id]).id in car.stop_floor_ids:
                to_floor = self.get_below_floor(self.floors[min_floor_id])
            else:
                raise DoubleCarRTTError('最小楼层错误')
        # 将轿厢运行到乘客中最小层时间
        t1 = self.get_travel_time_between_floors(car = car, 
                                                     from_floor = car.current_floor, 
                                                     to_floor = to_floor)    
        # 轿厢运送乘客时间
        if car.car_type == CarType.SINGLE:
            from_to_floor_pairs = self.__single_car_from_to_floor_pairs(passengers)
        if car.car_type == CarType.DOUBLE:
            from_to_floor_pairs = self.__double_car_from_to_floor_pairs(passengers=passengers,
                                                                        car=car)
        max_floor_id = from_to_floor_pairs[-1][-1]
        t2 = 0
        for floor_pair in from_to_floor_pairs:
            t2 += self.get_travel_time_between_floors(car = car, 
                                                    from_floor = self.floors[floor_pair[0]], 
                                                    to_floor = self.floors[floor_pair[1]])
        # 轿厢开关门时间
        t3 = (car.t_open_door+car.t_close_door)*(len(from_to_floor_pairs)+1)
        # 乘客上下门时间
        t4 = max(num_passengers_set)*(car.t_p+car.t_p)
        # 轿厢返程时间
        if back_floor.id in car.stop_floor_ids: # 乘客最小楼层是轿厢的停机楼层
            pass
        elif self.get_below_floor(back_floor).id in car.stop_floor_ids:
            back_floor = self.get_below_floor(back_floor)
        else:
            raise DoubleCarRTTError('最小楼层错误')
        t5 = self.get_travel_time_between_floors(car = car, 
                                                    from_floor = self.floors[max_floor_id], 
                                                    to_floor = back_floor)
        # 将轿厢的当前层设为回程楼层
        car.set_current_floor(c_floor=back_floor)
        return t1+t2+t3+t4+t5 

    def set_car_service_floor_range(self, 
                                    car:Car, 
                                    start_floor:Floor, 
                                    end_floor:Floor)->None:
        """
            设定建筑内轿厢服务楼层范围，从而修改轿厢的停机楼层。出发楼层总是停机楼层。
            开始到结束楼层按不同轿厢类型进行设置。
        """
        if (start_floor not in self.floors.values() or 
            end_floor not in self.floors.values()):
            raise ValueError('必须输入属于该建筑的楼层')
        if start_floor.id < 1 or start_floor.id > self.num_floors:
            raise ValueError('开始楼层必须大于等于1，且小于总楼层数')
        if end_floor.id <= start_floor.id:
            raise ValueError('结束楼层必须大于开始楼层')
        # 如果结束楼层超过了最高楼层，就将它置为最高楼层
        if end_floor.id > self.num_floors:
            end_floor.id = self.num_floors
        if car.car_type == CarType.SINGLE:
            unwanted_floors = []
            for _, floor_id in enumerate(car.stop_floor_ids):
                if floor_id not in self.original_floor_ids:
                    if floor_id < start_floor.id or floor_id > end_floor.id:
                        unwanted_floors.append(floor_id)
            car.stop_floor_ids = [ele for ele in car.stop_floor_ids 
                                      if ele not in unwanted_floors]

        if car.car_type == CarType.DOUBLE:     
            start = self.floor_ids.index(start_floor.id)
            end = self.floor_ids.index(end_floor.id)
            floor_ids = self.floor_ids[start:end+1]
            stops = self._set_double_car_stop_floors(floor_ids = floor_ids)
            wanted_floors = []
            for _, floor_id in enumerate(car.stop_floor_ids):
                if floor_id in self.original_floor_ids:
                    wanted_floors.append(floor_id)
            car.stop_floor_ids = list(set(stops+wanted_floors))
            car.stop_floor_ids.sort()
            
    def __init_origin_floor_percentages(self)->None:
        """将各个出发楼层乘客占比按均匀分布赋初值"""
        percentage = 1.0/len(self.original_floor_ids)
        self.set_origin_floor_percentages(origin_floors={self.floors[f_id]:percentage 
                                                         for f_id in self.original_floor_ids})
        
    def __update_origin_floors(self, car:Car)->None:
        """如果轿厢是双轿厢，且第1层是停机楼层，则将第二层也作为出发楼层"""
        if car.car_type == CarType.DOUBLE:
            if self.floors[1].id in car.stop_floor_ids:
                self.set_floor_as_origin(floor_id=self.floors[2].id)
    
    def __single_car_from_to_floor_pairs(self,passengers:list[Passenger])->list[(Floor, Floor)]:
        """将乘梯的乘客形成（出发，目的）对"""
        floor_from_ids = [p.floor_from.id for p in passengers]
        floor_to_ids = [p.floor_to.id for p in passengers]
        floor_ids = floor_from_ids + floor_to_ids
        floor_ids = list(set(floor_ids))
        floor_ids.sort()
        num_floors = len(floor_ids)

        return [(floor_ids[i], floor_ids[i+1]) for i in range(num_floors-1)]
    
    def __double_car_from_to_floor_pairs(self,
                                         passengers:list[Passenger], 
                                         car:Car)->list[(Floor, Floor)]:
        floor_ids = []
        stop_floor_ids = self.car_stop_floor_ids(car=car)
        stop_floor_pair_ids = [(self.floors[f_id].id, 
                             self.get_above_floor(self.floors[f_id]).id) 
                             for f_id in stop_floor_ids]
        for p in passengers:
            for f_pair_id in stop_floor_pair_ids:
                if p.floor_from.id in f_pair_id:
                    floor_ids.append(f_pair_id[0])
                elif p.floor_to.id in f_pair_id:
                    floor_ids.append(f_pair_id[0])
        floor_ids = list(set(floor_ids))
        floor_ids.sort()
        num_floors = len(floor_ids)

        return [(floor_ids[i], floor_ids[i+1]) for i in range(num_floors-1)]


    def _set_car_stop_floors(self, car:Car)->None:
        if car not in self.cars:
            raise CarNotInBuildingError
        if car.car_type == CarType.SINGLE:
            car.stop_floor_ids = self.floor_ids
        if car.car_type == CarType.DOUBLE:
            car.stop_floor_ids = self._set_double_car_stop_floors(floor_ids = self.floor_ids)
    
    def _set_double_car_stop_floors(self, floor_ids:list)->list:
        num_floors = len(floor_ids)
        if num_floors < 3:
            raise ValueError('双子轿厢的楼层数必须大于等于3')
        if (num_floors%2) == 0: # 总楼层数是偶数
            return [floor_id for i, floor_id 
                    in enumerate(floor_ids) if i%2 == 0]
        else:                  # 总楼层数是奇数
            stops = [floor_id for i, floor_id 
                    in enumerate(floor_ids) 
                    if (i%2 == 0 and i < (num_floors-3))]
            # 确保最高层能有轿厢到达，且不发生轿厢外溢
            return stops+[floor_ids[-1]-2, floor_ids[-1]-1] 

    def _set_transition_matrix(self, car:Car)->dict:
        ttm = {}
        ind_floors = self.floor_ids
        num_floors = len(ind_floors)

        def bound_1()->float:
            return 2*pow(car.a, 3)/pow(car.jerk, 2)
        
        def bound_2()->float:
            return (pow(car.a, 2)*car.v + pow(car.v, 2)*car.jerk)/(car.a*car.jerk)
        
        def distance_travel_time(d:float, b1:float, b2:float)->float:
            if d >= b2:
                return d/car.v + car.v/car.a + car.a/car.jerk 
            elif d < b1:
                return pow(32*d/car.jerk, 1/3)
            else:
                return car.a/car.jerk + sqrt(4*d/car.a + pow(car.a/car.jerk, 2))
        b1 = bound_1()
        b2 = bound_2()
        if b2 <= b1:
            raise ValueError('parameters of car are wrong')

        for i in range(num_floors-1):
            for j in range(i, num_floors):
                if j == i:
                    ttm[(self.floors[ind_floors[i]], 
                         self.floors[ind_floors[j]])] = 0.0 # 同一楼层的运行时间设为0
                else:
                    d = self.get_two_floors_height(self.floors[ind_floors[i]], 
                                                   self.floors[ind_floors[j]])
                    t = round(distance_travel_time(d=d, b1=b1, b2=b2), 2)
                    ttm[(self.floors[ind_floors[i]], 
                        self.floors[ind_floors[j]])] = t
                    ttm[(self.floors[ind_floors[j]], 
                        self.floors[ind_floors[i]])] = t
        return ttm
    
    def set_floor_height(self, 
                         floor_id:int, 
                         height:float)->None:
        if floor_id in self._floors:
            self._floors[floor_id].height = height
            
        else: 
            raise FloorIdError(floor_id = floor_id)
        
    def set_floor_num_passengers(self, 
                                 floor:Floor, 
                                 num_passengers:int)->None:
        if floor.id in self.floor_ids:
            self._floors[floor.id].num_passengers = num_passengers
        else:
            raise FloorIdError(floor_id = floor.id)
    
    def set_floor_as_origin(self, floor_id:int)->None:
        if floor_id in self._floors:
            self._floors[floor_id].is_origin = True 
        else:
            raise FloorIdError(floor_id = floor_id)
    
    def set_floor_as_non_origin(self, floor_id:int)->None:
        if floor_id in self._floors:
            self._floors[floor_id].is_origin = False 
        else:
            raise FloorIdError(floor_id = floor_id)
        
    def set_floors_as_origin(self, floors:list[int])->None:
        for floor in floors:
            self.set_floor_as_origin(floor)

    def set_origin_floor_percentage(self, floor_id:int, percentage:float)->None:
        if len(self.cars) == 0:
            raise NoCarInBuildingError('建筑内没有注册轿厢')
        if percentage > 1.0 or percentage < 0.0:
            raise ValueError('value must between 0 and 1')
        if floor_id in self.original_floor_ids:
            self._floors[floor_id].origin_floor_percentage = percentage 
        else:
            raise OriginFloorIdError(floor_id = floor_id)
    
    def set_origin_floor_percentages(self, 
                                     origin_floors:dict[Floor:float])->None:
        norm_sum = fsum(origin_floors.values())
        if norm_sum != 1:
            raise ValueError("norm_sum must be one") 
        for origin_floor, percentage in origin_floors.items():
            self.set_origin_floor_percentage(origin_floor.id, percentage/norm_sum) 

    def get_travel_time_between_floors(self, 
                                       car:Car, 
                                       from_floor:Floor, 
                                       to_floor:Floor)->float:
        if car not in  self.cars:
            raise CarNotInBuildingError
        if from_floor.id not in self.floors:
            raise FloorError("from floor error")
        if to_floor.id not in self.floors:
            raise FloorError("to floor error")
        if (from_floor, to_floor) not in self._car_transition_matrixs[car.id]:
            raise FloorError("(from floor, to floor) error")
        return self._car_transition_matrixs[car.id][(from_floor, to_floor)]
    
    def get_two_floors_height(self, from_floor:Floor, to_floor:Floor)->float:
        if from_floor.id > to_floor.id:
            raise ValueError('to_floor must be greater than from_floor')
        # 浮点数的内部表示方式是有限的，因此在进行浮点数计算时可能会出现误差
        return round(fsum([self.get_floor_height(self.floor_ids[i]) 
                    for i in range(self.floor_ids.index(from_floor.id), 
                                          self.floor_ids.index(to_floor.id))]), 2)

    def get_floor_height(self, floor_id:int)->float:
        if floor_id in self._floors:
            return self._floors[floor_id].height
        else:
            return -1
        
    def get_floor_num_passengers(self, floor:Floor)->int:
        if floor.id in self.floor_ids:
            return self._floors[floor.id].num_passengers
        else:
            raise FloorError(floor.id)
    
    def car_stop_floor_ids(self, car:Car)->list:
        if car not in self.cars:
            raise CarNotInBuildingError
        return car.stop_floor_ids
    
    def check_serve_stops(self)->bool:
        """TODO 检查建筑内各个轿厢的停机是否覆盖到所有楼层"""
        ...
    
    def get_below_floor(self, current_floor:Floor)->Floor:
        below_id = self.floor_ids.index(current_floor.id)
        if below_id == 0:#溢出楼层
            return None 
        else:
            return self.floors[self.floor_ids[below_id-1]]
        
    def get_above_floor(self, current_floor:Floor)->Floor:
        above_id = self.floor_ids.index(current_floor.id)
        if current_floor.id >= self.floor_ids[-1]:#溢出楼层
            return None 
        else:
            return self.floors[self.floor_ids[above_id+1]]
        
    @property
    def floor_num_passengers(self)->dict[Floor:int]:
        return OrderedDict((floor,floor.num_passengers) 
                           for _, floor in self.floors.items())
    
    @property
    def total_num_passengers(self)->int:
        return sum(list(self.floor_num_passengers.values()))
    
    @property
    def cars(self)->list:
        return self._cars
     
    @property
    def original_floor_ids(self)->list:
        return [floor.id for floor in self._floors.values() if floor.is_origin == True]
    
    @property
    def floor_ids(self)->list:
        return list(self._floors.keys())
    
    @property
    def floors(self)->dict:
        return self._floors
    
    @property 
    def num_floors(self)->int:
        return len(self._floors)
    
    @property
    def origin_floor_percentages(self)->dict:
        percentages = [self.floors[origin_floor].origin_floor_percentage 
                       for origin_floor in self.original_floor_ids]
        return OrderedDict((self.floors[k],v) for (k, v) in 
                           zip(self.original_floor_ids, percentages) )





