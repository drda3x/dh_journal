/**
 * Created by ПК on 20.02.2016.
 */

(function(W) {
    'use strict';

    /**
     * Класс-виджет для работы с таблицей.
     * Содержит всю логику поведения таблицы и предоставления ее данных всем остальным.
     * @param selector
     * @constructor
     */
    function Table(selector) {
        this.$element = $(selector);
        this.rowSelectorClass = '.row-selector';
        this.$rows = [];

        // init functions calling
        this.__updateRowsCache();


        // Events adding
        // Добавляем функционал для выбора всех строк таблицы
        this.$element.click($.proxy(function(event) {
            var $target = $(event.target);

            // Если кликнули в первый инпут - проставляем всем остальным его значение
            // иначе - смотрим, что у всех инпутов, за исключением первого, проставлены галочки. В этом сдучае
            // проставляем галочку у первого инпута...
            if($target.is(this.rowSelectorClass)) {
                if(parseInt($target.val()) < 0) {
                    this.$element.find(this.rowSelectorClass).each(function() {
                        $(this).prop('checked', $target.prop('checked'))
                    });
                } else {
                    var all_checked = true;
                    this.$element.find(this.rowSelectorClass + ':gt(0)').each(function() {
                        all_checked =  !$(this).prop('checked') ? false : all_checked;
                    });
                    this.$element.find(this.rowSelectorClass + ':eq(0)').prop('checked', all_checked);
                }
            }
        }, this));
    }

    /**
     * Добавляем строчку в табличку
     * @param data
     * @returns {Table}
     */
    Table.prototype.addRow = function(data) {
        this.__updateRowsCache();
        return this;
    };

    /**
     * Обновить кеш строк
     * @private
     */
    Table.prototype.__updateRowsCache = function() {
        this.$rows = this.$element.find('tr');
    };

    /**
     * Получить список выбранных пользователем строк таблицы
     */
    Table.prototype.getSelectedRows = function() {
        return $.grep(this.$rows, $.proxy(function(elem, i) {
            return i > 0 && $(elem).find(this.rowSelectorClass).prop('checked');
        }, this))
    };

    W.Table = Table;

})(window);

