"""Drivers for the simulation"""
from typing import Optional

from location import Location, manhattan_distance
from rider import Rider


class Driver:
    """A driver for a ride-sharing service.

    === Attributes ===
    id: A unique identifier for the driver.
    location: The current location of the driver.
    is_idle: True if the driver is idle and False otherwise.
    speed: The speed of the driver
    destination: The destination of the driver
    """

    id: str
    location: Location
    destination: Optional[Location]
    is_idle: bool
    speed: int

    def __init__(self, identifier: str, location: Location, speed: int) -> None:
        """Initialize a Driver.

        """
        self.id = identifier
        self.location = location
        self.speed = speed
        self.destination = None
        self.is_idle = True

    def __str__(self) -> str:
        """Return a string representation.

        >>> driver = Driver('Bob', Location(1, 1), 1)
        >>> str(driver)
        'Bob'
        """
        return self.id

    def __eq__(self, other: object) -> bool:
        """Return True if self equals other, and false otherwise.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> driver2 = Driver('Bob', Location(1, 1), 1)
        >>> driver1 == driver1
        True
        """
        if isinstance(other, Driver):
            return self.id == other.id
        else:
            return False

    def get_travel_time(self, destination: Location) -> int:
        """Return the time it will take to arrive at the destination,
        rounded to the nearest integer.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> driver1.get_travel_time(Location(2, 2))
        2
        """
        distance = manhattan_distance(self.location, destination)
        return round(distance / self.speed)

    def start_drive(self, location: Location) -> int:
        """Start driving to the location.
        Return the time that the drive will take.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> driver1.is_idle
        True
        >>> driver1.start_drive(Location(3, 3))
        4
        >>> driver1.is_idle
        False
        """
        self.is_idle = False
        self.destination = location
        return self.get_travel_time(self.destination)

    def end_drive(self) -> None:
        """End the drive and arrive at the destination.

        Precondition: self.destination is not None.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> driver1.start_drive(Location(3, 3))
        4
        >>> driver1.end_drive()
        >>> driver1.location == Location(3, 3)
        True
        """
        self.is_idle = True
        self.location = self.destination
        self.destination = None

    def start_ride(self, rider: Rider) -> int:
        """Start a ride and return the time the ride will take.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> rider1 = Rider("bobby", 0, Location(0,0), Location(2, 0))
        >>> driver1.start_ride(rider1)
        2
        >>> driver1.location == Location(0, 0)
        True
        """
        self.is_idle = False
        self.location = rider.origin
        self.destination = rider.destination
        return self.get_travel_time(self.destination)

    def end_ride(self) -> None:
        """End the current ride, and arrive at the rider's destination.

        Precondition: The driver has a rider.
        Precondition: self.destination is not None.

        >>> driver1 = Driver('Bob', Location(1, 1), 1)
        >>> rider1 = Rider("bobby", 0, Location(0,0), Location(2, 0))
        >>> driver1.start_ride(rider1)
        2
        >>> driver1.end_ride()
        >>> driver1.location == Location(2, 0)
        True
        """
        self.is_idle = True
        self.location = self.destination
        self.destination = None


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(
        config={'extra-imports': ['location', 'rider']})
