from dataclasses import dataclass

@dataclass
class Floor():
    id:int = 1
    height:float = 0.0
    num_passengers:int = 0
    is_origin:bool = False
    origin_floor_percentage:float = 0.0
    
    def __hash__(self) -> int:
        return self.id.__hash__()