/**
 * Класс для работы Popover'a в меню присутствия учеников на занятиях
 */

if(!window.vidgetsLogic) window.vidgetsLogic = {};

window.vidgetsLogic.Popover = (function($) {

    /**
     * Класс определяющий поведение popover'a
     * @constructor
     */
    function Popover(group) {
        this.html = $('#pass_menu');
        this.objSelector = '.popover';
        this.activeClass = 'popover-opened';
        this.group = group;
        this.timer = undefined;
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
        this.stopIntervals();
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
            } else {
                self.$target.removeAttr('subval');
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

        function responseProcessor(err, data) {
            if(err) {
                console.log(err);
            } else {
                $contentHtml.empty();
                var json = JSON.parse(data);
                for(var i= 0, j= json.length; i<j; i++) {
                    var elem = $('<li class="popover-pass_menu-content" data-id="'+json[i].pass_id+'">'+json[i].st_fam+' '+json[i].st_name+' ('+json[i].lessons+')</li>');

                    elem.click(function() {
                        self.$target.attr('subval', $(this).data('id'));
                        $(this).siblings().removeClass('popover-pass_menu-content-active');
                        $(this).addClass('popover-pass_menu-content-active');
                    });

                    if(subval) {
                        elem.addClass('popover-pass_menu-content-active');
                        subval = null;
                    }

                    $contentHtml.append(elem);
                }
            }
        }

        var $html = $(this.objSelector + ':visible').find('#pass_menu_advanced'),
            $contentHtml = $('.popover-content').find('#pass_menu_advanced_content'),
            self = this,
            $fio = $html.find('#pass_menu_fio');

        $fio.off('keypress');

        if(val == '-1') {

            $html.show();
            var kp = false;

            var subval = self.$target.attr('subval');

            if(subval) {
                self.get_passes({pid: subval}, responseProcessor);
            }

            self.timer = setInterval(function() {
                if(kp) {
                    var val = $fio.val();
                    if(val.length >= 3) {
                        self.get_passes({str: val, group: self.group}, responseProcessor);
                    } else {
                        $contentHtml.empty();
                    }
                    kp = false;
                }
            },500);

            $fio.keypress(function() {
                kp = true;
            });

        } else {
            $html.hide();
            self.stopIntervals();
            $fio.off('keypress');
            $contentHtml.empty();
            $('.popover-content').find('#pass_menu_fio').val('');
            self.$target.removeAttr('subval');
        }
    };

    Popover.prototype.get_passes = function(params, callback) {
        $.ajax({
            method: 'GET',
            url: 'getavailiablepasses',
            data: params
        }).error(function(err) {
            callback(err, null)
        }).done(function(data) {
            callback(null, data)
        })
    };

    Popover.prototype.stopIntervals = function() {
        if(this.timer) clearInterval(this.timer)
    };

    return Popover

})(window.jQuery);