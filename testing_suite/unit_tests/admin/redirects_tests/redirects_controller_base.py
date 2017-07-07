from testing_suite.unit_tests import BaseUnitTestCase
from tinker import app, db
from tinker.admin.redirects import RedirectsController


class RedirectsControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(RedirectsControllerBaseTestCase, self).__init__(methodName)
        self.controller = RedirectsController(db)

    def setUp(self):
        self.old_redirects_path = app.config['REDIRECTS_FILE_PATH']
        app.config['REDIRECTS_FILE_PATH'] = './redirects.txt'

    def tearDown(self):
        app.config['REDIRECTS_FILE_PATH'] = self.old_redirects_path
