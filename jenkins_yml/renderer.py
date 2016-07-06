import jinja2
import os.path
import yaml


DEFAULTS = dict(
    command='jenkins-yml-runner',
)


def generate(yml, defaults={}):
    defaults = dict(DEFAULTS, **defaults)

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
        template = env.get_template('freestyle.xml')
        yield name, template.render(**params)
