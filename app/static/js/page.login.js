var page = (function(page) {
    "use strict";


    // Form
    var $form         = $("#auth-form");

    // Header
    var $header       = $("header");

    // BOX
    var $container    = $("#auth-form-container");
    var $bntContainer = $("#auth-btns-container");
    var $btn          = $("#auth-btn");


    page.login = {

        init: function() { 

            $form.on('submit', handleSubmit);
            $btn.click(function(){
                $form.trigger("submit");
            });
        },

        render: function() {
            $header.hide();
            componentHandler.upgradeElements($form[0]);
            $form[0].reset();
        }
    };


    return page;

    
    function handleSubmit(e) {

        e.preventDefault();

        var username = $form.find("[name=username]").val();
        var password = $form.find("[name=password]").val();

        var redirect = "home";

        // secure password
        password = CryptoJS.MD5(password).toString();

        server.login({"username": username, "password": password})
            .done(function(data){
                
                if(data.status === false){
                    return;
                }
                
                loginSession.login(data.response.data, password);
                $header.show();

                var attr = $form.attr('next');

                if (typeof attr !== typeof undefined && attr !== false) {
                    // Element has this attribute
                    redirect = $form.attr("next");
                }

                $form[0].reset();
                location.hash = redirect;
            })
            .always(loader.start({container: $container, 
                                  element: $form.add($bntContainer)}));
    }

})(page || {});
