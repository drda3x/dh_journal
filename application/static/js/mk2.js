/**
 * Created by ПК on 20.02.2016.
 */

(function(W) {
    'use strict';

    function Table(selector) {
        this.$element = $(selector);
        this.$rows = this.$element.find('tr');
    }

    Table.prototype.addRow = function(data) {
        return this;
    };


    W.Table = Table;

})(window);

