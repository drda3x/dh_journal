/**
 * Created by dispatcher on 21.11.2015.
 */

window.sampoLogic = (function () {

  var fadeOutParam = 250;

  function init() {
    $('#addButton').click(function() {
      $('.to_fd').fadeOut(fadeOutParam, function() {
        $('#addSampoPass').fadeIn(fadeOutParam);
      });
    });

    $('#cancelButton').click(function() {
      $('#addSampoPass').fadeOut(fadeOutParam, function() {
        $('.to_fd').fadeIn(fadeOutParam);
      });

      return false;
    });
  }

  return init;
})();
