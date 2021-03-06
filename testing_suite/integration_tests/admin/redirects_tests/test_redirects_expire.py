from redirects_base import RedirectsBaseTestCase


class ExpireTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ExpireTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("expire")

    #######################
    ### Testing methods ###
    #######################

    def test_expire(self):
        expected_response = repr('g\x8e^\x01\x9ayRm\x0f\xcc\xa5\xe2\x9fn_x')  # b'done'
        response = self.send_get(self.request, basic_auth=True)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
