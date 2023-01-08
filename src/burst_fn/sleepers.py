"""This module contains the sleepers that are used to set the amount of time to sleep for each burst function."""
import asyncio
import time

import pendulum as pdl

class SyncSleeper:
    """This class is used to sleep for a specified amount of time."""

    def __init__(self, sleep_until: pdl.DateTime):
        self.sleep_until = sleep_until

    def wait(self) -> None:
        """This method waits until the sleep_until time has passed."""
        sleep_seconds = (self.sleep_until - pdl.now()).total_seconds()
        time.sleep(max(sleep_seconds, 0))
        

class AsyncSleeper:

    def __init__(self, sleep_until: pdl.DateTime):
        self.sleep_until = sleep_until

    async def wait(self) -> None:
        """This method waits until the sleep_until time has passed."""
        sleep_seconds = (self.sleep_until - pdl.now()).total_seconds()
        await asyncio.sleep(max(sleep_seconds, 0))