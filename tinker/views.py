from flask import render_template
from tinker import app


@app.route('/')
def home():
    # index page for adding events and things
    return render_template('home.html', **locals())


@app.route('/about')
def about():
    return render_template('about-page.html', **locals())


@app.route('/read/<read_id>')
def read_route(read_id):
    from tinker_base import TinkerBase
    base = TinkerBase()
    return "<pre>%s</pre>" % str(base.read_block(read_id))
