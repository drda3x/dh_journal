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

  //add release event
    this.$input.on(this.event, $.proxy(function() {
      this.release();
    }, this))
  }

  Tab.prototype.release = function() {};

  function Report() {}

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
