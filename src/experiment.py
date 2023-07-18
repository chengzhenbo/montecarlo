from src.building import Building  
from src.passenger import Passenger
from src.car import Car,CarType


import numpy as np


def generate_passengers(building:Building, 
                        car:Car,
                        num_passengers:int=0)->tuple[list[Passenger], int]:
    """根据建筑和轿厢随机生成数量为num_passengers的乘客。
        双轿厢最后输出的乘客数量可能小于num_passengers
    Args:
        building (Building): 建筑对象
        car (Car): 轿厢对象
        num_passengers (int, optional): 生成的乘客数量. Defaults to 0.

    Returns:
        tuple[list[Passenger], int]: 乘客与数量对
    """
    if car.car_type == CarType.DOUBLE:
        num_passengers = num_passengers*2
    # 得到轿厢除去到达层之外的停机楼层
    dest_floors = [building.floors[f_id] 
                   for f_id in car.serve_floor_ids 
                   if f_id not in building.original_floor_ids]
    # 得到这些停机楼层的总乘客数
    total_passengers = sum([building.floor_num_passengers[d_f] 
                            for d_f in  dest_floors])
    # 计算每一个停机楼层的概率
    dest_probs = [building.floor_num_passengers[d_f]/total_passengers  
                        for d_f in dest_floors]
    # 乘客到达楼层列表
    arival_floors = list(building.origin_floor_percentages.keys())
    # 乘客到达楼层的到达比率
    arival_probs = list(building.origin_floor_percentages.values())

    # 从目的楼层和目的楼层的人数占比随机生成目的楼层序列
    dest_floors = np.random.choice(dest_floors, num_passengers, p=dest_probs)
    # 从到达楼层和到达楼层人数比率随机生成到达楼层序列
    arival_floors = np.random.choice(arival_floors, num_passengers, p=arival_probs)
    if car.car_type == CarType.SINGLE:
        passengers = passengers_in_singlecar(arival_floors = arival_floors, 
                                             dest_floors = dest_floors)
    if car.car_type == CarType.DOUBLE:
        passengers = passengers_in_doublecar(building = building, 
                                             car = car, 
                                             arival_floors = arival_floors, 
                                             dest_floors = dest_floors)
    # 根据单轿厢或者双轿厢的输出，形成统一的输出格式
    gpassengers = passengers[0]
    num_passengers_set = (len(gpassengers), 0)
    if len(passengers)>1:
        gpassengers = passengers[0] + passengers[1]
        num_passengers_set = (len(passengers[0]), len(passengers[1]))

    return (gpassengers, num_passengers_set)

def passengers_in_singlecar(arival_floors:list, dest_floors:list)->list[Passenger]:
    """单轿厢乘客添加：将到达楼层和目的楼层形成数据对，再由数据对生成新的乘客

    Args:
        arival_floors (list): 到达楼层列表
        dest_floors (list): 目的楼层列表

    Returns:
        list[Passenger]: 乘客列表
    """
    k = 0
    passengers = []
    for af, df in zip(arival_floors, dest_floors):
        passengers.append(Passenger(id = k, 
                                    floor_from=af, 
                                    floor_to=df))
        k += 1
    return [passengers]
    
def passengers_in_doublecar(building:Building, 
                        car:Car,
                        arival_floors:list, 
                        dest_floors:list)->list[Passenger]:
    """双轿厢乘客添加。
       1）根据楼层单双生成将建筑的可出发楼层分为上轿厢服务楼层与下轿厢服务楼层
       2）根据到达乘客所属上轿厢服务楼层/下轿厢服务楼层，将乘客分别置于上下轿厢中
          同时确保上/下轿厢的总人数都小于等于各轿厢的容量。
          - 如果乘客都是到达上轿厢服务楼层，那么进入轿厢的人数将小于到达/目的楼层数
    Args:
        building (Building): 建筑对象
        car (Car): 轿厢对象
        arival_floors (list): 到达楼层
        dest_floors (list): 目的楼层

    Returns:
        list[Passenger]: 乘客列表
    """
    inner_passengers_downcar = []
    inner_passengers_upcar = []

    downcar_serve_origin_floors, upcar_serve_origin_floors = [], []
    for i, f_id in enumerate(building.original_floor_ids):
        (downcar_serve_origin_floors, 
         upcar_serve_origin_floors)[i%2 == 0].append(building.floors[f_id])
    
    k = 0
    for af, df in zip(arival_floors, dest_floors):
        if (af in downcar_serve_origin_floors 
        and len(inner_passengers_downcar)<car.capacity):
            p = Passenger(id = k, 
                        floor_from=af, 
                        floor_to=df)
            inner_passengers_downcar.append(p)
        elif (af in upcar_serve_origin_floors 
        and len(inner_passengers_upcar)<car.capacity):
            p = Passenger(id = k, 
                        floor_from=af, 
                        floor_to=df)
            inner_passengers_upcar.append(p)
        k += 1
    return [inner_passengers_downcar,inner_passengers_upcar]

   


