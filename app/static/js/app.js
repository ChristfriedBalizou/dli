"use strict";

$(function(){

    // ENDPOINTS
    var endpoint = {
        "home": page.home.render,
        "search": page.search.render,
        "prerelation": page.prerelation.render,
        "relation": page.relation.render,
        "login": page.login.render,
        "forgot-password": page.forgotPassword.render,
        "reset-password": page.resetPassword.render,
        "table": page.table.render,
        "column": page.column.render,
        "logout": function() {
            loginSession.logout();
            location.hash = "";
        }
    }; 

    // INITIALIZE PAGES
    page.login.init();
    page.forgotPassword.init();
    page.resetPassword.init();
    page.home.init();
    page.search.init();
    page.prerelation.init();
    page.relation.init();
    page.table.init();
    page.column.init();

    // Start router
    router.init(endpoint)
          .listen();

    // upgrade component
    componentHandler.upgradeDom();

    // Start page
    var hash = location.hash
                       .replace(/^#/, '');
    if(!hash) {
        hash = "home";
        location.hash = hash;
        return;
    }

    router.render(hash.split("/"));

}());
