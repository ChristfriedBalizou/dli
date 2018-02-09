"use strict";

var page = (function(page){

    var $form = $("#search-form");
    var $input = $form.find("#text-search");

    // TEMPLATES
    var tmplValue = $("#tmpl-value").html();

    Mustache.tags = [ '<%', '%>' ];
    Mustache.escape = function(value) { return value; };
    Mustache.parse(tmplValue);


    page.home = {

        init: function() {
            $form.on('submit', function(e){
                e.preventDefault();
                location.hash = "search/" + $input.val().split(" ").join("/");
            });
        },

        render: function() {
        }
           
    };

    return page;

})(page || {});
