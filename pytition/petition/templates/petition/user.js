{% load i18n %}

$(function () {
    $('[data-action="leave_org"]').on("click", function() {
        var org_name = $(this).closest("[data-org]").data("org");
        $.ajax("{% url "leave_org" %}?org=" + org_name).done(function() {
            window.location = window.location.href;
        })
        .fail(function (xhr, status, error) {
            if (xhr.status == 409) { // You are the only member left, leaving means DELETING the organization!!
            var modal = `
    <div class="modal fade" id="org_delete_modal`+ org_name +`">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{% trans "Delete organization?" %}</h4>
            <button type="button" class="close" data-dismiss="modal">&times;</button>
          </div>

          <div class="modal-body">
            {% blocktrans %}
              Do you really want to DELETE organization '`+ org_name +`'
            {% endblocktrans %}
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-danger" data-action="org-delete" data-dismiss="modal">{% trans "Delete" %}</button>
            <button type="button" class="btn btn-info" data-dismiss="modal">{% trans "Cancel" %}</button>
          </div>

        </div>
      </div>
    </div>`;
            $('#modalContainer').append(modal);
            $('#org_delete_modal' + org_name).modal('toggle');
            $('[data-action="org-delete"]').on('click', function() {
                $.ajax("{% url "leave_org" %}?org=" + org_name + "&confirm=1").done(function() {
                    window.location = window.location.href;
                });
            });
            }
        });
    });
});

{% url "user_dashboard" as dashboard_url %}
{% include "petition/generic.js" with dashboard=dashboard_url %}