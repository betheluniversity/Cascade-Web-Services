from program_search_base import ProgramSearchBaseTestCase


class IndexTestCase(ProgramSearchBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("index")

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
