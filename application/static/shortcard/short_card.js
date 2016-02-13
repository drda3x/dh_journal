(function(w, $) {

    function ShortCard() {
        this.container = $('<div id="shortCardMenu"></div>');
        this.list = $('<ul></ul>').appendTo(this.container);
        this.clickHandlers = {};
        return this;
    }

    ShortCard.prototype.data = function(attr, val) {
        return val ? this.container.data(attr, val) : this.container.data(val);
    };

    ShortCard.prototype.init = function() {
        $('body').append(this.container);
        return this;
    };

    ShortCard.prototype.addElement = function(name, clickHandler) {
        $('<li>'+name+'</li>')
            .appendTo(this.list)
            .click({scData: $.proxy(this.container.data, this.container)}, clickHandler);
    };

    ShortCard.prototype.show = function(x, y) {
        this.container.css('position', 'absolute');
        this.container.css('top', y);
        this.container.css(
            'left',
            (x + this.container.width() + 30 >  $(window).width()) ? x - this.container.width() - 25 : x
        );
        this.container.show();
    };

    ShortCard.prototype.hide = function() {
        this.container.hide();
    };

    w.createShortcard = function() {
        return new ShortCard();
    }

})(window, window.jQuery);