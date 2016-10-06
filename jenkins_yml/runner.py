import logging
import pkg_resources
import os
import stat
import sys

from .job import Job


logger = logging.getLogger(__name__)


def call_runner(runner, config):
    for ep in pkg_resources.iter_entry_points('jenkins_yml.runners'):
        if ep.name != runner:
            continue
        runner = ep.load()
        break
    else:
        logger.error('%s not found.', runner)
        sys.exit(1)

    runner(config)

    logger.error("Runner did not exit")
    sys.exit(1)


def console_script():
    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG,
    )

    name = os.environ.get('JOB_NAME')
    if not name:
        logger.error("JOB_NAME required.")
        sys.exit(1)
    name, _ = (name + '/').split('/', 1)

    if not os.path.exists('jenkins.yml'):
        logger.warn("Missing jenkins.yml. Skipping this commit.")
        sys.exit(0)

    jobs = {}
    try:
        yml = open('jenkins.yml').read()
        for job in Job.parse_all(yml):
            jobs[job.name] = job
    except Exception:
        logger.exception("Failed to parse jenkins.yml.")
        sys.exit(1)

    if name not in jobs:
        logger.warn("Job not defined for this commit. Skipping.")
        sys.exit(0)

    job = jobs[name]
    if 'axis' in job.config:
        for name, values in job.config['axis'].items():
            if name not in os.environ:
                logger.error("Missing axis %s value.", name)
                sys.exit(1)
            current = os.environ[name]
            values = {str(value) for value in values}
            if current not in values:
                logger.warn("%s=%s not available. Skipping.", name, current)
                sys.exit(0)

    call_runner(os.environ.get('JENKINS_YML_RUNNER', 'unconfined'), job)


def unconfined(job):
    # The unconfined runner even allow to choose the runner right from the yml.
    runner = job.config.pop('runner', None)
    if runner:
        call_runner(runner, job)
    else:
        logger.debug('Executing unconfined.')

    entry = os.environ.get('YML_SCRIPT', 'script')
    if entry not in {'script', 'after_script'}:
        logger.error('%r is not a valid YML entry.', entry)
        sys.exit(1)

    script = job.config.get(entry)
    if not script:
        logger.error('Missing script.')
        sys.exit(0)
    script = script.strip() + '\n'

    script_name = '_job'
    with open(script_name, 'w') as fo:
        fo.write("#!/bin/bash -eux\n")
        fo.write(script)
        os.chmod(
            fo.name,
            stat.S_IREAD | stat.S_IWUSR | stat.S_IXUSR
        )

    artefacts_dir = os.path.realpath(os.environ.get('CI_ARTEFACTS', '_ci'))
    environ = dict(job.config['parameters'], **os.environ)
    os.execle(
        script_name,
        dict(
            environ,
            CI='1',
            CI_ARTEFACTS=artefacts_dir,
        )
    )
