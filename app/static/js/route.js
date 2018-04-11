"use strict";

var router = (function(session) {

    var path = {};

    var delisted = ["login", "forgot-password"];

    return {
        init: function (endpoint) {
            path = $.extend(path, endpoint);
            return router;
        },

        addEndpoint: function (route) {
            path = $.extend(path, route);
            return router;
        },

        getEndpoints: function () {
            return path;
        },

        hasEndpoint: function (name) {
            return path[name] != null;
        },

        getCurrentPage: function(hash) {
            return hash.splice(0, 1).pop();
        },

        getArguments: function(hash) {
            // for ["TABLE_1", "TABLE_2&database=DB"]
            hash = hash.join() // "TABLE_1,TABLE_2&database=DB"
                       .split("&") // ["TABLE_1,TABLE_2", "&database=DB"]
                       .splice(0, 1) // ["TABLE_1,TABLE_2"]
                       .pop() //"TABLE_1,TABLE_2"
                       .split(","); // ["TABLE_1", "TABLE_2"]
            return hash;
        },
        
        render: function(hash) {
            var page = hash.splice(0, 1)
                           .pop();
            var database = getParam("database", hash);

            if (!session.isLogged() && (delisted.concat(["reset-password"]))
                                        .indexOf(page) === -1) {
                location.hash = "login";
                return;
            }

            if (session.isLogged() && delisted.indexOf(page) !== -1) {
                location.hash = "";
                return;
            }

            if (!page) {
                location.hash = "home";
                return;
            }

            if(database) {
                setDatabase(database);
            }

            $("[data-page]")
                .hide()
                .filter("[data-page="+ page +"]")
                .show();

            path[page].apply(null, router.getArguments(hash));
        },

        listen: function() {
            $(window).on("hashchange", function() {

                var hash = location.hash
                                   .replace(/^#/, '')
                                   .split("/");
                router.render(hash);

            });
            return router;
        }
    };

})(loginSession); 
