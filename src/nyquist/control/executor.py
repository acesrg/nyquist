from abc import ABC, abstractmethod
import asyncio
import time


class Experiment(ABC):
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._loop_period_s = 0.1
        self._run_time_s = 2 * 60
        self._before_loop_time_s = 0.5
        self._after_loop_time_s = 0

    def set_loop_frequency(self, frequency_hz):
        """
        Define the frequency of the control-loop [Hz].

        :param frequency_hz: The frequency in hertz.
        :type frequency_hz: float
        """
        self._loop_period_s = 1 / frequency_hz

    def set_run_time(self, time_s):
        """
        Define the simulation run time [s]. This includes only the time spent
        inside the control loop.

        :param time_s: The time in seconds.
        :type time_s: float
        """
        self._run_time_s = time_s

    def set_before_loop_time(self, time_s):
        """
        Set the delay time between the :meth:`Experiment.before_the_loop` and
        the start of the loop.

        :param time_s: The time in seconds.
        :type time_s: float
        """
        self._before_loop_time_s = time_s

    def set_after_loop_time(self, time_s):
        """
        Set the delay time between end of the loop and
        :meth:`Experiment.after_the_loop`.

        :param time_s: The time in seconds.
        :type time_s: float
        """

        self._after_loop_time_s = time_s

    async def control_algorithm(self):
        try:
            self.before_the_loop()
            await asyncio.sleep(self._before_loop_time_s)
            while (time.monotonic() - self._start_ts < self._run_time_s):
                self.in_the_loop()
                await asyncio.sleep(self._loop_period_s)
            await asyncio.sleep(self._after_loop_time_s)
        finally:
            self.after_the_loop()

    @abstractmethod
    def before_the_loop(self):
        """The user should define this method. When :meth:`Experiment.run` is
        called, this method will run first. Then it will wait for some time
        that can be set with :meth:`Experiment.set_before_loop_time` and after
        said delay, it will run the loop.
        """

    @abstractmethod
    def in_the_loop(self):
        """The user should define this method. When :meth:`Experiment.run` is
        called, this method will run in a loop, after
        :meth:`Experiment.before_the_loop`. This method will run in a loop
        with a frequency established by :meth:`Experiment.set_loop_frequency`.
        """

    @abstractmethod
    def after_the_loop(self):
        """The user should define this method. When :meth:`Experiment.run` is
        called, this method will run after the loop, and after a delay that
        can be configured with :meth:`Experiment.set_after_loop_time`.
        """

    def run(self, blocking=True):
        """Execute the control experiment, run:

        .. code-block:: python

            before_the_loop()
            sleep(_before_loop_time_s)
            while _time_spent < _run_time_s:
                in_the_loop()
                sleep(1 /_loop_period_s)
            sleep(_after_loop_time_s)
            after_the_loop()
        """
        self._start_ts = time.monotonic()
        if blocking:
            self._loop.run_until_complete(self.control_algorithm())
        else:
            self._loop.create_task(self.control_algorithm())
