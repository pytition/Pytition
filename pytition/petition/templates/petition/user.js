$(function () {
    $('[data-action="leave_org"]').on("click", function() {
        var org_name = $(this).closest("[data-org]").data("org");
        $.ajax("{% url "leave_org" %}?org=" + org_name).done(function() {
            location.reload(true);
        });
    });
});

{% include "petition/generic.js" %}