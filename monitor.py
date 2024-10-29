"""
The Monitor module contains the Monitor class, the Activity class,
and a collection of constants. Together the elements of the module
help keep a record of activities that have occurred.

Activities fall into two categories: Rider activities and Driver
activities. Each activity also has a description, which is one of
request, cancel, pickup, or dropoff.

=== Constants ===
RIDER: A constant used for the Rider activity category.
DRIVER: A constant used for the Driver activity category.
REQUEST: A constant used for the request activity description.
CANCEL: A constant used for the cancel activity description.
PICKUP: A constant used for the pickup activity description.
DROPOFF: A constant used for the dropoff activity description.
"""

from typing import Dict, List
from location import Location, manhattan_distance

RIDER = "rider"
DRIVER = "driver"

REQUEST = "request"
CANCEL = "cancel"
PICKUP = "pickup"
DROPOFF = "dropoff"


class Activity:
    """An activity that occurs in the simulation.

    === Attributes ===
    timestamp: The time at which the activity occurred.
    description: A description of the activity.
    identifier: An identifier for the person doing the activity.
    location: The location at which the activity occurred.
    """

    time: int
    description: str
    id: str
    location: Location

    def __init__(self, timestamp: int, description: str, identifier: str,
                 location: Location) -> None:
        """Initialize an Activity.

        """
        self.time = timestamp
        self.description = description
        self.id = identifier
        self.location = location

    def __eq__(self, other: object) -> bool:
        """
        Return True if self equals other, and false otherwise.
        """
        if isinstance(other, Activity):
            return ((self.id == other.id)
                    and (self.time == other.time)
                    and (self.location == other.location)
                    and (self.description == other.description))
        else:
            return False


class Monitor:
    """A monitor keeps a record of activities that it is notified about.
    When required, it generates a report of the activities it has recorded.
    """

    # === Private Attributes ===
    _activities: Dict[str, Dict[str, List[Activity]]]

    #       A dictionary whose key is a category, and value is another
    #       dictionary. The key of the second dictionary is an identifier
    #       and its value is a list of Activities.

    def __init__(self) -> None:
        """Initialize a Monitor.

        """
        self._activities = {
            RIDER: {},
            DRIVER: {}
        }
        """@type _activities: dict[str, dict[str, list[Activity]]]"""

    def __str__(self) -> str:
        """Return a string representation.

        """
        return "Monitor ({} drivers, {} riders)".format(
            len(self._activities[DRIVER]), len(self._activities[RIDER]))

    def notify(self, timestamp: int, category: str, description: str,
               identifier: str, location: Location) -> None:
        """Notify the monitor of the activity.

        timestamp: The time of the activity.
        category: The category (DRIVER or RIDER) for the activity.
        description: A description (REQUEST | CANCEL | PICKUP | DROPOFF)
            of the activity.
        identifier: The identifier for the actor.
        location: The location of the activity.
        """
        if identifier not in self._activities[category]:
            self._activities[category][identifier] = []

        activity = Activity(timestamp, description, identifier, location)
        self._activities[category][identifier].append(activity)

    def report(self) -> Dict[str, float]:
        """Return a report of the activities that have occurred.

        """
        return {"rider_wait_time": self._average_wait_time(),
                "driver_total_distance": self._average_total_distance(),
                "driver_ride_distance": self._average_ride_distance()}

    def _average_wait_time(self) -> float:
        """Return the average wait time of riders that have either been picked
        up or have cancelled their ride.

        """
        wait_time = 0.0
        count = 0
        for activities in self._activities[RIDER].values():
            # A rider that has less than two activities hasn't finished
            # waiting (they haven't cancelled or been picked up).
            if len(activities) >= 2:
                # The first activity is REQUEST, and the second is PICKUP
                # or CANCEL. The wait time is the difference between the two.
                wait_time += activities[1].time - activities[0].time
                count += 1
        if count == 0:
            return 0.0
        else:
            return wait_time / count

    def _average_total_distance(self) -> float:
        """Return the average distance drivers have driven.
        >>> monitor1 = Monitor()
        >>> monitor1.notify(0, DRIVER, REQUEST, 'Bob', Location(0, 0))
        >>> monitor1.notify(0, RIDER, REQUEST, 'Bobby', Location(1, 1))
        >>> monitor1.notify(2, DRIVER, PICKUP, 'Bob', Location(1, 1))
        >>> monitor1.notify(2, RIDER, PICKUP, 'Bobby', Location(1, 1))
        >>> monitor1.notify(4, DRIVER, DROPOFF, 'Bob', Location(2, 2))
        >>> monitor1.notify(4, RIDER, DROPOFF, 'Bobby', Location(2, 2))
        >>> monitor1._average_total_distance()
        4.0
        """
        # first set the total distance to 0
        total_distance = 0.0
        # when using.values() returns subnested lists, where each subnested list
        # is a driver
        # we loop over each subnested list, as a different driver
        for driver in self._activities[DRIVER].values():
            # we need to check if there is at least 2 activities, because
            # if there is only one activity, the driver has not moved.
            if len(driver) >= 2:
                # for all the activities in that specific driver
                # check the manhattan distance and if there is a difference
                # add it to total distance
                for i in range(0, len(driver) - 1):
                    loc1 = driver[i].location
                    loc2 = driver[i + 1].location
                    total_distance += manhattan_distance(loc1, loc2)
        # if there are no subnested lists, then that means there are no drivers
        # if there are no drivers, then the average total distance is 0
        if len(self._activities[DRIVER].values()) == 0:
            return 0.0
        else:
            return total_distance / len(self._activities[DRIVER].values())

    def _average_ride_distance(self) -> float:
        """Return the average distance drivers have driven on rides.
        >>> monitor1 = Monitor()
        >>> monitor1.notify(0, DRIVER, REQUEST, 'Bob', Location(0, 0))
        >>> monitor1.notify(0, RIDER, REQUEST, 'Bobby', Location(1, 1))
        >>> monitor1.notify(2, DRIVER, PICKUP, 'Bob', Location(1, 1))
        >>> monitor1.notify(2, RIDER, PICKUP, 'Bobby', Location(1, 1))
        >>> monitor1.notify(4, DRIVER, DROPOFF, 'Bob', Location(2, 2))
        >>> monitor1.notify(4, RIDER, DROPOFF, 'Bobby', Location(2, 2))
        >>> monitor1._average_ride_distance()
        2.0
        """
        # set a pickup location to none
        # .values() returns a subnested list where each list is a driver
        pickup_location = None
        total_distance = 0.0
        total_rides = 0
        for driver in self._activities[DRIVER].values():
            # check each activity in the driver and see if it's a pickup
            # if it's a pickup set the pickup location to the activity location
            for activity in driver:
                if activity.description == PICKUP:
                    pickup_location = activity.location
                # if the activity is a drop off that means a successful ride has
                # been completed. If so, then calculate the manhattan distance
                # and add it to total distance
                elif activity.description == DROPOFF:
                    total_distance += manhattan_distance(pickup_location,
                                                         activity.location)
                    total_rides += 1
        # if the total rides is 0, that means there has been no successful rides
        # if so return 0
        if total_rides == 0:
            return 0.0
        else:
            return total_distance / total_rides


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(
        config={
            'max-args': 6,
            'extra-imports': ['typing', 'location']})
