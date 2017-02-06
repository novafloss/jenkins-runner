from copy import deepcopy
import os.path
import xml.etree.ElementTree as ET
import logging

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


logger = logging.getLogger(__name__)


class Job(object):
    WELL_KNOWN_KEYS = {'settings', 'stages'}

    DEFAULTS_CONFIG = dict(
        axis={},
        blocking_jobs=None,
        build_name='#${BUILD_NUMBER} on ${GIT_BRANCH}',
        default_revision='**',
        description='Job defined from jenkins.yml.',
        disabled=False,
        parameters={},
        merged_nodes=[],
    )

    DEFAULTS_FEATURES = {
        'after_script',
        'artefacts',
        'coverage',
        'fetchpull',
        'notify',
        'reference',
        'xunit',
    }

    builtin_paramaters = {
        'REVISION',
        'YML_NOTIFY_URL',
    }

    required_plugins = [
        'build-blocker-plugin',
        'build-name-setter',
        'cobertura',
        'github',
        'matrix-combinations-parameter',
        'matrix-project',
        'nodelabelparameter',
        'postbuild-task',
    ]

    @classmethod
    def parse_all(cls, yml, defaults={}):
        config = yaml.load(yml)
        for name, config in config.items():
            if name[0] in '._':
                continue
            if name in cls.WELL_KNOWN_KEYS:
                continue
            yield cls.factory(name, config, defaults)

    @classmethod
    def from_xml(cls, name, xml):
        config = dict(axis={}, parameters={})
        if isinstance(xml, str):
            xml = ET.fromstring(xml)

        el = xml.find('./disabled')
        config['disabled'] = el is not None and el.text == 'true'

        for axis in xml.findall('./axes/hudson.matrix.TextAxis'):
            axis_name = axis.find('name').text
            config['axis'][axis_name] = values = []
            for value in axis.findall('values/*'):
                values.append(value.text)

        for axis in xml.findall('./axes/hudson.matrix.LabelAxis'):
            config['merged_nodes'] = [e.text for e in axis.findall('values/*')]
        else:
            xpath = './/org.jvnet.jenkins.plugins.nodelabelparameter.LabelParameterDefinition'  # noqa
            node_el = xml.find(xpath)
            if node_el is not None:
                config['node'] = node_el.find('defaultValue').text

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
            if param_name in cls.builtin_paramaters:
                continue
            default = param.find('defaultValue').text
            config['parameters'][param_name] = default

        features = set()

        xpath = './scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig'
        gitinfo = xml.find(xpath)
        if gitinfo:
            url = gitinfo.find('url')
            if url is not None:
                config['github_repository'] = url.text.replace('.git', '')

            creds_el = gitinfo.find('credentialsId')
            if creds_el is not None:
                config['scm_credentials'] = creds_el.text.strip()

            refspec = gitinfo.find('refspec')
            pull = '+refs/pull/*:refs/remotes/origin/pull/*'
            if refspec is not None and pull in refspec.text.strip():
                features.add('fetchpull')

        xpath = './/com.cloudbees.jenkins.GitHubSetCommitStatusBuilder'
        config['set_commit_status'] = bool(xml.findall(xpath))

        xpath = './/hudson.plugins.postbuildtask.TaskProperties/script'
        el = xml.find(xpath)
        after_script = el.text if el is not None else ''
        if "YML_SCRIPT=after_script jenkins-yml-runner" in after_script:
            features.add('after_script')

        if 'jenkins-yml-runner notify' in after_script:
            features.add('notify')

        xpath = './/hudson.tasks.ArtifactArchiver/artifacts'
        if xml.find(xpath) is not None:
            features.add('artefacts')

        xpath = './/hudson.plugins.git.extensions.impl.CloneOption/reference'
        el = xml.find(xpath)
        path = el.text if el is not None else ''
        if path.startswith('/var/lib/jenkins'):
            features.add('reference')

        el = xml.find('.//hudson.tasks.junit.JUnitResultArchiver')
        if el is not None:
            features.add('xunit')

        el = xml.find('.//hudson.plugins.cobertura.CoberturaPublisher')
        if el is not None:
            features.add('coverage')

        return cls.factory(name, config, features=features)

    @classmethod
    def factory(cls, name, config, defaults={}, features=None):
        if isinstance(config, str):
            config = dict(script=config)
        config = dict(defaults, **config)
        return cls(name, config, features)

    def __init__(self, name, config={}, features=None):
        self.name = name
        self.config = dict(self.DEFAULTS_CONFIG, **config)
        if features is None:
            self.features = self.DEFAULTS_FEATURES
        else:
            self.features = features

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def contains(self, other):
        my = self.as_dict()
        their = other.as_dict()
        missing = set(their['parameters']) - set(my['parameters'])
        if missing:
            logger.debug("Missing params %s.", ', '.join(missing))
            return False

        missing = set(their['axis']) - set(my['axis'])
        if missing:
            logger.debug("Missing axis %s.", ', '.join(missing))
            return False

        all_axis = set(my['axis']) | set(their['axis'])
        for axis in all_axis:
            mines = set(my['axis'].get(axis, []))
            theirs = set(their['axis'].get(axis, []))
            missing = theirs - mines
            if missing:
                logger.debug(
                    "Missing values %s in axis %s.", ', '.join(missing), axis
                )
                return False

        if all_axis:
            # Care available nodes in Jenkins only for matrix jobs.
            missing = set(their['merged_nodes']) - set(my['merged_nodes'])
            if missing:
                logger.debug(
                    "Missing %r in matrix node axis.", list(missing)[0]
                )
                return False
        else:
            # Else, only care that we have a node param.
            if their['merged_nodes'] and not my['merged_nodes']:
                logger.debug("Missing node parameter.")
                return False

        missing = other.features - self.features
        if missing:
            logger.debug("Missing features %s.", ', '.join(missing))
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

        features = self.features | other.features
        return self.factory(self.name, config, features=features)

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
