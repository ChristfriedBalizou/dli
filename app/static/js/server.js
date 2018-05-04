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
            return $.ajax(buildUrl(getDatabase(), "tables"))
        },

        getStatistics: function(tableList) {
            var link = buildUrl(getDatabase(), "statistics");
            if(tableList && tableList.length > 0){
                link += "/" + tableList.join(",")
            }
            return $.ajax(link);
        },

        getDiagram: function(tables, options) {
            return $.ajax({
                "url": buildUrl(getDatabase(), "tables", tables.join()) + "/",
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(options)
            });
        },

        updateRelation: function(a, b, field) {
            return $.ajax({
                "url": buildUrl(getDatabase(), "relation", a, b) + "/",
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
            return $.get(buildUrl(getDatabase(), "columns", name));
        },

        getTablesByColumn: function(name) {
            return $.get(buildUrl(getDatabase(), "tables", "column", name));
        },

        getTableDescription: function(name) {
            return $.get(buildUrl(getDatabase(), "table", name));
        },

        getMetadataTable: function(category, name, metaType) {
            return $.get(buildUrl(getDatabase(), "metadata", category, name, metaType));
        },

        setMetadataTable: function(category, name, metaType, data) {
            return $.ajax({
                "url": buildUrl(getDatabase(), "metadata", category, name, metaType),
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(data)
            });
        },

        search: function(query) {
            return $.ajax({
                "url": buildUrl(getDatabase(), "search/"),
                "method": "POST",
                "data": JSON.stringify({query: query}), 
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
            });
        },
        
        getFam: function() {
            return $.get(buildUrl(getDatabase(), "fam"));
        },

        forgotPassword: function(email) {
            return $.get(buildUrl("forgot_password", email));
        },

        getUserByToken: function(token) {
            return $.get(buildUrl("user", token));
        },

        resetPassword: function(email, auth) {
            return $.ajax({
                "url": buildUrl("reset_password", email) + "/",
                "method": "POST",
                "contentType": "application/json; charset=utf-8",
                "dataType": "json",
                "data": JSON.stringify(auth)
            });
        }
    
    };

})(jQuery);


