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

        parameters_tags = [
            'StringParameterDefinition',
            'TextParameterDefinition',
        ]
        xpath = './/parameterDefinitions/*'
        for param in xml.findall(xpath):
            tag = param.tag.split('.')[-1]
            if tag not in parameters_tags:
                continue

            param_name = param.find('name').text
            if 'REVISION' == param_name:
                continue
            default = param.find('defaultValue').text
            config['parameters'][param_name] = default

        xpath = './scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig'
        gitinfo = xml.find(xpath)
        if gitinfo:
            url = gitinfo.find('url')
            if url is not None:
                config['github_repository'] = url.text.replace('.git', '')

            creds_el = gitinfo.find('credentialsId')
            if creds_el is not None:
                config['scm_credentials'] = creds_el.text.strip()

        xpath = './/com.cloudbees.jenkins.GitHubSetCommitStatusBuilder'
        config['set_commit_status'] = bool(xml.findall(xpath))

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

    def contains(self, other):
        me = self.as_dict()
        other = other.as_dict()
        if not set(me['parameters']) >= set(other['parameters']):
            return False

        if not set(me['axis']) >= set(other['axis']):
            return False

        all_axis = set(me['axis']) | set(other['axis'])
        for axis in all_axis:
            mines = set(me['axis'].get(axis, []))
            theirs = set(other['axis'].get(axis, []))
            if not mines >= theirs:
                return False

        if all_axis:
            # Care available nodes in Jenkins only for matrix jobs.
            if not set(me['merged_nodes']) >= set(other['merged_nodes']):
                return False
        else:
            # Else, only care that we have a node param.
            if other['merged_nodes'] and not me['merged_nodes']:
                return False

        return True

    def merge(self, other):
        config = deepcopy(other.config)

        config['parameters'] = dict(
            other.config['parameters'], **self.config['parameters']
        )

        all_axis = set(self.config['axis']) | set(other.config['axis'])
        for axis in all_axis:
            all_values = (
                self.config['axis'].get(axis, []) +
                other.config['axis'].get(axis, [])
            )
            config['axis'][axis] = sorted({str(x) for x in all_values})

        if all_axis:
            merged_nodes = (
                set(self.config['merged_nodes']) |
                set(other.config['merged_nodes'])
            )
            if 'node' in self.config:
                merged_nodes.add(self.config['node'])
            if 'node' in other.config:
                merged_nodes.add(other.config['node'])

            config['merged_nodes'] = list(merged_nodes)

        return self.factory(self.name, config)

    def as_dict(self):
        config = dict(deepcopy(self.config), name=self.name)

        if 'node' in config and not config['merged_nodes']:
            config['merged_nodes'].append(config['node'])

        if 'axis' in config:
            for axis, values in config['axis'].items():
                config['axis'][axis] = sorted([str(x) for x in values])

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
