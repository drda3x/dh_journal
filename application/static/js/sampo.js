/**
 * Created by dispatcher on 21.11.2015.
 */

window.sampoLogic = (function () {

    var fadeOutParam = 250;

    function is_backspase(val) {
        return val.toLowerCase() == 'backspace'
    }

    function is_tab(val) {
        return val.toLowerCase() == 'tab'
    }

    function addZero(val) {
        return ('0' + val).slice(-2);
    }

    function showAddPassForm() {
        $('.to_fd').fadeOut(fadeOutParam, function () {
            $('#addSampoPass').fadeIn(fadeOutParam);
        });
    }

    function hideAddPassForm() {
        $('#addSampoPass').fadeOut(fadeOutParam, function () {
            $('.to_fd').fadeIn(fadeOutParam);
        });
    }

    function addClockBehavior(input_time) {

        input_time.keypress(function (event) {
            var key, val, go_back;
            key = event.key;
            go_back = is_backspase(key) || is_tab(key);

            if (!go_back && isNaN(parseInt(key))) {
                return false;
            }

            val = $(this).val() + (go_back ? '' : key);

            if (val.length > 5 && !go_back) {
                $(this).val('');
                //return false;
            } else if (val.length == 4 && go_back) {
                $(this).val(val.slice(0, -1));
            } else if (val.length == 3 && !go_back) {
                $(this).val($(this).val() + ':');
            }
        });

        input_time.keyup(function (event) {
            var arr, hours, minutes, val;
            val = $(this).val();
            arr = val.split(':');
            hours = (arr.length > 0) ? parseInt(arr[0]) : NaN;
            minutes = (arr.length > 1) ? parseInt(arr[1]) : NaN;

            if (hours > 9) {
                arr[0] = (hours <= 23) ? hours : 23;
            }

            if (minutes > 9) {
                arr[1] = (minutes <= 59) ? minutes : 59;
            }

            $(this).val(arr.join(':'));

        });
    }

    /**
     * Функция инициализирующая автообновление часов
     */
    function clockAutoUpdate(elem) {
        var timeInt, now;

        function updateTimes() {
            now = new Date();
            elem.val(addZero(now.getHours()) + ':' + addZero(now.getMinutes()));
        }

        function StartAutoUpd() {
            clearInterval(timeInt);
            timeInt = setInterval(updateTimes, 500);
        }

        function StopAutoUpd() {
            clearInterval(timeInt);
            setTimeout(StartAutoUpd, 30000)
        }

        $('.submitBtn').click(StartAutoUpd);
        $('input.time').focus(function () {
            $(this).val('');
            StopAutoUpd();
        });
        StartAutoUpd();
    }

    function getFormData(button) {

        var data = {};
        data.info = {};

        var $form = $('.money-action:visible');
        $form.find('input').each(function () {
            data.info[$(this).attr('name')] = $(this).val();
        });
        data.info.date = $('#date').val();
        return data;
    }

    function sendRequest(options, successCallBack, errorCallBack, context) {
        $.ajax('/sampo', {
            data: options
        })
            .success((function (context) {

                return function (data) {
                    if (context != undefined) {
                        successCallBack(data, context);
                    } else {
                        successCallBack(data);
                    }
                }

            })(context))
            .error(errorCallBack);
    }

    function errorProcess() {
    }

    function successProcess(json, data) {
        if (json != undefined) {
            var response = JSON.parse(json);

            if (response.hasOwnProperty('pid')) {
                var input = addToPassList(response.pid, data.info.name, data.info.surname);
                input.find('input').prop('checked', true);
            }

            if (response.hasOwnProperty('payments')) {
                refreshTable(response.payments)
            }

            addSampoPassEvents();
            addWriteOffBehavior();
        }
    }

    /**
     * Обновляшка для таблички журнала
     */
    function refreshTable(data) {
        var html_container = $('#payments tbody'),
            info = {};

        html_container.empty();

        for (var i = 0, j = data.length; i < j; i++) {
            info = data[i].info;

            var comment = (info.hasOwnProperty('comment')) ? '<div class="muted">' + info.comment + '</div>' : '';

            $('<tr>' +
                '<td>' + data[i].date + '</td>' +
                '<td class="' + info.type + '">' +
                '<div class="row-fluid">' +
                '<div class="span10">' +
                info.payment + comment +
                '</div>' +
                '<div class="span1 minus" data-id="' + info.id + '">' +
                '<span class="text-error">-</span>' +
                '</div>' +
                '</div>' +
                '</td>' +
                '</tr>'
            ).appendTo(html_container);
        }

        addSampoPassEvents();
        addWriteOffBehavior();
    }

    /**
     * Добавляшка обработчика удаления записей из таблицы
     */
    function addWriteOffBehavior() {
        var $elems = $('#payments .minus');

        $elems.off('click');
        $elems.click(function () {

            var $id = $(this).data('id');

            if ($id.search(/^u\d*$/) >= 0) {
                var elem = $('#sampo_passes li input[value=' + $id.slice(1) + ']');
                elem.trigger('change', [true]);
            } else {
                if (confirm('\nВосстановить удаленную запись будет невозможно\nПродолжить?')) {
                    sendRequest({
                        action: 'del',
                        pid: $id,
                        date: $("#date").val()
                    }, function (json) {
                        var data = JSON.parse(json);
                        refreshTable(data.payments);
                        refureshPassList(data.passes);
                    })
                }
            }
        })
    }

    /**
     * Добавлялка значения в список абонементов
     */
    function addToPassList(id, name, surname, usage) {
        var $input = $(
            '<li><label class="inline checkbox">' +
            '<input type="checkbox" value="' + id + '">' + surname + ' ' + name +
            '</label></li>'
        );

        $input.find('input').prop('checked', usage);

        $('#sampo_passes').append($input);

        return $input;
    }

    function refureshPassList(data) {

        var htmlContainer = $('#sampo_passes');
        htmlContainer.empty();

        for (var i = 0, j = data.length; i < j; i++) {
            addToPassList(data[i].id, data[i].name, data[i].surname, data[i].usage)
        }

        addSampoPassEvents();
    }

    function addSearchBehavior() {
        var buffer;

        function refreshBuffer() {
            buffer = {};
            $('#sampo_passes li').each(function () {
                var val = $(this).text().replace(/\s/g, '').toLowerCase();
                buffer[val] = $(this);
            });
        }

        refreshBuffer();

        $('#prependedInput').keyup(function () {
            var curval = $(this).val().toLowerCase(),
                re = new RegExp(curval);

            for (var name in buffer) {
                if (name.search(re) > -1) {
                    buffer[name].show();
                } else {
                    buffer[name].hide();
                }
            }
        });
    }

    function clearForms() {
        $('.tab-content input[type!=checkbox]').val('');
    }

    function addSampoPassEvents() {
        var $elements = $('#sampo_passes li');

        $elements.off('change');
        $elements.change(function (event, forseUnselect) {

            var confirm_msg = $(this).find('label').text().replace(/^\s*/, ''),
                input = $(this).find('input'),
                action;

            if (forseUnselect || !input.is(':checked')) {
                confirm_msg += '\nСнять отметку о посещении?';
                action = 'uncheck';
                input.prop('checked', false);
            } else {
                confirm_msg += '\nОтметить абонемент?';
                action = 'check'
            }

            if (confirm(confirm_msg)) {
                sendRequest({
                    action: action,
                    pid: input.val(),
                    date: $('#date').val(),
                    time: $('#addSampoPass #inputTime').val()
                }, successProcess, errorProcess);
            } else {
                var checked = input.prop('checked');
                input.prop('checked', !checked);
            }
        });
    }

    function getDateWatcher(date) {

        var day = date.getDate();

        return function () {
            var toDay = new Date();

            if (day < toDay.getDate()) {
                $('#date').val(dateToStr(toDay))
            }
        }
    }

    function map(func, arr) {
        var res = [];

        for(var i= 0, j= arr.length; i<j; i++) {
            res.push(func(arr[i]));
        }

        return res;
    }

    function dateToStr(date) {
        return date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear()
    }

    function init(params) {
        $('#addButton').click(function () {
            showAddPassForm();
        });

        $('#cancelButton').click(function () {
            hideAddPassForm();
            return false;
        });

        var clockInput = $('input.time'),
            $submit = $('.submitBtn');

        addClockBehavior(clockInput);
        addSearchBehavior();
        addWriteOffBehavior();
        addSampoPassEvents();

        $submit.click(function (event) {
            event.stopPropagation();
            var $this = $(this),
                data = getFormData($this),
                type;

            if ($this.hasClass('btn1')) {
                type = 'cash-add'
            } else if ($this.hasClass('btn2')) {
                type = 'cash-wrt'
            } else if ($this.hasClass('btn3')) {
                type = 'pass'
            } else {
                return;
            }

            clearForms();
            sendRequest({
                action: 'add',
                type: type,
                data: JSON.stringify(data)
            }, successProcess, errorProcess, data);

            hideAddPassForm();

            return false
        });

        var $date = $('#date');
        $date.datepicker({
            format: 'dd.mm.yyyy'
        }).on('changeDate', function () {
            $(this).datepicker('hide');
            $('#date-submit').focus();
        });

        // Логика работы виджета за сегодня и за все остальные дни
        var dateVal = $date.val(),
            now = new Date();

        if(dateVal == dateToStr(now)) {
            clockAutoUpdate(clockInput);
            var dateWatcher = getDateWatcher(now);
            setInterval(dateWatcher, 500);
        } else {
            // Добавляем круг с восклицательным знаком
            $('input[type=time]').parent().each(function() {

                var elem = $('<div class="blink1" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle; border-radius: 20px; border: 2px solid red; text-align: center; color: white; background-color: red; font-weight: bold; font-size: 14pt; cursor: default; margin-left: 5px;">!</div>');

                $(this).append(elem.tooltip({
                    placement: 'right',
                    title: 'Выбрана не текущая календарная дата. Автообновление часов и даты отключено'
                }));

                setTimeout((function(e) {
                    return function() {
                        e.removeClass('blink1');
                    }
                })(elem), 6000);
            });

            $submit.click(function() {
                $('input[type=time]:visible').focus();
            })
        }
    }

    return init;
})();
