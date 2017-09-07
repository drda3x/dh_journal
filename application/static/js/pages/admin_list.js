(function () {
    "use strict";
    
    function joinArray(arr) {
        var result = [];

        for(var i=0, j=arr.length; i<j; i++) {
            var cur = arr[i];
            result.push(cur);

            if(cur.groups.length > 1) {
                result = result.concat(cur.groups);
            }
        }

        return result
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

    window.pageInit = function(data, groups) {
        app.controller("AdminListCtrl", ["$scope", function($scope) {

            $scope.glued = true;
            $scope.data = data;
            $scope.groups = groups;

            // TEST
            /*
            $scope.data.push({
                student: {
                    first_name: 'Василий',
                    last_name: 'Нестеров',
                    phone: '+7(926) 161-85-59'
                },
                groups: [
                {
                    group: {
                        name: 'Хастл-Начинающие', 
                    },
                    comments: [{
                        text: 'Позвонить летом в среду',
                        date: '25.01.2017 12:00'
                    }]
                },
                {
                    group: {
                        name: 'Растяжка',
                    },
                    comments: [{
                        text: 'Не будет ходить, за чем записался вообще не знает',
                        date: '01.01.2017 12:00'
                    }]
                }
                ]
            });

            $scope.data.push({
                student: {
                    first_name: 'Михаил',
                    last_name: 'Кудрявцев',
                    phone: '+7(926) 161-58-59'
                },
                groups: [
                {
                    group: {
                        name: 'Хастл-Начинающие', 
                    },
                    comments: [{
                        text: 'Говорит, что уже умеет танцевать',
                        date: '01.01.2017 12:00'
                    }]
                },
                {
                    group: {
                        name: 'Растяжка',
                    },
                    comments: [{
                        text: 'Придет тянуть шпагат',
                        date: '01.01.2017 12:00'
                    }]
                }
                ]
            });
            */

            $scope.row = null;
            $scope.rowClick = function(index, event) {
                $scope.blockEvent(event);
                $scope.row = index;
                $scope.contextMenu.close();
            }

            $scope.addRow = function(event) {
                $scope.blockEvent(event);
                $scope.data.push({
                    student: {
                        first_name: null,
                        last_name: null,
                        phone: null 
                    },
                    groups : []
                });

                $scope.rowClick($scope.data.length - 1, event);
            }

            $scope.blockEvent = function(event) {
                event.preventDefault();
                event.stopPropagation();
            }

            $scope.checkTable = function() {
                var result = [];

                for(var i=0, j=$scope.data.length; i<j; i++) {
                    var st = $scope.data[i].student,
                        gr = $scope.data[i].groups;
                    
                    var filled = st.first_name && st.first_name && st.phone;
                    if (filled || gr.length > 0) {
                        result.push($scope.data[i]);
                    }
                }

                $scope.data = result;
            }

            $scope.contextMenu = {
                show: false,
                event: null,
                record: null,
                items: [],

                open: function(record, index, event) {
                    this.show = true;
                    this.event = event;
                    this.record = record;
                    this.record_index = index;
                },

                close: function() {
                    this.show = false;
                }
            }

            $scope.contextMenu.items = [
                {
                    label: 'Перевести', 
                    callback: $.proxy(function() {
                        this.show = false;
                        $scope.moveModal.open(this.record);
                    }, $scope.contextMenu) 
                },{
                    label: 'Удалить',
                    callback: $.proxy(function() {
                        this.show = false;
                        console.log(this.record);
                        if(confirm("Удалить ученика из списков?")) {

                        }
                        

                    }, $scope.contextMenu)
                }
            ];

            $scope.moveModal = {
                show: false,
                data: null,

                open: function(data) {
                    this.data = data;
                    this.show = true;
                },
                
                close: function() {
                    this.show = false;
                },

                toggle: function() {
                    this.show = !this.show;
                },

                save: function(group) {
                    var data = {
                        stid: this.data.student.id,
                        gid: group.id
                    }

                    sendData(data, 
                    'move_student', 
                    function(err, resp) {
                        var _alert = window.createWindowAlert();
                        if(err) {
                            _alert.error('Ошибка');
                        } else {
                            if(confirm("Удалить ученика из списков?")) {
                                for(var i=0, j=$scope.data.length; i<j; i++) {
                                    if ($scope.data[i].student.id == data.stid) {
                                        deleteStudent(data.stid, i, true);
                                        break;
                                    }
                                }
                            }
                            _alert.success('Сохранено');
                        }
                    });

                }
            }

            $scope.deleteStudent = function(stIndex) {
                if(confirm("Уверены, что хотите удалить ученика из этих списков?")) {
                    deleteStudent($scope.data[stIndex].student.id, stIndex)
                }
            }

            function deleteStudent(student, dataIndex, fulldelete) {
                sendData({
                    st_id: student,
                    fulldelete: fulldelete || false
                }, 
                'delete_student', 
                function(err, resp) {
                    var _alert = window.createWindowAlert();
                    if(err) {
                        _alert.error('Ошибка');
                    } else {
                        $scope.$apply(function() {
                            var lp = $scope.data.slice(0, dataIndex),
                                rp = $scope.data.slice(dataIndex+1);

                            $scope.data = lp.concat(rp);
                        });
                        _alert.success('Сохранено');
                    }
                });
            }

            $scope.saveComment = function(record, text, index) {
                record.comments = record.comments || [];

                sendData({
                    st_id: record.student.id,
                    text: text
                }, 
                'save_comment', 
                function(err, resp) {
                    var _alert = window.createWindowAlert();
                    if(err) {
                        _alert.error('Ошибка');
                    } else {
                        $scope.$apply(function() {
                            record.comments.push({
                                'text': text,
                                'add_date': moment().format('DD.MM.YYYY hh:mm')
                            });

                            $scope['comment_' + index] = null;
                        });
                        _alert.success('Сохранено');
                    }
                });
            }

            for(var i=0, j=$scope.data.length; i<j; i++) {
                $scope.data[i].display = true;
            }

            $scope.search_filter = '';
            $scope.$watch('search_filter', function(val) {
                var filtered = [],
                    first_name,
                    last_name,
                    phone;
                
                var p_val = val.replace(/[^0-9]/g, '');                

                for(var i=0, j=$scope.data.length; i<j; i++) {
                    first_name = $scope.data[i].student.first_name;
                    last_name = $scope.data[i].student.last_name; 
                    phone = $scope.data[i].student.phone.replace(/[^0-9]/g, '');

                    if(first_name.indexOf(val) >= 0 || last_name.indexOf(val) >= 0 || (p_val !== '' && phone.indexOf(p_val) >= 0)) {
                        $scope.data[i].display = true;
                    } else {
                        $scope.data[i].display = false;
                    }
                }
            });

            $('body').click(function() {
                $scope.$apply(function() {
                    $scope.row = null;
                    $scope.checkTable();
                });
            });
        }])
    }
})();
