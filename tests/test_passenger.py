import pytest
from src.passenger import Passenger 


def test_passenger()->None:
    p = Passenger(id = 1, floor_from=2, floor_to=3)
    assert p.id == 1



