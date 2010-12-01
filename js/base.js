$(document).ready(function() {

    // making submissions and projects draggable
    $(".submission, .project").draggable({
        stop : function(event, ui) {
            $(this).css({'top' : 0, 'left' : 0})
        }
    })

    // double click to edit
    $(".project").dblclick(function() {
        edit(this)
    })

    // making the containers droppable
    // submission can undo accept and trash
    $("#submission").droppable({
        accept: '.trashed, .accepted',
        drop: function(event, ui) {undo(this, ui)},
        hoverClass : 'submission'
    });
    // trash only takes submission
    $("#trash").droppable({
        accept : '.submission',
        drop: function(event, ui) {trash(this, ui)},
        hoverClass : 'orange'
    });
    // accept takes submission and published (unpublish)
    $("#accept").droppable({
        accept : '.submission, .published',
        drop : function(event, ui) {accept(this, ui)},
        hoverClass : 'green'
    });
    // publish accepted projects
    $("#publish").droppable({
        accept : '.accepted',
        drop : function(event, ui) {publish(this, ui)},
        hoverClass : 'grey'
    });

    // showing more info when mousover
    $(".item").live('mouseover', function() {
            $(this).addClass("hover")})
               .live('mouseout', function () {
            $(this).removeClass("hover")})

    // edit form submission
    $("form#edit").live('submit', function (e) {
        e.preventDefault()
        var container = $(this).parent()
        $.post($(this).attr('action'),
            $(this).serialize(),
            function(result) {
                container.html($(result).children())
                    .removeClass('hover').css({'height' : ''})
        });
    })

    // setting container height dynamically
    container_height()
    $(window).resize(function() { container_height() })
})


// set container height to match html
var container_height = function () {
    $(".container").height($(document).height())
    console.log($(document).height())
}

// get the id (DB) of the draggable
var get_draggable_id = function (draggable) {
    return $(draggable).attr('id').split('-')[1]
}

// snap the item to the container
var snap = function (item, container) {
    item.css({
        'left': 0,
        'top' : 0
    })
    item.appendTo($(container))
}

//
var trash = function(container, ui) {
    var data = {action : 'reject', id_ : get_draggable_id(ui.draggable)}
    $.post('ajax', data, function(result) {
        ui.draggable.addClass('trashed').removeClass('accepted published')
        snap(ui.draggable, container)
    })
}

var accept = function(container, ui) {
    if ($(ui.draggable).hasClass('submission')) {
        var data = {action : 'accept', id_ : get_draggable_id(ui.draggable)}
        $.post('ajax', data, function(result) {
            ui.draggable.addClass('accepted').
                removeClass('trashed published submission').
                addClass('project').attr('id', '#project-' + result).
                dblclick(function () {
                    edit(this)
                    })
            snap(ui.draggable, container)
        })
    } else if ($(ui.draggable).hasClass('published')) {
        var data = {action : 'unpublish', id_ : get_draggable_id(ui.draggable)}
        $.post('ajax', data, function(result) {
            ui.draggable.addClass('accepted').
                removeClass('trashed published submission')
            snap(ui.draggable, container)
        })
    }
}

var publish = function(container, ui) {
    var data = {action : 'publish', id_ : get_draggable_id(ui.draggable)}
    $.post('ajax', data, function(result) {
        ui.draggable.addClass('published').removeClass('trashed accepted')
        snap(ui.draggable, container)
    })
}

var unreject = function(container, ui) {
    var data = {action : 'unreject', id_ : get_draggable_id(ui.draggable)}
    $.post('ajax', data, function(result) {
        ui.draggable.removeClass('trashed accepted').addClass('submission')
        snap(ui.draggable, container)
    })
}

var undo = function(container, ui) {
    if ($(ui.draggable).hasClass('trashed')) {
        var data = {action : 'unreject', id_ : get_draggable_id(ui.draggable)}
        $.post('ajax', data, function(result) {
            ui.draggable.removeClass('trashed').addClass('submission')
            snap(ui.draggable, container)
        })
    } else if ($(ui.draggable).hasClass('accepted')) {
        var data = {action : 'unaccept', id_ : get_draggable_id(ui.draggable)}
        $.post('ajax', data, function(result) {
            ui.draggable.removeClass('accepted').addClass('submission').
                attr('id', '#submission-' + result).unbind('dblclick')
            snap(ui.draggable, container)
        })
    }
}

var edit = function(project) {
    var id = get_draggable_id(project)
    $.get('project/' + id + '/edit', function(result) {
        $(project).html(result).css({'height' : 'auto'})
        $("form a").click(function(e) {
            e.preventDefault()
            $.get($(this).attr('href'),
                function(result) {
                    $(project).html($(result).children())
                        .removeClass('hover').css({'height' : ''})
                })
            })
    })
}

