
//Timepicker plugin
(function($) {

    "use strict";

    String.prototype.addZero = function() {
        return ('0' + this.valueOf()).slice(-2)
    };

    function getTime() {
        var time = new Date(),
            hh = time.getHours(),
            mm = time.getMinutes(),
            ss = time.getSeconds();

        return hh.toString().addZero() + ':' + mm.toString().addZero();
    }

    var methods = {
        init: function(options) {

            var data = this.data('timepicker', {});

            // Устанавливаем дефолтное время и обновление
            if(options && options.update) {
                data.update = true;
                methods.startUpdate.apply(this);
            }

            // Очищаем поле при фокусе
            this.focus(function() {
                $(this).val('')
            });

            // Накладываем ограничения на ввод значений в поле
            this.keypress(function(event) {
                var $this = $(this),
                    val = $this.val(),
                    key = event.key || String.fromCharCode(event.charCode ? event.charCode : event.keyCode ? event.keyCode : 0),
                    numEntered = key.search(/^\d/) >= 0;

                if((!numEntered && key.toLowerCase().search(/^backspace|^arrow|^f\d|^tab/) < 0) || (numEntered && val.length >= 5)) {
                    return false;
                }

                if(numEntered && val.length == 2) {
                    val += ':';
                } else if(!numEntered && val.length == 4) {
                    val = val.slice(0, 3)
                }

                $this.val(val)
            });

            // Пост-проверка значения
            this.keyup(function(event) {
                var $this = $(this),
                    val = $this.val().split(':'),
                    hh = parseInt(val[0]),
                    mm = parseInt(val[1]);

                if(!isNaN(hh)) {
                    val[0] = hh <= 23 ? val[0] : '23';
                }
                if(!isNaN(mm)) {
                    val[1] = mm <= 59 ? val[1] : '59';
                }

                $this.val(val.join(':'));
            });

            return this;
        },

        stopUpdate: function() {
            var data = this.data('timepicker');
            data.update = false;
            clearInterval(data.updateInterval);

            return this;
        },

        startUpdate:(function() {

            // При первом запуске этой функции нужно добавить евенты на фокус,
            // но чтобы сохранить возможность добавлять эвенты к полю в будующем
            // установим флаг на повторное добавление обработчиков...
            var doNotAddEvents = false;

            return function() {
                var data = $(this).data('timepicker');
                data.update = true;

                // автообновление
                data.updateInterval = setInterval((function(data, context) {
                    return $.proxy(function() {
                        if (data.update) {
                            this.val(getTime())
                        }
                    }, context)
                })(data, this), 500);

                if(!doNotAddEvents) {
                    doNotAddEvents = true;

                    // Запрещаем обновление времени при фокусе
                    this.focus((function(data) {
                        return function(event) {
                            data.update = false;
                        }
                    })(data));

                    // Как только фокус уходит, через 30 секунд разрешаем обновление времени
                    this.focusout((function(data) {
                        return function() {
                            setTimeout(function() {
                                data.update = true;
                            }, 30000)
                        }
                    })(data));
                }

                return this;
            };
        })()
    };

    $.fn.timepicker = function(method) {
        if(methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call( arguments, 1 ));
        } else if(typeof method == 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            return this;
        }
    };

})(window.jQuery);

//Numinput plugin
(function($) {

    $.fn.positivenumber = function() {

        return this.each(function() {
            var $this = $(this);

            $this.keypress(function (event) {
                var $this = $(this),
                    val = $this.val(),
                    key = event.key || String.fromCharCode(event.charCode ? event.charCode : event.keyCode ? event.keyCode : 0),
                    numEntered = key.search(/^\d/) >= 0;

                if (key.toLowerCase().search(/^\d|^backspace|^arrow|^f\d|^tab/) < 0) {
                    return false;
                }


            });

            $this.keyup(function () {
                var val = parseInt($(this).val());
                if (val < 0) {
                    $(this).val(0);
                } else if(!isNaN(val)) {
                    $(this).val(val);
                }
            });
        });
    }

})(window.jQuery);