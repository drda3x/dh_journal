/**
 * Класс для работы Popover'a в меню присутствия учеников на занятиях
 */

if(!window.vidgetsLogic) window.vidgetsLogic = {};

window.vidgetsLogic.Popover = (function($) {

    /**
     * Класс определяющий поведение popover'a
     * @constructor
     */
    function Popover() {
        this.html = $('#pass_menu');
        this.objSelector = '.popover';
        this.activeClass = 'popover-opened';
    }

    /**
     * Инициализируем popover для объекта
     * @param $target
     */
    Popover.prototype.init = function($target) {
        $target.popover({content: this.html.html(), html: true, trigger: 'manual', animation: false});
    };

    /**
     * Получить сохраненное значение
     * @returns {*}
     */
    Popover.prototype.getExistedValue = function() {
        return this.$target.attr('val');
    };

    /**
     * Спрятать popover
     * @param timeout
     */
    Popover.prototype.hide = function(timeout) {
        if(this.$object) {
            this.$object.hide(timeout || 0);
            setTimeout(this.$object.remove, timeout || 0);
        }
    };

    /**
     * Показать popover
     * @param $target
     */
    Popover.prototype.show = function($target) {

        var self = this;

        // Если открываем popover для ячейки для которой он еще не открыт
        // иначе просто удаляем класс "popover-opened"(self.activeClass)
        // как следствие - popover просто закроется
        if(!$target.hasClass(self.activeClass)) {

            // init
            self.$target = $target;
            self.$container = $target.parent();
            self.$target.popover('show');
            self.$object = self.$container.find(self.objSelector);

            // Если нужно устанавливаем уже существующее значение
            var value = self.getExistedValue();
            if(value) {
                this.$object.find('input[value='+value+']').prop('checked', 'checked');
                self.toggleAdvanced(value);
            }

            // Вешаем евенты
            self.$object.find('input[type=radio]').click(function() {
                var $this = $(this),
                    newValue = $this.val();

                function stop(event) {
                    event.stopPropagation();
                }

                // Если кликнули по выделленному input'y - нужно снять с него фокус и обнулить контейнер данных и убрать выделение цветом
                if(newValue == self.getExistedValue()) {
                    $this.prop('checked', false);
                    self.$target.removeAttr('val');
                    self.$target.removeClass(self.$target.passClass);
                    self.$target.find('input').off('click', stop).remove();
                } else {
                    self.$target.attr('val', newValue);

                    if(self.$target.hasOwnProperty('passClass')) {
                        self.$target.removeClass(self.$target.passClass );
                    }

                    self.$target.passClass = $this.data('color');
                    self.$target.addClass(self.$target.passClass );
                    if (self.$target.find('input').length == 0) {
                        var $inp = $('<input type="checkbox" style="margin: 0; position: absolute;" checked>');
                        self.$target.append($inp);
                        $inp.click(stop);
                    }
                }

                // Возможно нужно открыть доп. окошко
                self.toggleAdvanced(self.getExistedValue());
            });

            // Класс с активным попапом может быть только один, так что сначала удалим все классы,
            // а потом поставим класс "popover-opened"(self.activeClass) в текущий $target
            $('body').find('.'+self.activeClass).each(function() {
                $(this).removeClass(self.activeClass);
            });

            self.$target.addClass(self.activeClass);
        } else {
            self.$target.removeClass(this.activeClass);
        }
    };

    /**
     * Показать или скрыть дополнительное окошко
     * @param val
     */
    Popover.prototype.toggleAdvanced = function(val) {

        var $html = $(this.objSelector + ':visible').find('#pass_menu_advanced');

        if(val == '-1') {
            var $fio = $html.find('#pass_menu_fio');
            $html.show();

            $fio.keypress();
        } else {
            $html.hide()
        }
    };

    return Popover

})(window.jQuery);