"""
The rider module contains the Rider class. It also contains
constants that represent the status of the rider.

=== Constants ===
WAITING: A constant used for the waiting rider status.
CANCELLED: A constant used for the cancelled rider status.
SATISFIED: A constant used for the satisfied rider status
"""
from location import Location

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Rider:
    """A rider for a ride-sharing service.
    === Public Attributes ===
    identifier - a unique identifier for a rider
    patience - number of minutes the rider will wait to be picked up before
    they cancel their ride
    origin - their original location when they request the ride
    destination - their desired destination when they request the ride
    status - the status of the rider
    """
    id: str
    patience: int
    origin: Location
    destination: Location
    status: str

    def __init__(self, identifier: str, patience: int, origin: Location,
                 destination: Location) -> None:
        """Initialize a Rider.

        """
        self.id = identifier
        self.patience = patience
        self.origin = origin
        self.destination = destination
        self.status = WAITING

    def __str__(self) -> str:
        """
        Return a string representation
        >>> rider = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> str(rider)
        'Bob'
        """
        return self.id

    def __eq__(self, other: object) -> bool:
        """
        Return True if self equals other, and false otherwise.
        >>> rider1 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> rider2 = Rider('Bob', 100, Location(0, 0), Location(0, 1))
        >>> rider1 == rider2
        True
        """
        if isinstance(other, Rider):
            return self.id == other.id
        else:
            return False


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['location']})
