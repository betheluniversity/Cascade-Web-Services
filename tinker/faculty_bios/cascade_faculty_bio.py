#python
import urllib2
import re
import base64
import httplib
import requests

from xml.etree import ElementTree as ET
from xml.dom.minidom import parseString
#flask

#local
from tinker.web_services import *
from tinker.tools import *
from tinker.cascade_tools import *
from tinker import app


def get_expertise(add_data):
    areas = add_data['areas']
    interests = add_data['research_interests']
    teaching = add_data['teaching_specialty']

    if areas != "" :
        select = "Areas of expertise"
    elif interests != "":
        select = "Research Interests"
    elif teaching != "":
        select = "Teaching Speciality"
    else:
        select = "Select"

    data_list = [
        structured_data_node("heading", select),
        structured_data_node("areas", areas),
        structured_data_node("research-interests", interests),
        structured_data_node("teaching-specialty", teaching),
    ]

    node = {
        'type': "group",
        'identifier': "expertise",
        'structuredDataNodes': {
            'structuredDataNode': data_list,
        },
    },

    return node


def get_job_titles(add_data):
    job_titles = []

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            job_title = add_data['job-title' + i]
        except KeyError:
            ##This will break once we run out of dates
            break

        job_titles.append( structured_data_node("job-title", job_title ))

    return job_titles


def get_add_a_degree(add_data):
    degrees=[]

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            school = add_data['school' + i]
            degree = add_data['degree-earned' + i]
            year = add_data['year' + i]
        except KeyError:
            ##This will break once we run out of degrees
            break

        data_list = [
            structured_data_node("school", school),
            structured_data_node("degree-earned", degree),
            structured_data_node("year", year),
        ]

        node = {
            'type': "group",
            'identifier': "add-degree",
            'structuredDataNodes': {
                'structuredDataNode': data_list,
            },
        },


        degrees.append(node)

    finalNode = {
            'type': "group",
            'identifier': "education",
            'structuredDataNodes': {
                'structuredDataNode': degrees,
            },
        },

    return finalNode


def get_add_to_bio(add_data):

    options = []

    biography = add_data['biography']
    awards = add_data['awards']
    publications = add_data['publications']
    certificates = add_data['certificates']
    hobbies = add_data['hobbies']
    quote = add_data['quote']
    website = add_data['website']

    if biography != "" :
        options.append("::CONTENT-XML-CHECKBOX::Biography")
    if awards != "":
        options.append("::CONTENT-XML-CHECKBOX::Awards")
    if publications != "":
        options.append("::CONTENT-XML-CHECKBOX::Publications")
    if certificates != "":
        options.append("::CONTENT-XML-CHECKBOX::Certificates and Licenses")
    if hobbies != "":
        options.append("::CONTENT-XML-CHECKBOX::Hobbies and Interests")
    if quote != "":
        options.append("::CONTENT-XML-CHECKBOX::Quote")
    if website != "":
        options.append("::CONTENT-XML-CHECKBOX::Website")

    options = ''.join(options)

    data_list = [
        structured_data_node("options", options),
        structured_data_node("biography", escape_wysiwyg_content(biography) ),
        structured_data_node("awards", escape_wysiwyg_content(awards) ),
        structured_data_node("publications", escape_wysiwyg_content(publications) ),
        structured_data_node("certificates", escape_wysiwyg_content(certificates) ),
        structured_data_node("hobbies", escape_wysiwyg_content(hobbies) ),
        structured_data_node("quote", quote),
        structured_data_node("website", website),

    ]

    node = {
        'type': "group",
        'identifier': "add-to-bio",
        'structuredDataNodes': {
            'structuredDataNode': data_list,
        },
    },

    return node


def get_faculty_bio_structure(add_data, username, faculty_bio_id=None, workflow=None):
    """
     Could this be cleaned up at all?
    """

    ## Create Image asset
    roles = get_roles()
    if "FACULTY-CAS" in roles:
        if add_data['image_name'] != "":
            image_structure = get_image_structure("/academics/faculty-images", add_data['image_name'])

            r = requests.get('https://www.bethel.edu/academics/faculty-images/' + add_data['image_name'])

            if r.status_code == 404:
                create_image(image_structure)
            else:
                image_structure['file']['path'] = "academics/faculty-images/" + add_data['image_name']
                edit_response = edit(image_structure)
                app.logger.warn(time.strftime("%c") + ": Image edit by " + username + " " + str(edit_response))
        image = structured_file_data_node('image', "/academics/faculty-images/" + add_data['image_name'])
    else:
        image = None



    ## Create a list of all the data nodes
    structured_data = [
        image,
        structured_data_node("first", add_data['first']),
        structured_data_node("last", add_data['last']),
        structured_data_node("email", add_data['email']),
        structured_data_node("started-at-bethel", add_data['started_at_bethel']),
        get_job_titles(add_data),

    ]

    structured_data.extend( get_expertise(add_data) )
    structured_data.extend( get_add_a_degree(add_data) )
    structured_data.extend( get_add_to_bio(add_data) )

    ## Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    #create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('school', add_data['school']),
            dynamic_field('department', add_data['department']),
            dynamic_field('adult-undergrad-program', add_data['adult_undergrad_program']),
            dynamic_field('graduate-program', add_data['graduate_program']),
            dynamic_field('seminary-program', add_data['seminary_program'])
        ],
    }

    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': "/academics/faculty",
            'metadataSetPath': "/Robust",
            'contentTypePath': "Academics/Faculty Bio",
            'configurationSetPath': "Faculty Bio",
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['first'] + " " + add_data['last'],
                'summary': 'summary',
                'author': add_data['author'],
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if faculty_bio_id:
        asset['page']['id'] = faculty_bio_id

    return asset


## A test to see if we can create images in cascade.
def get_image_structure(image_dest, image_name, faculty_bio_id=None, workflow=None):

    file = open(app.config['UPLOAD_FOLDER'] + image_name, 'r')
    stream = file.read()
    encoded_stream = base64.b64encode(stream)

    asset = {
        'file': {
            'name': image_name,
            'parentFolderPath': image_dest,
            'metadataSetPath': "Images",
            'siteId': app.config['SITE_ID'],
            'siteName': 'Public',
            'data': encoded_stream,
        },
        'workflowConfiguration': workflow
    }

    return asset


def create_image(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create image submission by " + username + " " + str(response))

    ## Publish
    publish(response.createdAssetId, "file")

    return response


## A lengthy hardcoded list that maps the metadata values to the Groups on Cascade.
def get_web_author_group(departmentMetadata):

    if "Anthropology, Sociology, & Reconciliation" == departmentMetadata:
        return "Anthropology Sociology"
    if "Art & Design" == departmentMetadata:
        return "Art"
    if "Biblical & Theological Studies" == departmentMetadata:
        return "Biblical Theological"
    if "Biological Sciences" == departmentMetadata:
        return "Biology"
    if "Business & Economics" == departmentMetadata:
        return "Business Economics"
    if "Chemistry" == departmentMetadata:
        return "Chemistry"
    if "Communication Studies" == departmentMetadata:
        return "Communication"
    if "Education" == departmentMetadata:
        return "Education"
    if "English" == departmentMetadata:
        return "English"
    if "Environmental Studies" == departmentMetadata:
        return "Environmental Studies"
    if "General Education" == departmentMetadata:
        return "General Education"
    if "History" == departmentMetadata:
        return "History"
    if "Honors" == departmentMetadata:
        return "Honors"
    if "Human Kinetics & Applied Health Science" == departmentMetadata:
        return "Human Kinetics"
    if "Math & Computer Science" == departmentMetadata:
        return "Math CS"
    if "Modern World Languages" == departmentMetadata:
        return "World Languages"
    if "Music" == departmentMetadata:
        return "Music"
    if "Nursing" == departmentMetadata:
        return "Anthropology Sociology"
    if "Philosophy" == departmentMetadata:
        return "Philosophy"
    if "Physics & Engineering" == departmentMetadata:
        return "Physics"
    if "Political Science" == departmentMetadata:
        return "Political Science"
    if "Psychology" == departmentMetadata:
        return "Psychology"
    if "Social Work" == departmentMetadata:
        return "Social Work"
    if "Theatre Arts" == departmentMetadata:
        return "Theatre"

    return ""


def create_faculty_bio(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create faculty bio submission by " + username + " " + str(response))
    ##publish the xml file so the new event shows up
    publish_faculty_bio_xml()

    return response


def get_faculty_bios_for_user(username):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/faculty-bios.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/faculty-bios.xml').getroot()
    matches = traverse_faculty_folder(form_xml, username)

    return matches


def traverse_faculty_folder(traverse_xml, username):
    ## Traverse an XML folder, adding system-pages to a dict of matches
    user = read(username, "user")
    try:
        allowedGroups = user.asset.user.groups
        allowedGroups = allowedGroups.split(";")
    except AttributeError:
        allowedGroups = []

    ## Todo: This function can be removed. The 'traverse_xml' variable above is already doing that.

    matches = []
    for child in traverse_xml:
        if child.tag == 'system-page':
            try:
                authors = child.find('author')
                if authors is not None:

                    dict_of_authors = authors.text.split( ", ")

                    if username in dict_of_authors:
                        page_values = {
                            'author': child.find('author').text,
                            'id': child.attrib['id'] or "",
                            'title': child.find('title').text or None,
                            'created-on': child.find('created-on').text or None,
                            'path': 'https://www.bethel.edu' + child.find('path').text or "",
                        }
                        ## This is a match, add it to array
                        matches.append(page_values)
                        continue
            finally:
                for md in child.findall("dynamic-metadata"):
                    if md.find('name').text == 'department' and md.find('value') is not None:
                        for allowedGroup in allowedGroups:

                            if allowedGroup == get_web_author_group(md.find('value').text):

                                page_values = {
                                    'author': child.find('author') or None,
                                    'id': child.attrib['id'] or "",
                                    'title': child.find('title').text or None,
                                    'created-on': child.find('created-on').text or None,
                                    'path': 'https://www.bethel.edu' + child.find('path').text or "",
                                }
                                a=1
                                matches.append(page_values)
                                break
    return matches


def get_add_data(lists, form):

    ##A dict to populate with all the interesting data.
    add_data = {}

    for key in form.keys():
        if key in lists:
            add_data[key] = form.getlist(key)
        else:
            add_data[key] = form[key]

    ##Make it lastname firstname
    system_name = add_data['last'] + " " + add_data['first']

    ##Create the system-name from title, all lowercase
    system_name = system_name.lower().replace(' ', '-')

    ##Now remove any non a-z, A-Z, 0-9
    system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

    add_data['system_name'] = system_name

    return add_data


def get_bio_publish_workflow(title="", username=""):

    name = "New Bio Submission"
    if title:
        name += ": " + title
    workflow = {
        "workflowName": name,
        "workflowDefinitionId": "f1638f598c58651313b6fe6b5ed835c5",
        "workflowComments": "New Faculty Bio submission"
    }
    return workflow


def check_publish_sets(school):
    for item in school:
        if item == "College of Arts & Sciences":
            publish("f580ac758c58651313b6fe6bced65fea", "publishset")
        if item == "Graduate Schol":
            publish("2ecbad1a8c5865132b2dadea8cdcb2be", "publishset")
        if item == "College of Adult & Professional Studies":
            publish("2ed0beef8c5865132b2dadea1ccf543e", "publishset")
        if item == "Bethel Seminary":
            publish("2ed19c8d8c5865132b2dadea60403657", "publishset")




