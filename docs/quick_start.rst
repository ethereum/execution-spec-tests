Quick Start
===========

Prerequisites
^^^^^^^^^^^^^

The following are required to either generate or develop tests:


#. Python ``3.10.0``.
#. `\ `go-ethereum <https://github.com/ethereum/go-ethereum>`_ ``v1.10.13`` for ``geth``\ 's ``evm`` utility which must be accessible in the ``PATH``. See https://github.com/ethereum/go-ethereum#building-the-source for information on how to build go-ethereum utilities.
#. `\ `solc <https://github.com/ethereum/solidity>`_ >= ``v0.8.17``\ ; ``solc`` must be in accessible in the ``PATH``.

Generating the Execution Spec Tests For Use With Clients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To generate tests from the test "fillers", it's necessary to install the Python packages provided by ``execution-spec-tests`` (it's recommended to use a virtual environment for the installation):

.. code-block:: console

   $ git clone https://github.com/ethereum/execution-spec-tests
   $ cd execution-spec-tests
   $ python -m venv ./venv/
   $ source ./venv/bin/activate
   $ pip install -e .

To generate all the tests defined in the ``./fillers`` sub-directory, run the ``tf`` command:

.. code-block:: console

   $ tf --output="fixtures"

Note that the test ``post`` conditions are tested against the output of the ``geth`` ``evm`` utility during test generation.

To generate all the tests in the ``./fillers/vm`` sub-directory (category), for example, run:

.. code-block:: console

   tf --output="fixtures" --test-categories vm

To generate all the tests in the ``./fillers/*/dup.py`` modules, for example, run:

.. code-block:: console

   tf --output="fixtures" --test-module dup

To generate specific tests, such as ``./fillers/*/*.py::test_dup``\ , for example, run (remove the ``test_`` prefix from the test case's function name):

.. code-block:: console

   tf --output="fixtures" --test-case dup

Testing the Execution Spec Tests Framework
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Python packages provided by the execution spec tests framework have their own test suite that can be ran via ``tox``\ :

.. code-block:: console

   $ python -m venv ./venv/
   $ source ./venv/bin/activate
   $ pip install tox
   $ tox -e py3
