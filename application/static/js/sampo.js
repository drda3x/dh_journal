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

  Tab.prototype.release = function () {
    var newValue = this.$input.val();

    if (newValue != this.value) {
      this.notifyAboutChange(newValue);
    }

    this.value = newValue;
    this.$html.trigger('click');
  };

  Tab.prototype.notifyAboutChange = function (val) {
    for (var i = 0, j = this.reports.length; i < j; i++) {
      this.reports[i].refresh(val);
    }
  };

  Tab.prototype.addListener = function (report) {
    this.reports.push(report);
  };

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

  function Form() {
  }

  // Отправить данные на сервер
  Form.prototype.submit = function () {
  };

  // Проверить форму
  Form.prototype.validate = function () {
  };

  // Очистить форму
  Form.prototype.clear = function() {};


  return {
    createTab: function (input, releaseEvent) {
      return new Tab(input, releaseEvent)
    },
    createReport: function (table, name) {
      return new Report(table, name)
    },
    createForm: function () {
      return new Form()
    }
  }
})(window.jQuery);
