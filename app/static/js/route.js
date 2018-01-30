"use strict";

var router = (function(session) {

    var path = {};

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
        
        render: function(hash) {
            var page = hash.splice(0, 1)
                           .pop();

            if (!session.isLogged() && page !== "login") {
                location.hash = "login";
                return;
            }

            if (session.isLogged() && page === "login") {
                location.hash = "";
                return;
            }

            if (!page) {
                location.hash = "home";
                return;
            }

            $("[data-page]")
                .hide()
                .filter("[data-page="+ page +"]")
                .show();

            path[page].apply(null, hash);
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
