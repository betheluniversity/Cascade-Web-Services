import re

from bu_cascade.asset_tools import find
from flask import Blueprint, render_template, session, url_for, redirect, request
from flask_classy import FlaskView, route
from flask import json as fjson, abort


# tinker
from tinker import app
from tinker.office_hours.forms import OfficeHoursForm
from tinker.office_hours.office_hours_controller import OfficeHoursController


OfficeHoursBlueprint = Blueprint('office_hours', __name__, template_folder='templates')


class OfficeHoursView(FlaskView):
    route_base = '/office-hours'

    def __init__(self):
        self.base = OfficeHoursController()

    def before_request(self, name, **kwargs):
        if "Administrators" in session['groups']:
            pass
        # homepage check
        elif request.path == '/office-hours/':
            try:
                # loop over all.
                office_blocks_can_access = self.base.traverse_xml('https://staging.bethel.edu/_shared-content/xml/office-hours.xml', 'system-block')
                if len(office_blocks_can_access) == 0:
                    abort(403)
            except:
                abort(403)
        # submit/edit check
        elif '/edit/' in request.path or '/submit/' in request.path:
            try:
                block_id = request.path.split('/')[-1]
                if not self.base.can_user_access_block(block_id):
                    abort(403)
            except:
                abort(403)
        else:
            abort(403)

    def index(self):
        username = session['username']

        forms = self.base.traverse_xml(app.config['OFFICE_HOURS_XML_URL'], 'system-block')
        standard_hours, office_hours = self.base.separate_office_hours(forms)

        office_hours.sort(key=lambda item: item['title'])

        return render_template('office-hours/home.html', **locals())

    def edit(self, block_id):
        edit_data, sdata, mdata = self.base.load_office_hours_block(block_id=block_id)
        standard_edit_data, s, m = self.base.load_office_hours_block(block_id=app.config['OFFICE_HOURS_STANDARD_BLOCK'])
        
        try:
            edit_data['next_start_date'] = edit_data['next_start_date'].strftime('%m/%d/%Y')
        except:
            pass

        for e in edit_data['exceptions']:
            if e['date']:
                e['date'] = e['date'].strftime('%m/%d/%Y')
            if not e['open']:
                e['open'] = ''
            if not e['close']:
                e['close'] = ''

        form = OfficeHoursForm(**edit_data)

        return render_template('office-hours/form.html', **locals())

    @route('/submit', methods=['POST'])
    def submit(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        block_id = rform.get('block_id')

        if block_id:
            block = self.base.read_block(block_id)

            data, mdata, sdata = block.read_asset()
            asset = self.base.update_structure(data, mdata, rform)
            # asset = self.base.rotate_hours(asset)

            resp = str(block.edit_asset(asset))
            self.base.cascade_call_logger(locals())
            self.base.log_sentry("Office Hour Submission", resp)

        return render_template('office-hours/confirm.html', **locals())

    def rotate_hours(self, block_id):
        block = self.base.read_block(block_id)
        data, mdata, sdata = block.read_asset()

        self.base.rotate_hours(sdata)
        block.edit_asset(data)
        return 'success'

    # todo: leave this code please, I want this test in version control for the time being.
    # this method tests using ldap
    # def test(self):
    #     con = ldap.initialize('ldap://bsp-ldap.bu.ac.bethel.edu:389')
    #     con.simple_bind_s('BU\svc-tinker', app.config['LDAP_SVC_TINKER_PASSWORD'])
    #
    #     results = con.search_s('ou=Groups,dc=bu,dc=ac,dc=bethel,dc=edu', ldap.SCOPE_SUBTREE, 'cn=*- Employee*')
    #     list = []
    #     for result in results:
    #         list.append(result[0].split(',OU')[0].split('CN=')[1])
    #
    #     sorted(list)
    #
    #     for item in list:
    #         print item
    #
    #     return 'test'

OfficeHoursView.register(OfficeHoursBlueprint)
