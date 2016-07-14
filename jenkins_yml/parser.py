from copy import deepcopy

import yaml

try:
    from .renderer import render
except ImportError:
    render = None


class Job(object):
    DEFAULTS_CONFIG = dict(
        blocking_jobs=None,
        build_name='#${BUILD_NUMBER} on ${GIT_BRANCH}',
        command='jenkins-yml-runner',
        description='Job defined from jenkins.yml.',
    )

    @classmethod
    def parse_all(cls, yml, defaults={}):
        config = yaml.load(yml)
        for name, config in config.items():
            yield cls.factory(name, config, defaults)

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

    def as_dict(self):
        return dict(deepcopy(self.config), name=self.name)

    def as_xml(self, current_xml=None):
        if not render:
            raise RuntimeError("Missing render dependencies")
        return render(self, current_xml)
