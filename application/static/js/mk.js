(function(w, $) {

    'use-strict';

    var currentCell;

    /**
     * Отправка запроса на сервер
     */
	function sendRequest(data) {
        setTimeout(function() {
            data.setGroupName();
            data.unsetLoading();
        }, 1000);
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

	w.onload = function() {
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
            }
        };

        $('table').click(function(event, type) {
            var $target = $(event.target),
                handlerName = $target.data('class');
            if(handlers.hasOwnProperty(handlerName)) {
                handlers[handlerName]($target);
            }
        });

        $(document).on('submit', handlers.submit);
	}

})(window, window.jQuery);