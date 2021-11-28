from nyquist.lab import System
from nyquist.control import Experiment
import time
import numpy as np


MIN_ANGLE = 22.0
SAFE_DUTY = 20.0


class PIDController:
    @staticmethod
    def _generate_coeffs(Kp, Ki, Kd, N, Ts):
        a0 = (1 + N * Ts)
        a1 = -(2 + N * Ts)
        a2 = 1
        b0 = Kp * (1 + N * Ts) + Ki * Ts * (1 + N * Ts) + Kd * N
        b1 = -(Kp * (2 + N * Ts) + Ki * Ts + 2 * Kd * N)
        b2 = Kp + Kd * N
        return (a0, a1, a2), (b0, b1, b2)

    def __init__(self, Kp, Ki, Kd, N, Ts):
        self.a, self.b = self._generate_coeffs(Kp, Ki, Kd, N, Ts)
        self.u = [0, 0, 0]
        self.e = [0, 0, 0]

    @staticmethod
    def _output_calculation(e, u, a, b):
        u[0] = (-a[1] * u[1] - a[2] * u[2] + b[0] * e[0] + b[1] * e[1] + b[2] * e[2]) / a[0]

    def update(self, e_0):
        self.e = [e_0] + self.e[:-1]
        self._output_calculation(self.e, self.u, self.a, self.b)
        self.u = [0] + self.u[:-1]
        return self.u[1]


class PendulumLinearizer:
    def __init__(self, Km, u0):
        self.Km = Km
        self.u0 = u0

    def compensate(self, angle_rad):
        return self.u0 + self.Km * np.sin(angle_rad)


def avoid_negative_angles(angle):
    if angle > 180:
        return MIN_ANGLE
    return angle


def safety_check(value, max_value, safe_value):
    if value > max_value:
        return safe_value
    return value


class MyExperiment(Experiment):

    def before_the_loop(self):
        self.aero = System("aeropendulum")
        self.aero.propeller.pwm.status.post("initialized")
        self.aero.telemetry.period.post(20)
        self.aero.logger.level.post("LOG_INFO")
        self.angle = []
        self.time = []

        self.pid = PIDController(19.8, 22.61, 4.33, 20, 0.05)
        self.linerizer = PendulumLinearizer(38.45125566, 8.31078772)
        angle = self.aero.sensors.encoder.angle.get()
        self.start_ts =  time.monotonic()

    def in_the_loop(self):
        angle = self.aero.sensors.encoder.angle.get()
        if angle is not None:

            self.time.append(time.monotonic() - self.start_ts)
            self.angle.append(angle)

            angle = avoid_negative_angles(angle)
            angle_rad = np.deg2rad(angle)

            pid_duty = self.pid.update(self.setpoint_rad - angle_rad)
            compensator_duty = self.linerizer.compensate(angle_rad)
            duty = pid_duty + compensator_duty
            duty = safety_check(duty, self.max_duty, SAFE_DUTY)
            self.aero.propeller.pwm.duty.post(duty)

    def after_the_loop(self):
        self.aero.propeller.pwm.duty.post(0)
        self.aero.propeller.pwm.status.post("disabled")
        self.aero.propeller.pwm.status.post("initialized")


exp = MyExperiment()

exp.setpoint_rad = np.deg2rad(50)
exp.max_duty = 55
exp.set_loop_frequency(20)
exp.set_run_time(10)
exp.set_before_loop_time(1)
exp.run()

import matplotlib.pyplot as plt
plt.figure()
setpoint = [np.sin(exp.setpoint_rad)]*len(exp.angle)
plt.plot(exp.time, np.sin(np.deg2rad(exp.angle)), ".", exp.time, setpoint)
plt.show()
