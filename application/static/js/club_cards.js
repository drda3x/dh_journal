window.ClubCards = {};

window.ClubCards.init = function() {

    $('.modal .groups li').click(function() {

        var $this = $(this),
            $id = $this.data('id');
        $('.modal .students_lists ul').addClass('hide');
        $('.modal .students_lists ul#'+$id).removeClass('hide');
    });

    $('.modal li').click(function() {
        var $this = $(this);
        if($this.parents('.groups').length > 0) {
            $('.modal .students_lists li').removeClass('active');
        }
        $this.siblings().removeClass('active');
        $this.addClass('active');
    });

    var datepicker = $('#multicard-add-menu .datepicker input').datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1
    });

    $('#multicard-add-menu .save_data').click(function() {
        var group = $('.groups').find('.active').first().data('id'),
            student = $('.students_lists').find('.active').first().data('stid'),
            date = datepicker.val();

        $.ajax('createmulty', {
            data: {
                group: group,
                student: student,
                date: date
            }
        }).done(function() {
            window.location.reload();
        }).error(function() {
            console.log('error');
        })
    });

    var pass, student, group;

    $('#all_passes tr').click(function() {

        var $this = $(this);
        pass = $this.data('pid');
        student = $this.data('stid');

        $('#multicard-pass-menu h4').first().text($($this.children()[1]).text());
        $('#multicard-pass-menu .groups li').addClass('hide');
        $('#multicard-pass-menu .groups .s'+student).removeClass('hide');

        $('#multicard-pass-menu').modal('show');

    });

    $('#multicard-pass-menu .groups').click(function(event) {
        var $this = $(event.target);
        group = $this.data('id');

        $('#multicard-pass-menu .dates li').addClass('hide');
        $('#multicard-pass-menu .dates .g'+group+'p'+pass).removeClass('hide');
    });

    $('#multicard-pass-menu').on('hide', function() {
        $('#multicard-pass-menu h4').first().text('');
        $('#multicard-pass-menu .active').removeClass('active');
        $('#multicard-pass-menu .dates li').addClass('hide');
    });

    $('#multicard-pass-menu .save_data').click(function() {
        var $date = $('#multicard-pass-menu .dates .active').text(),
            json = {
                group_id: group,
                date: $date,
                checked: [{
                    pass_id: pass
                }]
            };

        $.ajax('processlesson', {
            data: {
                data: JSON.stringify(json)
            }
        }).done(function() {
            window.location.reload();
        }).error(function(err) {
            console.log(err.responseText);
        });
    });

    $('#multicard-pass-menu .delete_pass').click(function() {
        $.ajax('deletemultypass', {
            data: {
                ids: JSON.stringify([pass])
            }
        }).done(function() {
            window.location.reload();
        }).error(function(err) {
            console.log(err.responseText);
        });
    });

}
