
if(!window.vidgetsLogic) window.vidgetsLogic = {};

window.vidgetsLogic.Popover = (function($) {

    function Popover() {
        this.html = $('#pass_menu').html();
        this.objSelector = '.popover';
        this.activeClass = 'popover-opened';
    }

    Popover.prototype.init = function($target) {
        $target.popover({content: this.html, html: true, trigger: 'manual', animation: false});
    };

    Popover.prototype.setSelected = function() {
        var value = this.$target.attr('val');
        this.$object.find('input[value='+value+']').prop('checked', 'checked');
    };

    Popover.prototype.hide = function(timeout) {
        if(this.$object) {
            this.$object.hide(timeout || 0);
            setTimeout(this.$object.remove, timeout || 0);
        }
    };

    Popover.prototype.show = function($target) {

        var self = this;

        if(!$target.hasClass(self.activeClass)) {

            self.$target = $target;
            self.$container = $target.parent();

            self.$target.popover('show');
            self.$object = self.$container.find(self.objSelector);

            self.setSelected();

            self.$object.find('input').click(function() {
                self.$target.attr('val', $(this).val());
            });

            $('body').find('.'+self.activeClass).each(function() {
                $(this).removeClass(self.activeClass);
            });

            self.$target.addClass(self.activeClass);
        } else {
            self.$target.removeClass(this.activeClass);
        }
    };

    return Popover

})(window.jQuery);