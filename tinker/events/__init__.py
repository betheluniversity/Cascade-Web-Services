import time
from flask.ext.classy import FlaskView, route
from tinker.events.events_controller import EventsController
from bu_cascade.asset_tools import update
from flask import Blueprint, redirect, session, render_template, request, url_for
from tinker import app
from events_metadata import metadata_list

EventsBlueprint = Blueprint('events', __name__, template_folder='templates')


class EventsView(FlaskView):
    route_base = '/events'

    def __init__(self):
        self.base = EventsController()

    # Allows any user to access events
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        forms = self.base.traverse_xml(app.config['EVENTS_URL'], 'system-page')
<<<<<<< HEAD
        if 'Events Approver' in session['groups']:
            # todo: call traverse_xml() in tinker_controller
            events_approver_forms = self.base.traverse_xml()
=======
        if 'Event Approver' in session['groups']:
            forms, event_approver_forms = self.base.get_approver_forms(forms)
>>>>>>> origin/create-base-view
        return render_template('events-home.html', **locals())

    def confirm(self):
        return render_template('submit-confirm.html', **locals())

    def events_in_workflow(self):
        return render_template('event-in-workflow.html')

    def add(self):
        # import this here so we dont load all the content from cascade during homepage load
        from tinker.events.forms import EventForm

        form = EventForm()
        add_form = True
        return render_template('events-form.html', **locals())

<<<<<<< HEAD
    @route('/delete/<page_id>')
    def delete_page(self, page_id):
        events_page = self.base.read_page(page_id)
        response = events_page.delete_asset()
        app.logger.debug(time.strftime("%c") + ": New folder creation by " + session['username'] + " " + str(response))
        self.base.publish(app.config['EVENTS_XML_ID'])
        return redirect(url_for('events.EventsView:delete_confirm'), code=302)

    @route('/edit/<events_id>')
    def edit_events_page(self, event_id):
=======
    @route('/edit/<event_id>')
    def edit_event_page(self, event_id):
>>>>>>> origin/create-base-view
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('events.EventsView:event_in_workflow'), code=302)

        edit_data, dates, author = self.base.build_edit_form(event_id)
        # todo: fix this with the submit_all() functionality ASK CALEB
        # convert 'On/Off campus' to 'On/Off Campus' for all events
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        if 'location' in edit_data and edit_data['location']:
            edit_data['location'].replace(' c', ' C')

        return render_template('event-form.html', **locals())

    @route('/duplicate/<events_id>')
    def duplicate_events_page(self, event_id):
        edit_data, dates, author = self.base.build_edit_form(event_id)
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        add_form = True

        return render_template('events-form.html', **locals())

    @route("/submit/<edit>", methods=['post'])
    @route("/submit", methods=['post'])
    def submit_form(self, edit=False):
        rform = request.form
        username = session['username']
        eid = rform.get('event_id')
        workflow = self.base.create_workflow("1ca9794e8c586513742d45fd39c5ffe3")
        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)
        failed = self.base.validate_form(rform, dates_good, event_dates)

        wysiwyg_keys = ['main_content', 'questions', 'link', 'registration_details', 'sponsors', 'maps_directions']
        if failed:
            return failed

        if not eid:
            bid = app.config['EVENTS_BASE_ASSET']
            event_data, metadata, structured_data = self.base.cascade_connector.load_base_asset_by_id(bid, 'page')
            add_data = self.base.get_add_data(metadata_list, rform, wysiwyg_keys)
            add_data['event-dates'] = self.base.get_dates(add_data)
            add_data['author'] = request.form['author']
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow)
<<<<<<< HEAD
            response = self.base.create(asset)
            self.base.log_sentry("New events submission", response)
=======
>>>>>>> origin/create-base-view

            resp = self.base.create_page(asset)
            self.base.log_sentry("New event submission", resp)
        else:
            page = self.base.read_page(eid)
            event_data, metadata, structured_data = page.get_asset()
            add_data = self.base.get_add_data(metadata_list, rform, wysiwyg_keys)
            add_data['event-dates'] = self.base.get_dates(add_data)
            add_data['author'] = request.form['author']
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow, event_id=eid)

            self.base.check_new_year_folder(eid, add_data, username)
            proxy_page = self.base.read_page(eid)
            resp = proxy_page.edit_asset(asset)
            self.base.log_sentry("Event edit submission", resp)

        # todo: ASK CALEB IF THIS IS OKAY.
        if 'link' in add_data and add_data['link']:
            from tinker.admin.redirects import RedirectsView
            view = RedirectsView()
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            view.new_internal_redirect_submit(path, add_data['link'])

        return redirect(url_for('events.EventsView:confirm'), code=302)

    @route('/api/reset-tinker-edits/<events_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        my_page = self.base.read_page(event_id)

        asset, md, sd = my_page.get_asset()
        update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

    def edit_all(self):
        type_to_find = 'system-page'
        xml_url = app.config['EVENTS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'

EventsView.register(EventsBlueprint)
