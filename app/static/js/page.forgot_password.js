var page = (function(page) {
    "use strict";


    // Form
    var $form         = $("#forgot-password-form");

    // Header
    var $header       = $("header");

    // BOX
    var $container    = $("#forgot-password-form-container");
    var $bntContainer = $("#forgot-password-btns-container");
    var $btn          = $("#forgot-password-btn");


    page.forgotPassword = {

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

        var email = $form.find("[name=email]").val();
        var redirect = "login";

        server.forgotPassword(email)
            .done(function(data){
                
                if(data.status === false){
                    snackbar.show(data.response.message);
                    return;
                }
                
                snackbar.show("Reset link was sent to " + email);
                location.hash = redirect;
            })
            .always(loader.start({container: $container, 
                                  element: $form.add($bntContainer)}));
    }

})(page || {});
