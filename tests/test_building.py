import pytest
from src.building import Building
from src.car import Car, CarType
from src.exception import FloorError,FloorIdError

def test_building_floor_heights()->None:
    b1 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    assert b1.floor_ids == [-2, -1, 1, 2], '楼层设置'
    assert b1.get_floor_id_height(-1) == 3.1, '楼层高度'
    with pytest.raises(FloorIdError, match='楼层编号100不在楼层编号范围内'):
        assert b1.get_floor_id_height(100), '楼层高度'
    b1.set_floor_height(1, 4.2)
    assert b1.get_floor_id_height(1) == 4.2, '楼层新高度'
    with pytest.raises(ValueError, match='to_floor must be greater than from_floor'):
        b1.get_two_floors_height(b1.floors[1], b1.floors[-1])
    assert b1.get_two_floors_height(b1.floors[-1], b1.floors[-1]) == 0.0, '两楼层之间距离'
    assert b1.get_two_floors_height(b1.floors[1], b1.floors[1]) == 0.0, '两楼层之间距离'
    assert b1.get_two_floors_height(b1.floors[-1], b1.floors[1]) == 3.1, '两楼层之间距离'
    assert b1.get_two_floors_height(b1.floors[-1], b1.floors[2]) == 7.3, '两楼层之间距离'

def test_building_floor_num_passengers():
    b1 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    with pytest.raises(Exception):
        b1.get_floor_num_passengers(floor=b1.floors[4])
    assert b1.get_floor_num_passengers(floor=b1.floors[1]) == 0, '某楼层的人数'
    b1.set_floor_num_passengers(floor = b1.floors[2], num_passengers=23),'设定某个楼层人数'
    assert b1.get_floor_num_passengers(floor=b1.floors[2]) == 23, '某楼层的人数'
    assert b1.floor_num_passengers == {b1.floors[-2]:0,
                                       b1.floors[-1]:0,
                                       b1.floors[1]:0,
                                       b1.floors[2]:23}

def test_building_origin_floor_percentage():
    b1 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    car1 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.SINGLE
              )
    b1.register_car(car1)
    with pytest.raises(Exception):
        b1.set_origin_floor_percentage(floor_id=-1, percentage=1.1)
    with pytest.raises(ValueError, match='value must between 0 and 1'):
        b1.set_origin_floor_percentage(floor_id=-1, percentage=-0.1)
    
    b1.set_origin_floor_percentage(floor_id=-1, percentage=0.75)
    assert b1.floors[-1].origin_floor_percentage == 0.75
    b1.set_origin_floor_percentages(origin_floors={b1.floors[-2]:0.3, 
                                                   b1.floors[-1]:0.2, 
                                                   b1.floors[1]:0.5})
    assert sum(b1.origin_floor_percentages.values()) == 1, '归一化出发楼层的比率'

def test_building_init_originfloors():
    b1 = Building(a_num_floors=20, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    assert b1.original_floor_ids == [-2, -1, 1], '建筑的出发楼层'
    b1.set_floor_as_origin(floor_id=2)
    assert b1.floors[2].is_origin == True, '楼层是出发层'
    assert b1.floors[-1].is_origin == True, '楼层是出发层'
    assert b1.original_floor_ids == [-2, -1, 1, 2], '楼层所有的出发层'
    b1.set_floor_as_non_origin(floor_id=2)
    b1.set_floor_as_non_origin(floor_id=1)
    assert b1.original_floor_ids == [-2, -1], '楼层所有的出发层'
    b1.set_floors_as_origin(floors = [1, 2])
    assert b1.original_floor_ids == [-2, -1, 1, 2], '楼层所有的出发层'

def test_building_set_singlecar_service_floor():
    b1 = Building(a_num_floors=10, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    car1 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.SINGLE
              ) 
    car2 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.SINGLE
              )
    b1.register_car(car1)
    b1.register_car(car2)
    assert b1.car_stop_floor_ids(car1) == [i for i in range(-2, 11) if i != 0], 'car1的停机楼层id'
    assert b1.car_stop_floor_ids(car2) == [i for i in range(-2, 11) if i != 0], 'car2的停机楼层id'
    b1.set_car_service_floor_range(car1, b1.floors[1], b1.floors[5])
    assert b1.car_stop_floor_ids(car1) == [-2, -1, 1, 2, 3, 4, 5], 'car1的停机楼层id'
    b1.set_car_service_floor_range(car2, b1.floors[6], b1.floors[10])
    assert b1.car_stop_floor_ids(car2) == [-2, -1, 1, 6, 7, 8, 9, 10], 'car1的停机楼层id'

def test_building_set_doublecar_service_floor():
    b1 = Building(a_num_floors=10, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b2 = Building(a_num_floors=11, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    car1 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              ) 
    car2 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              )
    b1.register_car(car1)
    b1.register_car(car2)
    assert b1.car_stop_floor_ids(car1) == [-2, 1, 3, 5, 7, 9], 'car1的停机楼层id'
    assert b1.car_stop_floor_ids(car2) == [-2, 1, 3, 5, 7, 9], 'car2的停机楼层id'
    b1.set_car_service_floor_range(car1, b1.floors[1], b1.floors[5])
    assert b1.car_stop_floor_ids(car1) == [-2, 1, 3, 4], 'car1的停机楼层id'
    b1.set_car_service_floor_range(car2, b1.floors[6], b1.floors[10])
    assert b1.car_stop_floor_ids(car2) == [-2, 1, 6, 8, 9], 'car2的停机楼层id'

    b2.register_car(car1)
    b2.register_car(car2)
    assert b2.car_stop_floor_ids(car1) == [-2, 1, 3, 5, 7, 9, 10], 'car1的停机楼层id'
    assert b2.car_stop_floor_ids(car2) == [-2, 1, 3, 5, 7, 9, 10], 'car2的停机楼层id'
    b2.set_car_service_floor_range(car1, b2.floors[1], b2.floors[5])
    assert b2.car_stop_floor_ids(car1) == [-2, 1, 3, 4], 'car1的停机楼层id'
    b2.set_car_service_floor_range(car2, b2.floors[6], b2.floors[11])
    assert b2.car_stop_floor_ids(car2) == [-2, 1, 6, 8, 10], 'car2的停机楼层id'

def test_building_car()->None:
    car1 = Car(id=1,
              v=8, 
              a=1, 
              jerk=0.6, 
              capacity=13
              ) 
    b2 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b2.register_car(car1)
    assert b2.cars[0] == car1, '给建筑添加轿厢'
    
def test_building_car_traveltime()->None:
    car1 = Car(id=1,
              v=8, 
              a=1, 
              jerk=0.6, 
              capacity=13
              ) 
    car2 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              ) 
    b2 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b2.register_car(car1)
    assert b2.cars[0] == car1, '给建筑添加轿厢'
    with pytest.raises(Exception):
        b2.get_travel_time_between_floors(car2, b2.floors[-1], b2.floors[2])
    with pytest.raises(Exception):
        b2.get_travel_time_between_floors(car1, b2.floors[-3], b2.floors[2])
    with pytest.raises(Exception):
        b2.get_travel_time_between_floors(car1, b2.floors[-3], b2.floors[3])
    with pytest.raises(Exception):
        b2.get_travel_time_between_floors(car1, b2.floors[3], b2.floors[-3])

    assert b2.get_travel_time_between_floors(car1, b2.floors[-1], b2.floors[-1]) == 0.0, '楼层运行时间'
    assert b2.get_travel_time_between_floors(car1, b2.floors[1], b2.floors[1]) == 0.0, '楼层运行时间'
    assert b2.get_travel_time_between_floors(car1, b2.floors[-1], b2.floors[1]) == 5.49, '楼层运行时间'
    assert b2.get_travel_time_between_floors(car1, b2.floors[1], b2.floors[-1]) == 5.49, '楼层运行时间'
    assert b2.get_travel_time_between_floors(car1, b2.floors[-1], b2.floors[2]) == 6.92, '楼层运行时间'
    assert b2.get_travel_time_between_floors(car1, b2.floors[-2], b2.floors[2]) == 7.99, '楼层运行时间'

def test_building_car_stops()->None: 
    car1 = Car(id=1,
              v=8, 
              a=1, 
              jerk=0.6, 
              capacity=13
              ) 
    car2 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              ) 
    b2 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b3 = Building(a_num_floors=2, 
                  b_num_floors=0, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b4 = Building(a_num_floors=6, 
                  b_num_floors=1, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b2.register_car(car1)   
    with pytest.raises(Exception):
        b2.car_stop_floor_ids(car2)
    assert b2.car_stop_floor_ids(car1) == [-2, -1, 1, 2], '单轿厢的可停机楼层'
    b2.register_car(car2)
    assert b2.car_stop_floor_ids(car2) == [-2, 1], '双子轿厢总楼层为偶数情况下的可停机楼层'
    with pytest.raises(Exception):
        b3.register_car(car2)
    b4.register_car(car2)
    assert b4.car_stop_floor_ids(car2) == [-1, 2, 4, 5], '双子轿厢总楼层为奇数情况下的可停机楼层'

def test_original_floors_update():
    car1 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              ) 
    b1 = Building(a_num_floors=2, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12) 
    
    assert b1.original_floor_ids == [-2, -1, 1]
    b1.register_car(car1)
    car1.stop_floor_ids == [-2, 1]
    assert b1.original_floor_ids == [-2, -1, 1, 2]

def test_next_prev_floor()->None:
    b1 = Building(a_num_floors=5, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12) 
    assert b1.get_above_floor(b1.floors[5]) == None, '最高楼层'
    assert b1.get_below_floor(b1.floors[-2]) == None, '最低楼层'
    assert b1.get_above_floor(b1.floors[4]) == b1.floors[5], '高一层'
    assert b1.get_below_floor(b1.floors[-1]) == b1.floors[-2], '低一层'

def test_double_car_origin_floors()->None:
    b1 = Building(a_num_floors=5, 
                  b_num_floors=2, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12) 
    b2 = Building(a_num_floors=5, 
                  b_num_floors=0, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12) 
    b3 = Building(a_num_floors=5, 
                  b_num_floors=1, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b4 = Building(a_num_floors=5, 
                  b_num_floors=3, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    b5 = Building(a_num_floors=5, 
                  b_num_floors=4, 
                  avg_floor_height=3.1, 
                  avg_floor_num_passengers=12)
    car1 = Car(id=2,
              v=8, 
              a=1, 
              jerk=6, 
              capacity=13,
              car_type=CarType.DOUBLE
              ) 
    b1.register_car(car1)
    assert b1.original_floor_ids == [-2, -1, 1, 2]

    b2.register_car(car1)
    assert b2.original_floor_ids == [1, 2]

    b3.register_car(car1)
    assert b3.original_floor_ids == [-1, 1]

    b4.register_car(car1)
    assert b4.original_floor_ids == [-3, -2, -1, 1]

    b5.register_car(car1)
    assert b5.original_floor_ids == [-4, -3, -2, -1, 1, 2]