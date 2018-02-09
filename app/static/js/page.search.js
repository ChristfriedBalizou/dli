"use strict";

var page = (function(page){

    var $resultContainer = $("#search-page-container > .results");
    var $container = $resultContainer.find('.container');
    var $results = $resultContainer.find("#results");
    var $list = $results.find("ul");
    var $stat = $results.find(".result-statistic");
    var $search = $("#text-search");


    // TEMPLATES
    var tmplValue = $("#tmpl-value").html();

    Mustache.tags = [ '<%', '%>' ];
    Mustache.escape = function(value) { return value; };
    Mustache.parse(tmplValue);

    page.search = {

        init: function() {
            $list.empty();
        },

        render: function() {

            var args = Array.prototype.slice.call(arguments);
            var query = args.join(" ");

            $list.empty();
            $search.val(query)
                   .closest(".mdl-textfield")
                   .addClass("is-dirty is-upgraded");

            server.search(query)
                .done(function(data){
                    if( data.status === false) {
                        snackbar.show(data.response.message);
                        return;
                    }

                    var counter = 0;

                    counter += data.response.data.columns.length;
                    counter += data.response.data.relations.length;
                    counter += data.response.data.tables.length;

                    $stat.text("About " + counter +
                        " results found in (" + data.elapsed_time + ").");

                    var $relations = [];
                    var $tables = [];
                    var $columns = [];

                    renderer(
                        data.response.data.relations,
                        $relations,
                        "relation",
                        query,
                        buildRender
                    );

                    renderer(
                        data.response.data.tables,
                        $tables,
                        "table",
                        query,
                        buildRender
                    );

                    renderer(
                        data.response.data.columns,
                        $columns,
                        "column",
                        query,
                        buildRender
                    );

                    $list.append($tables);
                    $list.append($relations);
                    $list.append($columns);

                })
                .always(loader.start({container: $container, element: $results}));

        }
    };

    return page;


    function renderer(data, $list, tag, query, callback) {
        data.forEach(function(obj){
            var html = callback(obj, query, tag);
            if(html.length !== 0) {
                $list.push(html);
            }
        });
    }

    function buildRender(obj, query, tag) {

        switch(typeof(obj)) {
            case "string":
                obj = {value: obj};
                break;
            default:
                obj = {
                    value: buildValue(obj.table || obj.link),
                    description: buildDesc(obj.description, query),
                    user: obj.user.lastName + " " + obj.user.firstName,
                    time: obj.record_date
                };
                break;
        }

        obj["tag"] = tag;
        obj["url"] = location.origin;

        return Mustache.render(tmplValue, obj); 
    }

    function buildValue(value) {
        if (typeof(value) === "string") {
            return value;
        }
        return (value || []).join("/");
    }

    function buildDesc(str, query) {
        var reg = new RegExp(query, 'gi');
        var maxChar = 200;

        if (str.length > maxChar) {
            str = (str.substring(0, maxChar) + "...");
        }

        return str.replace(reg, function(o){
            return "<b>"+ o +"</b>";
        });
    }

})(page || {});
