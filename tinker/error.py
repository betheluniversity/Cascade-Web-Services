
#flask
from flask import render_template

#local
from tinker import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html')