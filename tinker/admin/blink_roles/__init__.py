# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from roles_roledata import uid, portal
from tinker.tinker_controller import admin_permissions


class BlinkRolesView(FlaskView):
    route_base = '/admin/blink-roles'

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        uid_list = uid
        portal_list = portal
        return render_template('admin/blink-roles/home.html', **locals())
