$(function () {
    $('[data-action="leave_org"]').on("click", function() {
        var org_name = $(this).closest("[data-org]").data("org");
        $.ajax("{% url "leave_org" %}?org=" + org_name).done(function() {
            window.location = window.location.href;
        });
    });
});

{% url "user_dashboard" as dashboard_url %}
{% include "petition/generic.js" with dashboard=dashboard_url %}