from unit_tests import BaseTestCase


class IndexTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /e-announcement"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'Below is the list of E-Announcements you have access to edit. These are sorted by'
        response = self.send_get("/e-announcement")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)