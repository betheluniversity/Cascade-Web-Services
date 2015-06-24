# coding: utf-8
# python

# modules
from flask.ext.wtf import Form
from wtforms import ValidationError
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import SelectMultipleField
from wtforms import SelectField
from wtforms import HiddenField
from flask_wtf.file import FileField
from wtforms import Field
from wtforms import validators
from time import time

from flask_hmacauth import hmac

# local
from tinker import app
from tinker.tools import *
# from tinker import cache
from tinker.web_services import get_client, read


def get_md(metadata_path):
    # todo move this to a read()
    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': metadata_path,
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = get_client()
    md = client.service.read(auth, identifier)
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition


# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
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


#####################
# #Faculty Bio Forms
#####################

# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
class DummyField(TextAreaField):
    pass


def get_faculty_bio_choices():

    data = get_md("/Robust")

    md = {}
    for item in data:
        try:
            md[item.name] = item.possibleValues.possibleValue
        except AttributeError:
            # this will fail for text fields w/o values. We don't want those anwyay
            continue

    school = []
    for item in md['school']:
        if item.value != "Bethel University" and item.value != "Select":
            school.append((item.value, item.value))

    department = []
    for item in md['department']:
        department.append((item.value, item.value))

    adult_undergrad_program = []
    for item in md['adult-undergrad-program']:
        adult_undergrad_program.append((item.value, item.value))

    graduate_program = []
    for item in md['graduate-program']:
        graduate_program.append((item.value, item.value))

    seminary_program = []
    for item in md['seminary-program']:
        seminary_program.append((item.value, item.value))

    return {'school': school, 'department': department, 'adult_undergrad_program': adult_undergrad_program, 'graduate_program': graduate_program, 'seminary_program': seminary_program}


def validate_username(form, field):
    username = field.data
    host = "http://wsapi.bethel.edu"
    path = "/username/" + username + "/roles?TIMESTAMP="+str(int(time()))+"&ACCOUNT_ID=tinker"
    sig=hmac.new(app.config['WSAPI_SECRET'], path, hashlib.sha1 ).hexdigest()
    req = requests.get(host+path, headers={'X-Auth-Signature': sig})

    content = req.content
    if content == str({}):
        raise ValidationError("Invalid username.")


class FacultyBioForm(Form):
    roles = get_roles()

    ## if a cas faculty member or seminary faculty member, hide the image field.
    if 'FACULTY-CAS' in roles or 'FACULTY-BSSP' in roles or 'FACULTY-BSSD' in roles:
        image = HiddenField("Image")
        image_url = HiddenField("Image URL")
    else:
        image = FileField("Image")
        image_url = HiddenField("Image URL")

    first = TextField('Faculty first name', validators=[validators.DataRequired()])
    last = TextField('Faculty last name', validators=[validators.DataRequired()])
    author = TextField("Faculty member's username", validators=[validators.DataRequired(), validate_username], description="This username will become the author of the page.")

    job_titles = TextField('')

    email = TextField('Email', validators=[validators.DataRequired()])
    started_at_bethel = TextField('Started at Bethel in', validators=[validators.DataRequired()], description="Enter a year")

    heading_choices = (('', "-select-"), ('Areas of expertise', 'Areas of expertise'), ('Research interests', 'Research interests'), ('Teaching speciality', 'Teaching speciality'))

    heading = SelectField('Choose a heading that best fits your discipline', choices=heading_choices, validators=[validators.DataRequired()])
    areas = TextAreaField('Areas of expertise', description="A max of 350 characters is permitted. Current count: ", validators=[validators.length(max=350,message="Character limit exceeded. A max of 350 characters is allowed.")])
    research_interests = TextAreaField('Research interests', description="A max of 350 characters is permitted. Current count: ", validators=[validators.length(max=350,message="Character limit exceeded. A max of 350 characters is allowed.")])
    teaching_specialty = TextAreaField('Teaching speciality', description="A max of 350 characters is permitted. Current count: ", validators=[validators.length(max=350,message="Character limit exceeded. A max of 350 characters is allowed.")])

    degree = DummyField('')

    biography = CKEditorTextAreaField('Biography')
    courses = CKEditorTextAreaField('Courses Taught')
    awards = CKEditorTextAreaField('Awards')
    publications = CKEditorTextAreaField('Publications')
    presentations = CKEditorTextAreaField('Presentations')
    certificates = CKEditorTextAreaField('Certificates and licenses')
    organizations = CKEditorTextAreaField('Professional Organizations, Committees, and Boards')
    hobbies = CKEditorTextAreaField('Hobbies and interests')

    quote = TextField('Quote')

    website = TextField('Professional website or blog')


    choices = get_faculty_bio_choices()
    categories = HeadingField(label="Categories", id="categories_heading")
    school_choices = choices['school']
    department_choices = choices['department']
    caps_choices = choices['adult_undergrad_program']
    gs_choices = choices['graduate_program']
    sem_choices = choices['seminary_program']

    school = SelectMultipleField('School', choices=school_choices, default=['Select'], validators=[validators.DataRequired()])
    department = SelectMultipleField('Undergraduate Departments', default=['None'], choices=department_choices, validators=[validators.DataRequired()])
    adult_undergrad_program = SelectMultipleField('Adult Undergraduate Programs', default=['None'], choices=caps_choices, validators=[validators.DataRequired()])
    graduate_program = SelectMultipleField('Graduate Programs', default=['None'], choices=gs_choices, validators=[validators.DataRequired()])
    seminary_program = SelectMultipleField('Seminary Programs', default=['None'], choices=sem_choices, validators=[validators.DataRequired()])


    ## Manually override validate, in order to check the 3 headers below
    def validate(self):
        if not Form.validate(self):
            return False
        result = True

        if self.heading.data == "Areas of expertise":
            if self.areas.data == "":
                self.areas.errors.append('Area of expertise is required.')
                result = False
        elif self.heading.data == "Research interests":
            if self.research_interests.data == "":
                self.research_interests.append('Research interests is required.')
                result = False
        elif self.heading.data == "Teaching speciality":
            if self.teaching_specialty.data == "":
                self.teaching_specialty.errors.append('Teaching speciality is required.')
                result = False

        return result
