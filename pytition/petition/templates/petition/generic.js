$(document).ready(function() {
    $(".btn-invitation-join").on("click", function() {
        var org = $(this).data("org");
        $.ajax({
        url: "{% url "invite_accept" %}?org_name=" + org,
        }).done(function() {
            $(".btn-invitation-join").filter('[data-org="'+org+'"]').closest(".alert").alert("close");
        });
    });
});

$(document).ready(function() {
    $(".btn-invitation-join").closest(".alert").on("closed.bs.alert", function() {
        if ($("#invitations").find(".alert").length == 0) {
                location.reload(true);
        }
    });
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(function () {
   $('[data-action="template-delete"]').on("click", function() {
    var template_id = $(this).closest("[data-template]").data("template");
    //alert("template id: " + template_id);
    $.ajax("{% url "template_delete" %}?id=" + template_id).done(function() {
        location.reload(true);
        //$('[data-template="'+template_id+'"]').addClass("d-none").removeClass("d-flex");
    });
   });
});

$(function () {
   $('[data-action="template-edit"]').on("click", function() {
    var template_id = $(this).closest("[data-template]").data("template");
        window.location = "{% url "edit_template" %}?id=" + template_id;
   });
});

$(function () {
    $('[data-fav-toggle="true"]').on("click", function () {
        var template_id = $(this).closest("[data-template]").data("template");
        $.ajax("{% url "ptemplate_fav_toggle" %}?id=" + template_id).done(function() {
            location.reload(true);
        });
    });
});