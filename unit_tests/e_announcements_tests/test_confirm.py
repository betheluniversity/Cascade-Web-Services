from e_announcements_base import EAnnouncementsBaseTestCase


class ConfirmTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /e-announcement/confirm" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(ConfirmTestCase, self).send_get("/e-announcement/confirm")
        self.assertIn(b'Once your E-Announcement has been approved, it will appear on your Tinker',
                      response.data, msg=failure_message)
