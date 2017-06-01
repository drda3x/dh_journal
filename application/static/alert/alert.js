(function(w, $) {

    function Alert() {
        this.html = $('<div id="window-main-alert" class=""></div>');
        this.html.appendTo('body');
    }

    Alert.prototype.__show = function() {
        this.html.fadeIn(500);
        setTimeout($.proxy(function() {
            this.html.fadeOut(500);
            this.html.remove();
        }, this), 3000)
    };

    Alert.prototype.success = function(msg) {
        this.html.empty();
        this.html.removeAttr('class');
        this.html.attr('class', 'alert alert-success');
        this.html.html(msg);
        this.__show();
    };

    Alert.prototype.error = function(msg) {
        this.html.empty();
        this.html.removeAttr('class');
        this.html.attr('class', 'alert alert-error');
        this.html.html(msg);
        this.__show();
    };

    w.createWindowAlert = function() {
        return new Alert()
    }

})(window, jQuery);
