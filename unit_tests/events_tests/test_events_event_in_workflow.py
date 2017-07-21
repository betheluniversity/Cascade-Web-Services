from unit_tests import BaseTestCase


class EventInWorkflowTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EventInWorkflowTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("event_in_workflow")

    #######################
    ### Testing methods ###
    #######################

    def test_event_in_workflow(self):
        expected_response = repr('\x9a\xa1\xdd@b5\xad\xd1|\x83\x93"\xe0za\xc8')  # b'Edits pending approval'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)