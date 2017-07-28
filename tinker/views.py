import os
from flask import send_from_directory
from flask_classy import FlaskView
from flask import Flask, Blueprint
from flask import render_template, send_file
from tinker import app

BaseBlueprint = Blueprint('base', __name__, template_folder='templates')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


class Base(FlaskView):
    route_base = '/'

    def index(self):
        # index page for adding events and things
        return render_template('index.html', **locals())

    def about(self):
        return render_template('about-page.html', **locals())

    def get_image(self, image_name):
        return send_file('images/' + image_name, mimetype='image/png')

    def profile(self):
        return render_template('profile.html', **locals())

Base.register(BaseBlueprint)
