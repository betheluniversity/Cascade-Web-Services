from faculty_bio_base import FacultyBioBaseTestCase


class InWorkflowTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /faculty-bio/in-workflow" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(InWorkflowTestCase, self).send_get("/faculty-bio/in-workflow")
        self.assertIn(b'<p>You recently made edits to your bio and are currently pending approval. Please wait until the changes have been approved before you make additional edits. Go back to your',
                      response.data, msg=failure_message)
