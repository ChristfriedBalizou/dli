"use strict";

var page = (function(page){

    var $form = $("#search-form");
    var $input = $form.find("#text-search");
    var $container = $("#home-page-container");
    var $box = $(".fam-box");
    var $element = $(".fams-grid");

    // TEMPLATES
    var tmplValue = $("#tmpl-fams").html();

    Mustache.tags = [ '<%', '%>' ];
    Mustache.escape = function(value) { return value; };
    Mustache.parse(tmplValue);


    page.home = {

        init: function() {
            $form.on('submit', function(e){
                e.preventDefault();
                location.hash = "search/" + $input.val().split(" ").join("/") + "&database=" + getDatabase();
            });
        },

        render: function() {
            $element.empty();

            server.getFam().done(function(data){
                if( data.status === false) {
                    snackbar.show(data.response.message);
                    return;
                }

                var $row = data.response.data.map(render);

                $element.html($row);
                
            }).always(loader.start({container: $container, element: $box}));
        }
           
    };

    return page;


    function render(obj) {
        obj["dbargs"] = "&database=" + getDatabase(); 
        return Mustache.render(tmplValue, obj);
    }

})(page || {});
