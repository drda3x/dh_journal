/*

 tab = {
 event: null,
 val: null,
 relise: function() {},
 notify: function() {}
 }

 report = {
 refresh: function() {},
 needRefresh: function() {},
 data: null
 }

 form = {
 controlData: tab.val,
 setControl: function() {},
 _validate: function() {},
 submit: function() {}
 }

 */
window.Factories = (function ($) {
  /**
   *  Класс для работы с закладкладкой на странице
   *  Служит для реализации логики контрола и раздает отчетам комманду на об-
   *  новление.
   */
  function Tab(html, releaseEvent) {
    this.$html = $(html);
    this.event = releaseEvent;
    this.$input = this.$html.find('.control');
    this.reports = [];
    this.value = this.$input.val();

    //При клике на input тормозим событие...
    this.$input.click(function (event) {
      return false;
    });

    //add release event
    this.$input.on(this.event, $.proxy(function () {
      this.release();
    }, this))
  }
  
  // Обработчик события-продолжения, которое наступает после изменения зна-
  // чения контрола.
  Tab.prototype.release = function () {
    var newValue = this.$input.val();

    if (newValue != this.value) {
      this.notifyAboutChange(newValue);
    }

    this.value = newValue;
    this.$html.trigger('click');
  };

  // Обойти все отчеты, в закладке и передать комманду на обновление
  Tab.prototype.notifyAboutChange = function (val) {
    for (var i = 0, j = this.reports.length; i < j; i++) {
      this.reports[i].refresh(val);
    }
  };

  // Подписать новый отчет
  Tab.prototype.addListener = function (report) {
    this.reports.push(report);
  };

  /**
   * Класс для работы с отчетами на странице
   * Реализует:
   * 1. Обновление отчета
   * 2. Добавление/удаление строк
   * 3. Блокировку/разблокировку отчета
   */
  function Report(table, name) {
    this.table = $(table);
    this.rows = this.table.find('tr');
    this.needRefresh = false;
    this.controlValue = null;
  }

  // Обновить отчет
  Report.prototype.refresh = function (controlData) {
    console.log('refresh');
  };

  // Добавить одну строку в отчет
  Report.prototype.addRow = function () {
  };

  // Заблокировать отчет и показать screenSaver
  Report.prototype.lock = function () {
  };

  // Убрать screenSaver и показать отчет
  Report.prototype.unlock = function () {
  };

  /**
   * Класс для работы с формами страницы
   * 1. Отправка формы
   * 2. Проверка формы
   * 3. Очистка формы
   */
  function Form(selector) {
      this.html = $(selector);
      this.data = {};
      this.formParams = this.html.data();

      // Наполняем объект data
      $.map(this.html.find('input'), $.proxy(function(input) {
          Object.defineProperty(
              this.data, 
              $(input).prop('name'), 
              (function($input) {
                return {
                    get: function() {
                      return $input.val()
                    },
                    set: function(val) {
                      $input.val(val); 
                    }
                }
 
              })($(input))
          )  
      }, this));
  }

  // Отправить данные на сервер
  Form.prototype.submit = function () {
      $.ajax(
          
      );
  };

  // Проверить форму
  Form.prototype.validate = function () {
  };

  // Очистить форму
  Form.prototype.clear = function() {
    for(key in this.data) {
      this.data[key] = "";
    }
  };


  return {
    createTab: function (input, releaseEvent) {
      return new Tab(input, releaseEvent)
    },
    createReport: function (table, name) {
      return new Report(table, name)
    },
    createForm: function (form) {
      return new Form(form);
    }
  }
})(window.jQuery);
