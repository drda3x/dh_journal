/**
 * Created by ПК on 20.02.2016.
 */

function sendRequest(_data, subAction, callback) {

    var data = {};

    for(var i in _data) {
        data[i] = _data[i];
    }

    data['id'] = window.pageParams.group_id;
    data['sub_action'] = subAction;

    $.ajax({
        method: 'POST',
        data: data
    }).success(function(jsonString) {
        var responce = JSON.parse(jsonString);
        callback(null, responce);
    }).error(function(errString) {
        callback(errString, null)
    })
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
        this.currentRow = null;

        // fill data
        this.names = this.$element.find('tr:eq(0)').children().map(function(i, element) {
            return $(element).data('name')
        });

        this.$rows = this.$element.find('tr:gt(0)').each((function(context) {
            return function() {
                var $this = $(this),
                    m = context.createRowObject($this);
                $this.data('model', m);
            }
        })(this));

        // init functions calling

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
        
        this.__sort();

        // Подписки на еветны от других виджетов
        // data - StudentCard.$data
        $(window).on('add-student-submit', $.proxy(function(event, data) {
            this.createRow(data);
        }, this));

        $(window).on('add-form-submit', $.proxy(function(event, data) {
            sendRequest({
                    gid: data,
                    stid: this.currentRow.id
                },
                'add_pass',
                function(err, data) {
                    if(err) {
                        console.log(err);
                    } else {
                        console.log('success');
                        $(document).data('modalpopover').hide();
                    }
                }
            )
        }, this));
    }

    /**
     * Добавляем строчку в табличку
     * @param data
     * @returns {Table}
     */
    Table.prototype.createRow = function(data) {
        var curName,
            tr = $(
                '<tr>' +
                    '<td><input class="row-selector" type="checkbox" /></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td><input class="attendance" type="checkbox" /></td>' +
                    '<td><a data-class="add" class="add" href="#">Добавить</a></td>' +
                    '<td></td>' +
               '</tr>'
            );

        var model = this.createRowObject(tr);

        for(var i in model) {
            if(data.hasOwnProperty(i)) {
                model[i] = data[i]
            }
        }

        tr.data('model', model);
        this.$rows.push(model);
        this.$element.append(tr);
        this.__sort();

        return this;
    };

    Table.prototype.deleteRow = function(idArr) {
        function _in(e, _arr) {
            for(var i= arr.length-1; i>=0; i--) {
                if(arr[i] == e) {
                    return true;
                }
            }
            return false;
        }

        var arr = idArr instanceof Array ? idArr : [idArr];

        this.$element.find('tr:gt(0)').each(function() {
            var m = $(this).data('model');
            if(_in(m.id, arr)) {
                $(this).remove();
            }
        });

        this.__sort();
    }

    /**
     * Создать объект-обертку для удобной работы с DOM'ом строки... 
     */
    Table.prototype.createRowObject = function(row) {
        var res = {},
            tds = $(row).children(),
            elem, inner, propertyName;

        for(var i= 0, j= this.names.length; i<j; i++) {
            propertyName = this.names[i];
            elem = $(tds[i]);
            inner = this.__getTdInner(elem);

            res.__defineGetter__(propertyName, (function(_elem, _inner) {

                if(_inner && _inner.is('input')) {
                    return function() {
                        return _inner.val();
                    }
                } else {
                    return function() {
                        return _elem.text();
                    }
                }

            })(elem, inner));

            res.__defineSetter__(propertyName, (function(_elem, _inner) {

                if(_inner && _inner.is('input')) {
                    return function(val) {
                        _inner.val(val)
                    }
                } else {
                    return function(val) {
                        _elem.text(val);
                    }                    
                }

            })(elem, inner));

        }

        return res;
    }

    /**
     * Получить дочерний элемент ячейки, если он есть.
     */
    Table.prototype.__getTdInner = function(param) {
        var result;

        if(typeof param == 'string') {
            var variants = {
                id: $('<input class="row-selector" type="checkbox" />'),
                pass: $('<a data-class="add" class="add" href="#">Добавить</a>')
            }

            result = variants.hasOwnProperty(param) ? variants[param] : null
        } else {
            var child = param.children().first()
            result = child.size() > 0 ? child : null;
        }
        
        return result;
    }

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
            rows = this.$element.find('tr:gt(0)');

        sorted_rows = $.map(
            rows.clone(true).sort(function(a, b) {
                var left, right;

                left = $(a).data('model');
                right = $(b).data('model');

                return left.last_name.toLowerCase() < right.last_name.toLowerCase() ? -1 : 1;
            }),

            $.proxy(function(e, i) {
                var $e = $(e),
                    $e_model = this.createRowObject($e);

                $e_model.cnt = i + 1;
                $e.data('model', $e_model);

                return $e;
            }, this)

        );

        rows.remove();
        this.$element.append(sorted_rows);
        this.__refreshRowsEvents();
    };

    Table.prototype.__refreshRowsEvents = function() {
        var self = this,
            rows = this.$element.find('tr:gt(0)');

        rows.each(function() {
            var $this = $(this),
                model = $this.data('model');

            $this.find('.attendance').change(model, function(event) {
                var $td = $(this).parent(),
                    loading = 'loading2';
                $td.addClass(loading)

                sendRequest({
                    gid: window.pageParams.group_id,
                    stid: event.data.id,
                    val: $(this).prop('checked')
                }, 
                'attendance', 
                function(err, data) {
                    if(err) {
                        console.log(err);
                    } else {
                        $td.removeClass(loading);
                    }
                })
            });

            $this.find('.add').each(function() {
                $(this).modalpopover({
                    content: $('.form').html(),
                    html: true,
                    trigger: 'manual',
                    placement: 'bottom'
                })
            })
            .click(model, function() {
                self.currentRow = model;
                $(this).modalpopover('show');
            });

        });
    }

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
        var rows = $.grep(this.$element.find('tr:gt(0)'), $.proxy(function(elem, i) {
            return $(elem).find(this.rowSelectorClass).prop('checked');
        }, this)).map(function(elem) {
            return $(elem).data('model');
        });

        if(arguments.length == 0) {
            return rows
        } else {
            var args = arguments
            var oneElement = args.length == 1;
            return rows.map(function(elem) {
                if(oneElement) {
                    return elem[args[0]]
                } else {
                    var buff = {};
                    for(var i= args.length-1; i>=0; i--) {
                        buff[args[i]] = elem[args[i]]
                    }
                    return buff;
                }
            })
        }
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
            sendRequest(this.$data, 'add', function(err, data) {
                if(err) {
                    console.log(err);
                } else {
                    $(window).trigger('add-student-submit', data);
                }
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