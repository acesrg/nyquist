from unittest import TestCase

from nyquist.control import Experiment


class MyControlExperiment(Experiment):
    def before_the_loop(self):
        self.my_global = 0

    def in_the_loop(self):
        self.my_global += 1

    def after_the_loop(self):
        self.my_global += 1


class MyIncompleteExperiment(Experiment):
    def in_the_loop(self):
        self.hi = "hi!"


class ExecutorTestCase(TestCase):
    def test_basic_executor(self):
        exp = MyControlExperiment()
        exp.set_loop_frequency(frequency_hz=10)
        exp.set_before_loop_time(0.1)
        exp.set_after_loop_time(0.1)
        exp.set_run_time(time_s=0.25)

        exp.run()

        self.assertEqual(exp.my_global, 3)

    def test_raise_if_incomplete(self):
        with self.assertRaises(TypeError):
            MyIncompleteExperiment()
