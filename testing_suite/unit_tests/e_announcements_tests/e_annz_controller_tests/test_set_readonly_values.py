from datetime import datetime

from e_annz_controller_base import EAnnouncementsControllerBaseTestCase


class SetReadonlyValuesTestCase(EAnnouncementsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SetReadonlyValuesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_set_readonly_values(self):
        test_edit_data = {
            'first_date': datetime(2018, 8, 17),
            'second_date': datetime(2018, 8, 21)
        }
        self.controller.set_readonly_values(test_edit_data)

        self.assertTrue('first_readonly' in test_edit_data.keys())
        self.assertEqual(test_edit_data['first_readonly'], 'Friday August 17, 2018')

        self.assertTrue('second_readonly' in test_edit_data.keys())
        self.assertEqual(test_edit_data['second_readonly'], 'Tuesday August 21, 2018')

        test_edit_data = {
            'first_date': datetime(2017, 6, 17),
            'second_date': datetime(2017, 6, 21)
        }
        self.controller.set_readonly_values(test_edit_data)

        self.assertTrue('first_readonly' in test_edit_data.keys())
        self.assertTrue(test_edit_data['first_readonly'])

        self.assertTrue('second_readonly' in test_edit_data.keys())
        self.assertTrue(test_edit_data['second_readonly'])
