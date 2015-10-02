(function() {
    "use strict";

    var multipassName = 'Клубная карта';

    var matrix = new window.View.Matrix(),
        popoverLogic = new window.vidgetsLogic.Popover(window.group.id);

    // Логика sub-menu
    $('.sub-menu li').click(function(event) {
        $(this).siblings().find('input:checked').prop('checked', false);
        event.stopPropagation();
    });

    $('.sub-menu').click(function() {
        $(this).find('input:checked').prop('checked', false);
        $(this).find('input[type!=button]').val('');
    });

    var $datepicker = $('.sub-menu .datepicker').datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1
    }).on('changeDate', function(ev) {
        $(this).next().focus();
    });

    function getSiblingsVals(elem) {
        var params = [];
        elem.siblings().each(function() {
            params.push($(this).val())
        });

        return params;
    }

    $('.li-content input').on('focus', function() {
        $(this).siblings('.datepicker').datepicker('hide');
    });

    $('.li-content .move-btn').click(function() {
        if(confirm('Подтвердите перенос')) {
            backDrop('show');
            $.ajax('freezepass', {
                data: {
                    group: window.group.id,
                    date: JSON.stringify(getSiblingsVals($(this))),
                    ids: JSON.stringify([$(this).data('stid')])
                }
            }).done(function(data) {
                reload();
            }).error(function(err) {
                alert('Не выполнен перенос для следующих учеников:\n\n'+err.responseText+'\n\nна одну дату попадает несколько занятий');
                backDrop('hide');
            })
        }
    });

    $('.li-content .del-btn').click(function() {
        if(confirm('Подтвердите удаление')) {
            backDrop('show');
            $.ajax('deletepass', {
                data: {
                    gid: window.group.id,
                    params: JSON.stringify(getSiblingsVals($(this))),
                    stid: $(this).data('stid')
                }
            }).done(function(data) {
                reload();
            }).error(function(err) {
                alert('error');
                backDrop('hide');
            })
        }
    });


    /**
     * Получить дату из колонки
     * @param element
     * @returns {*}
     */
    function getDateFromColumn(element) {
        try {
            return matrix.getColumn(element)[0].text();
        } catch(e) {
            return NaN
        }
    }

    /**
     * Заполнить попап урока
     * @param context
     */
    function fillLessonsForm(context) {
        try {
            var $date = $('#lesson_window_date'),
            data = matrix.getColumn(context),
            $targets = $('.lesson_data'),
            $popover = $('.popover');

            $targets.empty();
            $targets.off();
            $targets.removeAttr('val');

            $popover.remove();

            var date_val = getDateFromColumn(context);
            $date.text(date_val);

            var i = 1;

            $targets.each(function() {
                var $this = $(this);

                $this.attr('class', data[i].attr('class'));
                $this.addClass('lesson_data');

                // Удаляем следы hover-эффекта от родительской таблицы
                $this.removeClass('active');
                $this.removeClass('highlight');

                if(data[i].data('pass') === 'True') {
                    var attended = data[i].data('sign') == 'True',
                        $inp = $('<input type="checkbox" style="margin: 0" />'),
                        label = data[i].text();

                    $this.attr('data-pid', data[i].data('pid'));

                    $this.append($inp);
                    $this.append(label);
                    if(attended) {
                        $inp.prop('checked', 'checked');
                    }

                    $this.click(function(event) {
                        var $target = $(event.target);
                        if(!$target.is('input') && !$target.is('a') && !$target.is('span') && !$target.is('b.caret') && !$target.is('li')) {
                            var cb = $(this).children().first();

                            if(cb.prop('checked')) {
                                cb.removeAttr('checked');
                            } else {
                                cb.prop('checked', 'checked');
                            }
                        }
                    });
                } else {
                    $this.addClass('add-pass');
                    popoverLogic.init($this);

                    $this.click(function() {
                        popoverLogic.hide();
                        popoverLogic.show($(this));

                        if ($this.attr('data-multipass_id')) {
                            $('.popover-content').find('.control-group').each(function() {
                                var $label = $(this).find('label span');
                                if($label.text().toLowerCase().indexOf(multipassName.toLowerCase()) >= 0) {
                                    $label.html('<strong>Клубная карта ('+$this.data('multipass_lessons')+')</strong>')
                                }
                            });
                        }

                        $this.parents('table').find('.highlight').removeClass('highlight');
                        $this.siblings('td').addClass('highlight');
                        $this.addClass('highlight');

                    });
                }

                i++;
            });

            var $blockTable = $('#block_table'),
                $inp = $('#cancel_lesson_inp');

            // Если стоит галочка в поле "Отменено"
            if($inp.prop('checked')) {
                $blockTable.show();
            }

            $inp.click(function() {
                var container = $('#lesson_container'),
                    content = $('#lesson_content');

                if($(this).prop('checked')) {
                    container.css('position','relative');
                    container.css('overflow-y','hidden');
                    popoverLogic.hide();
                    $blockTable.height(content.height() + 20);
                    $blockTable.show();
                } else {
                    container.css('position','static');
                    container.css('overflow-y','scroll');
                    $blockTable.hide();
                    $('.popover-opened').removeClass('popover-opened');
                }
            });

            var printBtn = $('#printBtn');
                printBtn.off('click');
                printBtn.click(function() {
                    window.open('/print?id=window.group.id&type=lesson&date='+getDateFromColumn(context).replace(/\./g, ''), '', 'width=500, height=800, location=no')
                });
        } catch (e) {

        }
    }

    // ====================================================================================================
    // ====================================================================================================

    // Add DOM events
    var cl = $('.hover-able');
    cl.mouseenter(function(event) {

        var $this = $(this);

        if($this.hasClass('fio_cell')) {
            if(!$this.hasClass('active')) $this.addClass('highlight');
        } else {
            if(!$this.hasClass('active')) matrix.highlightColumn($this);
        }

    });

    cl.mouseleave(function() {

        var $this = $(this);

        if($this.hasClass('fio_cell')) {
            if(!$(this).hasClass('active')) $this.removeClass('highlight');
        } else {
            if(!$(this).hasClass('active')) matrix.unHighlightColumn($(this));
        }

    });

    // ====================================================================================================
    // ====================================================================================================

    var tr = $('#journal tr');
    tr.click(function(event) {

        var $this = $(event.target);

        if($this.hasClass('hover-able')) {

            matrix.deactivateAll();

            if(!$this.hasClass('fio_cell')) {
                matrix.deactivateAll();
                matrix.makeActive(event.target);
            } else {
                $this.addClass('highlight');
                $this.addClass('active');
            }

        }
    });

    tr.click(function(event) {
        var $this = $(event.target),
            date = getDateFromColumn($this);

        if($this.hasClass('canceled')) {

            $('#lesson_restore').modal('show');
            $('#restore_lesson_window_date').text(date);

        } else if($this.hasClass('hover-able')) {

            fillLessonsForm($this);

            if (!$this.hasClass('fio_cell')) {
                $('#lesson_window').modal('show');
            }
        }
    });

    $('#restore_lesson_submit').click(function() {
        backDrop('show');
        $.ajax({
            method: 'GET',
            url: 'restorelesson',
            data: {
                id: window.group.id,
                date: $('#restore_lesson_window_date').text().replace(/[^\w\.]/g,'')
            }
        }).error(function(err) {
            alert('Возникла ошибка при восстановлении отмененного занятия');
           backDrop('hide');
        }).done(function(data) {
            window.location.pathname = 'group?id=window.group.id&date=' + window.controlData.currentDate;
        });
    });

    var $lesson_window = $('#lesson_window'),
        opened = false;

    $lesson_window.click(function(event) {
        var $target = $(event.target),
            top = $target.parentsUntil('.popover');

        if(!($(top[top.length-1]).is('.popover-inner') || $target.is('.lesson_data')) && popoverLogic.opened && opened) {
            popoverLogic.hide();
        }
        opened = popoverLogic.opened;
    });

    $lesson_window.on('hide', function(event) {
        if(popoverLogic.opened) {
            popoverLogic.hide();
            opened = false;
            return false;
        }
    });

    $lesson_window.on('hidden', function(){
        popoverLogic.stopIntervals();
        $(this).find('.highlight').removeClass('highlight');
        $('#full_attended').prop('checked', false);
        $('#cancel_lesson_inp').prop('checked', false);
    });

    // ====================================================================================================
    // ====================================================================================================

    var $saveButton = $('.save_data');

    $saveButton.click(function() {

        var full_attended = $('#full_attended').prop('checked');

        if(!full_attended && !confirm('ВНИМАНИЕ!\nНе установлен флаг "Проставить пропуски"\n(Пропущенные занятия не будут зафиксированы)\n\nПродолжить?')) {
            return false;
        }

        backDrop('show');
        popoverLogic.hide();

        var data_source = $('#lesson_content').find('tr:gt(0)'),
            json = {
                group_id: window.group.id,
                date: $('#lesson_window_date').text(),
                checked: [],
                unchecked: [],
                canceled: false
            };

        if(!$(this).data('context') === 'lesson_window') {
            return;
        }

        if(!$('#cancel_lesson_inp').prop('checked')) {
            data_source.each(function() {
                var cont = $(this).children(),
                    lesson = $(cont[1]),
                    student_id = $(cont[0]).data('stid');

                var lesson_inp = lesson.find('input');

                if(lesson.find('input').length > 0) {
                    if(lesson.find('input:checked').length > 0) {
                        if(lesson.hasClass('add-pass')) {

                            var values = {
                                student_id: student_id,
                                pass_type: lesson.attr('val'),
                                from_another: (lesson.attr('val') == -1) ? lesson.attr('subval') : null,
                                presence: true,
                                debt: lesson.data('debt'),
                                lcnt: lesson.data('lcnt'),
                                scnt: lesson.data('scnt')
                            };

                            json.checked.push(values);
                        } else {
                            json.checked.push(lesson.data('pid'));
                        }
                    } else if(lesson.attr('val') !== undefined) {
                        json.checked.push({
                            student_id: student_id,
                            pass_type: lesson.attr('val'),
                            presence: false
                        });
                    } else if(full_attended) {
                        json.unchecked.push(lesson.data('pid'));
                    }
                }
            });

        } else {
            json.canceled = true
        }

        $.ajax({
            method: 'GET',
            url: 'processlesson',
            data: {
                data: JSON.stringify(json)
            }
        }).done(function() {
            reload()
        }).error(function(err) {
            var json = JSON.parse(err.responseText);
            alert('ОШИБКА!\n\nНе удалось сохранить следующие абонементы:\n\n'+json.join('\n')+'\n');
            reload();
        });
    });

    function backDrop(param) {
        var handlers = {
            show: function() {
                $('<div class="modal-backdrop">Тут должна быть анимация</div>').appendTo('body')
            },
            hide: function() {
                $('modal-backdrop').remove()
            }
        };

        handlers[param]();
    }

    var $debtLinks = $('.debt-main');

    $debtLinks.popover({
        content: $('.debt-write_off').html(),
        html: true,
        show: false
    });

    $debtLinks.click(function() {
        var $this = $(this);

        try{
            $this.popover('toggle');
        } catch (e) {}


        var $popover = $this.siblings('.popover'),
        $clickBtn = $popover.find('.debt-write_off-btn');
        $clickBtn.off('click');

        $clickBtn.click(function() {

            var $td = $(this).parentsUntil('td'),
                $val = $popover.find('input');

            function cb(err, data) {
                if(!err) {
                    needReload = true;
                    reload();
                    /*if(parseInt(data) == 0) {
                        $this.remove();
                    } else {
                        $this.text('долг: '+ data);
                    }*/
                }
            }

            $.ajax({
                method: 'GET',
                url: 'writeoffdebt',
                data: {
                    gid: window.group.id,
                    sid: $this.data('id'),
                    val: $val.val()
                }
            }).done(function(data) {
                cb(null, data)
            }).error(function(err) {
                cb(err, null)
            });

            $this.popover('hide');
        });
    });

    $('.pass_menu-cnt').hide();

    var needReload = false;

    function reload() {
        window.location.reload();
    }

     // Перезагрузка страницы если надо
    $('.close').click(function() {
        if(needReload) {
            needReload = false;
            reload()
        }
    });

    $('.cancel').click(function() {
        if(needReload) {
            needReload = false;
            reload()
        }
    });

    $('.modal').on('hidden', function() {
        if(needReload) {
            needReload = false;
            reload()
        }
    });
})();