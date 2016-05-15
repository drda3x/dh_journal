/**
 * Created by ПК on 20.02.2016.
 */

function sendRequest(_data, subAction, callback) {

    var data = {};

    for(var i in _data) {
        data[i] = _data[i];
    }

    if(!data.hasOwnProperty('id')) {
        data['id'] = window.pageParams.group_id;
    }

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
        this.add_td = null;

        this.errorCallback = null; // Outer callback, called on errors

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
        //this.$element.click($.proxy(function(event) {
        //    var $target = $(event.target);
        //
        //    // Если кликнули в первый input - проставляем всем остальным его значение
        //    // иначе - смотрим, что у всех input'ов, за исключением первого, проставлены галочки. В этом сдучае
        //    // проставляем галочку у первого input'a...
        //    if($target.is(this.rowSelectorClass)) {
        //        if(parseInt($target.val()) < 0) {
        //            this.$element.find(this.rowSelectorClass).each(function() {
        //                $(this).prop('checked', $target.prop('checked'))
        //            });
        //        } else {
        //            var all_checked = true;
        //            this.$element.find(this.rowSelectorClass + ':gt(0)').each(function() {
        //                all_checked =  !$(this).prop('checked') ? false : all_checked;
        //            });
        //            this.$element.find(this.rowSelectorClass + ':eq(0)').prop('checked', all_checked);
        //        }
        //    }
        //}, this));
        
        this.__sort();

        // Подписки на еветны от других виджетов
        // data - StudentCard.$data
        $(window).on('add-student-submit', $.proxy(function(event, data) {
            if(data.edit) {
                for(var i in this.currentRow) {
                    this.currentRow[i] = data[i];
                }
            } else {
                this.createRow(data);
            }

        }, this));

        $(window).on('add-form-submit', $.proxy(function(event, data) {
            var _data = {},
                model = this.currentRow,
                td = model.jq('pass');
            for(var i in data) {
              _data[i] = data[i];
            }

            model.pass = '';
            td.addClass('loading2');
            _data.stid = model.id;
            _data.mkid = window.pageParams.group_id;

            sendRequest(_data, 'add_pass', function(err, data) {
                if(err) {
                    console.log(err);
                } else {
                    model.pass = $('<div>'+_data.gid_str+'<span>(<a class="del" href="#">удалить</a>)</span>' + '</div>');
                    td.parent().find('td:eq(6) input').prop('checked', true);
                    td.removeClass('loading2');
                }
            });

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
                    '<td class="cp"><input class="row-selector" type="checkbox" /></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td></td>' +
                    '<td class="center cp no-click"><input class="attendance" type="checkbox" /></td>' +
                    '<td class="center no-events no-click"><a data-class="add" class="add" href="#">Добавить</a></td>' +
                    '<td class="comment no-click" data-mem="[]"></td>' +
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
    };

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

            res.__defineGetter__(propertyName, (function(_elem, _inner, res, propertyName) {
                if(_inner && _inner.is('input')) {
                    return function() {
                        return _inner.val();
                    }
                } else {
                    return function() {
                        var m = _elem.data('mem');

                        if(m != undefined) {
                            if(m instanceof Array) {
                                var filtered = $.grep(m, function(elem) {
                                    return elem != undefined;
                                });
                                res[propertyName] = filtered;
                                return filtered;
                            }
                            
                        }

                        return _elem.text();
                    }
                }

            })(elem, inner, res, propertyName));

            res.__defineSetter__(propertyName, (function(_elem, _inner) {

                if(_inner && _inner.is('input')) {
                    return function(val) {
                        _inner.val(val)
                    }
                } else {
                    return function(val) {
                        if(val instanceof jQuery) {
                          _elem.html(val);
                        } else if(typeof val == 'object') {
                            _elem.data('mem', val);
                        } else {
                          _elem.text(val);
                        }
                    }                    
                }

            })(elem, inner, res.mem));

        }

        res.jq = (function(tds, names) {
            return function(name) {
                for(var i= 0, j= names.length; i<j; i++) {
                    if(names[i] == name) {
                        return $(tds[i]);
                    }
                }
                return null;
            }
        })(tds, this.names);

        return res;
    };

    /**
     * Получить дочерний элемент ячейки, если он есть.
     */
    Table.prototype.__getTdInner = function(param) {
        var result;

        if(typeof param == 'string') {
            var variants = {
                id: $('<input class="row-selector" type="checkbox" />'),
                pass: $('<a data-class="add" class="add" href="#">Добавить</a>'),
                comment: $('<a class="comment-add" href="#">Добавить</a>')
            };

            result = variants.hasOwnProperty(param) ? variants[param] : null
        } else {
            var child = param.children().first();
            result = child.size() > 0 ? child : null;
        }
        
        return result;
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
    };

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
            rows = this.$element.find('tr');

        var handlers = {
            attendance: function(event, model, target, table) {
                var $td = target.parent(),
                    loading = 'loading2',
                    requestData = {
                        gid: window.pageParams.group_id,
                        stid: model.id,
                        val: target.prop('checked')
                    };

                $td.addClass(loading);

                sendRequest(requestData, 'attendance', function(err, data) {
                    if(err) {
                        console.log(err);
                    } else {
                        $td.removeClass(loading);
                    }
                });
            },
            add: function(event, model, target, table) {
                target.modalpopover({
                    content: $('.form').html(),
                    html: true,
                    trigger: 'manual',
                    placement: 'bottom'
                }).modalpopover('show');

            },
            del: function(event, model, target, table) {
                var $td = model.jq('pass'),
                    loading = 'loading2',
                    buffer;

                buffer = model.jq('pass').clone();
                model.pass = '';
                $td.addClass(loading);

                sendRequest({
                        stid: model.id,
                        gid: window.pageParams.group_id
                    },
                    'delete_pass',
                    function(err, data) {
                        $td.removeClass(loading);
                        if(err) {
                            if(self.hasOwnProperty('errorCallback')) {
                                try{
                                    buffer.find('span').remove();
                                    model.pass = buffer.html();
                                    self.errorCallback(err);
                                } catch(e) {

                                }
                            }
                        } else {
                            $td.html('<a data-class="add" class="add" href="#">Добавить</a>');
                        }
                    }
                )
            },
            'row-selector': function(event, model, target, table) {
                // Если кликнули в первый input - проставляем всем остальным его значение
                // иначе - смотрим, что у всех input'ов, за исключением первого, проставлены галочки. В этом сдучае
                // проставляем галочку у первого input'a...
                if(parseInt(target.val()) < 0) {
                    table.$element.find('.row-selector').each(function() {
                        $(this).prop('checked', target.prop('checked'))
                    });
                } else {
                    var all_checked = true;
                    table.$element.find('.row-selector:gt(0)').each(function() {
                        all_checked =  !$(this).prop('checked') ? false : all_checked;
                    });
                    table.$element.find('.row-selector:eq(0)').prop('checked', all_checked);
                }
            }
        };

        var delegate_to = ['attendance', 'row-selector'];

        rows.off('click')
        .click(function(event) {
            var $this = $(this),
                $target = $(event.target),
                handler = $target.attr('class');

            // Если кликнули в 1ю ячейку 1й строки...
            if(($this.index() == 0 && !($target.is('.row-selector') || $target.has('input').length > 0))) {
                return;
            }

            self.currentRow = $this.data('model');

            if(handlers.hasOwnProperty(handler)) {
              handlers[handler](event, self.currentRow, $target, self)
            } else {

                // Если кликнули по ячейке содержащей элемент из массива delegate_to
                var new_target;
                for(var i= delegate_to.length-1; i>=0; i--) {
                    new_target = $target.find('.'+delegate_to[i]);
                    if(new_target.size() > 0) {
                        new_target.trigger('click');
                        //handlers[delegate_to[i]](event, self.currentRow, new_target, self);
                        return false;
                    }
                }

                event.stopPropagation();
                if(!$target.is('td.no-click') && !$target.is('button')) {
                    $(document).trigger('table-row-click', [event, self.currentRow]);
                }
            }
        });
    };

    Table.prototype.__getNameIndex = function(name) {
        for(var i= this.names.length - 1; i>=0; i--) {
            if(this.names[i] == name) {
                return i;
            }
        }

        return NaN;
    };

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
            var args = arguments;
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

    function ModalVidget(params) {
        var inputsSelector = '.data';
        this.$element = $(params.selector);
        this.config = {};


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

        // Добавляем реакцию на внешние эвенты
        if(params.hasOwnProperty('handleEvents')) {
            $.map(params.handleEvents, $.proxy(function(event) {
                var e = event[0],
                    h = event[1];

                this.$element.on(e, $.proxy(h, this));
            }, this))
        }

        var alert1 = this.$element.find('.alert1'),
            alert2 = this.$element.find('.alert2');

        // Событие отправки формы
        this.$element.find('input[type=submit]').click($.proxy(function() {

            // Валидация
            if(!this.validate()) {
                return;
            }

            alert1.css('display', 'inline-block');

            this.$data.gid = window.pageParams.group_id;

            sendRequest(this.$data, this.$element.data('action'), $.proxy(function(err, data) {
                if(err) {
                    console.log(err);
                } else {
                    data.edit = this.$element.hasClass('edit');

                    if(params.hasOwnProperty('triggerEvents')) {
                        $.map(params.triggerEvents, function(event) {
                            $(window).trigger(event, data)
                        });
                    }

                    alert1.hide();
                    alert2.css('display', 'inline-block');

                    setTimeout(function() {
                        alert2.fadeOut(500);
                    }, 3000);

                    if(!data.edit) {
                        this.clear();
                    }
                }
            }, this))
        }, this));

        this.$element.on('hidden', function() {
            alert1.hide();
            alert2.hide()
        })
    }

    ModalVidget.prototype.clear = function() {
        for(var i in this.$data) {
            this.$data[i] = '';
        }
    };

    ModalVidget.prototype.validate = function() {
        return true;
    };

    W.ModalVidget = ModalVidget;

})(window);
