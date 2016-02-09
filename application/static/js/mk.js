(function(w, $) {

    'use-strict';

	function sendRequest() {}

	function MyPopover(stId, htmlContent) {
		/**
		Класс для задания поведения поповеров которые отвечают за добавление/удаление абонементов
		Создается при клике на ссылку далее происходит следующее:
			!!!! Поповер на добавление
			1. Инициализируется класс (во внутрь передается id ученика)
			2. Нажимается кнопка "Внести"
			3. Вместо формы появляется скринсейвер
			4. Выполняется обход формы и отправка данных
			5. Получается и обрабатывается ответ
			6. В ячейке таблицы заменяется "Добавить" на текст группы
			7. В случае положительного ответа показыватся сообщение для пользователя и уничтожается объект

			!!! Поповер на удаление
			1. Инициализируется класс (во внутрь передается id ученика и id группы в которую куплен абонемент)
			2. Нажимается кнопка "Удалить"
			3. Отправляется запрос на сервер
			4. Показывается скринсейвер
			5. В случае положительного ответа показывается сообщение "Удалено"
			6. Текст группы меняется на "Добавить"
			
			Реализовывать через базовый класс и наследников
		*/
        this.studentId = stId;
        this.html = htmlContent;
        this.html.$tip.find('button').click($.proxy(this.submit, this));
	}

    MyPopover.prototype.submit = function() {
        console.log('submit');
    };

    MyPopover.prototype.destroy = function() {
        this.html.destroy();
    };

	w.onload = function() {
		$('a.add').popover({
			content: $(
				'<div id="popoverContent">'+
					'<select>'+
						'<option>Начинающие Третьяковская</option>'+
						'<option>Начинающие Волгоградский проспект</option>'+
						'<option>Начинающие Краснопресненская</option>'+
					'</select>'+
					'<button>Внести</button>'+
				'</div>'
			).html(),
			html: true,
			trigger: 'manual',
			placement: 'bottom'
		});

        $('body').click(function(event) {
            $target = $(event.target),
            $this = $(this);

            if($target.is('.add')) {
                $target.popover('show');
                $this.data('popover', new MyPopover(11, $target.data('popover')));
            } else if(!$target.is('.popover') && !$($target.parentsUntil('td').toArray().pop()).is('.popover') ) {
                var p = $this.data('popover');
                p.destroy();
            }
        });
	}

})(window, window.jQuery);