# Global
import ast
import json

# Packages
from datetime import datetime, timedelta
from flask import abort, render_template, request
from flask_classy import FlaskView, route
from os.path import getmtime
from sqlalchemy import or_, and_


# Local
from tinker import app, db
from tinker.admin.program_search.models import ProgramTag
from tinker.admin.program_search.program_search_controller import ProgramSearchController
from tinker.tinker_controller import admin_permissions, requires_auth


class ProgramSearchView(FlaskView):
    route_base = '/admin/program-search'

    def __init__(self):
        self.base = ProgramSearchController()

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        school_labels = self.base.get_school_labels()
        program_concentrations = self.base.get_programs_for_dropdown()

        return render_template('admin/program-search/home.html', **locals())

    @route('/submit', methods=['post'])
    def submit(self):
        school_labels = self.base.get_school_labels()
        program_concentrations = self.base.get_programs_for_dropdown()

        try:
            rform = json.loads(request.data)
            key = rform.get('key')
            tag = rform.get('tag')

            if key == 'Any' or key == '' or tag == '' or tag is None:
                return render_template('admin/program-search/home.html', **locals())

            outcome = ast.literal_eval(rform.get('outcome'))
            topic = ast.literal_eval(rform.get('topic'))
            other = ast.literal_eval(rform.get('other'))
        except ValueError:
            return abort(400)

        try:
            program_tag = ProgramTag(key=key, tag=tag, outcome=outcome, other=other, topic=topic)
            session = db.session

            session.add(program_tag)
            session.commit()

            self.base.create_new_csv_file()
        except:
            db.session.rollback()

        return render_template('admin/program-search/home.html', **locals())

    @route('/multi-delete', methods=['POST'])
    def multi_delete(self):
        list_of_ids_to_delete = json.loads(request.data)
        for id_to_delete in list_of_ids_to_delete:
            if isinstance(id_to_delete, str):
                id_to_delete = id_to_delete.strip()
                ProgramTag.query.filter_by(id=id_to_delete).delete()
            else:
                return "One of the ids given to this method was not a string"
        db.session.commit()
        self.base.create_new_csv_file()
        return 'Deleted ids: ' + ', '.join(list_of_ids_to_delete)

    @route('/manual-sftp-publish', methods=['post'])
    def manual_sftp_publish(self):
        if app.config['ENVIRON'] == 'prod':
            self.base.create_new_csv_file()
            return self.base.write_to_sftp(app.config['PROGRAM_SEARCH_CSV_LOCAL'], app.config['PROGRAM_SEARCH_CSV_SFTP'], False, True)
        else:
            return json.dumps({
                'type': 'success',
                'message': 'Test Environment: No updates were made'
            })

    @requires_auth
    @route('/public/cron-sftp-publish')
    def cron_sftp_publish(self):
        if app.config['ENVIRON'] == 'prod':
            self.base.create_new_csv_file()
            last_modified = datetime.now() - datetime.fromtimestamp(getmtime(app.config['PROGRAM_SEARCH_CSV']))
            cron_interval = timedelta(minutes=30)

            if last_modified < cron_interval:
                # SFTP
                return self.base.write_to_sftp(app.config['PROGRAM_SEARCH_CSV_LOCAL'], app.config['PROGRAM_SEARCH_CSV_SFTP'], True, True)
            else:
                return "Program Search file hasn't been updated since the last cron run"
        else:
            return 'Nothing to do'

    @route('/search', methods=['post'])
    def search(self):
        try:
            data = json.loads(request.data)

            search_tag = data['search_tag']
            if search_tag is None:
                return abort(500)

            search_key = data['search_key']
            if search_key is None:
                return abort(500)
        except ValueError:
            return abort(500)

        if len(search_tag) == 0:  # If empty string, make generic wildcard
            search_tag = "%"
        else:
            search_tag = "%" + search_tag + "%"

        if len(search_key) == 0:  # If empty string, make generic wildcard
            search_key = "%"
        else:
            search_key = "%" + search_key + "%"

        search_results = ProgramTag.query.filter(
            and_(ProgramTag.tag.like(search_tag), ProgramTag.key.like(search_key))
        ).all()

        # builds a dict that is used to change concentration codes to program names
        program_concentrations = self.base.get_programs_for_dropdown(True)

        return render_template('admin/program-search/ajax.html', **locals())

    @route('/audit', methods=['get'])
    @route('/database-audit', methods=['get'])
    def database_audit(self):
        return render_template('admin/program-search/database-audit.html', **locals())

    @route('/database-audit-table', methods=['post'])
    def database_audit_table(self):
        # tinker local db
        search_results = ProgramTag.query.distinct('key').group_by('key').all()
        keys_in_tinker_db = []
        for search_result in search_results:
            keys_in_tinker_db.append(search_result.key)

        # cascade block info
        keys_in_cascade = []
        program_concentrations = self.base.get_programs_for_dropdown()
        for program_concentration in program_concentrations:
            keys_in_cascade.append(program_concentration.get('value'))

        # get the list of differences
        list_of_issue_programs = list(set(keys_in_tinker_db) - set(keys_in_cascade))

        # get individual differences
        unmatched_keys_in_tinker_db = list(set(list_of_issue_programs) & set(keys_in_tinker_db))
        unmatched_keys_in_cascade = list(set(list_of_issue_programs) & set(keys_in_cascade))

        return render_template('admin/program-search/database-audit-table.html', **locals())

    @route('/database-audit-update', methods=['post'])
    def database_audit_update(self):
        data = json.loads(request.data)
        old_key = data['old_key']
        new_key = data['new_key']

        if old_key and new_key:
            search_results = ProgramTag.query.filter(ProgramTag.key == old_key).update({'key': new_key})
            db.session.commit()

        return 'DONE'

    @route('/database-audit-delete', methods=['post'])
    def database_audit_delete(self):
        data = json.loads(request.data)
        old_key = data['old_key']

        search_results = ProgramTag.query.filter(ProgramTag.key == old_key).delete()
        db.session.commit()

        return 'DONE'
