"use strict";

var cache = (function () {
    var instance;
 
    function createInstance() {
       var store = {};

        return {
            add: function(key, value) {
				store[key] = value;
            },
			
			get: function(key) {
				return store[key];
			},

            remove: function(key) {
                delete store[key];
			},

            hasData: function(key) {
                return store.hasOwnProperty(key);
            }
        };
    }
 
    return {
        getInstance: function () {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})(); 

