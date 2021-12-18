import csv
import time

import numpy as np

from nyquist.lab import System
from nyquist.control import Experiment


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


def ziegler_nichols(Ku, Tu, control_type):
    if control_type == 'classic':
        return {
            'Kp': 0.6 * Ku,
            'Ki': 1.2 * Ku / Tu,
            'Kd': 0.075 * Ku * Tu,
        }
    elif control_type == 'p':
        return {
            'Kp': 0.5 * Ku,
            'Ki': 0 * Ku / Tu,
            'Kd': 0 * Ku * Tu,
        }
    elif control_type == 'pi':
        return {
            'Kp': 0.45 * Ku,
            'Ki': 0.54 * Ku / Tu,
            'Kd': 0 * Ku * Tu,
        }
    elif control_type == 'pd':
        return {
            'Kp': 0.8 * Ku,
            'Ki': 0 * Ku / Tu,
            'Kd': 0.1 * Ku * Tu,
        }
    elif control_type == 'some overshoot':
        return {
            'Kp': 0.333 * Ku,
            'Ki': 0.666 * Ku / Tu,
            'Kd': 0.111 * Ku * Tu,
        }
    elif control_type == 'no overshoot':
        return {
            'Kp': 0.2 * Ku,
            'Ki': 0.4 * Ku / Tu,
            'Kd': 0.0666 * Ku * Tu,
        }
    else:
        raise RuntimeError("Unknown control type")



class MyExperiment(Experiment):

    def before_the_loop(self):
        self.aero = System("aeropendulum")
        self.aero.propeller.pwm.status.post("initialized")
        self.aero.telemetry.period.post(20)
        self.aero.logger.level.post("LOG_INFO")
        self.data = []  # {'time': %f, 'angle': %f, 'setpoint': %f}

        pid_coeffs = ziegler_nichols(Ku=40, Tu=1.45, control_type='no overshoot')

        self.pid = PIDController(
            pid_coeffs['Kp'],
            pid_coeffs['Ki'],
            pid_coeffs['Kd'],
            20,
            0.05
        )
        self.linerizer = PendulumLinearizer(
            41.67880775502065, # 38.45125566,
            4.570736581055918, # 8.31078772,
        )
        self.aero.sensors.encoder.angle.get()
        self.start_ts =  time.monotonic()

    def in_the_loop(self):
        angle_deg = self.aero.sensors.encoder.angle.get()
        if angle_deg is None:
            return

        angle_deg = avoid_negative_angles(angle_deg)
        angle_rad = np.deg2rad(angle_deg)

        spent = time.monotonic() - self.start_ts


        pid_duty = self.pid.update(self.setpoint_rad - angle_rad)
        compensator_duty = self.linerizer.compensate(angle_rad)
        duty = pid_duty + compensator_duty
        duty = safety_check(duty, self.max_duty, SAFE_DUTY)
        self.aero.propeller.pwm.duty.post(duty)

        self.data.append(
            {
                'time': spent,
                'sin_angle': np.sin(angle_rad),
                'duty': duty,
                'sin_setpoint': np.sin(self.setpoint_rad),
            }
        )

    def after_the_loop(self):
        self.aero.propeller.pwm.duty.post(0)
        self.aero.propeller.pwm.status.post("disabled")
        self.aero.propeller.pwm.status.post("initialized")


exp = MyExperiment()

exp.setpoint_rad = np.deg2rad(50)
exp.max_duty = 55
exp.set_loop_frequency(20)
exp.set_run_time(20)
exp.set_before_loop_time(2)
exp.run()

if exp.data:
    with open(f'pid_{time.time()}.csv','w') as f:
        fieldnames = exp.data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(exp.data)

time, sin_angle, duty, sin_setpoint = zip(*[d.values() for d in exp.data])

import matplotlib.pyplot as plt
plt.figure()
plt.plot(time, sin_angle, ".", time, sin_setpoint)
plt.show()
