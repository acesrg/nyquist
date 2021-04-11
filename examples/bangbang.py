from nyquist.lab import System
from nyquist.control import Experiment


# we create an inherited class from Experiment
class MyExperiment(Experiment):

    # the three fundamental functions should be defined
    def before_the_loop(self):
        # we will use aero to comunicate with the system
        self.aero = System("aeropendulum")
        self.aero.propeller.pwm.status.post("initialized")
        self.aero.logger.level.post("LOG_INFO")
        self.aero.propeller.pwm.duty.post(self.duty_low)

    def in_the_loop(self):
        angle = self.aero.sensors.encoder.angle.get()
        if angle < self.setpoint_deg:
            self.aero.propeller.pwm.duty.post(self.duty_high)
        else:
            self.aero.propeller.pwm.duty.post(self.duty_low)

    # the after script will be executed even on failure
    def after_the_loop(self):
        self.aero.propeller.pwm.duty.post(0)
        self.aero.propeller.pwm.status.post("disabled")


# instance experiment
exp = MyExperiment()

# set constants
exp.setpoint_deg = 90
exp.duty_high = 10
exp.duty_low = 5

# and run!
exp.run()
