/**
 * This is a comments widget
 */

(function($, w) {

    'use strict';

    function addZero(n) {
        return ('0' + n).slice(-2);
    }

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
                <h3 class="ib">Коментарии</h3>
            </div>
            <div style="margin: 4px 0 0 170px; z-index: 9999; display:none;" class="alert ib"></div>
            <div id="commentWidgetContent"></div>
            <div class="modal-footer">
                <span id="addCommentButtonBlock">
                    <button id="addComment" class="btn btn-primary" style="margin: 5px 0 5px 15px;" class="btn">Добавить</button>
                    <button id="closeComment" class="btn" data-dismiss="modal" aria-hidden="true">Закрыть</button>
                </span>
                <span id="saveCommentButtonBlock">
                    <button id="saveComment" class="btn btn-primary" style="margin: 5px 0 5px 15px;" class="btn" rel="tooltip" title="сохранять можно через Ctrl+Enter">Сохранить</button>
                    <button id="cancelButton" class="btn">Отмена</button>
                </span>
            </div>
        </div>
         */
    }.toString()));

    var comment_html_template = $(parse(function() {
        /*
        <div class="comment-content">
            <div class="comment-date">27.02.2016 13:23</div>
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
        this.header = this.html.find('h3');
        this.content = this.html.find('#commentWidgetContent');
        this.html.appendTo('body');

        this.addButtons = this.html.find('#addCommentButtonBlock');
        this.editButtons = this.html.find('#saveCommentButtonBlock');

        this.addButton = this.html.find('#addComment');
        this.closeButton = this.html.find('#closeComment');
        this.saveButton = this.html.find('#saveComment');
        this.cancelButton = this.html.find('#cancelButton');

        var newComment;

        this.addButton.click($.proxy(function() {
            newComment = this.createComment();
            newComment.saveButton.hide();
            newComment.cancelButton.hide();
            newComment.editButton.hide();
            newComment.deleteButton.hide();
            newComment.readOnly(false);
            newComment.focus();

            this.setEditState();
        }, this));

        this.saveButton.click($.proxy(function() {
            newComment.readOnly(true);
            newComment.editButton.show();
            newComment.deleteButton.show();

            this.setAddState();
        }, this));

        this.cancelButton.click($.proxy(this.setAddState, this));

        this.html.on('hidden', $.proxy(this.hide, this));
    }

    Widget.prototype.setEditState = function() {
        this.addButtons.hide();
        this.editButtons.show();
    };

    Widget.prototype.setAddState = function() {
        this.addButtons.show();
        this.editButtons.hide();
    };

    Widget.prototype.show = function() {
        this.html.modal('show');
    };

    Widget.prototype.hide = function() {
        this.content.empty();
    };

    Widget.prototype.setHeader = function(newHeader) {
        this.header.text(newHeader);
    };

    Widget.prototype.createComment = function() {
        var comment = comment_html_template.clone(),
            editButton = comment.find('.edit-comment'),
            saveButton = comment.find('.save-comment'),
            cancelButton = comment.find('.cancel-edit-comment'),
            deleteButton = comment.find('.delete-comment'),
            textArea = comment.find('textarea'),
            date = comment.find('.comment-date'),
            buffer;

        this.content.prepend(comment);

        editButton.click(function() {
            editButton.hide();
            deleteButton.hide();
            saveButton.show();
            cancelButton.show();
            textArea.prop('readonly', false);
            textArea.focus();
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
        });

        deleteButton.click(function() {
            comment.remove();
        });

        textArea.keydown($.proxy(function(e) {
            if(e.ctrlKey && e.keyCode === 13) {
                saveButton.trigger('click');
                this.setAddState();
            }
        }, this));

        comment.saveButton = saveButton;
        comment.cancelButton = cancelButton;
        comment.editButton = editButton;
        comment.deleteButton = deleteButton;

        comment.text = function(newText) {
            textArea.text(newText);
        };

        comment.date = function(newDate) {
            if(newDate == undefined) {
                date.text()
            } else {
                date.text(addZero(newDate.getDate()) + '.' + addZero(newDate.getMonth() + 1) + '.' + newDate.getFullYear()  + ' ' + addZero(newDate.getHours()) + ':' + addZero(newDate.getMinutes()))
            }
        };

        comment.readOnly = function(val) {
            textArea.prop('readonly', val);
        };

        comment.focus = function() {
            textArea.focus();
        };

        return comment;
    };


    w.createComment = function() {
        return new Widget();
    }

})(jQuery, window);

