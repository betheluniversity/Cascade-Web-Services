# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Get the url_for() function working in the unit tests so that when the endpoint location changes, the tests won't
#       auto-fail for no good reason.
# 2. Make the unit tests much more robust; instead of just testing endpoints of a module, it can also check that each
#       respective DB or Cascade object gets updated appropriately so that there's no possibility of silent failures
# 3. Find some way to pass test object ids back and forth between unit tests so that the test_sequentially files can be
#       split into individual, granular unit tests.
# 4. Write a unit test factory class that can auto-generate unit test files given a set of parameters about the endpoint
#       it's going to be testing.
#
# Currently, the unit testing suite takes about 2 minutes to run.

import os
from inspect import stack
import tinker
import unittest
from tinker import get_url_from_path


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    def generate_url(self, method_name, **kwargs):
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        dir_path_to_current_frame = os.path.dirname(file_of_current_frame)
        name_of_last_folder = dir_path_to_current_frame.split("/")[-1]
        local_folder_name = name_of_last_folder.split("_tests")[0]
        flask_classy_name = ""
        words_in_folder_name = local_folder_name.split("_")
        for word in words_in_folder_name:
            flask_classy_name += word.capitalize()
        flask_classy_name += "View"
        endpoint_path = local_folder_name + "." + flask_classy_name + ":" + method_name
        return get_url_from_path(endpoint_path, **kwargs)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def generate_failure_message(self, type, request, response_data, expected_response, class_name):
        return '"%(0)s %(1)s" received "%(2)s" when it was expecting "%(3)s" in %(4)s.' % \
               {'0': type, '1': request, '2': response_data, '3': expected_response, '4':class_name}

    def tearDown(self):
        pass


if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)


# Missing unit test files:
# admin/redirects/new_api_submit
# admin/redirects/new_api_submit_asset_expiration
# admin/redirects/new_internal_redirect_submit
# e_announcements/edit_all
# events/confirm
# events/edit_all
# events/reset_tinker_edits
# faculty_bio/confirm
# faculty_bio/delete_confirm
# faculty_bio/activate
# faculty_bio/edit_all
# office_hours/rotate_hours
