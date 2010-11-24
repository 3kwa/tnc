from formencode import Schema
from formencode import validators
from formencode import Invalid
from formencode import htmlfill

from templates import serve_template

class SubmissionSchema(Schema):
    firstname = validators.String(not_empty=True)
    lastname = validators.String(not_empty=True)
    email = validators.Email(not_empty=True)
    town = validators.String(not_empty=True)
    postcode = validators.Int(not_empty=True)
    project_name = validators.String(not_empty=True)
    what = validators.String(not_empty=True)
    why = validators.String(not_empty=True)
    people = validators.Int(not_empty=True)
    optin = validators.StringBool(if_missing=False)
    tc = validators.StringBool(not_empty=True)

def validate_submission(form):
    """
    >>> VALID = {'firstname' : 'eugene',
    ...          'lastname': 'van den bulke',
    ...          'email' : 'eugene.vandenbulke@gmail.com',
    ...          'town' : 'manly',
    ...          'postcode' : '2095',
    ...          'project_name' : 'South Steyne SLSC',
    ...          'what' : 'add one floor to the building',
    ...          'why' : 'allow us to serve our community better',
    ...          'people' : 327,
    ...          'tc' : 'on'}
    >>> validate_submission(VALID)
    {'town': 'manly', 'what': 'add one floor to the building', 'project_name': 'South Steyne SLSC', 'firstname': 'eugene', 'people': 327, 'lastname': 'van den bulke', 'why': 'allow us to serve our community better', 'optin': False, 'email': 'eugene.vandenbulke@gmail.com', 'postcode': 2095, 'tc': True}
"""
    return SubmissionSchema(allow_extra_fields=True).to_python(form)

def render_submission(defaults={}, errors={}):
    """
    >>> 'value="eugene"' in render_submission()
    False
    >>> 'value="eugene"' in render_submission(defaults={'firstname' : 'eugene'})
    True
    >>> '<span class="error-message">missing</span>' in render_submission(errors={'firstname' : 'missing'})
    True
    """
    form = serve_template('forms/submission.html')
    return htmlfill.render(form, defaults, errors, error_class="error-input")


class StatusSchema(Schema):
    text = validators.String()
    beer = validators.Int(if_empty=-1)

def validate_status(form):
    return StatusSchema(allow_extra_fields=True).to_python(form)

def render_status(current, defaults={}, errors={}):
    form = serve_template('forms/status.html', current=current)
    return htmlfill.render(form, defaults, errors, error_class="error-input")


class ProjectSchema(Schema):
    title = validators.String(not_empty=True, strip=True)
    description = validators.String(not_empty=True, strip=True)
    photos = validators.URL()
    videos = validators.URL()

def validate_project(form):
    """
    >>> VALID = {'title' : 'Manly Oval',
    ...          'description' : 'Paint the white fence pink ...',
    ...          'videos' : 'http://www.videos.com',
    ...          'photos' : ''}
    >>> validate_project(VALID)
    {'photos': None, 'description': 'Paint the white fence pink ...', 'videos': 'http://www.videos.com', 'title': 'Manly Oval'}

    >>> VALID = {'title' : 'Manly Oval',
    ...          'description' : 'Paint the white fence pink ...',
    ...          'videos' : 'videos.com',
    ...          'photos' : ''}
    >>> validate_project(VALID)
    {'photos': None, 'description': 'Paint the white fence pink ...', 'videos': 'http://videos.com', 'title': 'Manly Oval'}

    >>> INVALID = {'title' : 'Manly Oval',
    ...          'description' : 'Paint the white fence pink ...',
    ...          'videos' : 'videos',
    ...          'photos' : ''}
    >>> validate_project(INVALID)
    Traceback (most recent call last):
    ...
    Invalid: videos: You must provide a full domain name (like videos.com)

    >>> INVALID = {'title' : 'Manly Oval',
    ...          'description' : '',
    ...          'videos' : '',
    ...          'photos' : ''}
    >>> validate_project(INVALID)
    Traceback (most recent call last):
    ...
    Invalid: description: Please enter a value

    >>> INVALID = {'title' : 'Manly Oval',
    ...          'description' : '    ',
    ...          'videos' : '',
    ...          'photos' : ''}
    >>> validate_project(INVALID)
    Traceback (most recent call last):
    ...
    Invalid: description: Please enter a value
    """
    return ProjectSchema(allow_extrafields=True).to_python(form)

def render_project(project, defaults={}, errors={}):
    form = serve_template('forms/project.html', project=project)
    return htmlfill.render(form, defaults, errors, error_class="error-input")

if __name__ == "__main__":
    import doctest
    doctest.testmod()

