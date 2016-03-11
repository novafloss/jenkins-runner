| |PyPI|

==========================
 Define jobs from project
==========================

``jenkins-runner`` is a test runner that reads tests commands from source
checkout rather than jenkins configuration.

``jenkins.yml`` format
======================


Put a ``jenkins.yml`` file at the root of the project. This file contains a
mapping of ``JOB_NAME`` to scripts. For example::


  app-tests: |
    tox -r

  app-doc:
    script: |
      tox -e sphinx -r

.. |PyPI| image:: https://img.shields.io/pypi/v/jenkins-yml.svg
   :target: https://pypi.python.org/pypi/jenkins-yml
   :alt: Version on PyPI
