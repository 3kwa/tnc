from formencode import Schema
from formencode import validators
from formencode import Invalid
from formencode import htmlfill

from templates import serve_template

FIRSTNAME_MESSAGES = {
    'empty' : 'Please enter your firstname'
}
LASTNAME_MESSAGES = {
    'empty' : 'Please enter your lastname'
}
EMAIL_MESSAGES = {
    'badDomain' : 'Please enter a valid email',
    'badType' : 'Please enter a valid email',
    'badUsername' : 'Please enter a valid email',
    'noAt' : 'Please enter a valid email'}
TOWN_MESSAGES = {
    'empty' : 'Please enter a town'
}
POSTCODE_MESSAGES = {
    'integer' : 'Please enter a valid postcode',
    'empty' : 'Please enter a valid postcode'
}
PROJECT_MESSAGES = {
    'empty' : 'Please name your project'
}
WHAT_MESSAGES = {
    'empty' : 'Please describe the favour'
}
WHY_MESSAGES = {
    'empty' : 'Please describe who will benefit'
}
PEOPLE_MESSAGES = {
    'empty' : 'Please enter the amount of people'
}
TC_MESSAGES = {
    'empty' : 'Please agree to the terms and conditions',
    'missing' : 'Please agree to the terms and conditions'
}

class SubmissionSchema(Schema):
    messages = {'tc' : 'nope'}
    firstname = validators.String(not_empty=True, messages=FIRSTNAME_MESSAGES)
    lastname = validators.String(not_empty=True, messages=LASTNAME_MESSAGES)
    email = validators.Email(not_empty=True, messages=EMAIL_MESSAGES)
    town = validators.String(not_empty=True, messages=TOWN_MESSAGES)
    postcode = validators.Int(not_empty=True, messages=POSTCODE_MESSAGES)
    project_name = validators.String(not_empty=True, messages=PROJECT_MESSAGES)
    what = validators.String(not_empty=True, messages=WHAT_MESSAGES)
    why = validators.String(not_empty=True, messages=WHY_MESSAGES)
    people = validators.String(not_empty=True, messages=PEOPLE_MESSAGES)
    optin = validators.StringBool(if_missing=False)
    tc = validators.StringBool(not_empty=True, messages=TC_MESSAGES)

def validate_submission(form):
    """
    >>> try:
    ...     validate_submission({'firstname': None,
    ...                          'lastname' : None,
    ...                          'email' : 'NOT',
    ...                          'town' : None,
    ...                          'postcode' : 'NOT',
    ...                          'project_name' : None,
    ...                          'what' : None,
    ...                          'why' : None,
    ...                          'people' : None})
    ... except Invalid, e:
    ...     e.unpack_errors()
    {'town': u'Please enter a town', 'what': u'Please describe the favour', 'project_name': u'Please name your project', 'firstname': u'Please enter your firstname', 'people': u'Please enter the amount of people', 'lastname': u'Please enter your lastname', 'why': u'Please describe who will benefit', 'email': u'Please enter a valid email', 'postcode': u'Please enter a valid postcode', 'tc': u'Please agree to the terms and conditions'}
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
    {'town': 'manly', 'what': 'add one floor to the building', 'project_name': 'South Steyne SLSC', 'firstname': 'eugene', 'people': '327', 'lastname': 'van den bulke', 'why': 'allow us to serve our community better', 'optin': False, 'email': 'eugene.vandenbulke@gmail.com', 'postcode': 2095, 'tc': True}
"""
    return SubmissionSchema(allow_extra_fields=True).to_python(form)

def render_submission(defaults=dict(), errors=dict()):
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

def render_status(current, defaults=dict(), errors=dict()):
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

def render_project(project, defaults=dict(), errors=dict()):
    form = serve_template('forms/project.html', project=project)
    return htmlfill.render(form, defaults, errors, error_class="error-input")

if __name__ == "__main__":
    import doctest
    doctest.testmod()

