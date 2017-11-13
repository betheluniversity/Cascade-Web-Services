
# tinker
import urllib

import requests
from requests.exceptions import SSLError, ConnectionError

# Global
from datetime import datetime

# Packages
from flask_sqlalchemy import SQLAlchemy

# Local
from urllib3.exceptions import ProtocolError, MaxRetryError

from tinker import app
from tinker.admin.redirects.models import BethelRedirect
from tinker.tinker_controller import TinkerController


class RedirectsController(TinkerController):

    def __init__(self, database):
        super(RedirectsController, self).__init__()
        if isinstance(database, SQLAlchemy):
            self.db = database
        else:
            raise TypeError('tinker/admin/redirects/redirects_controller requires that the database arg is SQLAlchemy')

    # Creates a new redirect text file
    def create_redirect_text_file(self):
        map_file = open(app.config['REDIRECTS_FILE_PATH'], 'w')
        map_file_back = open(app.config['REDIRECTS_FILE_PATH'] + ".back", 'w')
        redirects = BethelRedirect.query.all()

        for item in redirects:
            map_file.write("%s %s\n" % (item.from_path, item.to_url))
            map_file_back.write("%s %s\n" % (item.from_path, item.to_url))

        return 'done'

    def add_row_to_db(self, from_path, to_url, short_url, expiration_date):
        new_redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url,
                                      expiration_date=expiration_date)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def api_add_row(self, from_path, to_url):
        new_redirect = BethelRedirect(from_path=from_path, to_url=to_url)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def search_db(self, search_type, term):
        term += "%"
        if search_type == "from_path":  # Search by from_path
            results = BethelRedirect.query.filter(BethelRedirect.from_path.like(term)).limit(100).all()
        else:  # Search by to_url
            results = BethelRedirect.query.filter(BethelRedirect.to_url.like(term)).limit(100).all()
        results.sort()
        return results

    def delete_row_from_db(self, from_path):
        redirect_to_delete = BethelRedirect.query.get(from_path)
        self.db.session.delete(redirect_to_delete)
        self.db.session.commit()

    def expire_old_redirects(self):
        today = datetime.utcnow()
        redirects = BethelRedirect.query.filter(BethelRedirect.expiration_date < today).all()
        for redirect in redirects:
            self.db.session.delete(redirect)
        self.db.session.commit()

    def get_all_rows(self):
        return BethelRedirect.query.all()

    def rollback(self):
        self.db.session.rollback()

    def redirect_change(self):

        loop_counter = 0

        redirects = BethelRedirect.query.all()
        # following are files to be written so we can pass the 'change log' over to marketing
        # with this, they can approve or ask us to fix/replace some of the redirects
        checkDelete = open('Check_For_Deletion.html', 'w+')
        changed = open('Redirect_Changed.html', 'w+')
        redundant_changes = open('Redundant_Changes.html', 'w+')

        today = datetime.now()
        today = today.strftime("%m/%d/%y %I:%M")

        # Might stay, might not :)
        changed.write('These are the redirects that are being changed. \n' + str(today) + '</br></br>')
        changed.write("""<table>
                        <thead>
                        <tr>
                        <th style = 'text-align: left'> From Path </th>
                        <th style = 'text-align: left'> To Url </th>
                        <th style = 'text-align: left'> Changed to </th>
                        </tr>
                        </thead>
                        <tfoot>""")

        checkDelete.write('These are the redirects that are being deleted. \n' + str(today) + '</br></br>')
        checkDelete.write("""<table>
                        <thead>
                        <tr>
                        <th style = 'text-align: left'> From Path </th>
                        <th style = 'text-align: left'> To Url </th>
                        </tr>
                        </thead>
                        <tfoot>""")

        redundant_changes.write("""<table>
                                    <thead>
                                    <tr>
                                    <th style = 'text-align: left'> From Path </th>
                                    <th style = 'text-align: left'> To Url </th>
                                    <th style = 'text-align: left'> Change </th>
                                    </tr>
                                    </thead>
                                    <tfoot>""")

        for redirect in redirects:
            loop_counter += 1
            if loop_counter % 2000 == 0:
                print loop_counter
            try:
                response = requests.get('https://www.bethel.edu' + redirect.from_path)
                redirect.to_url.replace('\n', '')
                redirect.to_url.replace(' ', '')

            except SSLError as e:
                # BKJ SSLError.SSLError and SSLError.CertificateError thrown here. Not sure how to prevent these.
                # print redirect.from_path
                # print e.args
                continue

            except ConnectionError as e:
                # BKJ MaxRetryError and ProtocolError being thrown here. Not sure how to prevent these.
                # MaxRetryError is being caught and deleted
                # print redirect.from_path
                # print e.args

                if 'Max retries exceeded' in e.args[0].args[0]:
                    # catches and deletes the MaxRetryErrors

                    yield "Printing to check for deletion: " + redirect.from_path + "<br/>"
                    # print e.args[0][0]  # e.args[0][0] is the section of the tuple containing the error message
                    checkDelete.write("<tr>\n" +
                                    "<td>" + redirect.from_path + "</td>\n"
                                    "<td>" + redirect.to_url + "</td>\n"
                                  "</tr>\n")
                    continue

                else:
                    # If it gets here, it's a ProtocolError and life goes on
                    continue

            except:
                # BKJ Can't print these arguments, but all the other errors are being caught here. Nothing else should break this.
                continue

            if response.url != redirect.to_url:

                if 'auth' in response.url:  # checks if the response.url is an auth page, decodes it and replaces the to_url to that
                    response.url = urllib.unquote(urllib.unquote(response.url))
                    redirect.to_url.replace(redirect.to_url, response.url)
                    self.db.session.delete(redirect)
                    self.db.session.add(redirect)
                    # self.db.session.commit()
                    continue

                # checking for redundant changes in the to_url
                if 'https' not in redirect.to_url:
                    https_test = redirect.to_url.replace('http', 'https')
                    if response.url == https_test:
                        # [redirects.replace(redirect.to_url, response.url) for item in redirect]
                        redirect.to_url.replace(redirect.to_url, response.url)
                        self.db.session.delete(redirect)
                        self.db.session.add(redirect)
                        # self.db.session.commit()
                        redundant_changes.write("<tr>\n" +
                                                "<td>" + redirect.from_path + "</td>\n"
                                                "<td>" + redirect.to_url + "</td>\n"
                                                "<td> Changing http to https </td>\n"
                                                "</tr>\n")
                        continue
                elif response.url == redirect.to_url + '/':
                    # [redirects.replace(redirect.to_url, response.url) for item in redirect]
                    redirect.to_url.replace(redirect.to_url, response.url)
                    self.db.session.delete(redirect)
                    self.db.session.add(redirect)
                    # self.db.session.commit()
                    redundant_changes.write("<tr>\n" +
                                            "<td>" + redirect.from_path + "</td>\n"
                                            "<td>" + redirect.to_url + "</td>\n"
                                            "<td> Adding '/' at end </td>\n"
                                            "</tr>\n")
                    continue

                yield 'changing %s to %s <br/>' % (redirect.to_url, response.url)
                # [redirects.replace(redirect.to_url, response.url) for item in redirect]
                redirect.to_url.replace(redirect.to_url, response.url)
                self.db.session.delete(redirect)
                self.db.session.add(redirect)
                # self.db.session.commit()
                changed.write("<tr>\n" +
                                "<td>" + redirect.from_path + "</td>\n"
                                "<td>" + redirect.to_url + "</td>\n"
                                "<td>" + response.url + "</td>"
                                "</tr>\n")

        contact_footer = 'If you have any questions/concerns, please contact web services.'

        changed.write('</tfoot></table> \n \n' + contact_footer)
        checkDelete.write('</tfoot></table> \n \n' + contact_footer)
        redundant_changes.write('</tfoot></table>')

        self.db.session.commit()
        changed.close()
        checkDelete.close()
        redundant_changes.close()

        print 'done'
