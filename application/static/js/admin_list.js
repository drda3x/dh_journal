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

    window.pageInit = function(data) {
        app.controller("AdminListCtrl", ["$scope", function($scope) {
            $scope.data = data;

            $scope.row = null;
            $scope.rowClick = function(index, event) {
                $scope.blockEvent(event);
                $scope.row = index;
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

            $('body').click(function() {
                $scope.$apply(function() {
                    $scope.row = null;
                    $scope.checkTable();
                });
            });
        }])
    }
})();
