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
    '{"status": "", "comment": [], "landing": []}'
    """
    landing = []
    for project in unpublished_projects():
        landing.append({
            'title' : project.title,
            'town' : project.submission.town,
            'postcode' : project.submission.postcode,
            'description' : project.description,
            'photos' : project.photos,
            'videos' : project.videos
            })

    comment = []
    for project in published_projects():
        comment.append({
            'title' : project.title,
            'town' : project.submission.town,
            'postcode' : project.submission.postcode,
            'description' : project.description,
            'photos' : project.photos,
            'videos' : project.videos
            })
    return json.dumps({'status' : current_status(),
                       'comment' : comment,
                       'landing' : landing})

def current_status():
    """
    when no status return None

    >>> current_status()
    ''

    >>> man = Status(text='first')
    >>> current_status()
    'first'

    >>> man = Status(text='latest')
    >>> current_status()
    'latest'

    tear down
    >>> for status in Status.select():
    ...     status.destroySelf()
    """
    try:
        return Status.select(orderBy='-id')[0].text
    except IndexError:
        return ''

def save_status(form):
    Status(**form)

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
