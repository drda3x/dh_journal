(function() {
    /**
     * Заполнение таблицы редактирования
     * @type {*|jQuery|HTMLElement}
     */
    var $infoTable = $('#info table'),
        $studentForm = $('#editStudent'),
        addUrl = '/group/addstudent',
        editUrl = '/group/editstudent';

    var $shortCardMenu_lastIndex, $row, $id, $name, $family, $index;
    var $groupId = window.group.id;
    var needReload = false;

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

    // Алерт
    var $alert = $('.alert');
    $alert.hide();
    $alert.types = ['red', 'green'];
    $alert.show = function(msg, type, hideAfter, fadeOut) {
        this.text(msg);
        this.css('display', 'inline-block');

        for(var i= this.types.length - 1; i>=0; i--) {
            this.removeClass(this.types[i]);
        }

        this.addClass(type);

        if(hideAfter != undefined) {
            if(fadeOut != undefined) {
                setTimeout((function(context) {
                    return function() {
                        context.fadeOut(fadeOut);
                    }
                })(this), hideAfter)
            } else {
                setTimeout(this.hide, hideAfter)
            }

        }
    };

    $infoTable.find('tr').click(function(event) {
        if(!$(event.target).hasClass('shotcard-disabled') && $(event.target).parentsUntil('.shotcard-disabled').last().is('html')) {
            event.stopPropagation();
            var $shortCardMenu = $('#shortCardMenu');

            if($(this).data('active') == 0) {
                $shortCardMenu.find('#changeStudentData').hide();
                $shortCardMenu.find('#deleteStudent').hide();
                $shortCardMenu.find('#restoreStudent').show();
            } else {
                $shortCardMenu.find('#changeStudentData').show();
                $shortCardMenu.find('#deleteStudent').show();
                $shortCardMenu.find('#restoreStudent').hide();
            }

            $shortCardMenu.css('top', event.clientY);
            if(event.clientX + $shortCardMenu.width() + 30 >  $(window).width()) {
                $shortCardMenu.css('left', event.clientX - $shortCardMenu.width() - 25);
            } else {
                $shortCardMenu.css('left', event.clientX);
            }
            $id = $(this).data('id');

            var chld = $(this).children();

            $name = $(chld[1]).text();
            $family = $(chld[2]).text();
            $index = $(this).index();

            function hide() {
                $shortCardMenu.hide();
                $shortCardMenu_lastIndex = null;
                $('body').off('click', hide);
            }

            function show() {
                $shortCardMenu_lastIndex = $index;
                $shortCardMenu.show();
            }

            if($shortCardMenu_lastIndex == $index) {
                hide();
                $row = null;
            } else {
                show();
                $('body').on('click', hide);
                $row = $(this);
            }


        }
    });
    
    function getIdFromSelectedRows() {
        var result = [];
        
        $infoTable.find('tr:gt(0)').each(function() {
            if($(this).find('input:checked').length > 0) {
                result.push($(this).data('id'));
            }
        });
        return result;
    }
    
    $('#changeStudentData').click(function() {
        $(window).scrollTop(0);
        showStudentCard();
    });

    $('#deleteStudent').click(function() {
        if (!confirm('Удалить ученика из группы?')) {
            return
        }
        backDrop('show');
        processData('deletestudent', {ids: JSON.stringify([$id]), gid: window.group.id }, function(err, data) {
            if(!err) {
                reload()
            } else {
                console.log(err);
            }
        })
    });

    $('#restoreStudent').click(function() {
        if(!confirm('Восстановить ученика в списке группы?')) {
            return;
        }
        backDrop('show');
        processData('restorestudent', {ids: JSON.stringify([$id]), gid: window.group.id }, function(err, data) {
            if(!err) {
                reload()
            } else {
                console.log(err);
            }
        })
    });

    $('#deleteStudentBtn').click(function() {
        var toDelete = getIdFromSelectedRows();

        var msg = (toDelete.length > 1) ? 'Удалить учеников из группы' : 'Удалить ученика из группы?';

        if(toDelete.length > 0) {
            if (!confirm(msg)) {
                return;
            }
            processData('deletestudent', {ids: JSON.stringify(toDelete), gid: window.group.id }, function(err, data) {
            backDrop('show');
            if(!err) {
                reload()
            } else {
                console.log(err);
            }
        })
        }
    });

    var $freezePass = $('#freezePassModal');
    var $datepicker = $freezePass.find('.datepicker');
    var now = new Date();
    var freezeData = [];

    $datepicker.datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1
    }).on('changeDate', function(ev) {
        $datepicker.datepicker('hide');
    });

    $freezePass.modal({show: false});

    $('#freezeStudentPass').click(function() {
        freezeData = [$id];
        $datepicker.datepicker('setValue', now);
        $datepicker.attr('data-date', now.valueOf());
        $freezePass.find('.modal-header h4').text($family+' '+$name+' - заморозка абонемента');
        $freezePass.modal('show');
    });

    $('#freezePassBtn').click(function() {
        clearFreeze();
        freezeData = getIdFromSelectedRows();

        if(freezeData.length > 0) {
            $datepicker.datepicker('setValue', now);
            $datepicker.attr('data-date', now.valueOf());
            $freezePass.find('.modal-header h4').text(window.group.name + ' - заморозка абонементов (выбрано: '+freezeData.length+')');
            $freezePass.modal('show');
        }
    });

    function freezePass() {
        backDrop('show');

        var dates = [];
        $datepicker.each(function() {
            dates.push($(this).val());
        });
        $freezePass.modal('hide');
        processData('freezepass',
                {
                    ids: JSON.stringify(freezeData),
                    group: window.group.id,
                    date: JSON.stringify(dates)
                }, function(err, data) {
            if(!err) {
                clearFreeze();
                reload();
            } else {
                alert('Не выполнен перенос для следующих учеников:\n\n'+err.responseText+'\n\nна одну дату попадает несколько занятий');
                reload();
            }
        });
    }

    function clearFreeze() {
        freezeData = [];
    }

    $freezePass.find('.modal-footer .cancel').click(clearFreeze);
    $freezePass.find('.modal-footer .btn-primary').click(freezePass);

    var $passList = $('#passList');
    $passList.modal({show: false});

    $('#writeOffPass').click(function() {
        var $btn = $passList.find('.modal-footer .btn-primary');
        $btn.val('Списать');

        $btn.off('click');
        $btn.click(function() {

            var ids = getPassListData(),
                msg = (ids.length > 1) ?  'Списать абонементы' : 'Списать абонемент';

            if(confirm(msg)) {
                backDrop('show');
                processData('writeoffpass', {ids: JSON.stringify(ids)}, function(err, data) {
                    if(!err) {
                        $passList.modal('hide');
                        reload()
                    } else {
                        $passList.modal('hide');
                        alert('Что-то пошло не так, пожалуйста попробуйте еще раз.')
                    }
                });
            }
        });

        $passList.find('.modal-header h4').text($family+' '+$name+' - списание остатка');
        processData('getpasses', {owner: $id, group: $groupId}, processPassList);
    });

    $('#deletePass').click(function() {
        var $btn = $passList.find('.modal-footer .btn-primary');
        $btn.val('Удалить');

        $btn.off('click');
        $btn.click(function() {

            var ids = getPassListData(),
                msg = (ids.length > 1) ?  'Удалить абонементы' : 'Удалить абонемент';

            if(confirm(msg)) {
                backDrop('show');
                processData('deletepass', {ids: JSON.stringify(ids)}, function(err, data) {
                    if(!err) {
                        $passList.modal('hide');
                        reload()
                    } else {
                        $passList.modal('hide');
                        alert('Что-то пошло не так, пожалуйста попробуйте еще раз.')
                    }
                });
            }
        });

        $passList.find('.modal-header h4').text($family+' '+$name+' - удаление абонемента');
        processData('getpasses', {owner: $id, group: $groupId}, processPassList);
    });

    var $changePassOwnerModal = $('#changePassOwnerModal');
    $changePassOwnerModal.modal({show: false});

    $('#changePassOwner').click(function() {

        var $container = $('#changePassOwnerModal .owners');

        $container.empty();

        $infoTable.find('tr:gt(0)').each(function() {
            if($(this).index() != $index) {
                var chld= $(this).children();
                var name, family, id;

                id = $(this).data('id');
                name = $(chld[1]).text();
                family = $(chld[2]).text();

                $container.append($('<li><label class="radio"><input type="radio" name="owhers" data-id="'+id+'">'+family+' '+name+'</label></li>'));
            }
        });

        $changePassOwnerModal.modal('show');
    });

    $changePassOwnerModal.find('.btn.btn-primary').click(function() {
        var new_owner = $changePassOwnerModal.find('input:checked').data('id');
        backDrop('show');
        processData(
            'changeowner',
            {
                cur_owner: $id,
                new_owner: new_owner,
                group: window.group.id
            },
            function(err, data) {
                if(!err) {
                    reload()
                } else {
                    console.log(err);
                }
            }
        );
    });

    function processData(url, params, callback) {
        $.ajax({
            method: 'GET',
            url: url,
            data: params
        }).error(function(err) {
            backDrop('hide');
            callback(err, null)
        }).done(function(data) {
            callback(null, JSON.parse(data))
        });
    }

    function processPassList(err, passes) {
        if(!err) {
            var $pl = $('#passListContainer');
            $pl.empty();
            if(passes.length > 0) {
                for(var i= 0, j= passes.length; i<j; i++) {
                    var pass = passes[i];
                    console.log(pass);
                    $('<li><label class="checkbox"><input type="checkbox" data-val="'+pass.id+'">'+pass.pass_type.name+' c '+pass.start_date+'</label></li>').appendTo($pl);
                }
                $passList.modal('show');

            } else {
                alert('У ученика нету ни одного открытого абонемента.')
            }
        }
    }

    function getPassListData() {
        var ids = [];
        $('#passListContainer').children().find('input:checked').each(function() {
            ids.push($(this).data('val'));
        });

        return ids;
    }

    function checkForm(params) {
         return (params.first_name != '') && (params.last_name != '') && (params.phone != '')
    }

    function showStudentCard(event) {
        var $this = $row,
        $children = $this.children();

        $('#stid').val($id);
        $('#last_name').val($($children[2]).text());
        $('#first_name').val($($children[3]).text());
        $('#phone').val($($children[4]).text());
        $('#e_mail').val($($children[5]).text());
        $('#is_org').prop('checked', $($children[6]).text() == 'ОРГ' ? 'checked' : false);

        var $submit = $studentForm.find('.btn.btn-primary');
        $submit.off('click');
        $submit.click(function() {

            var params = getStudentFormParams();

            if(checkForm(params)) {
                backDrop('show');
                processData(editUrl, getStudentFormParams(), function (err, data) {
                    if (!err) {
                        reload();
                    } else {
                        backDrop('hide');
                        $alert.show('ОШИБКА! Не удалось сохранить данные', 'red', 2500, 1500);
                    }
                })
            } else {
                $alert.show('ОШИБКА! Не заполнено одно из следующих полей: "Фамилия", "Имя", "Номер телефона"', 'red', 2500, 1500);
            }
        });

        $submit.val('Сохранить');
        $studentForm.modal('show');
    }

    $('#editStudentBtn').click(function() {

        $('#last_name').val('');
        $('#first_name').val('');
        $('#phone').val('');
        $('#e_mail').val('');
        $('#is_org').prop('checked', false);

        var $submit = $studentForm.find('.btn.btn-primary');

        $submit.off('click');
        $submit.click(function() {
            var params = getStudentFormParams();

            if(checkForm(params)) {
                processData(addUrl, getStudentFormParams(), function(err, data) {
                    if(!err) {
                        needReload = true;
                        $studentForm.find('.modal-body').find('input').val('').prop('checked', false);
                        $alert.show('Сохранено (можно добавить еще одного)', 'green', 2500, 1500);
                    } else {
                        if(err.responseText == 'PersonExistedError') {
                            $alert.show('ОШИБКА! Человек с такими личными данными уже внесен в эту группу', 'red', 2500, 1500);
                        } else {
                            $alert.show('ОШИБКА! Не удалось добавить ученика. Попробуйте еще раз', 'red', 2500, 1500);
                        }
                    }
                })
            } else {
                $alert.show('ОШИБКА! Не заполнено одно из следующих полей: "Фамилия", "Имя", "Номер телефона"', 'red', 2500, 1500);
            }
        });

        $submit.val('Добавить');
        $studentForm.modal('show');
    });

    function getStudentFormParams() {
        return {
            id: window.group.id,
            stid: $id,
            last_name: $('#last_name').val(),
            first_name: $('#first_name').val(),
            phone: $('#phone').val(),
            e_mail: $('#e_mail').val(),
            is_org: $('#is_org').prop('checked')
        }
    }

    /**
     * checkbox
     */
    var $inputs = $('.info-fio input'),
        checkAllValue = -1;

    $inputs.click(function() {
        var $this = $(this),
            $val = $this.val();

        if($val == checkAllValue) {

            if($this.prop('checked')) {
                $inputs.each(function() {
                    $(this).prop('checked', 'checked');
                    $('#deleteStudentBtn').removeClass('disabled');
                });
            } else {
                $inputs.each(function() {
                    $(this).prop('checked', false);
                });
            }
        } else {
            var $checked = $inputs.filter(':checked'),
                $target = $inputs.filter('[value='+checkAllValue+']');
            if($checked.length == $inputs.length-1 && !($target.prop('checked'))) {
                $target.prop('checked','checked')
            } else {
                $target.prop('checked',false)
            }
        }

        if($inputs.filter(':checked').length > 0) {
            $('.allowdisable').removeClass('disabled');
        } else {
            $('.allowdisable').addClass('disabled');
        }
    });

    function reload() {
        window.location.pathname = 'group?id=window.group.id&date=' + window.window.controlData.currentDate;
    }

    function backDrop(param) {
        var handlers = {
            show: function() {
                $('<div class="modal-backdrop">Тут должна быть анимация</div>').appendTo('body')
            },
            hide: function() {
                $('.modal-backdrop').remove()
            }
        };

        handlers[param]();
    }

    var $commentWidget = $('#commentWidget'),
        $commentWidgetContent = $('#commentWidgetContent');
    $commentWidget.modal({show: false});

    $('#comment').click(function() {
        $(window).scrollTop(0);
        $commentWidget.modal('show');
        $commentWidgetContent.empty();
        $commentWidget.find('h3 span').text($family+' '+$name);

        processData('get_comments', {group_id: window.group.id, stid: $id}, function(err, data) {
            if(!err) {
                var messages = data.data;

                for(var i= 0, j= messages.length; i<j; i++) {
                    var container = addComment(messages[i]);
                    if(i > 0) {
                        container.css('border-top', '1px solid #dddddd');
                    }
                    container.appendTo($commentWidgetContent);
                }
            }
        });
    });


    function addComment(data) {
        var container = $('<div class="comment-content"></div>'),
            dt = $('<div class="comment-date"></div'),
            ta = $('<textarea maxlength="100" readonly></textarea>'),
            buttonsContainer = $('<div class="comment-buttonsblock"></div>'),
            editButton = $('<button class="btn btn-mini edit-comment">Изменить</button>'),
            saveButton = $('<button class="btn btn-mini edit-comment">Сохранить</button>'),
            cancelButton = $('<button class="btn btn-mini edit-comment" style="margin-left: 15px;">Отмена</button>'),
            deleteButton = $('<button class="btn btn-mini btn-danger delete-comment">Удалить</button>');

            buttonsContainer.append(deleteButton);
            buttonsContainer.append(editButton);
            buttonsContainer.append(cancelButton);
            buttonsContainer.append(saveButton);


            saveButton.hide();
            cancelButton.hide();

            dt.text(data.date);
            ta.val(data.msg);

            container.append(dt);
            container.append(buttonsContainer);
            container.append(ta);

            editButton.click((function() {
                var msgId = data.id,
                    _container = container,
                    _textarea = ta,
                    _saveBtn = saveButton,
                    _cancelBtn = cancelButton;
                return function() {
                     var buffer = _textarea.clone();

                    buffer.val(_textarea.val());
                    buffer.hide();
                    buffer.addClass('comment-buffer');
                    _container.append(buffer);

                    _textarea.attr('data-prevval', _textarea.val());
                    _textarea.removeAttr('readonly');
                    _saveBtn.show();
                    _cancelBtn.show();
                    $(this).hide();
                }
            })());

            saveButton.click((function() {
                var _container = container,
                    _editBtn = editButton,
                    _cancelBtn = cancelButton,
                    _saveBtn = saveButton,
                    msgId = data.id,
                    _textarea = ta;

                function cb(err, data) {
                    if(!err) {
                        _container.find('.comment-buffer').remove();
                        _textarea.attr('readonly', true);

                        _editBtn.show();
                        _cancelBtn.hide();
                        _saveBtn.hide();

                        var firstComment;
                        try {
                            firstComment = $('.comment-content').first();
                        } catch (e) {

                        } finally {
                            if(firstComment != undefined) {
                                firstComment.css('border', '0px');
                                changeCommentInMainTable(firstComment.find('textarea').val())
                            } else {
                                changeCommentInMainTable('')
                            }
                        }

                        $alert.show('Сохранено', 'green', 2500, 1500);
                    } else {
                        $alert.show('Не сохранено. Ошибка!', 'red', 2500, 1500);
                    }
                }

                return function() {
                    var text = _textarea.val();
                    processData('edit_comment', {cid: msgId, msg: text}, cb);
                }
            })());

            cancelButton.click((function() {
                var _container = container,
                    _editBtn = editButton,
                    _saveBtn = saveButton,
                    _textarea = ta;

                return function() {
                    var buffer = _container.find('.comment-buffer');

                    _textarea.val(buffer.val());
                    buffer.remove();
                    _textarea.attr('readonly', true);

                    _editBtn.show();
                    _saveBtn.hide();
                    $(this).hide();
                }
            })());

            deleteButton.click((function() {
                var _container = container,
                    msgId = data.id;

                function callback(err, data) {
                    if(!err) {
                        var firstComment;
                        try {
                            firstComment = $(_container.siblings().first());
                        } catch (e) {
                        } finally {
                            if(firstComment.length > 0) {
                                firstComment.css('border', '0px');
                                changeCommentInMainTable(firstComment.find('textarea').val())
                            } else {
                                changeCommentInMainTable('')
                            }
                            $alert.show('Коментарий удален', 'green', 2500, 1500);
                            _container.remove();
                        }
                    }
                }

                return function() {
                    processData('delete_comment', {cid: msgId}, callback);
                }
            })());

            return container;

    }

    function changeCommentInMainTable(msg) {
        var $tr = $($infoTable.find('tr')[$index]),
            $commentCell = $tr.find('.comment');

        $commentCell.text(msg);
    }

    var $currentElement;

    $('#addComment').click(function() {
        $('#addCommentButtonBlock').hide();
        $('#saveCommentButtonBlock').show();

        var now = new Date(),
            dt = $('<div class="comment-date"></div');

        dt.text(now.toLocaleString().replace(',',''));

        $currentElement = $('<div class="comment-content new"><textarea maxlength="100"></textarea></div>');
        $currentElement.prepend(dt);
        $('#commentWidgetContent').prepend($currentElement);
    });

    function hideCommentSaveBlock() {
        $('#addCommentButtonBlock').show();
        $('#saveCommentButtonBlock').hide();
        if($currentElement.hasClass('new')) {
            $currentElement.remove();
        }
        $currentElement = null;
    }

    $('#saveCommentButtonBlockHide').click(hideCommentSaveBlock);

    $('#saveComment').click(function() {
        var text = $currentElement.find('textarea').val(),
            params;

        if(text.length > 0) {
            if($currentElement.hasOwnProperty('commentId')) {
            params = {
                cid: $currentElement.commentId
            }
            } else {
                params = {
                    stid: $id,
                    group_id: window.group.id
                }
            }

            params.msg = text;

            processData('edit_comment', params, function(err, data) {
                if(err) {
                    $alert.show('Ошибка сохранения', 'red', 2500, 1500);
                } else {
                    var newHtml = addComment(data.data);

                    $commentWidgetContent.prepend(newHtml);
                    hideCommentSaveBlock();
                    changeCommentInMainTable(data.data.msg);
                    $alert.show('Сохранено', 'green', 2500, 1500);
                }

            })
        } else {
            $alert.show('Введите коментарий', 'red', 2500, 1500);
        }
    });

    $commentWidget.find('.close').click(function() {
        hideCommentSaveBlock();
        $currentElement = null;
    });

    $('#changeGroupContent .datepicker').datepicker({
        format: 'dd.mm.yyyy'
    });

})();