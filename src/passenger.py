from dataclasses import dataclass

from src.floor import Floor

@dataclass
class Passenger():
    id: int 
    floor_from: Floor 
    floor_to: Floor 


