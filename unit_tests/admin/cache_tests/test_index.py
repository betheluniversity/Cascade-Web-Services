from cache_base import ClearCacheBaseTestCase


class IndexTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(IndexTestCase, self).send_get("/admin/cache-clear")
        assert b'<div class="large-6 columns">' in response.data

        # assert b'<div class="large-6 columns">\
        #             <label>Path\
        #                 <input type="text" value=\'/\' id="cpath"/>\
        #             </label>\
        #             <a id="submit" class="button">Submit</a>\
        #         <div id="output"></div>\
        #     </div>\
        # \
        #     <script>\
        #         function submitpath() {\
        #             var urlpath = $("#cpath").val();\
        #             var input_data = {\'url\': urlpath};\
        #             var cacheurl = "{{ url_for(\'CacheBlueprint.CacheClear:submit\') }}";\
        #             $.post(cacheurl, input_data, function (data) {\
        #                 $("#output").text(data);\
        #             });\
        #             $("#output").text(urlpath);\
        #         }\
        # \
        #         $("#submit").bind("click", submitpath);\
        # \
        #         // Ensure the path contains a \'/\' in the front and no spaces\
        #         $(\'#cpath\').keyup(function() {\
        #             var input = $(this);\
        #             input.val(input.val().replace(/ /g,''));\
        #             var value = input.val();\
        #             if (value[0] != \'/\' && value.length > 0) {\
        #               input.val("/" + value);\
        #               value = input.val();\
        #             }\
        #         });\
        # </script>' in response.data
