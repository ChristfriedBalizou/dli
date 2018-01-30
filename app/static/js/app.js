"use strict";

$(function(){

    // ENDPOINTS
    var endpoint = {
        "home": page.home.render,
        "relation": page.relation.render,
        "login": page.login.render,
        "table": page.table.render,
        "column": page.column.render,
        "logout": function() {
            loginSession.logout();
            location.hash = "";
        }
    }; 

    // INITIALIZE PAGES
    page.login.init();
    page.home.init();
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
