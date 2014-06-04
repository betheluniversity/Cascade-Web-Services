#python
import datetime


#modules
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import SelectMultipleField
from wtforms import SelectField
from wtforms import RadioField
from wtforms import DateTimeField
from wtforms import FieldList
from wtforms import FormField
from wtforms import Field
from wtforms import Label
from wtforms.validators import Required
#local
from cascade_web_services import app
from tools import get_client


def get_md():

    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': '/Event',
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = get_client()
    md = client.service.read(auth, identifier)
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition


def get_choices():

    data = get_md()

    general_list = data[0].possibleValues.possibleValue
    offices_list = data[1].possibleValues.possibleValue
    academics_dates_list = data[2].possibleValues.possibleValue
    cas_departments_list = data[3].possibleValues.possibleValue
    internal_list = data[4].possibleValues.possibleValue

    general = []
    for item in general_list:
        general.append((item.value, item.value))

    offices = []
    for item in offices_list:
        offices.append((item.value, item.value))

    academics_dates = []
    for item in academics_dates_list:
        academics_dates.append((item.value, item.value))

    internal = []
    for item in internal_list:
        internal.append((item.value, item.value))

    cas_departments = []
    for item in cas_departments_list:
        cas_departments.append((item.value, item.value))

    return {'general': general, 'offices': offices, 'academics_dates': academics_dates,
            'internal': internal, 'cas_departments': cas_departments}


##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class CKEditorTextAreaField(TextAreaField):
    pass


class HeadingField(Field):

    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None):

        self.default = default
        self.description = description
        self.filters = filters
        self.flags = None
        self.name = _prefix + _name
        self.short_name = _name
        self.type = type(self).__name__
        self.validators = validators or list(self.validators)

        self.id = id or self.name
        self.label = label

    def __unicode__(self):
        return None

    def __str__(self):
        return None

    def __html__(self):
        return None


class EventForm(Form):

    choices = get_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    academics_dates_choices = choices['academics_dates']
    internal_choices = choices['internal']
    cas_departments_choices = choices['cas_departments']

    location_choices = (('On Campus', 'On Campus'), ('Off Campus', 'Off Campus'))
    heading_choices = (('Registration', 'Registration'), ('Ticketing', 'Ticketing'))

    what = HeadingField(label="What?")
    title = TextField('Event Name', validators=[Required()])
    teaser = TextField('Teaser', validators=[Required()])
    featuring = TextField('Featuring', validators=[Required()])
    sponsors = TextAreaField('Sponsors')
    description = CKEditorTextAreaField('Event description', validators=[Required()])

    when = HeadingField(label="When?")
    start = DateTimeField("Start Date", default=datetime.datetime.now)

    where = HeadingField(label="Where?")
    location = SelectField('Location', choices=location_choices, validators=[Required()])
    off_location = TextField("Off Campus Location")
    directions = CKEditorTextAreaField('Directions')

    why = HeadingField(label="Does your event require registration or payment?")
    heading = RadioField('Heading', choices=heading_choices)
    details = CKEditorTextAreaField('Registration/ticketing details', validators=[Required()])
    wufoo = TextField('Approved Wufoo Hash Code')
    cost = TextAreaField('Cost')
    refunds = TextAreaField('Cancellations and refunds')

    other = HeadingField(label="Who should folks contact with questions?")
    questions = CKEditorTextAreaField('Questions', validators=[Required()])

    categories = HeadingField(label="Categories")

    general = SelectMultipleField('General Categories', choices=general_choices, validators=[Required()])
    offices = SelectMultipleField('Offices', choices=offices_choices, validators=[Required()])
    academics_dates = SelectMultipleField('Academics Dates', choices=academics_dates_choices, validators=[Required()])
    cas_departments = SelectMultipleField('CAS Academic Department', choices=cas_departments_choices, validators=[Required()])
    internal = SelectMultipleField('Internal Only', choices=internal_choices, validators=[Required()])


