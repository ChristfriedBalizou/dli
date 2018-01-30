var loginSession = (function(){
    "use strict";

    var instance;
    
    if (!instance) {
        instance = createIntance();
    }

    return instance;

    function createIntance() {

        var $username = $(".username");

        return {

            user: function() {
                if(!this.isLogged()) {
                    return null;
                }
                
                var key = sessionStorage.getItem('key');

                return {
                    username: sessionStorage.getItem(key + '_username'),
                    firstName: sessionStorage.getItem(key + '_firstName'),
                    lastName: sessionStorage.getItem(key + '_lastName'),
                    email: sessionStorage.getItem(key + '_email')
                };
            },
            
            login: function(u, password) {

                var key = btoa(u.username);

                sessionStorage.setItem('key', key);
                sessionStorage.setItem(key + '_username', u.username);
                sessionStorage.setItem(key + '_firstName', u.firstName);
                sessionStorage.setItem(key + '_lastName', u.lastName);
                sessionStorage.setItem(key + '_email', u.email);

                sessionStorage.setItem(key + '_token', "Basic " + btoa(u.username + ":" + password));

            },

            isLogged: function () {
               
                var key = sessionStorage.getItem('key');

                // check early registration key
                if(!key) {
                    return false;
                }

                // check sessionKey
                if(!sessionStorage.getItem(key + '_token')) {
                    return false;
                }
                
                $username.text(sessionStorage.getItem(key + '_lastName') + " " +
                               sessionStorage.getItem(key + '_firstName'));

                return true;
            },

            logout: function () {
                $username.empty();
                sessionStorage.clear();
            },

            token: function() {
                if (!this.isLogged()) {
                    return null;
                }

                var key = sessionStorage.getItem('key');
                return sessionStorage.getItem(key + '_token');
            }

        };

    }


})();
