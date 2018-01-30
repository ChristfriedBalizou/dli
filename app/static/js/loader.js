"use strict";

var loader = (function($) {
    "use strict";

    var template = "<div class=\"loader\"></div>";

    return {

        start: function(options) {
            
            var $loader = $(template);

            options.element.hide()
            options.container.prepend($loader);

            return function() {
                $loader.remove();
                options.element.show();
            }
        }
    };

})(jQuery);
