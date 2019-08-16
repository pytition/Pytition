{% load i18n %}

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(function () {
   $('[data-action="template-delete"]').on("click", function() {
    var template_delete_url = $(this).closest("[data-template-delete]").data("template-delete");
    $.ajax(template_delete_url).done(function() {
       if (window.location.href.endsWith('/edit')) {
           // If we were on this template edit page and the user clicks on delete
           // we cannot reload the edit page, we then reload the dashboard
           window.location = "{{ dashboard }}";
       } else
           window.location = window.location.href;
    });
   });
});

function do_toggle_template_picture(template) {
    if (template.prop("class").includes("text-warning"))
        template.removeClass("text-warning").addClass("text-dark");
    else
        template.removeClass("text-dark").addClass("text-warning");
}

$(function () {
    $('[data-fav-toggle="true"]').on("click", function () {
        var template_fav_url = $(this).closest("[data-template-fav]").data("template-fav");
        var template = $(this);
        $.ajax(template_fav_url).done(function() {
            var hash = document.location.hash;
            if (hash)
                do_toggle_template_picture(template);
            else
                window.location = window.location.href;
        });
    });
});

$(function () {
   $('[data-action="petition-delete"]').on("click", function() {
    var petition_delete_url = $(this).closest("[data-petition-delete]").data("petition-delete");
    $.ajax(petition_delete_url).done(function() {
           window.location = window.location.href;
    });
   });
});

$(function () {
   $('[data-action="publish"]').find('input:checkbox').on("change", function() {
    var petition_publish_url = $(this).closest("[data-petition-publish]").data("petition-publish");
    var petition_unpublish_url = $(this).closest("[data-petition-unpublish]").data("petition-unpublish");
    var box = $(this);
    var checked = box.prop('checked');
    var label = box.siblings('label');
    var custom_switch = box.closest('.custom-switch');
    box.prop('disabled', true);
    if (checked) {
        label.text("{% trans "Published" %}");
        custom_switch.removeClass("text-danger");
        custom_switch.addClass("text-success");
        $.ajax(petition_publish_url
        ).done(function(){
            box.prop('disabled', false);
        }).fail(function () { // reset checkbox state upon failure
            setTimeout(function(){
                box.prop('checked', false);
                label.text("{% trans "Not published" %}");
                custom_switch.removeClass("text-success");
                custom_switch.addClass("text-danger");
                box.prop('disabled', false);
            }, 1000);
            //FIXME: show an alert message to the user about the failure
        });
    } else {
        label.text("{% trans "Not published" %}");
        custom_switch.removeClass("text-success");
        custom_switch.addClass("text-danger");
        $.ajax(petition_unpublish_url
        ).done(function(){
            box.prop('disabled', false);
        }).fail(function () { // reset checkbox state upon failure
            setTimeout(function() {
                box.prop('checked', true);
                label.text("{% trans "Published" %}");
                custom_switch.removeClass("text-danger");
                custom_switch.addClass("text-success");
                box.prop('disabled', false);
            }, 1000);
            //FIXME: show an alert message to the user about the failure
        });
    }
   });
});
