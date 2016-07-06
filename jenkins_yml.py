import logging
import pkg_resources
import os
import stat
import sys
import yaml


logger = logging.getLogger(__name__)


def call_runner(runner, config):
    for ep in pkg_resources.iter_entry_points(__name__ + '.runners'):
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

    if not os.path.exists('jenkins.yml'):
        logger.warn("Missing jenkins.yml. Skipping this commit.")
        sys.exit(0)

    try:
        config = yaml.load(open('jenkins.yml').read())
    except Exception:
        logger.exception("Failed to parse jenkins.yml.")
        sys.exit(1)

    config = config.get(name)
    if config is None:
        logger.warn("Job not defined for this commit. Skipping.")
        sys.exit(0)

    if isinstance(config, dict) and 'axis' in config:
        for name, values in config['axis'].items():
            if name not in os.environ:
                logger.error("Missing axis %s value.", name)
                sys.exit(1)
            current = os.environ[name]
            if current not in values:
                logger.warn("%s=%s not available. Skipping.", name, current)
                sys.exit(0)

    call_runner(os.environ.get('JENKINS_YML_RUNNER', 'unconfined'), config)


def unconfined(config):
    if isinstance(config, str):
        config = dict(script=str(config))
    elif not isinstance(config, dict):
        logger.error("Invalid jenkins.yml.")
        sys.exit(1)

    # The unconfined runner even allow to choose the runner right from the yml.
    runner = config.pop('runner', None)
    if runner:
        call_runner(runner, config)
    else:
        logger.debug('Executing unconfined.')

    script = config.get('script')
    if not script:
        logger.error('Missing script.')
        sys.exit(1)
    script = script.strip() + '\n'

    script_name = '_job'
    with open(script_name, 'w') as fo:
        fo.write("#!/bin/bash -eux\n")
        fo.write(script)
        os.chmod(
            fo.name,
            stat.S_IREAD | stat.S_IWUSR | stat.S_IXUSR
        )

    os.execle(
        script_name,
        dict(
            os.environ,
            CI='1',
        )
    )
