# Global
import csv

# Packages
import requests
from xml.etree import ElementTree as ET
from paramiko import RSAKey, SFTPClient, Transport
from paramiko.hostkeys import HostKeyEntry

# Local
from tinker import app
from tinker.admin.program_search.models import ProgramTag
from tinker.tinker_controller import TinkerController


class ProgramSearchController(TinkerController):

    def create_new_csv_file(self):
        outfile = open(app.config['PROGRAM_SEARCH_CSV_LOCAL'], 'wb')
        outcsv = csv.writer(outfile)
        rows = []
        records = ProgramTag.query.all()
        rows.append(['key', 'tag', 'outcome', 'other', 'topic'])
        for record in records:
            rows.append([record.key, record.tag, record.outcome, record.other, record.topic])

        outcsv.writerows(iter(rows))
        outfile.close()

        # SFTP
        self.write_to_sftp(app.config['PROGRAM_SEARCH_CSV_LOCAL'], app.config['PROGRAM_SEARCH_CSV_SFTP'], False, True)

        return "<pre>%s</pre>" % str(rows)

    def get_programs_for_dropdown(self, return_dict_for_renaming=False):
        # gather a list of all program concentrations
        if return_dict_for_renaming:
            program_concentrations = {}
        else:
            program_concentrations = []

        response = self.tinker_requests(app.config['PROGRAMS_XML'])
        xml = ET.fromstring(response.content)
        program_blocks = xml.findall('.//system-block')

        for block in program_blocks:
            concentrations = block.findall('system-data-structure/concentration')
            for concentration in concentrations:
                # get name -- create the key used by the db
                concentration_code = concentration.find('concentration_code').text
                if concentration_code is None:
                    concentration_code = block.find('name').text

                program_name = self.get_program_name(block, concentration)

                if program_name is None:
                    continue

                # get school
                school_element = self.search_for_key_in_dynamic_md(block, 'school')
                if len(school_element) > 0:
                    school = school_element[0]
                else:
                    school = None

                if return_dict_for_renaming:
                    program_concentrations[concentration_code] = program_name
                else:
                    program_concentrations.append({
                        'name': program_name,
                        'value': concentration_code,
                        'school': school
                    })

        if return_dict_for_renaming is False:
            program_concentrations = sorted(program_concentrations, key=lambda k: k['name'])
        return program_concentrations

    def get_program_name(self, block, concentration):
        # get value
        concentration_name = concentration.find('.//concentration_name')
        block_display_name = block.find('display-name')
        block_title = block.find('title')

        if hasattr(concentration_name, 'text') and concentration_name.text:
            program_name = concentration_name.text
        elif hasattr(block_display_name, 'text') and block_display_name.text:
            program_name = block_display_name.text
        elif hasattr(block_title, 'text') and block_title.text:
            program_name = block_title.text
        else:
            return None

        # add in major/minor

        major_or_minor = self.search_for_key_in_dynamic_md(block, 'program-type')
        if major_or_minor:
            if 'minor' not in program_name.lower() and 'major' not in program_name.lower() and 'program' not in program_name.lower():
                program_name += ' ' + major_or_minor[0]

        return program_name

    def get_school_labels(self):
        school_labels = [
            'College of Arts & Sciences',
            'College of Adult & Professional Studies',
            'Graduate School',
            'Bethel Seminary'
        ]
        return school_labels
