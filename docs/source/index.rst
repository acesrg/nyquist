nyquist
=======

|pypi-v| |pypi-l| |gitlab-ci| |coverage|

.. |pypi-v| image:: https://img.shields.io/pypi/v/nyquist.svg
    :target: https://pypi.python.org/pypi/nyquist

.. |pypi-l| image:: https://img.shields.io/pypi/l/nyquist.svg
    :target: https://pypi.python.org/pypi/nyquist

.. |gitlab-ci| image:: https://gitlab.com/marcomiretti/nyquist/badges/master/pipeline.svg
   :target: https://gitlab.com/marcomiretti/nyquist/-/commits/master

.. |coverage| image:: https://gitlab.com/marcomiretti/nyquist/badges/master/coverage.svg
    :target: https://gitlab.com/marcomiretti/nyquist/-/jobs/artifacts/master/file/htmlcov/index.html?job=unittest

``nyquist`` is a library for programming control-systems experiments and 
execute them in remote laboratories.

Here is an example of a bang-bang control loop with ``nyquist``:

.. literalinclude:: ../../examples/bangbang.py

.. toctree::
   :maxdepth: 3
   :caption: Contents:

Tutorial
--------
Get started with ``nyquist``!

.. toctree::
   :maxdepth: 3

   getting_started

Reference
---------
Find all the details about the API.

.. toctree::
   :maxdepth: 3

   api
   external_docs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
