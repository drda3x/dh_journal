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

    $('.modal .groups li').click(function() {

        var $this = $(this),
            $id = $this.data('id');
        $('.modal .students_lists ul').addClass('hide');
        $('.modal .students_lists ul#'+$id).removeClass('hide');
    });

    $('.modal li').click(function() {
        var $this = $(this);
        if($this.parents('.groups').length > 0) {
            $('.modal .students_lists li').removeClass('active');
        }
        $this.siblings().removeClass('active');
        $this.addClass('active');
    });

    var datepicker = $('#multicard-add-menu .datepicker input').datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1
    });

    $('#multicard-add-menu .save_data').click(function() {
        var group = $('.groups').find('.active').first().data('id'),
            student = $('.students_lists').find('.active').first().data('stid'),
            date = datepicker.val();

        $.ajax('createmulty', {
            data: {
                group: group,
                student: student,
                date: date
            }
        }).done(function() {
            window.location.reload();
        }).error(function() {
            console.log('error');
        })
    });

    var pass, student, group;

    /**
     * Отрисовка данных в виджете.
     * @param data
     * @param tableData
     */
    function drawWidget(data, info) {
        var htmlContainer = $('#pass-detail-container');
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
                var th = $('<th>'+ lessons[k][0] +'</th>'), // дата
                    td = $('<td data-date="'+lessons[k][0]+'"></td>');

                if(lessons[k][1].available) {
                    // todo сделать подсвечивание отмеченных по мультикарте занятий
                    // todo и написать на них "удалить"
                    // todo к ячейке добавить классы "добавление" и "удаление"
                    td.append('<span class="write_off">списать</span>');
                } else {
                    td.addClass('disabled');
                }

                headers.append(th);
                body.append(td);

                // Добавляем event'ы
                if(lessons[k][1].available) {
                    td.click(function() {});
                }
            }

            htmlContainer.append(div);
        }

        $('#multicard-pass-menu').modal('show');
    }

    $('#all_passes tr').click(function() {

        var $this, pass, student, info;

        $this = $(this);
        pass = $this.data('pid');
        student = $this.data('stid');
        info = {
            pass: pass,
            student: student,
            tr: $this
        };

        processData('getmcdetai', {pid: pass}, function(err, data) {
            if(err) {
                alert('Выполнение завершилось с ошибкой');
            } else {
                drawWidget(data, info);
            }
        });

    });

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
