import os
import sys
import ConfigParser
import json

from sqlobject import *


class Submission(SQLObject):
    firstname = StringCol()
    lastname = StringCol()
    email = StringCol()
    town = StringCol()
    postcode = IntCol()
    project_name = StringCol()
    what = StringCol()
    why = StringCol()
    people = StringCol()
    optin = BoolCol()
    checked = BoolCol(default=False)

class Project(SQLObject):
    submission = ForeignKey('Submission')
    title = StringCol()
    description = StringCol()
    photos = StringCol(default='')
    videos = StringCol(default='')
    publish = BoolCol(default=False)

class Status(SQLObject):
    text = StringCol()
    beer = IntCol()


def save_submission(form):
    del form['tc']
    return Submission(**form)

def unchecked_submissions():
    return Submission.select(Submission.q.checked == False)

def reject_submission(id_):
    Submission.get(id_).checked=True

def accept_submission(id_):
    submission = Submission.get(id_)
    submission.checked = True
    return Project(submission=submission,
            title=submission.project_name,
            description=submission.what)

def trashed_submissions():
    # submission that are projects
    projects = [project.submission.id for project in Project.select()]
    # checked submission
    return [submission for submission
        in Submission.select(Submission.q.checked == True)
        if submission.id not in projects]

def unpublished_projects():
    return Project.select(Project.q.publish == False)

def published_projects():
    return Project.select(Project.q.publish == True)

def publish_project(id_):
    Project.get(id_).publish=True

def unreject(id_):
    Submission.get(id_).checked = False

def unaccept(id_):
    project = Project.get(id_)
    submission = project.submission
    submission.checked = False
    project.destroySelf()
    return submission.id

def unpublish(id_):
    Project.get(id_).publish = False


def create_db():
    Submission.createTable()
    Project.createTable()
    Status.createTable()

def publish_json():
    """
    >>> publish_json()
    '{"status": "The Tooheys New Crew is getting ready to rock your world", "comment": [], "beer": 0, "landing": []}'
    """
    landing = []
    for project in published_projects():
        landing.append({
            'title' : project.title,
            'town' : project.submission.town,
            'postcode' : project.submission.postcode,
            'description' : project.description,
            'photos' : project.photos,
            'videos' : project.videos
            })

    comment = []
    for project in unpublished_projects():
        comment.append({
            'title' : project.title,
            'town' : project.submission.town,
            'postcode' : project.submission.postcode,
            'description' : project.description,
            'photos' : project.photos,
            'videos' : project.videos
            })
    status = current_status()
    if status is not None:
        text = status.text
        beer = status.beer
    else:
        text = ''
        beer = 0
    return json.dumps({'status' : text,
                       'beer' : beer,
                       'comment' : comment,
                       'landing' : landing})

def current_status():
    """
    >>> current_status().text
    'The Tooheys New Crew is getting ready to rock your world'

    >>> man = Status(text='first', beer=1)
    >>> current_status().text
    'first'

    >>> man = Status(text='latest', beer=1)
    >>> current_status().text
    'latest'

    tear down
    >>> for status in Status.select():
    ...     status.destroySelf()
    """
    try:
        return Status.select(orderBy='-id')[0]
    except IndexError:
        return Status(text=
            'The Tooheys New Crew is getting ready to rock your world',
            beer=0)

def save_status(form):
    """
    >>> save_status({'text' : 'Only status'})
    <Status 2 text='Only status' beer=0>

    >>> save_status({'beer' : 666})
    <Status 3 text='Only status' beer=666>

    >>> save_status({'text' : '', 'beer' : 777})
    <Status 4 text='Only status' beer=777>

    >>> save_status({'text' : 'The full monty', 'beer' : 1000})
    <Status 5 text='The full monty' beer=1000>
    """
    # ugly change of requirement fix (beer)
    # String validators defaults to '' when empty
    # Int defaults to None but set to -1 in Schema using if_empty
    current = current_status()
    was = {'text' : current.text, 'beer' : current.beer}
    # using get so doctest can be agnostic (smart?)
    if form.get('text', None) =='':
        del form['text']
    if form.get('beer', None) == -1:
        del form['beer']
    was.update(form)
    return Status(**was)

def get_project(id_):
    return Project.get(id_)


def update_project(id_, form):
    project = Project.get(id_)
    project.set(**form)

if __name__ == "__main__":

    sqlhub.processConnection = connectionForURI('sqlite:/:memory:')
    create_db()

    import doctest
    doctest.testmod()

else:

    config = ConfigParser.ConfigParser()
    config.readfp(open('web.conf'))
    db = config.get('database', 'uri')[1:-1]

    sqlhub.processConnection = connectionForURI(db)

    #try:
        #os.unlink(os.path.join(sys.path[0], 'db.sqlite'))
    #except OSError:
        #pass

    #create_db()
