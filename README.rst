| |CI| |PyPI|

==========================
 Define jobs from project
==========================

Render Jenkins job and execute commands from ``jenkins.yml``. These two steps
are completely independant.

``jenkins_yml`` provide a python API to render a Jenkins job XML config from a
YAML payload. It does not manage Jenkins I/O to effectively create the job. See
`Jenkins EPO <https://github.com/novafloss/jenkins-epo>`_ to create jobs and
schedule builds from GitHub.

Finally, ``jenkins_yml`` provide a simple yet pluggable CLI script to executes
de tests commands from ``jenkins.yml``.


Jenkins Job features
====================

The purpose of Jenkins YML is not to expose all Jenkins features, but to setup
a sane default set of features you expect from a CI, and ask you the question
you value.

- Define parameters and default values.
- Define matrix job axis.
- Define periodic job.
- Target Jenkins node per **build**.
- Search git clone reference in
  ``/var/lib/jenkins/references/<owner>/<repository>/``. It's up to you to
  create a mirror clone here or not.
- Set GitHub commit status to pending.
- Parameterized revision.
- Define ``after_script``, always runned after build, even on abort.
- Collect arctefacts from ``_ci/`` directory. Full path is available in
  ``CI_ARTEFACTS`` env var.
- Reads XUnit XML from ``_ci/xunit*.xml``.
- Reads coverage report from ``coverage.xml``.
- Globally disable jobs from Jenkins.


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
