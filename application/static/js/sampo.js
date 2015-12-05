/**
 * Created by dispatcher on 21.11.2015.
 */

window.sampoLogic = (function () {

  var fadeOutParam = 250;

  function is_backspase(val) {
    return val.toLowerCase() == 'backspace'
  }

  function addZero(val) {
    return ('0' + val).slice(-2);
  }

  function showAddPassForm() {
    $('.to_fd').fadeOut(fadeOutParam, function() {
        $('#addSampoPass').fadeIn(fadeOutParam);
      });
  }

  function hideAddPassForm() {
    $('#addSampoPass').fadeOut(fadeOutParam, function() {
        $('.to_fd').fadeIn(fadeOutParam);
      });
  }

  function addClockBehavior() {
    var input_time = $('input.time');

    input_time.keypress(function(event) {
      var key, val, go_back;
      key = event.key;
      go_back = is_backspase(key);

      if(!go_back && isNaN(parseInt(key))) {
        return false;
      }

      val = $(this).val() + (go_back ? '' : key);

      if(val.length > 5 && !go_back) {
        return false;
      } else if(val.length == 4 && go_back) {
        $(this).val(val.slice(0, -1));
      } else if (val.length == 3 && !go_back) {
        $(this).val($(this).val() + ':');
      }
    });

    input_time.keyup(function(event) {
      var arr, hours, minutes, val;
      val = $(this).val();
      arr = val.split(':');
      hours = (arr.length > 0) ? parseInt(arr[0]) : NaN;
      minutes = (arr.length > 1) ? parseInt(arr[1]) : NaN;

      if(hours > 9) {
        arr[0] = (hours <= 23) ? hours : 23;
      }

      if(minutes > 9) {
        arr[1] = (minutes <= 59) ? minutes : 59;
      }

      $(this).val(arr.join(':'));

    });

    input_time.focus(function() {
      $(this).val('');
      StopAutoUpd();
    });

    var timeInt, now;
    function updateTimes() {
      now = new Date();
      input_time.val(addZero(now.getHours()) + ':' + addZero(now.getMinutes()) );
    }

    function StartAutoUpd() {
      timeInt = setInterval(updateTimes, 500);
    }

    function StopAutoUpd() {
      clearInterval(timeInt);
      setTimeout(StartAutoUpd, 30000)
    }

    StartAutoUpd();
  }

  function getFormData(button) {

    var data = {};
    data.info = {};

    var $form = $('.money-action:visible');
    $form.find('input').each(function () {
      data.info[$(this).attr('name')] = $(this).val();
    });

    return data;
  }

  function sendRequest(options, successCallBack, errorCallBack, context) {
    $.ajax('/sampo', {
        data: options
      })
      .success((function(context) {

            return function(data) {
                if(context != undefined) {
                    successCallBack(data, context);
                } else {
                    successCallBack(data);
                }
            }

        })(context))
      .error(errorCallBack);
  }

  function errorProcess() {}

  function successProcess(json, data) {
    if(json != undefined) {
        var response = JSON.parse(json);

        if(response.hasOwnProperty('pid')) {
            refreshPassList(response.pid, data.info.name, data.info.surname)
        }

        if(response.hasOwnProperty('payments')) {
            refreshTable(response.payments)
        }
    }
  }

    /**
     * Обновляшка для таблички журнала
     */
    function refreshTable(data) {
        var html_container = $('#payments tbody'),
            info = {};

        html_container.empty();

        for(var i= 0, j= data.length; i<j; i++) {
          info = data[i].info;

          var comment = (info.hasOwnProperty('comment')) ? '<div class="muted">'+info.comment+'</div>' : '';

          $('<tr>' +
            '<td>' + data[i].date + '</td>' +
            '<td class="' + info.type + '">' +
              '<div class="row-fluid">' +
                '<div class="span10">' +
                  info.payment + comment +
                '</div>' +
                '<div class="span1 minus">' +
                  '<span class="text-error">-</span>' +
                '</div>' +
              '</div>' +
            '</td>' +
            '</tr>'
          ).appendTo(html_container);
        }
    }

    /**
     * Обновляшка для списка абонементов
     */
    function refreshPassList(id, name, surname) {
        $('#sampo_passes').append(
             '<li><label class="inline checkbox">' +
             '<input type="checkbox" value="'+ id +'">' + surname +' '+ name +
             '</label></li>'
          );
    }

  function addSearchBehavior() {
    var buffer;

    function refreshBuffer() {
      buffer = {};
      $('#sampo_passes li').each(function () {
        var val = $(this).text().replace(/\s/g, '').toLowerCase();
        buffer[val] = $(this);
      });
    }

    refreshBuffer();

    $('#prependedInput').keyup(function() {
      var curval = $(this).val().toLowerCase(),
          re = new RegExp(curval);

      for(var name in buffer) {
        if(name.search(re) > -1) {
          buffer[name].show();
        } else {
          buffer[name].hide();
        }
      }
    });
  }

  function clearForms() {
      $('input').val('');
    }

  function init() {
    $('#addButton').click(function() {
      showAddPassForm();
    });

    $('#cancelButton').click(function() {
      hideAddPassForm();
      return false;
    });

    addClockBehavior();
    addSearchBehavior();

    $('.submitBtn').click(function (event) {
      event.stopPropagation();
      var $this = $(this),
          data = getFormData($this),
          type;

      if($this.hasClass('btn1')) {
        type = 'cash-add'
      } else if($this.hasClass('btn2')) {
        type = 'cash-wrt'
      } else if($this.hasClass('btn3')) {
        type = 'pass'
      } else {
        console.log('Wrong submit type');
        return;
      }

      clearForms();
      sendRequest({
        action: 'add',
        type: type,
        data: JSON.stringify(data)
      }, successProcess, errorProcess, data);

      hideAddPassForm();

      return false
    });

    $('#sampo_passes li').change(function(event) {

      var confirm_msg = $(this).find('label').text().replace(/^\s*/, ''),
          input = $(this).find('input'),
          action;

      if(!input.is(':checked')) {
        confirm_msg += '\nСнять отметку о посещении?';
        action = 'uncheck'
      } else {
        confirm_msg += '\nОтметить абонемент?';
        action = 'check'
      }

      if(confirm(confirm_msg)) {
        sendRequest({
          action: action,
          pid: input.val(),
          time: $('#addSampoPass #inputTime').val()
        }, successProcess, errorProcess);
      }
    });
  }

  return init;
})();
