var page = (function(page) {
    "use strict";


    // Form
    var $form         = $("#reset-password-form");

    // Header
    var $header       = $("header");

    // BOX
    var $container    = $("#reset-password-form-container");
    var $bntContainer = $("#reset-password-btns-container");
    var $btn          = $("#reset-password-btn");

    var email;


    page.resetPassword = {

        init: function() { 

            $form.on('submit', handleSubmit);
            $btn.click(function(){
                $form.trigger("submit");
            });
        },

        render: function(token) {
            $header.hide();
            componentHandler.upgradeElements($form[0]);
            $form[0].reset();

            if(!loginSession.isLogged() && !token) {
                location.hash = "home";
                return;
            }

            if(loginSession.isLogged()) {
                email = loginSession.user().email;
            } else {
                server.getUserByToken(token)
                      .done(function(response){
                          if(response.status === false) {
                              snackbar.show("Token " + token + " expired or does not exist.", 5000);
                              location.hash = "login";
                              return;
                          }
                          email = response.data.email;
                      }).always(loader.start({container: $container, 
                                element: $form.add($bntContainer)}));
            }
        }
    };


    return page;

    
    function handleSubmit(e) {

        e.preventDefault();

        var newPassword = $form.find("[name=reset-password]").val();
        var confirmPassword = $form.find("[name=confirm-password]").val();
        var redirect = "home";

        if(newPassword !== confirmPassword) {
            snackbar.show("Given password are not the same.", 5000);
            return;
        }

        // secure password
        newPassword = CryptoJS.MD5(newPassword).toString();
        confirmPassword = CryptoJS.MD5(confirmPassword).toString();

        server.resetPassword(email, {"newPassword": newPassword})
            .done(function(data){
                
                if(data.status === false){
                    snackbar.show("Password was not reseted.", 5000);
                    return;
                }
               
                if(loginSession.isLogged()) {
                    redirect = "logout";
                }

                snackbar.show("Password reseted", 5000);
                location.hash = redirect;
            })
            .always(loader.start({container: $container, 
                                  element: $form.add($bntContainer)}));
    }

})(page || {});
