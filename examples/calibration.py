import asyncio
from asyncio.exceptions import CancelledError, TimeoutError
import csv
import math
import time

import numpy as np

from nyquist.lab import System
from nyquist.control import Experiment



def is_steady(values, ts_s, steady_time_s, margin):
    """
    checks if values have reached steady state.

    true if values have been between +- margin for steady_time.
    """
    enough_values = math.ceil(steady_time_s / ts_s)
    if len(values) < enough_values:
        return False

    last_values = values[-enough_values:]
    reference = last_values[-1]
    top = reference + margin
    bottom = reference - margin
    return all([value > bottom and value < top for value in last_values])


def to_dicts_list(a, d):
    db = []
    for i in range(len(a)):
        db.append({'angle': a[i], 'duty': d[i]})

    return db


def ignore_initial_step(db, min_angle):
    ret = []
    for data in db:
        if data['angle'] == min_angle:
            ret = []

        else:
            ret.append(data)
    return ret


def coeffs_analysis(angles, duties, plot=False):
    MIN_ANGLE = 22.0
    MAX_ANGLE = 90.0
    db = to_dicts_list(angles, duties)

    # remove last element
    db = db[:-1]
    db = ignore_initial_step(db, MIN_ANGLE)

    res = np.polyfit([np.sin(np.deg2rad(d['angle'])) for d in db], [d['duty'] for d in db], 1)
    print(f'intercept: {res[0]}, slope: {res[1]}')

    if plot:
        import matplotlib.pyplot as plt
        PLOT_RESOLUTION = 100
        x_axis = np.linspace(np.sin(np.deg2rad(MIN_ANGLE)), np.sin(np.deg2rad(MAX_ANGLE)), PLOT_RESOLUTION)
        plt.plot([np.sin(np.deg2rad(d['angle'])) for d in db], [d['duty'] for d in db], '.', x_axis, res[1] + res[0] * x_axis)
        plt.show()


class MyExperiment(Experiment):
    def before_the_loop(self):
        self.aero = System("aeropendulum")
        self.aero.propeller.pwm.status.post("initialized")
        self.aero.telemetry.period.post(50)
        self.aero.logger.level.post("LOG_WARN")
        self.angle_buffer = []
        self.angles = []
        self.time = []
        self.duties = []
        self.aero.sensors.encoder.angle.get()
        self.aero.propeller.pwm.duty.post(self.duty_start)
        self.prev_duty = self.duty_start
        self.start_ts =  time.monotonic()

    def in_the_loop(self):
        angle = self.aero.sensors.encoder.angle.get()
        if angle is not None:
            if angle > 180:
                print("Faulty angle, force 22")
                angle = 22.0

            if angle > self.max_angle_deg:
                print("Angle too high! Stop!")
                self.set_run_time(0)
                return None

            self.angle_buffer.append(angle)
            steady = is_steady(
                self.angle_buffer,
                self.period_s,
                self.steady_time_s,
                self.steady_margin_deg,
            )
            if steady:
                self.duties.append(self.prev_duty)
                self.iteration += 1

                self.angle_buffer = []
                self.angles.append(angle)

                duty = self.duty_start + self.iteration * self.duty_step
                self.aero.propeller.pwm.duty.post(duty)
                self.prev_duty = duty

                print(f"angle={angle} duty={duty}")

    def after_the_loop(self):
        self.aero.propeller.pwm.duty.post(0)
        self.aero.propeller.pwm.status.post("disabled")
        self.aero.propeller.pwm.status.post("initialized")
        coeffs_analysis(self.angles, self.duties, plot=True)



exp = MyExperiment()

exp.max_angle_deg = 85
exp.duty_start = 17
exp.duty_step = 1

exp.period_s = 0.2
exp.steady_time_s = 5
exp.steady_margin_deg = 2

exp.set_loop_frequency(1 / exp.period_s)
exp.set_run_time(600)
exp.set_before_loop_time(1)
exp.iteration = 0
exp.run()
