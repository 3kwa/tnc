from mako.template import Template
from mako.lookup import TemplateLookup


lookup = TemplateLookup(directories=['templates'],
                        default_filters=['h'],
                        output_encoding = 'utf-8')

def serve_template(filename, **data):
    man = {'form_errors' : {}, 'form_values' : {}}
    man.update(data)
    template = lookup.get_template(filename)
    return template.render(**man)
