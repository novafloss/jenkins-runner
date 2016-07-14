import os.path
import xml.etree.ElementTree as ET

import jinja2


JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')
    ),
    lstrip_blocks=True,
    trim_blocks=True,
    undefined=jinja2.StrictUndefined,
)


def render(job, current_xml):
    config = job.as_dict()
    if 'axis' in config:
        template_name = 'matrix.xml'
        current_axises = {}
        if current_xml:
            current = ET.fromstring(current_xml)
            for axis in current.findall('./axes/*'):
                axis_name = axis.find('name').text
                current_axises[axis_name] = values = []
                for value in axis.findall('values/*'):
                    values.append(value.text)
            for axis, values in config['axis'].items():
                current_axises[axis] = sorted(
                    set(values) | set(current_axises.get(axis, []))
                )

            config['axis'] = current_axises
    else:
        template_name = 'freestyle.xml'

    return JINJA.get_template(template_name).render(**config)
