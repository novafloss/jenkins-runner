from copy import deepcopy
import os.path
import xml.etree.ElementTree as ET

import yaml

try:
    import jinja2
except ImportError:
    JINJA = None
else:
    JINJA = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates')
        ),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=jinja2.StrictUndefined,
    )


class Job(object):
    DEFAULTS_CONFIG = dict(
        axis={},
        blocking_jobs=None,
        build_name='#${BUILD_NUMBER} on ${GIT_BRANCH}',
        command='jenkins-yml-runner',
        description='Job defined from jenkins.yml.',
        parameters={},
        merged_nodes=[],
    )

    @classmethod
    def parse_all(cls, yml, defaults={}):
        config = yaml.load(yml)
        for name, config in config.items():
            yield cls.factory(name, config, defaults)

    @classmethod
    def from_xml(cls, name, xml):
        config = dict(axis={}, parameters={})
        if isinstance(xml, str):
            xml = ET.fromstring(xml)

        for axis in xml.findall('./axes/hudson.matrix.TextAxis'):
            axis_name = axis.find('name').text
            config['axis'][axis_name] = values = []
            for value in axis.findall('values/*'):
                values.append(value.text)

        for axis in xml.findall('./axes/hudson.matrix.LabelAxis'):
            config['merged_nodes'] = [e.text for e in axis.findall('values/*')]

        xpath = './/hudson.model.StringParameterDefinition'
        for param in xml.findall(xpath):
            param_name = param.find('name').text
            if 'REVISION' == param_name:
                continue
            default = param.find('defaultValue').text
            config['parameters'][param_name] = default

        return cls.factory(name, config)

    @classmethod
    def factory(cls, name, config, defaults={}):
        if isinstance(config, str):
            config = dict(script=config)
        config = dict(defaults, **config)
        return cls(name, config)

    def __init__(self, name, config={}):
        self.name = name
        self.config = dict(self.DEFAULTS_CONFIG, **config)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def merge(self, other):
        config = deepcopy(self.config)
        for axis, values in config['axis'].items():
            config['axis'][axis] = sorted(
                set(values) | set(other.config['axis'].get(axis, []))
            )

        merged_nodes = set(config['merged_nodes'])
        if 'node' in config:
            merged_nodes.add(config['node'])
        if 'node' in other.config:
            merged_nodes.add(other.config['node'])
        merged_nodes |= set(other.config['merged_nodes'])
        config['merged_nodes'] = list(merged_nodes)

        config['parameters'] = dict(
            other.config['parameters'], **self.config['parameters']
        )

        return self.factory(self.name, config)

    def as_dict(self):
        config = dict(deepcopy(self.config), name=self.name)

        if 'node' in config and not config['merged_nodes']:
            config['merged_nodes'].append(config['node'])

        return config

    def as_xml(self):
        if not JINJA:
            raise RuntimeError("Missing render dependencies")

        config = self.as_dict()
        if config['axis']:
            template_name = 'matrix.xml'
        else:
            template_name = 'freestyle.xml'

        return JINJA.get_template(template_name).render(**config)
