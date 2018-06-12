// General File for Tinker's JavaScript

$(document).ready(function () {
    $("#search-filters").click(function () {
        if($("#search-filters").hasClass("show")) {
            $("#additional-search-params").slideUp();
            $("#search-filters").removeClass("show");
            $("#search-filters").addClass("no-show");
            $(".input-field").val(""); // Clears values if hidden so not included in search
        }else{
            $("#additional-search-params").slideDown();
            $("#search-filters").removeClass("no-show");
            $("#search-filters").addClass("show");
        }
    });
});