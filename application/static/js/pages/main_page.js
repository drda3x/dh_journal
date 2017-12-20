
window.sideBarInit = function(menuData, group_id) {
    app.controller("sideBarCtrl", ["$scope", "$rootScope", "$sce", function($scope, $rootScope, $sce) {
        $scope.sidebar_menu = processSideBarHeader(menuData);
        $scope.current_group = parseInt(group_id);

        $scope.isActive = (function() {
            var current_group = '' + group_id;

            return function(elem) {
                if (elem.hasOwnProperty('url') && elem.url != undefined && elem.url.match(/[0-9]+/, '') == current_group) {
                    return true
                } else {
                    return false
                }
            }
        })();

        $scope.isAnyPageOpened = (function() {
            for(var i in $scope.sidebar_menu) {
                if($scope.isActive($scope.sidebar_menu[i])) {
                    return true;
                }
            }

            return false;
        })();

        $scope.isHeader = function(elem) {
            return elem.type == 'header';
        }

        $scope.calcClasses = function(elem) {
            var classes = [];

            if ($scope.isHeader(elem)) {
                classes.push('nav-header');
            }

            if ($scope.isActive(elem)) {
                classes.push('active');
            }
            
            return classes;
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
        
        var hidden = localStorage.getItem('hidden_menu'); 
        
        if(hidden == null) {
            hidden = _.map($scope.sidebar_menu, function(elem, index) {
                return (elem.hideable && elem.type == "header") ? index : null;
            });
        } else {
            hidden = _.map(hidden.split(','), function(elem) {
                return parseInt(elem);
            });
        }

        $scope.hidden = _.filter(hidden, function(elem) {
            return elem != null;
        });
        $scope.hideMenuPart = function(index) {
            $scope.hidden.push(index);
            localStorage.setItem('hidden_menu', $scope.hidden.toString());
            for(var i=index+1, j=$scope.sidebar_menu.length; i<j; i++) {
                if ($scope.sidebar_menu[i].type == 'header') {
                    break;
                }

                $scope.sidebar_menu[i].show = false;
            }
        };

        $scope.showMenuPart = function(index) {
            $scope.hidden = _.without($scope.hidden, index);
            localStorage.setItem('hidden_menu', $scope.hidden.toString());
            for(var i=index+1, j=$scope.sidebar_menu.length; i<j; i++) {
                if ($scope.sidebar_menu[i].type == 'header') {
                    break;
                }

                $scope.sidebar_menu[i].show = true;
            }
        };

        $scope.toggleMenuPart = function(index) {
            if(_.indexOf($scope.hidden, index) > -1) {
                $scope.showMenuPart(index);
            } else {
                $scope.hideMenuPart(index);
            }
        }

        $scope.checkIndex = function(index) {
            return $scope.hidden.indexOf(index) >= 0;
        }

        function processSideBarHeader(menuData) {
            var result = [];

            for (var i=0, j=menuData.length; i<j; i++) {
                var elem = menuData[i];
                result.push({label: elem.label, type: 'header', hideable: elem.hideable, show: true});

                for (var k=0, l=elem.urls.length; k<l; k++) {
                    var urlElem = elem.urls[k];
                    if (urlElem.hasOwnProperty('type') && urlElem.type=="urls") {
                        result = result.concat(processSideBarHeader([urlElem]));
                    } else {
                        var label;
                        
                        try {
                            label = urlElem.name+"<br>"+urlElem.dance_hall.station+"<br>"+urlElem.days+" "+urlElem.time;
                            if(urlElem.show_st) {
                                label = 'с ' + urlElem.start_date + '<br>' + label;
                            }
                        } catch(e) {
                            label = urlElem.label;
                        }

                        result.push({
                            label: $sce.trustAsHtml(label),
                            url: urlElem.url, 
                            type: 'link', 
                            show: !elem.hideable,
                            profit: urlElem.profit
                        })
                        console.log(urlElem.profit);
                    }
                }
            }

            return result;
        }
        
        _.map($scope.sidebar_menu, function(elem, index) {
            if(elem.type == 'header' && !$scope.checkIndex(index)) {
                $scope.showMenuPart(index);
            }
        });

    }]);
}
