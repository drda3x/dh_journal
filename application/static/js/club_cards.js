window.ClubCards = {};

window.ClubCards.init = function() {

    function processData(url, params, callback) {
        $.ajax({
            method: 'GET',
            url: url,
            data: params
        }).error(function(err) {
            callback(err, null)
        }).done(function(data) {
            callback(null, JSON.parse(data))
        });
    }

    $('.modal .groups option').click(function() {
        var $this = $(this),
            $id = $this.val();

        var all, target;

        all = $('.modal .students_lists select');
        target = $('.modal .students_lists select#'+$id);

        all.addClass('hide');
        all.removeClass('active');

        target.removeClass('hide');
        target.addClass('active');
    });

    $('#multicard-add-menu').on('hidden', function () {
        var all, target;

        $('.modal .groups select').val('def');

        all = $('.modal .students_lists select');
        target = $('.modal .students_lists select#def');

        all.addClass('hide');
        all.removeClass('active');

        target.removeClass('hide');
        target.addClass('active');
    });

    var datepicker = $('#multicard-add-menu .datepicker input').datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1
    }).on('changeDate', function() {
        $(this).datepicker('hide');
    });

    $('#multicard-add-menu .save_data').click(function() {
        var group = $('.groups select').val(),
            student = $('.students_lists').find('.active').first().val(),
            date = datepicker.val(),
            pass_type = $('.pass_types select').val();

        $.ajax('createmulty', {
            data: {
                group: group,
                student: student,
                date: date,
                ptid: pass_type
            }
        }).done(function() {
            window.location.reload();
        }).error(function() {
            console.log('error');
        })
    });

    var pass, student, group;

    function getLessons(tr) {
        return parseInt(tr.find('td:eq(5)').text())
    }

    function setLessons(tr, val) {
        var v = (val > 0) ? val : 0;
        tr.find('td:eq(5)').text(v)
    }

    // Универсальная функция, должна сама определять что ей надо сделать с ячейкой...
    function get_handler(inc_context) {
        var context = inc_context;

        return function() {

            function getPassCnt(arr) {
                for(var i=arr.length-1; i>=0; i--) {
                    if(arr[i].pid == context.pid) {
                        return arr[i].cnt;
                    }
                }

                return NaN;
            }

            function clear_processes() {
                context.td.removeClass('in_process_colored');
                context.td.removeClass('in_process_white');
            }
            clear_processes();

            var data;
            if(!context.del) {
                context.td.addClass('in_process_white');
                data = {
                    group_id: context.gid,
                    date: context.date,
                    checked: [{pass_id: context.pid}]
                };

                var current_cnt = getLessons(context.tr);

                if(current_cnt - 1 < 0) {
                    clear_processes();
                    return
                }

                setLessons(context.tr, current_cnt - 1);

                processData('processlesson',
                    {
                        data: JSON.stringify(data)
                    },
                    function(err, data) {
                        clear_processes();
                        if(!err) {
                            context.td.css('background-color', '#ffd700');
                            context.td.find('span').text('удалить');
                            context.del = !context.del;
                        } else {
                            setLessons(context.tr, current_cnt + 1);
                        }
                    }
                );
            } else {
                context.td.addClass('in_process_colored');

                data = {
                    gid: context.gid,
                    stid: context.stid,
                    params: JSON.stringify([context.date, 1])
                };

                processData('deletepass', data, function(err, data) {
                    clear_processes();
                    if(!err) {
                        context.td.css('background-color', '#ffffff');
                        context.td.find('span').text('списать');
                        context.del = !context.del;
                        setLessons(
                            context.tr,
                            getPassCnt(data)
                        )
                    }
                });
            }
        }
    }


    /**
     * Отрисовка данных в виджете.
     * @param data
     * @param tableData
     */
    function drawWidget(htmlContainer, data, info) {
        htmlContainer.empty();
        $('#multicard-pass-menu .modal-header h4').text(
            info.tr.find('td:eq(1)').text()
        );

        // Формируем таблички групп
        for(var i= 0, j= data.length; i<j; i++) {
            // html
            var div = $('<div></div>'),
                table = $('<table class="table table-bordered table-striped"></table>').appendTo(div),
                headers = $('<tr></tr>').appendTo(table),
                body = $('<tr></tr>').appendTo(table);

            // data
            var group = data[i].group,
                lessons = data[i].lessons;

            div.prepend('<h4>'+group.name+'</h4');

            for(var k= 0, m= lessons.length; k<m; k++) {

                // Формируем html
                var th = $('<th>' + lessons[k][0] + '</th>'), // дата
                    td = $('<td data-date="' + lessons[k][0] + '"></td>');

                switch (lessons[k][1].status) {
                    case 1:
                        // Занятие доступно для списания
                        td.append('<span class="write_off">списать</span>');
                        td.click(get_handler({
                            tr: info.tr,
                            td: td,
                            date: lessons[k][0],
                            pid: info.pass,
                            gid: group.id,
                            stid: info.student,
                            del: false
                        }));
                        break;

                    case 0:
                        // Занятие можно удалить
                        td.append('<span class="write_off">удалить</span>');
                        td.css('background-color', '#ffd700');
                        td.click(get_handler({
                            tr: info.tr,
                            td: td,
                            date: lessons[k][0],
                            pid: info.pass,
                            gid: group.id,
                            stid: info.student,
                            del: true
                        }));
                        break;

                    case -1:
                        // Занятие не доступно для списания
                        td.addClass('disabled');
                        break;
                }

                headers.append(th);
                body.append(td);

            }

            htmlContainer.append(div);
        }
    }

    // todo ТАК ДЕЛАТЬ НЕ НАДО!!!!
    // todo ЭТО НАДО ПЕРЕДЕЛАТЬ, НО СЕЙЧАС МНЕ ЛЕНЬ!!!!
    var pass;

    $('#all_passes tr').click(function() {

        resetWidget();

        var $this, student, info, htmlContainer;

        $this = $(this);
        pass = $this.data('pid');
        student = $this.data('stid');
        info = {
            pass: pass,
            student: student,
            tr: $this
        };

        htmlContainer = $('#pass-detail-container');
        htmlContainer.hide();
        $('#multicard-pass-menu').modal('show');
        processData('getmcdetai', {pid: pass}, function(err, data) {
            if(err) {
                alert('Выполнение завершилось с ошибкой');
            } else {
                drawWidget(htmlContainer, data, info);
                htmlContainer.show();
                htmlContainer.siblings('img').hide()
            }
        });

    });

    function resetWidget() {
        var widget = $('#multicard-pass-menu');
        widget.find('h4').text('Загрузка данных...');
        widget.find('img').show();
    }

    $('#multicard-pass-menu .groups').click(function(event) {
        var $this = $(event.target);
        group = $this.data('id');

        $('#multicard-pass-menu .dates li').addClass('hide');
        $('#multicard-pass-menu .dates .g'+group+'p'+pass).removeClass('hide');
    });

    $('#multicard-pass-menu').on('hide', function() {
        $('#multicard-pass-menu h4').first().text('');
        $('#multicard-pass-menu .active').removeClass('active');
        $('#multicard-pass-menu .dates li').addClass('hide');
    });

    $('#multicard-pass-menu .save_data').click(function() {
        var $date = $('#multicard-pass-menu .dates .active').text(),
            json = {
                group_id: group,
                date: $date,
                checked: [{
                    pass_id: pass
                }]
            };

        $.ajax('processlesson', {
            data: {
                data: JSON.stringify(json)
            }
        }).done(function() {
            window.location.reload();
        }).error(function(err) {
            console.log(err.responseText);
        });
    });

    $('#multicard-pass-menu .delete_pass').click(function() {
        $.ajax('deletemultypass', {
            data: {
                ids: JSON.stringify([pass])
            }
        }).done(function() {
            window.location.reload();
        }).error(function(err) {
            console.log(err.responseText);
        });
    });

}
