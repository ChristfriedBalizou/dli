var snackbar = (function() {
    'use strict';
    
    var snackbarContainer = document.querySelector('#snackbar');
  
    return {
        show: function(message, time) {
            snackbarContainer.MaterialSnackbar.showSnackbar({
                message: message,
                timeout: time || 2000,
            });
        }
    };

}());
