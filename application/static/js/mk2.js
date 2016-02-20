/**
 * Created by ПК on 20.02.2016.
 */

function sendRequest(data, callback) {
    callback(data);
}

// Логика таблички
(function(W) {
    'use strict';

    /**
     * Класс-виджет для работы с таблицей.
     * Содержит всю логику поведения таблицы и предоставления ее данных всем остальным.
     * @param selector
     * @constructor
     */
    function Table(selector) {
        this.$element = $(selector);
        this.rowSelectorClass = '.row-selector';
        this.$rows = []; // TODO Сделать элементами массива объекты, атрибуты которого будут автоматом менять данные в строке
                         // TODO как сделано в модальном диалоге
        this.names = this.$element.find('tr:eq(0)').children().map(function(i, element) {
            return $(element).data('name')
        });

        // init functions calling
        this.__updateRowsCache();

        // Events adding
        // Добавляем функционал для выбора всех строк таблицы
        this.$element.click($.proxy(function(event) {
            var $target = $(event.target);

            // Если кликнули в первый input - проставляем всем остальным его значение
            // иначе - смотрим, что у всех input'ов, за исключением первого, проставлены галочки. В этом сдучае
            // проставляем галочку у первого input'a...
            if($target.is(this.rowSelectorClass)) {
                if(parseInt($target.val()) < 0) {
                    this.$element.find(this.rowSelectorClass).each(function() {
                        $(this).prop('checked', $target.prop('checked'))
                    });
                } else {
                    var all_checked = true;
                    this.$element.find(this.rowSelectorClass + ':gt(0)').each(function() {
                        all_checked =  !$(this).prop('checked') ? false : all_checked;
                    });
                    this.$element.find(this.rowSelectorClass + ':eq(0)').prop('checked', all_checked);
                }
            }
        }, this));

        // Подписки на еветны от других виджетов
        // data - StudentCard.$data
        $(window).on('add-student-submit', $.proxy(function(event, data) {
            this.addRow(data);
        }, this))
    }

    /**
     * Добавляем строчку в табличку
     * @param data
     * @returns {Table}
     */
    Table.prototype.addRow = function(data) {
        var curName,
            tr = $('<tr></tr>');

        for(var i= 0, j= this.names.length; i<j; i++) {
            curName = this.names[i];
            var td = $('<td></td>'),
                val = '';

            if(data.hasOwnProperty(curName)) {
                val = data[curName];
            }

            // Вставляем input в нужных местах
            var inp = (function(n) {
                switch(n) {
                    case 'id': return $('<input class="row-selector" type="checkbox" value="'+val+'" />');
                    case 'pass': return $('<a data-class="add" class="add" href="#">Добавить</a>');
                    default: return null;
                }
            })(curName)

            td.append(inp ? inp : val);
            tr.append(td);
        }

        this.$element.append(tr);
        this.__updateRowsCache();
        this.__sort();
        return this;
    };

    Table.prototype.__cacheRowData = function(row) {
        var cache = {},
            tds = row.children();
        
        for(var i= 0, j= this.names.length; i<j; i++) {
            var $td = $(tds[i]),
                $tdInner = $td.children().first();
            cache[this.names[i]] = $tdInner.size() > 0 ? $tdInner.val() : $td.text()
        }

        row.data('cache', cache);

        return this;
    }

    /**
     * Обновить кеш строк
     * @private
     */
    Table.prototype.__updateRowsCache = function() {
        var self = this;
        self.$rows = self.$element.find('tr').each(function() {
            self.__cacheRowData($(this));
        });

        return self;
    };

    /**
     * Сортировка строк по алфавиту
     * @private
     */
    Table.prototype.__sort = function() {
        var sorted_rows,
            famIndex = this.__getNameIndex('last_name');

        sorted_rows = this.$rows.slice(1).sort(function(l, r) {
            var l_name = $(l).data('cache').last_name,
                r_name = $(r).data('cache').last_name;
            return l_name.toLowerCase() < r_name.toLowerCase() ? -1 : 1;
        })

        for(var i= 0, j= sorted_rows.length; i<j; i++) {
            //todo Сюда надо вставить определение порядкового номаера
        }
    };

    Table.prototype.__getNameIndex = function(name) {
        for(var i= this.names.length - 1; i>=0; i--) {
            if(this.names[i] == name) {
                return i;
            }
        }

        return NaN;
    }

    /**
     * Получить список выбранных пользователем строк таблицы
     */
    Table.prototype.getSelectedRows = function() {
        return $.grep(this.$rows, $.proxy(function(elem, i) {
            return i > 0 && $(elem).find(this.rowSelectorClass).prop('checked');
        }, this))
    };

    W.Table = Table;

})(window);

// Логика модального окна
(function(W) {

    function StudentCard(selector) {
        var inputsSelector = 'input.data';
        this.$element = $(selector);

        // Удобный способ доступа к полям формы
        this.$data = (function(context) {
            var res = {};

            context.$element.find(inputsSelector).each(function() {
                var $this = $(this),
                    propertyName = $this.attr('name');

                res.__defineGetter__(propertyName, (function(elem) {
                    return function() {
                        return elem.val();
                    }
                })($this));

                res.__defineSetter__(propertyName, (function(elem) {
                    return function(val) {
                        elem.val(val);
                    }
                })($this));
            });

            return res;
        })(this);

        // Событие отправки формы
        this.$element.find('input[type=submit]').click($.proxy(function() {
            sendRequest(this.$data, function(data) {
                $(window).trigger('add-student-submit', data);
            })
        }, this));
    }

    StudentCard.prototype.clear = function() {
        for(var i in this.$data) {
            this.$data[i] = '';
        }
    }
    
    W.StudentCard = StudentCard;

})(window);