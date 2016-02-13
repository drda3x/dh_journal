
(function(jQuery) {
    function isArraylike( obj ) {
        var length = obj.length,
            type = jQuery.type( obj );

        if ( type === "function" || jQuery.isWindow( obj ) ) {
            return false;
        }

        if ( obj.nodeType === 1 && length ) {
            return true;
        }

        return type === "array" || length === 0 ||
            typeof length === "number" && length > 0 && ( length - 1 ) in obj;
    }

    jQuery.fn.all = function(callback, arg) {
        var value,
            i = 0,
            len = this.length,
            isArray = isArraylike(this);

        if (isArray) {
            for (; i < len; i++) {
                if (!callback.call(this[i], i, arg)) {
                    return false;
                }
            }
        } else {
            for (i in this) {
                if (!callback.call(this[i], i, arg)) {
                    return false;
                }
            }
        }

        return true;
    }
})(window.jQuery);
