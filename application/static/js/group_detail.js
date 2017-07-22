(function() {
    "use strict";
    window.pageInit = function(group_data, control_data, passes, substitutions, teachers) {
        app.controller("GroupCtrl", ["$scope", "$rootScope", function($scope, $rootScope) {
            $scope.teachers = teachers;

            $scope.teachers[-1] = {
                id: -1,
                last_name: '--небыло--'
            }

            var substitutions_origin = substitutions;
            $scope.substitutions = _.map(substitutions_origin, _.clone);
            $scope.data = group_data;
            $scope.control_data = control_data;
            $scope.data.group_data.teachers_repr = (function(arr) {
                var res = [];
                for (var i = 0, j = arr.length; i < j; i++) {
                    res.push(arr[i].last_name);
                }

                return res.join('-')

            })($scope.data.group_data.teachers);

            $scope.passes = passes;

            $scope.getProfit = function(val) {
                if (val < 0) {
                    return 'profitbad';
                } else if (val > 0) {
                    return 'profitgood';
                } else {
                    return 'profitnormal';
                }
            };

            function saveStudentData(student, data) {
                student.person.first_name = data.first_name;
                student.person.last_name = data.last_name;
                student.person.phone = data.phone;
                student.person.org = data.org;
                student.just_added = false;

                sendData({
                    person: student.person,
                    group: $scope.data.group_data.id,
                }, 
                'save_student', 
                function(err, resp) {
                    var _alert = window.createWindowAlert();
                    if(err) {
                        _alert.error('Ошибка');
                    } else {
                        _alert.success('Сохранено');
                        student.person.id = resp;
                    }
                });
            }

            $scope.salary = (function(data) {
                var _buf = [];

                function findList(name) {
                    for (var i = 0, j = _buf.length; i < j; i++) {
                        if (_buf[i][0] == name) {
                            return _buf[i];
                        }
                    }

                    return null;
                }

                for (var i = 0, j = data.moneys.length; i < j; i++) {
                    var rec = data.moneys[i];

                    var teachers = Object.keys(rec.salary);
                    for (var k = 0, m = teachers.length; k < m; k++) {

                        var _teacher = teachers[k],
                            teacher_name =  $scope.teachers[_teacher].last_name + ' ' + $scope.teachers[_teacher].first_name,
                            salList = findList(teacher_name);

                        if (!salList) {
                            _buf.push([teacher_name, rec.salary[_teacher]]);
                        } else {
                            salList.push(rec.salary[_teacher]);
                        }
                    }
                }

                return _buf

            })($scope.data);

            $scope.month_sal = _.map(Object.keys($scope.data.money_total.salary), function(obj) {
                return {
                    teacher: $scope.teachers[obj],
                    sal: $scope.data.money_total.salary[obj]
                }
            });

            $scope.cancelLesson = function() {
                var json = {
                    date: $scope.data.calendar[$scope.column].date,
                    group: $scope.data.group_data.id
                };

                if(confirm('Подтвердите отмену занятия')) {
                    sendData(json, 'cancel_lesson', function() {
                        location.reload();
                    });
                }
            }

            $scope.column = null;
            $scope.columnClick = function(index) {
                if ($scope.row == null && !checkAndRestoreLesson()) {
                    if(index != null) {
                        $scope.fillDayPopup(index);
                    }
                    $scope.column = index;
                }
            }

            function checkAndRestoreLesson(index) {
                var lesson = $scope.data.calendar[index];
                
                if(lesson != undefined && lesson.canceled) {
                    if (confirm('Занятие отменено. Восстановить?')) {
                        var json = {
                            date: lesson.date,
                            group: $scope.data.group_data.id
                        }

                        sendData(json, 'restore_lesson', function() {
                            location.reload();
                        }); 
                    }

                    return true;
                }

                return false;
            }

            $scope.hoveredColumn = null;
            $scope.columnIndexCache = function(index) {
                $scope.hoveredColumn = index;
            }

            $scope.hoveredRow = null;
            $scope.rowIndexCache = function(index) {
                $scope.hoveredRow = index;
            }

            $scope.row = null;
            $scope.selected_student = null;

            $scope.rowClick = function(index, student_rec) {
                $scope.new_comment = null;

                if ($scope.column == null) {
                    $scope.row = index;

                    if ($scope.row == null) {
                        return;
                    }

                    $scope.selected_student = student_rec
                    $scope.selected_student = {
                        id: student_rec.person.id,
                        first_name: student_rec.person.first_name,
                        last_name: student_rec.person.last_name,
                        phone: student_rec.person.phone,
                        org: student_rec.person.org,
                        comments: student_rec.comments
                    }

                    $scope.saveStudent = function() {
                        saveStudentData(student_rec, $scope.selected_student);
                    }

                    $scope.saveComment = function() {
                        student_rec.comments.push({
                            add_date: moment().format("DD.MM.YYYY h:mm:ss"),
                            text: $scope.new_comment
                        });

                        $scope.selected_student.comments = student_rec.comments;
                        $scope.new_comment = null;
                    }
                    
                    $scope.editComment = function(comment) {
                        $scope.new_comment = comment;
                    }
                }
            }

        $scope.goMainPage = function() {
            window.location = window.location.origin + '/'
        }
            
        $scope.Comments = {
            showEditor: false,
            isNew: false,
            editedCommentNum: null,
            prevCommentText: null,

            addOrEditComment: function(comment, student, num) {
                this.showEditor = true;
                this.isNew = (comment == null);

                var editedComment;
                
                if(this.isNew) {
                    editedComment = {
                        add_date: moment().format("DD.MM.YYYY h:mm:ss"),
                        text: ''
                    };
                    student.comments.push(editedComment);
                    this.editedCommentNum = student.comments.length - 1;

                } else {
                    editedComment = comment;
                    this.editedCommentNum = num;
                    this.prevCommentText = comment.text;
                }
            },

            showPopover: function(comment, student, index, event) {

                $('body').off('click', '.comment-popover-link');
                $('.coment-text').popover('destroy'); 
                event.stopPropagation();
                
                var editLink = "coment-popover-edit" + index,
                    deleteLink = "coment-popover-delete" + index;

                $('#coment'+index).popover({
                    content: '<div style="text-align: center; width: 90%"><a class="comment-popover-link edit" ng-click=addOrEditComment() href="#">Изменить</>  <a class="comment-popover-link delete" href="#">Удалить</></div>',
                    placement: 'bottom',
                    html: true
                }).popover('show');

                $('body').one('click', function() {
                    $('body').off('click', '.comment-popover-link');
                    $('.coment-text').popover('destroy'); 
                })

                .one('click', '.comment-popover-link', (function (comment, student, index) {
                    return function(event) {
                        var target = $(event.target);
                        
                        if(target.hasClass('edit')) {
                            $scope.$apply(function() {
                                $scope.Comments.addOrEditComment(comment, student, index);
                            });
                        } else if(confirm('Подтвердите удаление коментария')) {
                            $scope.$apply(function() {
                                $scope.Comments.delete(comment, student, index)
                            });
                        }

                        $('body').off('click', '.comment-popover-link');
                    }
                })(comment, student, index))
            },

            save: function(comment, student) {
                var json = {};

                json.cid = comment.pk || null;
                json.type = (this.isNew) ? 'add' : 'edit';
                json.stid = student.id;
                json.grid = $scope.data.group_data.id;
                json.msg = comment.text;

                var _alert = window.createWindowAlert();
                
                sendData(json, 'process_comment', (function(comment, _alert) {
                    return function(err, resp) {
                        $scope.$apply(function() {
                            if(!err) {
                                comment.pk = resp;
                                _alert.success('Коментарий успешно сохранен');
                            } else {
                                _alert.error('Ошибка');
                            }
                        });
                    }
                })(comment, _alert));

                this.isNew = false;
                this.showEditor = false;
                this.editedCommentNum = null;
            },

            delete: function(comment, student, index) {
                if(!comment.pk) {
                    return;
                }

                var json = {};

                json.cid = comment.pk;
                json.type = 'delete';
                json.stid = student.id;
                json.grid = $scope.data.group_data.id;


                var _alert = window.createWindowAlert();

                sendData(json, 'process_comment', (function(student, index, _alert) {

                    return function(err, resp) {
                        if(!err) {
                            $scope.$apply(function() {
                                for(var i=0, j=$scope.data.students.length; i<j; i++) {
                                    var s = $scope.data.students[i];
                                    if(s.person.id == student.id) {
                                        s.comments = s.comments
                                            .slice(0, index)
                                            .concat(s.comments.slice(index+1))
                                        break;
                                    }

                                    $scope.selected_student.comments = $scope.selected_student.comments
                                        .slice(0, index).concat($scope.selected_student.comments.slice(index+1));
                                }
                            });

                            _alert.success('Коментарий успешно удален')
                        } else {
                            _alert.error('Ошибка')
                        }
                    }
                })(student, index, _alert));
            },

            cancel: function(comment, student) {
                if(this.isNew) {
                    student.comments.pop();
                } else {
                    comment.text = this.prevCommentText;
                }

                this.isNew = false;
                this.showEditor = false;
                this.editedCommentNum = null;
            }
        }

            $scope.addOrEditComment = function(comment, student) {

                var editedComment =  (comment == null) ? {} : comment;
            }


            $scope.processPayment = function(lesson, student, is_newbie, day_index) {

                if (lesson.type != 'pass') {
                    var club_card = getClubCard(student);

                    $scope.paymentModal = {
                        student: student, //.person,
                        is_newbie: is_newbie,
                        club_card: club_card
                    }

                    $scope.savePayment = function(pass) {
                        if(student.just_added) {
                            saveStudentData(student, $scope.paymentModal.student.person)
                        }

                        student.just_added = false;

                        var pass_is_club_card = (club_card != undefined && pass.id == club_card.id),
                            is_debt = pass.id == -2,
                            cnt = (is_debt || pass_is_club_card || !pass.oneGroupPass) ? 1 : pass._lessons;
                        
                        for(var i=day_index, j=cnt; i < student.calendar.length && j > 0; i++, j--) {
                            var lesson = student.calendar[i];

                            if(pass_is_club_card) {
                                lesson.pid = club_card.id;
                            }

                            lesson.pass = true;
                            lesson.attended = i == day_index;
                            lesson.color = pass.html_color_class;
                            lesson.type = (pass_is_club_card) ? 'pass' : 'just_added';
                            lesson.pass_type_id = pass.id || pass.pass_type.id;
                            lesson.lessons_cnt = pass._lessons;
                            lesson.skips_cnt = pass._skips;
                            lesson.debt = is_debt;
                            
                            if(lesson.attended) {
                                if(is_debt) {
                                    lesson.sign = 'долг'
                                } else {
                                    var prise1 = pass.prise / pass.lessons,
                                        prise2 = (pass.hasOwnProperty('pass_type')) ? pass.pass_type.prise / pass.pass_type.lessons : 0;

                                    lesson.sign = prise1 || prise2;
                                }

                            } else {
                                lesson.sign = null;
                            }
                        }
                    }
                }
            }

            $scope.fillDayPopup = function(column) {

                $scope.day_popup = { 
                    rows: _.map($scope.data.students, function(student) {
                        return {
                            student: student,
                            day_data: student.calendar[column]
                        }
                    }),

                    teachers: $scope.substitutions[column],
                    day_index: column
                };

                $scope.showDayPopup = true;

            }

            $scope.destroyDayPopup = function() {
                $scope.day_popup = null;
                $scope.showDayPopup = false;
            }

            function getClubCard(student) {
                var searchId = student.person.id;

                for(var i in $scope.data.club_cards) {
                    var card = $scope.data.club_cards[i];
                    if(searchId == card.student.id) {
                        return card
                    }
                }

                return undefined
            }

            function isDebt(id) {
                return id == -2;
            }

            $scope.paymentChange = function(pass) {
                pass._lessons = pass.lessons;
                pass._skips = pass.skips;
            }

            $scope.resetModal = function() {
                $scope.paymentModal = null;
                $scope.selectedPass = null;
            }

            $scope.selectTeacher = function(day_subst, teacherIndex, teacher) {
                day_subst[teacherIndex] = teacher.id;
                $scope.substitutions[$scope.column][teacherIndex] = teacher.id;
            }

            $scope.addStudentFromMain = function() {
                var new_student = getNewStudent(); 
                $scope.data.students.push(new_student);
                $scope.rowClick($scope.data.students.length - 1, new_student);
            }

            $scope.addStudentFromPopup = function(day_index) {
                var new_student = getNewStudent(); 
                $scope.data.students.push(new_student);
                $scope.processPayment(new_student.calendar[day_index], new_student, true, day_index);
            }

            function getNewStudent() {
                var new_student = {
                    calendar: _.map($scope.data.calendar, function() {
                        return {
                            attended: false,
                            canceled: false,
                            color: "",
                            first: false,
                            last: false,
                            pass: false,
                            sign: "",
                            sign_type: ""
                        }
                    }),
                    coments: [],
                    debt: false,
                    is_newbie: true,
                    lessons_count: 0,
                    pass_remaining: 0,
                    person: {
                        first_name: null,
                        last_name: null,
                        phone: null
                    },
                    just_added: true,
                    save: function() {

                    }
                };

                return new_student;
            }

            $scope.deleteStudent = function() {
                var json = {
                    gid: $scope.data.group_data.id,
                    ids: [$scope.data.students[$scope.row].person.id]
                };
                sendData(json, 'delete_student', function(err) {
                    $scope.$apply(function() {
                        var _alert = window.createWindowAlert();

                        if(err) {
                            _alert.error('Ошибка');
                        } else {
                            $scope.data.students = _.union(
                                $scope.data.students.slice(0, $scope.row),
                                $scope.data.students.slice($scope.row + 1)
                            ); 
                            _alert.success('Сохранено');
                            $scope.rowClick(null);
                        }
                    });
                })
            }

            $scope.checkStudents = function() {
                var student = _.last($scope.data.students);
                if (student.hasOwnProperty('just_added') && student.just_added) {
                    $scope.data.students.pop();
                }
            }

            $scope.checkActive = function(student) {
                var any_lesson = _.filter(student.calendar, function(date) {
                    return date.pass || date.debt;
                });
                return any_lesson.length > 0;
            }

            $scope.checkSign = function(sign) {
                var num = parseFloat(sign);
                return (isNaN(num)) ? true : num > 0;
            }

            $scope.setSideBarStatus = function(val) {
                $rootScope.toggleSideBar = val;
            }
            $scope.setSideBarStatus(true);

            $rootScope.$watch(function(obj) {
                return obj.toggleSideBar;
            }, function(val) {
                $scope.toggleSideBar_local = val;
            });

            $scope.getColspan = function(index) {
                return ($scope.toggleSideBar_local && (index==null || index != 0)) ? 1 : 2;
            }

            $scope.saveLessons = function(setMisses, column) {
                var lessons = _.map($scope.data.students, function(student) {
                    var lesson = _.clone(student.calendar[column]);
                    lesson.student_id = student.person.id;

                    return lesson;
                });

                var json = {
                    group_id: $scope.data.group_data.id,
                    date: $scope.data.calendar[column].date,
                    lessons: lessons,
                    setMisses: setMisses,
                    teachers: $scope.substitutions[column]
                }
                sendData(json, 'process_lesson', function() {
                    location.reload();
                });
            }

            $scope.trimComment = function(commentMessage, maxCommentLen) {
                 
                if(commentMessage != undefined && commentMessage.length > maxCommentLen) {
                    return commentMessage.slice(0, maxCommentLen) + ' ...'
                } else {
                    return commentMessage
                }
            }

            function sendData(json, action, callback) {
                $.ajax({
                    method: 'POST',
                    url: '',
                    data: {
                        data: JSON.stringify(json),
                        action: action
                    }
                }).done(function(data) {
                    callback.apply(null, [null, data]);
                }).error(function(error) {
                    callback.apply(null, [error, null]);
                });
            }

            $('body').keydown(function(event) {
                $scope.$apply(function() {
                    if (event.keyCode == 39) {
                        $scope.hoveredColumn = ($scope.hoveredColumn == null) ? 0 : $scope.hoveredColumn + 1;
                        $scope.hoveredColumn = ($scope.hoveredColumn > $scope.data.calendar.length - 1) ? $scope.data.calendar.length - 1 : $scope.hoveredColumn;
                    } else if (event.keyCode == 37) {
                        $scope.hoveredColumn = ($scope.hoveredColumn == null) ? $scope.data.calendar.length - 1 : $scope.hoveredColumn - 1;
                        $scope.hoveredColumn = ($scope.hoveredColumn < 0) ? 0 : $scope.hoveredColumn;
                    } else if (event.keyCode == 13) {
                        if ($scope.hoveredColumn != null) {
                            $scope.column = $scope.hoveredColumn;
                        }
                    } else if (event.keyCode == 27) {
                        $scope.columnClick(null);
                        $scope.rowClick(null);
                    } else {
                    }
                });
            });

            // Show the backdrop
            //$('<div class="modal-backdrop"></div>').appendTo(document.body);

            // Remove it (later)
            //$(".modal-backdrop").remove(); 

        }]);
    }
})();
