"""Dispatcher for the simulation"""

from typing import Optional
from driver import Driver
from rider import Rider, CANCELLED


class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.

    """
    # === Private Attributes ===
    _waiting_list: list
    #     A list of all waiting riders
    _driver_list: list

    #     A list of all drivers

    def __init__(self) -> None:
        """Initialize a Dispatcher.
        """
        self._waiting_list = []
        self._driver_list = []

    def __str__(self) -> str:
        """Return a string representation.
        >>> from location import Location
        >>> dispatch = Dispatcher()
        >>> bob = Driver("bob", Location(0,0), 0)
        >>> dispatch._driver_list = [bob]
        >>> bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
        >>> dispatch._waiting_list = [bobby]
        >>> print(dispatch)
        Total Drivers: 1
        Total Waiting Riders: 1
        """
        return (f"Total Drivers: {len(self._driver_list)}" + "\n"
                + f"Total Waiting Riders: {len(self._waiting_list)}")

    def request_driver(self, rider: Rider) -> Optional[Driver]:
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.
        >>> from location import Location
        >>> dispatch = Dispatcher()
        >>> bob = Driver("bob", Location(0,0), 1)
        >>> bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
        >>> dispatch._driver_list.append(bob)
        >>> dispatch.request_driver(bobby).id
        'bob'
        >>> dispatch2 = Dispatcher()
        >>> bobby2 = Rider("bobby2", 0, Location(0,0), Location(1, 0))
        >>> dispatch2.request_driver(bobby2) is None
        True
        >>> dispatch3 = Dispatcher()
        >>> bob2 = Driver('bob2', Location(0,0), 1)
        >>> bob = Driver("bob", Location(0,0), 1)
        >>> bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
        >>> dispatch3._driver_list.append(bob2)
        >>> dispatch3._driver_list.append(bob)
        >>> dispatch3.request_driver(bobby).id
        'bob2'
        """
        # First find the first available driver and stop the loop as soon as
        # we find one driver that is idle
        first_available_driver = None
        any_available = False
        found = 0
        for driver in self._driver_list:
            if driver.is_idle and found != 1:
                first_available_driver = driver
                any_available = True
                found += 1
        # If we go through the first loop and there are no drivers that are idle
        # Then we return None and append the rider to the waiting list
        if any_available is False:
            self._waiting_list.append(rider)
            return None
        # If that forloop is not executed, then we set the closest driver to
        # the first available driver, and we compare and find the closest
        # driver
        closest_driver = first_available_driver
        for driver in self._driver_list:
            if driver.is_idle:
                rider_location = rider.origin
                if (driver.get_travel_time(rider_location)
                        < closest_driver.get_travel_time(rider_location)):
                    closest_driver = driver
        return closest_driver

    def request_rider(self, driver: Driver) -> Optional[Rider]:
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.
        >>> from location import Location
        >>> bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
        >>> bob = Driver("bob", Location(0,0), 1)
        >>> dispatch1 = Dispatcher()
        >>> dispatch1.request_driver(bobby)
        >>> dispatch1.request_rider(bob).id
        'bobby'
        """
        # Register the driver to the list if it's a new driver
        if driver not in self._driver_list:
            self._driver_list.append(driver)
        # If there is at least 1 rider in the waiting list, pop off the first
        # waiting rider in the list
        if len(self._waiting_list) > 0:
            return self._waiting_list.pop(0)
        # Else there are no riders, and return no riders for the driver
        else:
            return None

    def cancel_ride(self, rider: Rider) -> None:
        """Cancel the ride for rider.
        >>> from location import Location
        >>> bobby = Rider("bobby", 0, Location(0,0), Location(1, 0))
        >>> dispatch1 = Dispatcher()
        >>> dispatch1.request_driver(bobby)
        >>> dispatch1._waiting_list[0].id
        'bobby'
        >>> dispatch1.cancel_ride(bobby)
        >>> bobby.status
        'cancelled'
        >>> len(dispatch1._waiting_list) == 0
        True
        """
        # Change rider status to cancelled
        # Remove the rider from the waiting list if he is in the waiting list
        rider.status = CANCELLED
        if rider in self._waiting_list:
            self._waiting_list.remove(rider)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['typing', 'driver', 'rider']})
