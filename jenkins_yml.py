import logging
import os
import stat
import sys
import yaml


logger = logging.getLogger(__name__)


def entrypoint():
    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG,
    )

    name = os.environ.get('JOB_NAME')
    if not name:
        logger.error("Not job name undefined")
        sys.exit(1)

    if not os.path.exists('jenkins.yml'):
        logger.warn("Missing jenkins.yml. Skipping this commit.")
        sys.exit(0)

    try:
        config = yaml.load(open('jenkins.yml').read())
    except Exception:
        logger.exception("Failed to parse jenkins.yml")
        sys.exit(1)

    config = config.get(name)
    if not config:
        logger.warn("Nothing to do in this PR")
        sys.exit(0)

    if isinstance(config, str):
        script = config
    elif isinstance(config, dict):
        script = config.get('script')
        if not script:
            logger.error("Missing scripts")
            sys.exit(1)
    else:
        logger.error("Invalid jenkins.yml.")
        sys.exit(1)

    script_name = '_job'
    with open(script_name, 'w') as fo:
        fo.write("#!/bin/bash -eux\n")
        fo.write(script.strip() + '\n')
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
