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
            var data = JSON.parse(json);
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

    function addRow(data) {

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
            var data = {
                requestType: 'addStudent'
            };
            $('#editStudent input[type!=button]').each(function() {
                var $this = $(this);
                data[$this.attr('name')] = $this.val();
            });

            sendRequest(data, addRow);
        });

        $(document).on('submit', handlers.submit);
        $(document).on('click', function() {
            shortCard.hide();
            shortCard.data('row', null)
        });
	}

})(window, window.jQuery);