var snackbar = (function() {
    'use strict';
    
    var snackbarContainer = document.querySelector('#snackbar');
  
    return {
        show: function(message) {
            snackbarContainer.MaterialSnackbar.showSnackbar({
                message: message,
                timeout: 2000,
            });
        }
    };

}());
