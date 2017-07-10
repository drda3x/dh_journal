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

                }
            }


            $scope.processPayment = function(lesson, student, is_newbie) {
                /* 
                if ($scope.column == null) {
                    return;
                }
                */

                if (lesson.type == 'pass') {
                    lesson.attended = !lesson.attended;
                } else {
                    var club_card = null;//getClubCard(student);

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

                        var pass_is_club_card = club_card != undefined && pass.id == club_card.id,
                            is_debt = pass.id == -2,
                            cnt = (is_debt || pass_is_club_card) ? 1 : pass.lessons;

                        _.map(student.calendar, function(lesson, index) {
                            if (cnt > 0 && index >= $scope.column) {

                                if(pass_is_club_card) {
                                    lesson.pid = club_card.id;
                                }

                                lesson.pass = true;
                                lesson.attended = index == $scope.column;
                                lesson.color = pass.html_color_class;
                                lesson.type = (pass_is_club_card) ? 'pass' : 'just_added';
                                lesson.pass_type_id = pass.id || pass.pass_type.id;
                                lesson.lessons_cnt = pass._lessons;
                                lesson.skips_cnt = pass._skips;
                                lesson.debt = is_debt;
                                lesson.sign = (is_debt) ? 'долг' : (pass.prise / pass.lessons) || (pass.pass_type.prise / pass.pass_type.lessons);

                                cnt--;
                            }
                        });
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

                    teachers: $scope.substitutions[column]
                }

                $scope.showBackDrop = true;

            }

            $scope.fillDayPopup(0);

            function checkClubCard(student) {
                var has_club_card = _.find($scope.data.club_cards, function(card) {
                        return card.student.first_name == student.person.first_name && card.student.last_name == student.person.last_name
                    }) != undefined;

                return has_club_card;
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

            $scope.addStudent = function() {
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

                $scope.data.students.push(new_student);

                $scope.rowClick($scope.data.students.length - 1, new_student);

                if ($scope.column != null) {
                    $scope.processPayment(new_student.calendar[$scope.column], new_student, true);
                }
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

            $scope.saveLessons = function(setMisses) {
                var lessons = _.map($scope.data.students, function(student) {
                    var lesson = _.clone(student.calendar[$scope.column]);
                    lesson.student_id = student.person.id;

                    return lesson;
                });

                var json = {
                    group_id: $scope.data.group_data.id,
                    date: $scope.data.calendar[$scope.column].date,
                    lessons: lessons,
                    teachers: $scope.substitutions[$scope.column],
                    setMisses: setMisses,
                    teachers: $scope.substitutions[$scope.column]
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
