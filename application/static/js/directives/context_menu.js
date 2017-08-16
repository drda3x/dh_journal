app.directive('contextMenu', function() {
    return {
        restrict: 'E',

        template: '<div class="context-menu" style="left: {{pose.left}}px; top: {{pose.top}}px">' +
            '<ul>' +
                '<li ng-repeat="item in menuItems">' +
                    '<a href="" ng-click="item.callback()" >{{item.label}}</a>'+
                '</li>' +
            '</ul>' +
            '</div>',
        replace: true,

        scope: {
            menuItems: '=',
            event: '='
        },

        link: function($scope, element, attrs) {
            console.log($scope);

            $scope.pose = {
                left: 0,
                top: 0
            }

            $scope.$watch('event', function(event) {
                if(event != null) {
                    $scope.pose.left = event.clientX;
                    $scope.pose.top = event.clientY;
                }
            })
        }
    }
});
