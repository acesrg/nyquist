API
===

Lab Client
----------

The System Class
~~~~~~~~~~~~~~~~
.. autoclass:: nyquist.lab.System

Methods for HTTP endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: nyquist._private.network.http._HTTPResourcer.get
.. automethod:: nyquist._private.network.http._HTTPResourcer.post

Methods for WS endpoints
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: nyquist._private.network.ws._WSResourcer.get
.. automethod:: nyquist._private.network.ws._WSResourcer.post

Experiments
-----------

Defining the control algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: nyquist.control.Experiment.before_the_loop
.. automethod:: nyquist.control.Experiment.in_the_loop
.. automethod:: nyquist.control.Experiment.after_the_loop


Experiment object configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: nyquist.control.Experiment.set_loop_frequency
.. automethod:: nyquist.control.Experiment.set_run_time
.. automethod:: nyquist.control.Experiment.set_before_loop_time
.. automethod:: nyquist.control.Experiment.set_after_loop_time

Execution
~~~~~~~~~
.. automethod:: nyquist.control.Experiment.run
