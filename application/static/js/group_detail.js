(function() {
    "use strict";

    app.controller("GroupCtrl", ["$scope", function($scope) {
        $scope.dates = [
            {date: '04.03.2017', profit: 0 },
            {date: '05.03.2017', profit: 1 },
            {date: '11.03.2017', profit: -1},
            {date: '12.03.2017', profit: 0 },
            {date: '18.03.2017', profit: 1 },
            {date: '19.03.2017', profit: 0 },
            {date: '25.03.2017', profit: -1},
            {date: '26.03.2017', profit: 0 }           
        ];

        $scope.students = [
            {
                name: 'Дерендеева Анна', 
                lessons: [
                    null,null,null,null,null,null,null,null
                ] 
            },
            {
                name: 'Закутасов Юрий', 
                lessons: [
                    null,null,null,null,null,null,null,null
                ] 
            }
        ]

        $scope.getProfit = function(val) {
            if(val < 0) {
                return 'profitbad';
            } else if(val > 0) {
                return 'profitgood';
            } else {
                return 'profitnormal';
            }
        };
        
        $scope.column = null;
        $scope.columnClick = function(index) {
            if ($scope.row == null) {
                $scope.column = index;
            }
        }

        $scope.row = null;
        $scope.rowClick = function(index) {
            if ($scope.column == null) {
                $scope.row = index;
            }
        }

        $scope.abc = 112211
    }]); 
})();
