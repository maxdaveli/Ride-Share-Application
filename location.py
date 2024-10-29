"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location.

    === Public Attributes ===
    row - the number of row from a grid position
    column - the number of columns starting from the furthest left side
    of the grid
    """
    row: int
    column: int

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        self.row = row
        self.column = column

    def __str__(self) -> str:
        """Return a string representation.
        >>> loc1 = Location(1, 2)
        >>> str(loc1)
        '(1, 2)'
        """
        return f"({self.row}, {self.column})"

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.
        >>> loc1 = Location(1,2)
        >>> loc2 = Location(1,2)
        >>> loc1 == loc2
        True
        >>> loc3 = Location(1,3)
        >>> loc4 = 'hi'
        >>> loc3 == loc4
        False
        """
        if isinstance(other, Location):
            return self.row == other.row and self.column == other.column
        else:
            return False


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    >>> loc1 = Location(1, 2)
    >>> loc2 = Location(3, 5)
    >>> manhattan_distance(loc1, loc2)
    5
    """
    difference_row = abs(origin.row - destination.row)
    difference_column = abs(origin.column - destination.column)
    return difference_row + difference_column


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'

    >>> loc = deserialize_location('1,2')
    >>> loc.row
    1
    >>> loc.column
    2
    >>> loc2 = deserialize_location('1,   3')
    >>> loc2.row
    1
    >>> loc2.column
    3
    """
    location_str.strip()
    location_str = location_str.split(',')
    return Location(int(location_str[0]), int(location_str[1]))


if __name__ == '__main__':
    import python_ta

    python_ta.check_all()
