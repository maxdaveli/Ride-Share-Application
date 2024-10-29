"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of events in the simulation.
"""
from __future__ import annotations
from typing import List
from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    timestamp: A timestamp for this event.
    """

    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize an Event with a given timestamp.

        Precondition: timestamp must be a non-negative integer.

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Return True iff this Event is not equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other: Event) -> bool:
        """Return True iff this Event is less than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Return True iff this Event is less than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Return True iff this Event is greater than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other: Event) -> bool:
        """Return True iff this Event is greater than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a RiderRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.
        >>> from location import Location
        >>> event = Event(10)
        >>> bob = Driver('bob', Location(0, 0), 1)
        >>> bob2 = Driver('bob2', Location(10, 10), 1)
        >>> bobby = Rider('bobby', 100, Location(1,1), Location(2,2))
        >>> dispatcher1 = Dispatcher()
        >>> monitor1 = Monitor()
        >>> rider_request = RiderRequest(event.timestamp, bobby)
        >>> print(rider_request.do(dispatcher1, monitor1)[0])
        110 -- bobby: Cancels the ride
        """
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.rider.id, self.rider.origin)

        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            travel_time = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + travel_time,
                                 self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience,
                                   self.rider))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.
        >>> from location import Location
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> request = RiderRequest(10, rider1)
        >>> print(request)
        10 -- Bob: Request a driver
        """
        return "{} -- {}: Request a driver".format(self.timestamp, self.rider)


class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    driver: The driver.
    """

    driver: Driver

    def __init__(self, timestamp: int, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver

    def __str__(self) -> str:
        """Return a string representation of this event.
        >>> from location import Location
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> driver1 = Driver('Bobby', Location(0, 0), 10)
        >>> request = DriverRequest(10, driver1)
        >>> print(request)
        10 -- Bobby: Request a rider
        """
        return "{} -- {}: Request a rider".format(self.timestamp, self.driver)

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Register the driver, if this is the first request, and
        assign a rider to the driver, if one is available.

        If a rider is available, return a Pickup event.
        >>> from location import Location
        >>> event = Event(100)
        >>> bob = Driver('bob', Location(0, 0), 1)
        >>> bob2 = Driver('bob2', Location(10, 10), 1)
        >>> bobby = Rider('bobby', 100, Location(1,1), Location(2,2))
        >>> dispatcher1 = Dispatcher()
        >>> monitor1 = Monitor()
        >>> driver_request = DriverRequest(event.timestamp, bob)
        >>> driver_request.do(dispatcher1, monitor1)
        []
        >>> dispatcher1.request_driver(bobby) == bob
        True
        """
        # Notify the monitor about the request.

        # Request a rider from the dispatcher.
        # If there is one available, the driver starts driving towards the
        # rider, and the method returns a Pickup event for when the driver
        # arrives at the rider's location.
        events = []
        monitor.notify(self.timestamp, DRIVER, REQUEST, self.driver.id,
                       self.driver.location)

        rider = dispatcher.request_rider(self.driver)

        if rider is not None:
            time_to_rider = self.driver.start_drive(rider.origin)
            pickup = Pickup(self.timestamp + time_to_rider, rider, self.driver)
            events.append(pickup)

        return events


class Cancellation(Event):
    """
    A Cancellation event.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """
        Initialize a cancellation event.
        """
        Event.__init__(self, timestamp)
        self.rider = rider

    def __str__(self) -> str:
        """Return a string representation of this event.
        >>> from location import Location
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> request = Cancellation(10, rider1)
        >>> print(request)
        10 -- Bob: Cancels the ride
        """
        return "{} -- {}: Cancels the ride".format(self.timestamp, self.rider)

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        When a cancellation event is executed. The rider's status is set to
        cancelled and doesn't schedule any future events.
        >>> from location import Location
        >>> bob = Driver('bob', Location(0, 0), 1)
        >>> bob2 = Driver('bob2', Location(10, 10), 1)
        >>> bobby = Rider('bobby', 100, Location(1,1), Location(2,2))
        >>> cancellation1 = Cancellation(100, bobby)
        >>> dispatcher1 = Dispatcher()
        >>> monitor1 = Monitor()
        >>> cancellation1.do(dispatcher1, monitor1)
        []
        """
        events = []
        # check that the rider is not none and the status is waiting
        # if the status is waiting then change the status to cancel
        # and ask dispatcher to cancel the ride
        # notify the monitor that a rider has cancelled their ride
        if self.rider is not None and self.rider.status == WAITING:
            self.rider.status = CANCELLED
            dispatcher.cancel_ride(self.rider)
            monitor.notify(self.timestamp, RIDER, CANCEL, self.rider.id,
                           self.rider.origin)
        return events


class Pickup(Event):
    """
    A Pickup event.

    === Attributes ===
    rider: The rider
    driver: The driver
    """

    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """
        Initializes a pickup event.
        """
        Event.__init__(self, timestamp)
        self.rider = rider
        self.driver = driver

    def __str__(self) -> str:
        """Return a string representation of this event.
        >>> from location import Location
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> driver1 = Driver('Bobby', Location(0, 0), 1)
        >>> pickup = Pickup(1, rider1, driver1)
        >>> print(pickup)
        1: Bobby picks up Bob
        """
        return f"{self.timestamp}: {self.driver} picks up {self.rider}"

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        A pickup event sets the driver location to the rider's location.
        if a rider's status is waiting, the driver begins the ride to the
        rider's destination.
        A dropoff event is also scheduled for the time they will arrive at the
        destination.
        If the rider cancelled, then a new driver request is scheduled to take
        place
        >>> from location import Location
        >>> bob = Driver('bob', Location(0, 0), 1)
        >>> bob2 = Driver('bob2', Location(10, 10), 1)
        >>> bobby = Rider('bobby', 100, Location(1,1), Location(2,2))
        >>> pickup1 = Pickup(2, bobby, bob)
        >>> dispatcher1 = Dispatcher()
        >>> monitor1 = Monitor()
        >>> print(pickup1)
        2: bob picks up bobby
        """
        # First end the drive so driver location gets updated to riders origin
        self.driver.end_drive()
        events = []
        # Notify the monitor that the driver has picked up the rider
        monitor.notify(self.timestamp, DRIVER, PICKUP, self.driver.id,
                       self.driver.location)
        # Check if rider status is waiting and rider is not None
        # If they are waiting, then we notify the monitor the rider is picked
        # up and start the ride
        # also we need to return a drop off event and change the rider status to
        # satisfied
        if self.rider.status == WAITING and self.rider is not None:
            monitor.notify(self.timestamp, RIDER, PICKUP, self.rider.id,
                           self.rider.origin)
            time_to_destination = self.driver.start_ride(self.rider)
            drop_off = Dropoff(self.timestamp + time_to_destination, self.rider,
                               self.driver)
            events.append(drop_off)
            self.rider.status = SATISFIED
        # if the rider has cancelled, then a new driver request event is
        # initiated and is appended to events
        elif self.rider.status == CANCELLED and self.rider is not None:
            new_request = DriverRequest(self.timestamp, self.driver)
            events.append(new_request)

        return events


class Dropoff(Event):
    """
    A Dropoff event

    === Attributes ===
    rider: The Rider
    driver: The Driver
    """
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """
        Initializes a dropoff event
        """
        Event.__init__(self, timestamp)
        self.rider = rider
        self.driver = driver

    def __str__(self) -> str:
        """Return a string representation of this event.
        >>> from location import Location
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> driver1 = Driver('Bobby', Location(0, 0), 1)
        >>> drop_off = Dropoff(1, rider1, driver1)
        >>> print(drop_off)
        1: Bobby drops off Bob
        """
        return f"{self.timestamp}: {self.driver} drops off {self.rider}"

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        When a rider is dropped off, a new event for driver requesting a rider
        is created immediately.
        >>> from location import Location
        >>> bob = Driver('bob', Location(0, 0), 1)
        >>> bob2 = Driver('bob2', Location(10, 10), 1)
        >>> bobby = Rider('bobby', 100, Location(1,1), Location(2,2))
        >>> dropoff1 = Dropoff(4, bobby, bob)
        >>> dispatcher1 = Dispatcher()
        >>> monitor1 = Monitor()
        >>> print(dropoff1)
        4: bob drops off bobby
        """
        # First end the ride so the driver status changes back to idle
        # and set the destination of the driver to None
        events = []
        self.driver.end_ride()
        # If the rider status is satisfied, we notify the monitor that a
        # rider has been successfully dropped off
        if self.rider.status == SATISFIED:
            monitor.notify(self.timestamp, RIDER, DROPOFF,
                           self.rider.id, self.rider.destination)
            monitor.notify(self.timestamp, DRIVER, DROPOFF, self.driver.id,
                           self.rider.destination)
        # a new driver request is initiated since the ride has been completed
        new_request = DriverRequest(self.timestamp, self.driver)
        events.append(new_request)
        return events


def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                # Skip lines that are blank or start with #.
                continue

            # Create a list of words in the line, e.g.
            # ['10', 'RiderRequest', 'Cerise', '4,2', '1,5', '15'].
            # Note that these are strings, and you'll need to convert some
            # of them to a different type.
            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]

            # HINT: Use Location.deserialize to convert the location string to
            # a location.

            if event_type == "DriverRequest":
                event = DriverRequest(timestamp, Driver(tokens[2],
                                                        deserialize_location(
                                                            tokens[3]),
                                                        int(tokens[4])))
                events.append(event)
            elif event_type == "RiderRequest":
                event = RiderRequest(timestamp, Rider(tokens[2], int(tokens[5]),
                                                      deserialize_location(
                                                          tokens[3]),
                                                      deserialize_location(
                                                          tokens[4])))
                events.append(event)

    return events


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'allowed-io': ['create_event_list'],
            'extra-imports': ['rider', 'dispatcher', 'driver',
                              'location', 'monitor']})
