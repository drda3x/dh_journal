
if(!window.View) window.View = {};

(function() {

    /**
     * Класс 'Матрица'
     */
    function Matrix() {
        this.current_column_num = null;
        this.content = [];

        var rows = $('.table tbody').children();

        for(var i= 0, j=rows.length; i<j; i++) {
            var row=rows[i],
                cells = $(row).children();

            for(var k= 0, m= cells.length; k<m; k++) {
                if (i == 0) this.content[k] = [];
                var cell = $(cells[k]);

                cell.column_index = k;
                cell.attr('data-column', k);

                this.content[k].push(cell);
            }
        }
    }

    /**
     * Получить всю колонку в которую входит переданный элемент
     * @param element
     * @returns {*}
     */
    Matrix.prototype.getColumn = function(element) {
        var $element = $(element),
            column_num = typeof element == 'object' ? $element.data('column') : element;

        return this.content[column_num];
    };

    /**
     * Добавить класс для колонки
     * @param element
     * @param cl
     */
    Matrix.prototype.addClassToColumn = function(element, cl) {

        var column = this.getColumn(element);

        for(var i= 0, j= column.length; i<j; i++) {
            column[i].addClass(cl);
        }
    };

    /**
     * Удалить класс для колонки
     * @param element
     * @param cl
     */
    Matrix.prototype.removeClassFromColumn = function(element, cl) {
        var column = this.getColumn(element);

        for(var i= 0, j= column.length; i<j; i++) {
            column[i].removeClass(cl);
        }
    };

    /**
     * Подсветить колонку
     * @param element
     */
    Matrix.prototype.highlightColumn = function(element) {
        this.addClassToColumn(element, 'highlight')
    };

    /**
     * Убрать подсветку колонки
     * @param element
     */
    Matrix.prototype.unHighlightColumn = function(element) {
        this.removeClassFromColumn(element, 'highlight')
    };

    /**
     * Сделать колонку активной
     * @param element
     */
    Matrix.prototype.makeActive = function(element) {
        this.highlightColumn(element);
        this.addClassToColumn(element, 'active')
    };

    /**
     * Сделать все колонки не активными
     */
    Matrix.prototype.deactivateAll = function() {
        for(var i= this.content.length - 1; i >= 0; i--) {

            var elem = this.content[i][0];

            this.unHighlightColumn(elem);
            this.removeClassFromColumn(elem, 'active')
        }
    };

    window.View.Matrix = Matrix;

})();