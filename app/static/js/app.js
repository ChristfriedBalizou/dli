"use strict";

function getDatabase() {
    // return selected database each
    // time its called
    return ($("#databases").val() || 
            $("[for=databases]").find("li[data-selected]").text());
}


function setDatabase(name) {
    // set database if it exist in list and
    // not already selected
    if(name != getDatabase() 
        && $("[data-val="+ name +"]").length > 0) {
        $('#databases').val(name);
        $(".getmdl-select [data-val]").removeAttr("data-selected")
                                      .filter("[data-val="+ name +"]")
                                      .attr("data-selected", "true");
    }
}

// https://stackoverflow.com/a/901144
// get GET params from url
function getParam(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


$(function(){

    var $database = $("#databases");// Database list

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

    // reload page on database change
    $database.change(function(){
        var hash = location.hash
                           .replace(/^#/, '')
                           .split("/");
        var page = router.getCurrentPage(hash);
        var args = router.getArguments(hash);
        location.hash = page + "/" + args.join("/") + "&database=" + getDatabase();
    });

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
