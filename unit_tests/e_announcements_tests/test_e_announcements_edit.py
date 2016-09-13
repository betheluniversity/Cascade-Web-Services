# from unit_tests import BaseTestCase
#
#
# class EditTestCase(BaseTestCase):
#     #######################
#     ### Utility methods ###
#     #######################
#
#     def __init__(self, methodName):
#         super(EditTestCase, self).__init__(methodName)
#         self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
#         self.request_type = "GET"
#         self.request = self.generate_url("edit")
#
#     #######################
#     ### Testing methods ###
#     #######################
#
#     def test_edit(self):
#         expected_response = b'<div class="container-fluid row">'
#         response = self.send_get(self.request)
#         failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
#         self.assertIn(expected_response, response.data, msg=failure_message)
