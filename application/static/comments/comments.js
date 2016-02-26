/**
 * This is a comments widget
 */

(function($, w) {

    'use strict';

    // Парсер
    function parse(str) {
        var arr = str.toString().split('\n'),
            res = [];

        for(var i= 0, j= arr.length; i<j; i++) {
          if(arr[i].search('<') >= 0) {
            res.push(arr[i]);
          }
        }

        return res.join('');
    }

    // Шаблон для виджета
    var widget_html_template = $(parse(function () {
        /*
        <div id="commentWidget" class="modal hide fade">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h3 class="ib">Коментарии - <span></span></h3>
            </div>
            <div style="margin: 4px 0 0 170px; z-index: 9999;" class="alert ib"></div>
            <div id="commentWidgetContent"></div>
            <div class="modal-footer">
                <span id="addCommentButtonBlock">
                    <button id="addComment" class="btn btn-primary" style="margin: 5px 0 5px 15px;" class="btn">Добавить</button>
                    <button class="btn" data-dismiss="modal" aria-hidden="true">Закрыть</button>
                </span>
                <span id="saveCommentButtonBlock">
                    <button id="saveComment" class="btn btn-primary" style="margin: 5px 0 5px 15px;" class="btn">Сохранить</button>
                    <button id="saveCommentButtonBlockHide" class="btn">Отмена</button>
                </span>
            </div>
        </div>
         */
    }.toString()));

    var comment_html_template = $(parse(function() {
        /*
        <div class="comment-content">
            <div class="comment-date"></div>
            <div class="comment-buttonsblock">
                <button class="btn btn-mini btn-danger delete-comment">Удалить</button>
                <button class="btn btn-mini edit-comment">Изменить</button>
                <button style="margin-left: 15px; display: none;" class="btn btn-mini cancel-edit-comment">Отмена</button>
                <button class="btn btn-mini save-comment" style="display: none;">Сохранить</button>
            </div>
            <textarea readonly="" maxlength="100"></textarea>
        </div>
        */
    }));

    function Widget() {
        this.html = widget_html_template.clone();
        this.content = this.html.find('#commentWidgetContent');
        this.html.appendTo('body');

        this.html.find('#addComment').click($.proxy(this.createComment, this));
        this.html.on('hidden', $.proxy(this.hide, this));
    }

    Widget.prototype.show = function() {
        this.html.modal('show');
    };

    Widget.prototype.hide = function() {
        this.content.empty();
    };

    Widget.prototype.createComment = function(val) {
        var comment = comment_html_template.clone(),
            editButton = comment.find('.edit-comment'),
            saveButton = comment.find('.save-comment'),
            cancelButton = comment.find('.cancel-edit-comment'),
            deleteButton = comment.find('.delete-comment'),
            textArea = comment.find('textarea'),
            buffer;

        this.content.prepend(comment);

        function editComment() {
            editButton.hide();
            saveButton.show();
            textArea.removeAttr('readonly');
        }

        deleteButton.click(function() {
            comment.remove();
        });

        editButton.click(function() {
            editButton.hide();
            deleteButton.hide();
            saveButton.show();
            cancelButton.show();
            textArea.prop('readonly', false);
            buffer = textArea.val();
        });

        cancelButton.click(function() {
            editButton.show();
            deleteButton.show();
            saveButton.hide();
            cancelButton.hide();
            textArea.prop('readonly', true);
            textArea.val(buffer);
        });

        saveButton.click(function() {
            editButton.show();
            deleteButton.show();
            saveButton.hide();
            cancelButton.hide();
            textArea.prop('readonly', true);
        })
    };

    w.createComment = function() {
        return new Widget();
    }

})(jQuery, window);

