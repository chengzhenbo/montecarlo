from src.building import Building  
from src.passenger import Passenger
from src.car import Car,CarType


import numpy as np


def generate_passengers(building:Building, 
                        car:Car,
                        num_passengers:int=0)->tuple[list[Passenger], int]:

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
    
    arival_floors = list(building.origin_floor_percentages.keys())
    arival_probs = list(building.origin_floor_percentages.values())
    dest_floors = np.random.choice(dest_floors, num_passengers, p=dest_probs)
    arival_floors = np.random.choice(arival_floors, num_passengers, p=arival_probs)
    if car.car_type == CarType.SINGLE:
        passengers = passengers_in_singlecar(arival_floors = arival_floors, 
                                             dest_floors = dest_floors)
    if car.car_type == CarType.DOUBLE:
        passengers = passengers_in_doublecar(building = building, 
                                             car = car, 
                                             arival_floors = arival_floors, 
                                             dest_floors = dest_floors)
    gpassengers = passengers[0]
    num_passengers_set = (len(gpassengers), 0)
    if len(passengers)>1:
        gpassengers = passengers[0] + passengers[1]
        num_passengers_set = (len(passengers[0]), len(passengers[1]))

    return (gpassengers, num_passengers_set)

def passengers_in_singlecar(arival_floors:list, dest_floors:list)->list[Passenger]:
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

   


