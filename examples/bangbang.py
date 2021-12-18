import time
import numpy as np
import matplotlib.pyplot as plt

from nyquist.lab import System
from nyquist.control import Experiment


# we create an inherited class from Experiment
class MyExperiment(Experiment):

    # the three fundamental functions should be defined
    def before_the_loop(self):
        # we will use aero to comunicate with the system
        self.aero = System("aeropendulum")
        self.aero.propeller.pwm.status.post("initialized")
        self.aero.telemetry.period.post(20)
        self.aero.logger.level.post("LOG_INFO")
        self.angle = []
        self.time = []
        self.aero.sensors.encoder.angle.get()
        self.start_ts = time.monotonic()

    def in_the_loop(self):
        if self.aero.sensors.encoder.angle._Endpoint__resourcer.new_message:
            angle = self.aero.sensors.encoder.angle.get()
            self.time.append(time.monotonic() - self.start_ts)
            self.angle.append(angle)
            print(angle)
            if angle is not None:
                if angle < self.setpoint_deg:
                    self.aero.propeller.pwm.duty.post(self.duty_high)
                else:
                    self.aero.propeller.pwm.duty.post(self.duty_low)

    # the after script will be executed even on failure
    def after_the_loop(self):
        self.aero.propeller.pwm.duty.post(0)
        self.aero.propeller.pwm.status.post("disabled")
        self.aero.propeller.pwm.status.post("initialized")


# instance experiment
exp = MyExperiment()

# set constants
exp.setpoint_deg = 40
exp.duty_high = 35
exp.duty_low = 25
exp.set_loop_frequency(20)
exp.set_run_time(6)
exp.set_before_loop_time(1)
# and run!
exp.run()

plt.figure()
print("---")
print(exp.time[-1] - exp.time[0])
print(len(exp.angle))
plt.plot(exp.time, np.sin(np.deg2rad(exp.angle)))
plt.show()
