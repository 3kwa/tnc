from mako.template import Template
from mako.lookup import TemplateLookup


lookup = TemplateLookup(directories=['templates'])

def serve_template(filename, **data):
    template = lookup.get_template(filename)
    return template.render(**data)
