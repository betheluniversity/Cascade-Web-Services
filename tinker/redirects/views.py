__author__ = 'ejc84332'

from flask import Blueprint, render_template, abort, request
from flask.ext.sqlalchemy import SQLAlchemy, Session

from tinker import app, db

from tinker.redirects.models import BethelRedirect

redirect_blueprint = Blueprint('redirect_blueprint', __name__,
                               template_folder='templates')


@redirect_blueprint.route('/')
def show():

    redirects = BethelRedirect.query.all()

    return render_template('redirects.html', **locals())


@redirect_blueprint.route('/search', methods=['post'])
def search():
    #todo: limit results to...100?
    from_path = request.form['from_path'] + "%"

    if from_path == "%":
        return ""

    redirects = BethelRedirect.query.filter(BethelRedirect.from_path.like(from_path)).limit(100).all()
    redirects.sort()
    return render_template('redirect-ajax.html', **locals())


@redirect_blueprint.route('/new-submit', methods=['post'])
def new_redirect_submti():

    form = request.form
    from_path = form['new-redirect-from']
    to_url = form['new-redirect-to']

    if not from_path.startswith("/"):
        from_path = "/" + from_path

    redirect = BethelRedirect(from_path=from_path, to_url=to_url)

    db.session.add(redirect)
    db.session.commit()

    return str(redirect)


@redirect_blueprint.route('/delete', methods=['post'])
def delete_redirect():

    path = request.form['from_path']

    resp = str(path)

    try:
        redirect = BethelRedirect.query.get(path)
        db.session.delete(redirect)
        db.session.commit()

    except:
        return "fail"

    return "deleted %s" % resp


@redirect_blueprint.route('/load')
def load_redirects():

    from sqlalchemy.exc import IntegrityError

    url_file = open('/Users/ejc84332/Desktop/rewrites.txt', 'r')
    lines = [line.strip() for line in url_file.readlines()]

    for line in lines:
        if line.startswith("#"):
            continue
        try:
            from_path, to_url = line.split()
            redirect = BethelRedirect(from_path=from_path, to_url=to_url)
            db.session.add(redirect)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


    return "done"