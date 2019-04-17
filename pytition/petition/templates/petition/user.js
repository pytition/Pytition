{% load i18n %}

$(function () {
});

{% url "user_dashboard" as dashboard_url %}
{% include "petition/generic.js" with dashboard=dashboard_url %}
