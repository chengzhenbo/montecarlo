from src.building import Building
from src.car import Car, CarType
from src.experiment import generate_passengers

import numpy as np

def test_onecar()->None:
    b1 = Building(a_num_floors=42, 
                b_num_floors=0, 
                avg_floor_height=4.2, 
                avg_floor_num_passengers=125)
    car1 = Car(id=1,
                v=8, 
                a=1, 
                jerk=1, 
                capacity=13,
                car_type=CarType.SINGLE) 
    car2 = Car(id=2,
                v=8, 
                a=1, 
                jerk=1, 
                capacity=13,
                car_type=CarType.SINGLE)
    # b1.set_floor_num_passengers(floor=b1.floors[23], num_passengers=0)
    b1.register_car(car = car1)
    b1.register_car(car = car2)
    print('building num passengers = ', b1.total_num_passengers)

    b1.set_car_service_floor_range(car=b1.cars[0], 
                                start_floor=b1.floors[1], 
                                end_floor=b1.floors[24])

    b1.set_car_service_floor_range(car=b1.cars[1], 
                                start_floor=b1.floors[25], 
                                end_floor=b1.floors[42])

    rtts_1 = []
    rtts_2 = []
    num_passengers_list1 = []
    num_passengers_list2 = []
    passengers_1_c, num_passengers_1_c = generate_passengers(b1, 
                                                             b1.cars[0], 
                                                             num_passengers=car1.capacity)
    passengers_2_c, num_passengers_2_c = generate_passengers(b1, 
                                                             b1.cars[1], 
                                                             num_passengers=car2.capacity)
    num_trials = 10000
    for _ in range(num_trials):
        passengers_1_n,num_passengers_1_n = generate_passengers(b1, 
                                                                b1.cars[0], 
                                                                num_passengers=car1.capacity)
        passengers_2_n,num_passengers_2_n = generate_passengers(b1, 
                                                                b1.cars[1], 
                                                                num_passengers=car2.capacity)

        back_floor_id_1 = min([p.floor_from.id for p in passengers_1_n])
        back_floor_id_2 = min([p.floor_from.id for p in passengers_2_n])

        rtt_1 = b1.get_round_trip_time(passengers=passengers_1_c, 
                                    car = b1.cars[0], 
                                    back_floor=b1.floors[back_floor_id_1],
                                    num_passengers_set=num_passengers_1_c)
        rtt_2 = b1.get_round_trip_time(passengers=passengers_2_c, 
                                    car = b1.cars[1], 
                                    back_floor=b1.floors[back_floor_id_2],
                                    num_passengers_set=num_passengers_2_c)
        num_passengers_list1.append(num_passengers_1_c[0])
        num_passengers_list2.append(num_passengers_2_c[0])

        passengers_1_c = passengers_1_n
        passengers_2_c = passengers_2_n
        num_passengers_1_c = num_passengers_1_n
        num_passengers_2_c = num_passengers_2_n
        rtts_1.append(rtt_1)
        rtts_2.append(rtt_2)

    print('rtt1= ', np.average(rtts_1))
    print('rtt2= ', np.average(rtts_2))
    print('num_passengers_1= ', np.average(num_passengers_list1))
    print('num_passengers_2= ', np.average(num_passengers_list2))

def test_doublecar():
    b1 = Building(a_num_floors=42, 
                b_num_floors=1, 
                avg_floor_height=4.2, 
                avg_floor_num_passengers=125)
    car1 = Car(id=1,
                v=8, 
                a=1.0, 
                jerk=1.0, 
                capacity=16,
                car_type=CarType.DOUBLE) 
    car2 = Car(id=2,
                v=8, 
                a=1.0, 
                jerk=1.0, 
                capacity=13,
                car_type=CarType.DOUBLE)   
    # b1.set_floor_num_passengers(floor=b1.floors[23], num_passengers=0) 
    b1.register_car(car = car1)
    b1.register_car(car = car2)
    print('building num passengers = ', b1.total_num_passengers)
   
    b1.set_car_service_floor_range(car=b1.cars[0], 
                                start_floor=b1.floors[1], 
                                end_floor=b1.floors[24])

    b1.set_car_service_floor_range(car=b1.cars[1], 
                                start_floor=b1.floors[25], 
                                end_floor=b1.floors[42])
    print('car1 stop floors = ', b1.car_stop_floor_ids(car=car1))
    print('car2 stop floors = ', b1.car_stop_floor_ids(car=car2))
    rtts_1 = []
    rtts_2 = []
    num_passengers_list1 = []
    num_passengers_list2 = []
    passengers_1_c, num_passengers_1_c = generate_passengers(b1, 
                                                             b1.cars[0], 
                                                             num_passengers=car1.capacity)
    passengers_2_c, num_passengers_2_c = generate_passengers(b1, 
                                                             b1.cars[1], 
                                                             num_passengers=car2.capacity)
    num_trials = 10000
    for _ in range(num_trials):
        passengers_1_n, num_passengers_1_n= generate_passengers(b1, b1.cars[0], 
                                                                num_passengers=car1.capacity)
        passengers_2_n, num_passengers_2_n = generate_passengers(b1, b1.cars[1], 
                                                                 num_passengers=car2.capacity)

        back_floor_id_1 = min([p.floor_from.id for p in passengers_1_n])
        back_floor_id_2 = min([p.floor_from.id for p in passengers_2_n])

        rtt_1 = b1.get_round_trip_time(passengers=passengers_1_c, 
                                    car = b1.cars[0], 
                                    back_floor=b1.floors[back_floor_id_1], 
                                    num_passengers_set=num_passengers_1_c)
        rtt_2 = b1.get_round_trip_time(passengers=passengers_2_c, 
                                    car = b1.cars[1], 
                                    back_floor=b1.floors[back_floor_id_2], 
                                    num_passengers_set=num_passengers_2_c)
        num_passengers_list1.append(sum(num_passengers_1_c))
        num_passengers_list2.append(sum(num_passengers_2_c))
        passengers_1_c = passengers_1_n
        passengers_2_c = passengers_2_n

        num_passengers_1_c = num_passengers_1_n
        num_passengers_2_c = num_passengers_2_n
        rtts_1.append(rtt_1)
        rtts_2.append(rtt_2)

    print(np.average(rtts_1))
    print(np.average(rtts_2))
    print('num_passengers_1= ', np.average(num_passengers_list1))
    print('num_passengers_2= ', np.average(num_passengers_list2))

def test_standard_onecar()->None:
    b1 = Building(a_num_floors=27, 
                b_num_floors=0, 
                avg_floor_height=4.0, 
                avg_floor_num_passengers=84)
    car1 = Car(id=1,
                v=2.5, 
                a=1, 
                jerk=1, 
                capacity=13,
                car_type=CarType.SINGLE) 
    car2 = Car(id=2,
                v=5, 
                a=1, 
                jerk=1, 
                capacity=13,
                car_type=CarType.SINGLE)

    b1.register_car(car = car1)
    b1.register_car(car = car2)
    print('building num passengers = ', b1.total_num_passengers)

    b1.set_car_service_floor_range(car=b1.cars[0], 
                                start_floor=b1.floors[1], 
                                end_floor=b1.floors[14])

    b1.set_car_service_floor_range(car=b1.cars[1], 
                                start_floor=b1.floors[15], 
                                end_floor=b1.floors[27])

    rtts_1 = []
    rtts_2 = []
    num_passengers_list1 = []
    num_passengers_list2 = []
    passengers_1_c, num_passengers_1_c = generate_passengers(b1, 
                                                             b1.cars[0], 
                                                             num_passengers=car1.capacity)
    passengers_2_c, num_passengers_2_c = generate_passengers(b1, 
                                                             b1.cars[1], 
                                                             num_passengers=car2.capacity)
    num_trials = 10000
    for _ in range(num_trials):
        passengers_1_n,num_passengers_1_n = generate_passengers(b1, 
                                                                b1.cars[0], 
                                                                num_passengers=car1.capacity)
        passengers_2_n,num_passengers_2_n = generate_passengers(b1, 
                                                                b1.cars[1], 
                                                                num_passengers=car2.capacity)

        back_floor_id_1 = min([p.floor_from.id for p in passengers_1_n])
        back_floor_id_2 = min([p.floor_from.id for p in passengers_2_n])

        rtt_1 = b1.get_round_trip_time(passengers=passengers_1_c, 
                                    car = b1.cars[0], 
                                    back_floor=b1.floors[back_floor_id_1],
                                    num_passengers_set=num_passengers_1_c)
        rtt_2 = b1.get_round_trip_time(passengers=passengers_2_c, 
                                    car = b1.cars[1], 
                                    back_floor=b1.floors[back_floor_id_2],
                                    num_passengers_set=num_passengers_2_c)
        num_passengers_list1.append(num_passengers_1_c[0])
        num_passengers_list2.append(num_passengers_2_c[0])

        passengers_1_c = passengers_1_n
        passengers_2_c = passengers_2_n
        num_passengers_1_c = num_passengers_1_n
        num_passengers_2_c = num_passengers_2_n
        rtts_1.append(rtt_1)
        rtts_2.append(rtt_2)

    print('rtt1= ', np.average(rtts_1))
    print('rtt2= ', np.average(rtts_2))
    print('num_passengers_1= ', np.average(num_passengers_list1))
    print('num_passengers_2= ', np.average(num_passengers_list2))

def test_standard_doublecar():
    b1 = Building(a_num_floors=27, 
                b_num_floors=0, 
                avg_floor_height=4.0, 
                avg_floor_num_passengers=84)
    car1 = Car(id=1,
                v=2.5, 
                a=1.0, 
                jerk=1.0, 
                capacity=13,
                car_type=CarType.DOUBLE) 
    car2 = Car(id=2,
                v=5.0, 
                a=1.0, 
                jerk=1.0, 
                capacity=13,
                car_type=CarType.DOUBLE)    
    b1.register_car(car = car1)
    b1.register_car(car = car2)
    print('building num passengers = ', b1.total_num_passengers)
   

    b1.set_car_service_floor_range(car=b1.cars[0], 
                                start_floor=b1.floors[1], 
                                end_floor=b1.floors[14])

    b1.set_car_service_floor_range(car=b1.cars[1], 
                                start_floor=b1.floors[15], 
                                end_floor=b1.floors[27])
    print('car1 stop floors = ', b1.car_stop_floor_ids(car=car1))
    print('car2 stop floors = ', b1.car_stop_floor_ids(car=car2))
    rtts_1 = []
    rtts_2 = []
    num_passengers_list1 = []
    num_passengers_list2 = []
    passengers_1_c, num_passengers_1_c = generate_passengers(b1, 
                                                             b1.cars[0], 
                                                             num_passengers=car1.capacity)
    passengers_2_c, num_passengers_2_c = generate_passengers(b1, 
                                                             b1.cars[1], 
                                                             num_passengers=car2.capacity)
    num_trials = 10000
    for _ in range(num_trials):
        passengers_1_n, num_passengers_1_n= generate_passengers(b1, b1.cars[0], 
                                                                num_passengers=car1.capacity)
        passengers_2_n, num_passengers_2_n = generate_passengers(b1, b1.cars[1], 
                                                                 num_passengers=car2.capacity)

        back_floor_id_1 = min([p.floor_from.id for p in passengers_1_n])
        back_floor_id_2 = min([p.floor_from.id for p in passengers_2_n])

        rtt_1 = b1.get_round_trip_time(passengers=passengers_1_c, 
                                    car = b1.cars[0], 
                                    back_floor=b1.floors[back_floor_id_1], 
                                    num_passengers_set=num_passengers_1_c)
        rtt_2 = b1.get_round_trip_time(passengers=passengers_2_c, 
                                    car = b1.cars[1], 
                                    back_floor=b1.floors[back_floor_id_2], 
                                    num_passengers_set=num_passengers_2_c)
        num_passengers_list1.append(sum(num_passengers_1_c))
        num_passengers_list2.append(sum(num_passengers_2_c))
        passengers_1_c = passengers_1_n
        passengers_2_c = passengers_2_n

        num_passengers_1_c = num_passengers_1_n
        num_passengers_2_c = num_passengers_2_n
        rtts_1.append(rtt_1)
        rtts_2.append(rtt_2)

    print(np.average(rtts_1))
    print(np.average(rtts_2))
    print('num_passengers_1= ', np.average(num_passengers_list1))
    print('num_passengers_2= ', np.average(num_passengers_list2))

def main() -> None:
    test_standard_onecar() # test
    # test_standard_doublecar()
    # test_onecar()
    # test_doublecar()

if __name__ == "__main__":
    main()    



