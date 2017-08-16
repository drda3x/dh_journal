app.filter('makePositive', function() {
    return function(num) { 
        var _num = parseFloat(num);
        return (isNaN(_num)) ? num : Math.abs(_num); 
    }
});

app.filter('slice', function() {
    return function(arr, start, end) {
        return arr.slice(
                    start || 0, 
                    end || arr.length
                );
    };
});

app.filter('last', function() {
    return function(arr) {
        return _.last(arr);
    }
});

app.filter('first', function() {
    return function(arr) {
        return _.first(arr);
    }
});

app.filter('len', function() {
    return function(arr) {
        if(arr != undefined) {
            return arr.length;
        } else {
            return null;
        }
    }
});
