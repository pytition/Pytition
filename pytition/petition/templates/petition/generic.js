{% load i18n %}
var joined = false;

$(document).ready(function() {
    $(".btn-invitation-join").on("click", function() {
        var org = $(this).data("org");
        $.ajax({
        url: "{% url "invite_accept" %}?org=" + org,
        }).done(function() {
            joined = true;
            $(".btn-invitation-join").filter('[data-org="'+org+'"]').closest(".alert").alert("close");
        });
    });
});

$(document).ready(function() {
    $(".btn-invitation-join").closest(".alert").on("closed.bs.alert", function() {
        if ($("#invitations").find(".alert").length == 0) {
                if (joined)
                    window.location = window.location.href;
        }
    });
});

$(function () {
    $(".btn-invitation-dismiss").on("click", function () {
        var org = $(this).data("org");
        $.ajax({
        url: "{% url "invite_dismiss" %}?org=" + org,
        }).done(function() {
            $(".btn-invitation-dismiss").filter('[data-org="'+org+'"]').closest(".alert").alert("close");
        });
    });
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(function () {
   $('[data-action="template-delete"]').on("click", function() {
    var template_id = $(this).closest("[data-template]").data("template");
    $.ajax("{% url "template_delete" %}?id=" + template_id).done(function() {
       if (window.location.href.endsWith('edit_template/' + template_id)) {
           // If we were on this template edit page and the user clicks on delete
           // we cannot reload the edit page, we then reload the dashboard
           window.location = "{{ dashboard }}";
       } else
           window.location = window.location.href;
    });
   });
});

$(function () {
    $('[data-fav-toggle="true"]').on("click", function () {
        var template_id = $(this).closest("[data-template]").data("template");
        $.ajax("{% url "ptemplate_fav_toggle" %}?id=" + template_id).done(function() {
            window.location = window.location.href;
        });
    });
});

$(function () {
   $('[data-action="petition-delete"]').on("click", function() {
    var petition_id = $(this).closest("[data-petition]").data("petition");
    $.ajax("{% url "petition_delete" %}?id=" + petition_id).done(function() {
        if (window.location.href.endsWith('edit_petition/' + petition_id)) {
           // If we were on this petition edit page and the user clicks on delete
           // we cannot reload the edit page, we then reload the dashboard
           // NOTE: today there is no delete button from petition edit page. This is hypothetical.
           window.location = "{{ dashboard }}";
       } else
           window.location = window.location.href;
    });
   });
});

$(function () {
   $('[data-action="publish"]').find('input:checkbox').on("change", function() {
    var petition_id = $(this).closest("[data-petition]").data("petition");
    var box = $(this);
    var checked = box.prop('checked');
    var label = box.siblings('label');
    var custom_switch = box.closest('.custom-switch');
    box.prop('disabled', true);
    if (checked) {
        label.text("{% trans "Published" %}");
        custom_switch.removeClass("text-danger");
        custom_switch.addClass("text-success");
        $.ajax("{% url "petition_publish" %}?id=" + petition_id
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
        $.ajax("{% url "petition_unpublish" %}?id=" + petition_id
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