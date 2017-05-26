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

            $scope.column = null;
            $scope.columnClick = function(index) {
                if ($scope.row == null) {
                    $scope.column = index;
                }
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
                        student_rec.person.first_name = $scope.selected_student.first_name;
                        student_rec.person.last_name = $scope.selected_student.last_name;
                        student_rec.person.phone = $scope.selected_student.phone;
                        student_rec.person.org = $scope.selected_student.org;
                        student_rec.just_added = false;
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
                if ($scope.column == null) {
                    return;
                }

                if (lesson.pass) {
                    lesson.attended = !lesson.attended;
                } else {
                    $scope.paymentModal = {
                        student: student, //.person,
                        is_newbie: is_newbie
                    }

                    $scope.savePayment = function(pass) {
                        student.just_added = false;

                        var cnt = pass.lessons;

                        _.map(student.calendar, function(lesson, index) {
                            if (cnt-- > 0 && index >= $scope.column) {
                                lesson.pass = true;
                                lesson.attended = index == $scope.column;
                                lesson.color = pass.html_color_class;
                            }
                        });
                    }
                }
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
                    just_added: true
                };

                $scope.data.students.push(new_student);

                $scope.rowClick($scope.data.students.length - 1, new_student);

                if ($scope.column != null) {
                    $scope.processPayment(new_student.calendar[$scope.column], new_student, true);
                }
            }

            $scope.checkStudents = function() {
                var student = _.last($scope.data.students);
                if (student.hasOwnProperty('just_added') && student.just_added) {
                    $scope.data.students.pop();
                }
            }

            $scope.checkActive = function(student) {
                var any_lesson = _.filter(student.calendar, function(date) {
                    return date.pass
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
                        console.log(event.keyCode);
                    }
                });
            });

        }]);
    }
})();
