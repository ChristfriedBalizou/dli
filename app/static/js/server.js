var server = (function($){

    "use strict";

    var url = "/"
       
    // configure basic authentication
    $.ajaxSetup({
        beforeSend: function(xhr) {
            if(!loginSession.isLogged()){
                return;
            }

            xhr.setRequestHeader('Authorization', loginSession.token());
        }
    });

    function buildUrl() {
        var args = Array.prototype.slice.call(arguments);
        return url + args.join('/');
    }

    return {

        getTableList: function() {
            return $.ajax(buildUrl("tables"))
        },

        getStatistics: function(tableList) {
            var link = buildUrl("statistics");
            if(tableList && tableList.length > 0){
                link += "/" + tableList.join(",")
            }
            return $.ajax(link);
        },

        getDiagram: function(tables, showCols, decoration) {
            var link = buildUrl("tables", tables.join(), showCols, decoration);
            return $.ajax(link);
        },

        updateRelation: function(a, b, field) {
            return $.ajax({
                "url": buildUrl("relation", a, b) + "/",
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(field)
            });
        },

        imageExist: function(name) {
            return $.ajax(buildUrl("image", "check", name));
        },

        login: function(auth){

            return $.ajax({
                "url": buildUrl("login") + "/",
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(auth)
            });
        },

        getTableColumns: function(name) {
            return $.get(buildUrl("columns", name));
        },

        getTableDescription: function(name) {
            return $.get(buildUrl("table", name));
        },

        getMetadataTable: function(category, name, metaType) {
            return $.get(buildUrl("metadata", category, name, metaType));
        },

        setMetadataTable: function(category, name, metaType, data) {
            return $.ajax({
                "url": buildUrl("metadata", category, name, metaType),
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(data)
            });
        },

        search: function(query) {
            return $.ajax({
                "url": buildUrl("search/"),
                "method": "POST",
                "data": JSON.stringify({query: query}), 
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
            });
        },
        
        getFam: function() {
            return $.get(buildUrl("fam"));
        }
    
    };

})(jQuery);


