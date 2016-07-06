| |CI| |PyPI|

==========================
 Define jobs from project
==========================

``jenkins-yml`` is a test runner that reads tests commands from source checkout
rather than jenkins configuration.


Setup
=====

On your Jenkins executor, ``pip3 install jenkins-yml`` and then use
``jenkins-yml-runner`` as shell command.


``jenkins.yml`` format
======================


Put a ``jenkins.yml`` file at the root of the project. This file contains a
mapping of ``JOB_NAME`` to scripts. For example::


  app-lint: |
    flake8 app/

  app-tests:
    axis:
      TOXENV: [py27, py34, py35]
    script: |
      tox -r

  app-doc:
    script: |
      tox -e sphinx -r


To test a job, simply run::

  JOB_NAME=app-test jenkins-yml-runner


.. |CI| image:: https://circleci.com/gh/novafloss/jenkins-yml.svg?style=shield
   :target: https://circleci.com/gh/novafloss/jenkins-yml
   :alt: CI Status

.. |PyPI| image:: https://img.shields.io/pypi/v/jenkins-yml.svg
   :target: https://pypi.python.org/pypi/jenkins-yml
   :alt: Version on PyPI
