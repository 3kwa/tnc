import os.path
import json

import cherrypy

from templates import serve_template
import forms
from models import save_submission, unchecked_submissions, reject_submission, \
                   accept_submission, unpublished_projects, publish_project, \
                   unreject, unaccept, unpublish, published_projects, \
                   publish_json, current_status
import models

class App(object):

    @cherrypy.expose
    def index(self, **form):

        if cherrypy.request.method == "GET":
            return serve_template('index.html', form=forms.render_submission())

        if cherrypy.request.method == "POST":
            try:
                values = forms.validate_submission(form)
            except forms.Invalid, e:
                return serve_template('index.html',
                                      form=forms.render_submission(
                                          defaults=e.value,
                                          errors=e.unpack_errors()))
            else:
                save_submission(values)
                raise cherrypy.HTTPRedirect("thankyou")

    @cherrypy.expose
    def thankyou(self):
        return serve_template('thankyou.html')

    @cherrypy.expose
    def admin(self, **form):

        if cherrypy.request.method == "POST":
            if 'text' in form:
                try:
                    values = forms.validate_status(form)
                except forms.Invalid, e:
                    status = forms.render_status(current=current_status(),
                                                 defaults=e.value,
                                                 errors=e.unpack_errors())
                else:
                    models.save_status(values)
                    status = forms.render_status(current=current_status())

        if cherrypy.request.method == "GET":
            status = forms.render_status(current=current_status())

        trash = models.trashed_submissions()
        projects = unpublished_projects()
        submissions = unchecked_submissions()
        public = published_projects()
        return serve_template('admin.html',
                              trash=trash,
                              submissions=submissions,
                              projects=projects,
                              public=public,
                              status=status)

    @cherrypy.expose
    def project(self, id_, action, **form):

        p = models.get_project(id_)
        errors = {}

        if cherrypy.request.method == "GET":
            if action == 'edit':
                defaults = {'title' : p.title,
                            'description' : p.description,
                            'photos' : p.photos,
                            'videos' : p.videos}
            elif action == 'cancel':
                return serve_template('project.html', project=p)

        if cherrypy.request.method == "POST":
            try:
                defaults = forms.validate_project(form)
            except forms.Invalid, e:
                defaults = e.value
                errors = e.unpack_errors()
            else:
                models.update_project(id_, defaults)
                return serve_template('project.html', project=p)

        return forms.render_project(p, defaults=defaults, errors=errors)



    @cherrypy.expose
    def ajax(self, action, id_):
        if action == 'reject':
            reject_submission(id_)
            return 'OK'
        elif action == 'unreject':
            unreject(id_)
            return 'OK'
        elif action == 'accept':
            project = accept_submission(id_)
            return str(project.id)
        elif action == 'unaccept':
            return str(unaccept(id_))
        elif action == 'publish':
            publish_project(id_)
            return 'OK'
        elif action == 'unpublish':
            unpublish(id_)
            return 'OK'
        else:
            raise cherrypy.HTTPError(501)

    @cherrypy.expose
    def publish(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return publish_json()

    @cherrypy.expose
    def submission(self, **form):
        try:
            values = forms.validate_submission(form)
            errors = {}
        except forms.Invalid, e:
            values = e.value
            errors = e.unpack_errors()
        else:
            models.save_submission(values)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({'values' : values, 'errors' : errors})

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(current_dir, 'web.conf')

cherrypy.quickstart(App(), '/tnc', config=config_file)
