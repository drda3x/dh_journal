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
window.Factories = (function($) {

  function Tab(input, releaseEvent) {
  this.event = releaseEvent;
  this.$input = $(input);

  //При клике на input тормозим событие...
  this.$input.click(function(event) {
    return false;
  })

  //add release event
    this.$input.on(this.event, $.proxy(function() {
      this.release();
    }, this))
  }

  Tab.prototype.release = function() {};

  function Report(table, name) {
    this.table = $(table);
    this.rows = this.table.find('tr');
    this.needRefresh = false;
    this.controlValue = null;
  }

  // Обновить отчет
  Report.prototype.fullRefresh = function(controlData) {};

  // Добавить одну строку в отчет
  Report.prototype.addRow = function() {};

  // Заблокировать отчет и показать creenSaver
  Report.prototype.lock = function() {};

  // Убрать screenSaver и показать отчет
  Report.prototype.unlock = function() {};

  function Form() {}

  return {
    createTab: function(input, releaseEvent) {
      return new Tab(input, releaseEvent)
    },
    createReport: function() {
      return new Report()
    },
    createForm: function() {
      return new Form()
    }
  }
})($);
