import os.path
import xml.etree.ElementTree as ET

import jinja2
import yaml


DEFAULTS = dict(
    blocking_jobs=None,
    build_name='#${BUILD_NUMBER} on ${GIT_BRANCH}',
    command='jenkins-yml-runner',
    description='Job defined from jenkins.yml.',
)


def generate(yml, defaults={}, currents=None):
    defaults = dict(DEFAULTS, **defaults)
    currents = currents or {}

    config = yaml.load(yml)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates')
        ),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=jinja2.StrictUndefined,
    )

    for name, params in config.items():
        if isinstance(params, str):
            params = dict(script=params)
        params = dict(defaults, **params)
        if 'axis' in params:
            template_name = 'matrix.xml'
            current_axises = {}
            if name in currents:
                current = ET.fromstring(currents[name])
                for axis in current.findall('./axes/*'):
                    axis_name = axis.find('name').text
                    current_axises[axis_name] = values = []
                    for value in axis.findall('values/*'):
                        values.append(value.text)
            for axis, values in params['axis'].items():
                current_axises[axis] = sorted(
                    set(values) | set(current_axises.get(axis, []))
                )

            params['axis'] = current_axises

        else:
            template_name = 'freestyle.xml'
        template = env.get_template(template_name)
        yield name, template.render(**params)
