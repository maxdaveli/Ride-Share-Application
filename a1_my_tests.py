import pytest
from location import (Location, manhattan_distance, deserialize_location)
from container import PriorityQueue
from rider import Rider, WAITING, CANCELLED, SATISFIED
from driver import Driver
from dispatcher import Dispatcher
from event import (RiderRequest, DriverRequest, Pickup, Dropoff, Cancellation,
                   create_event_list)
from monitor import Activity, Monitor, DRIVER, RIDER, REQUEST, CANCEL, PICKUP, \
    DROPOFF


def test_pq_priority_with_same_timestamp() -> None:
    """Tests the priority of two events in pq with same timestamp"""
    d1 = Driver("TJ", Location(1, 2), 10)
    d2 = Driver("AJ", Location(1, 3), 10)
    pq = PriorityQueue()
    dr1 = DriverRequest(0, d1)
    pq.add(dr1)
    assert pq._items == [dr1]
    dr2 = DriverRequest(0, d2)
    pq.add(dr2)

    assert pq._items == [dr1, dr2]


def test_dispatcher_waiting_list() -> None:
    """
    Tests the dispatcher waiting list is properly created
    """
    dispatch = Dispatcher()
    bob = Driver("bob", Location(0,0), 0)
    dispatch._driver_list = [bob]
    bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
    dispatch._waiting_list = [bobby]
    assert len(dispatch._waiting_list) == 1

