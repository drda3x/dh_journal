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
        this.header = this.html.find('h3');
        this.content = this.html.find('#commentWidgetContent');
        this.html.appendTo('body');

        this.addButtons = this.html.find('#addCommentButtonBlock');
        this.editButtons = this.html.find('#saveCommentButtonBlock');

        this.addButton = this.html.find('#addComment');
        this.closeButton = this.html.find('#closeComment');
        this.saveButton = this.html.find('#saveComment');
        this.cancelButton = this.html.find('#cancelButton');

        this.allComments = [];

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
            newComment.saveButton.trigger('click');
            this.allComments.unshift(newComment);
            this.setAddState();
            newComment = undefined;
        }, this));

        this.cancelButton.click($.proxy(function() {
            if(newComment.text == '') {
                newComment.remove();
            } else {
                newComment.readOnly(true);
            }
            this.setAddState();
            newComment = undefined;
        }, this))

        this.html.on('hidden', $.proxy(this.hide, this));
        $(document).on('ctrl_enter_pressed', $.proxy(function() {
            if(newComment) {
                this.saveButton.trigger('click');
            }
            this.setAddState();
        }, this));
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
        var comment, buff;
        for(var i= 0, j= this.allComments.length; i<j; i++) {

            if(this.allComments[i] instanceof Comment) {
                this.allComments[i].show();
            } else {
                buff = this.allComments[i];
                comment = this.createComment();
                comment.text = buff.text;
                comment.date = new Date(buff.date);
                this.allComments[i] = comment;
            }
        }

        this.html.modal('show');
    };

    Widget.prototype.hide = function() {
        $.map(this.allComments, $.proxy(function(elem, i) {
            if(elem.deleted) {
                delete this.allComments[i];
            }
        }, this));
        this.content.children().hide();
        this.setAddState();
        $(document).trigger('comment-save');
    };

    Widget.prototype.setHeader = function(newHeader) {
        this.header.text(newHeader);
    };

    Widget.prototype.createComment = function() {
        return new Comment(this.content);
    };


    function Comment(container) {
        this.html = comment_html_template.clone();
        this.editButton = this.html.find('.edit-comment');
        this.saveButton = this.html.find('.save-comment');
        this.cancelButton = this.html.find('.cancel-edit-comment');
        this.deleteButton = this.html.find('.delete-comment');
        this.textArea = this.html.find('textarea');
        this.date_html = this.html.find('.comment-date');
        this.deleted = false;

        this.__defineGetter__('text', $.proxy(function() {
            return this.textArea.val();
        }, this));

        this.__defineSetter__('text', $.proxy(function(val) {
            this.textArea.val(val);
        }, this));

        this.__defineGetter__('date', $.proxy(function() {
            return this.date_html.text();
        }, this));

        this.__defineSetter__('date', $.proxy(function(newDate) {
            this.date_html.text(addZero(newDate.getDate()) + '.' + addZero(newDate.getMonth() + 1) + '.' + newDate.getFullYear()  + ' ' + addZero(newDate.getHours()) + ':' + addZero(newDate.getMinutes()))
        }, this));

        this.date = new Date();

        var buffer;

        this.editButton.click($.proxy(function() {
            this.editButton.hide();
            this.deleteButton.hide();
            this.saveButton.show();
            this.cancelButton.show();
            this.readOnly(false);
            this.focus();
            buffer = this.text;
        }, this));

        this.cancelButton.click($.proxy(function() {
            this.editButton.show();
            this.deleteButton.show();
            this.saveButton.hide();
            this.cancelButton.hide();
            console.log(buffer);
            this.text = buffer;
            this.readOnly(true);
        }, this));

        this.saveButton.click($.proxy(function() {
            this.editButton.show();
            this.deleteButton.show();
            this.saveButton.hide();
            this.cancelButton.hide();
            this.readOnly(true);
        }, this));

        this.deleteButton.click($.proxy(function() {
            this.deleted = true;
            this.html.remove();
        }, this));

        this.textArea.keydown($.proxy(function(e) {
            if(e.ctrlKey && e.keyCode === 13) {
                this.saveButton.trigger('click');
                $(document).trigger('ctrl_enter_pressed');
            }
        }, this));

        this.appendTo(container);
    }

    Comment.prototype.remove = function() {
        this.html.remove();

        
    }

    Comment.prototype.show = function() {
        this.html.show();
    }

    Comment.prototype.appendTo = function(container) {
        container.prepend(this.html);
        return this;
    }

    Comment.prototype.readOnly = function(val) {
        this.textArea.prop('readonly', val);
    }

    Comment.prototype.focus = function() {
        this.textArea.focus();
    }

    w.createComment = function() {
        return new Widget();
    }

})(jQuery, window);

