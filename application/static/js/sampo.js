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

  function init() {
    $('#addButton').click(function() {
      showAddPassForm();
    });

    $('#cancelButton').click(function() {
      hideAddPassForm();
      return false;
    });

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

    function clearForms() {
      $('input').val('');
    }

    $('.submitBtn').click(function (event) {

      event.stopPropagation();

      var data = {};

      if($(this).hasClass('btn2')) {
        data.passes = {};

        $('#addSampoPass input').each(function() {
          data.passes[$(this).attr('name')] = $(this).val();
        });
      } else {
        data.payments = {};
        $('#cash-payment input').each(function() {
          data.payments[$(this).attr('name')] = $(this).val();
        });
      }

      clearForms();

      $.ajax('/sampo', {
        data: {
          action: 'add',
          data :JSON.stringify(data)
        }
      }).success(function(json) {
          if(json != undefined) {
            var response = JSON.parse(json);

            $('#sampo_passes').append(
               '<li><label class="inline checkbox">' +
               '<input type="checkbox" value="'+ response.pid +'">' + data.passes.surname +' '+ data.passes.name +
               '</label></li>'
            );

            refreshBuffer();
            hideAddPassForm();
          }
      });

      return false
    });

    $('#sampo_passes li').click(function(event) {

      event.preventDefault();

      var confirm_msg = $(this).find('label').text().replace(/^\s*/, ''),
          input = $(this).find('input'),
          action;

      if(input.is(':checked')) {
        confirm_msg += '\nСнять отметку о посещении?';
        input.removeAttr('checked');
        action = 'uncheck'
      } else {
        confirm_msg += '\nОтметить абонемент?';
        input.prop('checked', true);
        action = 'check'
      }

      if(confirm(confirm_msg)) {
        $.ajax('/sampo', {
          data: {
            action: action,
            pid: input.val()
          }
        }).success(function (json) {

        });
      }
    });
  }

  return init;
})();
