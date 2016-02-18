(function(w, $) {

    'use-strict';

    var currentCell;

    /**
     * Отправка запроса на сервер
     */
	function sendRequest(data, callback) {
        $.ajax('mk',{
            data: data
        }).success(function(json) {
            var data;
            try {
                data = JSON.parse(json);
            } catch(e) {
                data = null;
            }

            callback(null, data);
        }).error(function(error) {
            callback(error);
        })
    }

    function Cell(type, elem) {
        try {
            this.type = type;
            this.id = elem.find('select').val();
            this.name = elem.find('option[value='+this.id+']').text();
        } catch (e) {}

        this.td = elem.parent();
    }

    Cell.prototype.setLoading = function() {
        this.td.addClass('loading');
    };

    Cell.prototype.unsetLoading = function() {
        this.td.removeClass('loading');
    };

    Cell.prototype.setGroupName = function() {
        var $deleter = $('<span data-class="deleter" class="deleter">X</span>');
        $deleter.data('td', this.td);
        this.td.text(this.name);
        this.td.append($deleter)
    };

    Cell.prototype.setDefault = function() {
        this.td.html('<a data-class="add" class="add" href="#">Добавить</a>');
    };


    /**
     * Добавить строку в таблицу
     * @param data
     */
    function addRow(data) {
        var $table = $('table'),
            rowsLen = $table.find('tr').toArray().length,
            row = $('<tr></tr>')
            .append('<td><input data-class="marker" type="checkbox" value="'+ data.id +'" /></td>')
            .append('<td>'+rowsLen+'</td>')
            .append('<td>'+data.last_name+'</td>')
            .append('<td>'+data.first_name+'</td>')
            .append('<td>'+data.phone.formated+'</td>')
            .append('<td>'+data.e_mail+'</td>')
            .append('<td><input type="checkbox" value="'+ data.id +'"></td>')
            .append('<td><a data-class="add" class="add" href="#">Добавить</a></td>')
            .append('<td></td>');

        row.appendTo($table);
    }

    /**
     * Удаление строк из таблицы
     * @param rows
     */
    function removeRow(rows) {
        rows.remove();
        $('table').find('tr:gt(0)').each(function(i) {
            $(this).find('td:eq(1)').text(i+1);
        });
    }

	w.onload = function() {

        var shortCard = w.createShortcard().init();

        shortCard.addElement('Изменить', function(event) {
            var row = event.data.scData('row'),
                vals = $.grep(row.find('td'), function(e, i) {
                    return i != 1 && i <= 5;
                }).map(function(elem) {
                    var $elem = $(elem),
                        $inp = $elem.find('input');
                    return $inp.length == 0 ? $elem.text() : $inp.val();
                }),
                inputs = $('#editStudent input[type!=submit]');

            for(var i = inputs.length-1; i>=0; i--) {
                $(inputs[i]).val(vals[i]);
            }

            $('#editStudentBtn').trigger('click');
        });

        shortCard.addElement('Удалить', function() {
            console.log('delete')
        });

        shortCard.addElement('Коментарий', function() {
            console.log('comment');
        });

        var handlers = {
            add: function(elem) {
                if(!elem.data('modalpopover')) {
                    elem.modalpopover({
                        content: $('.form').html(),
                        html: true,
                        trigger: 'manual',
                        placement: 'bottom'
                    });
                }
                elem.modalpopover('show');
            },

            deleter: function(elem) {
                cell = new Cell('del', elem);
                cell.setDefault();
            },

            submit: function(elem) {
                var $disturber = $(document).data('modalpopover'),
                $form = $disturber.$tip,
                cell = new Cell('add', $form);

                if(cell.id > 0) {
                    cell.setLoading();
                    $disturber.hide();
                    sendRequest(cell);
                } else {
                    alert('No group selecte');
                }

                return false;
            },

            marker: function(elem) {
                var inputs = elem.parentsUntil('table').children('tr').map(function() {
                    var $this = $(this);
                    return $this.children().first().find('input');
                });

                if(elem.val() < 0) {
                    inputs.each(function() {
                       $(this).prop('checked', elem.prop('checked'));
                    });
                } else {
                    inputs[0].prop('checked', inputs.slice(1).all(function() {
                        return $(this).prop('checked');
                    }));
                }
            },

            showShortCard: function(x, y, elem) {
                shortCard.data('row', elem);
                shortCard.show(x, y);
            }
        };

        $('table').click(function(event, type) {
            var $target = $(event.target),
                handlerName = $target.data('class'),
                row = $target.parentsUntil('tbody').last();

            if(handlers.hasOwnProperty(handlerName)) {
                handlers[handlerName]($target);
            } else if(!$target.is('input') && row.data('index') > 0) {
                var x = event.pageX,
                    y = event.pageY;
                handlers.showShortCard(x, y, row);
                event.stopPropagation();
            }
        });

        $('#editStudent .btn-primary').click(function() {
            var $this = $(this),
                data = {
                    id: window.pageParams.group_id,
                    requestType: 'addStudent'
                };
            $('#editStudent input[type!=button]').each(function() {
                var $this = $(this);
                data[$this.attr('name')] = $this.val();
            });

            sendRequest(data, function(err, data) {
                if(err) {
                    alert('ERROR');
                }
                addRow(data);
                $('#editStudent').modal('hide');
            });
        });

        $('#deleteStudentBtn').click(function() {
            var $table, inputs, ids, rows, data;

            $table = $('table');
            inputs = $table.find('input[data-class=marker]:gt(0):checked');
            rows = $.grep($table.find('tr:gt(0)').toArray(), function(elem) {
                return $(elem).find('input[data-class=marker]').is(':checked')
            });
            ids = inputs.map(function() {
                return parseInt($(this).val());
            }).toArray();
            data = {
                gid: window.pageParams.group_id,
                requestType: 'removeStudent',
                ids: JSON.stringify(ids)
            };

            sendRequest(data, function(err, data) {
                if(err) {
                    alert('Ошибка');
                    return
                }
               removeRow($(rows));
            });
        });

        $('.attendance').change(function() {
            var $this = $(this),
                val = $this.prop('checked');
            $this.parent().addClass('loading2');

            sendRequest({
               gid: window.pageParams.group_id,
               requestType: 'setAttendance',
               stid: $this.val(),
               val: val
            }, function(err) {
               if(err) {
                   console.log(err);
                   $this.prop('checked', val);
               } else {
                   $this.parent().removeClass('loading2');

               }
            })
        });

        $(document).on('submit', handlers.submit);
        $(document).on('click', function() {
            shortCard.hide();
            shortCard.data('row', null)
        });
	}

})(window, window.jQuery);