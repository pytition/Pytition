{% load i18n %}
function addUser(user) {
    $("#user_search_result").html("<span class=\"oi oi-cog\" title=\"waiting\" aria-hidden=\"true\"></span>");
    $.ajax({
        url: "{% url "org_add_user" org.slugname %}?user=" + user,
        dataType: "json",
    }).done(function(data) {
        $("#user_search_result").html("");
        var html = `
        <div class="alert alert-success alert-dismissible show fade">
        <button type="button" class="close" data-dismiss="alert">&times;</button>
        <div class="row">
            <div class="col-1 alert-icon-col">
                <span class="oi oi-check"></span>
            </div>
        <div class="col">
        ` + data.message + "</div></div></div>";
        $("#user_search_result").append(html);
    }).fail(function($xhr) {
        var data = $xhr.responseJSON;
        console.log(data);
        $("#user_search_result").html("");
        var html;
        if (typeof data === "undefined") {
            html = `
            <div class="alert alert-danger alert-dismissible show fade">
                <button type="button" class="close" data-dismiss="alert">&times;</button>
                <div class="row">
                    <div class="col-1 alert-icon-col">
                        <span class="oi oi-warning"></span>
                    </div>
                    <div class="col">
                        {% blocktrans with orgname=org.name %}
                        An unknown error happened. We could not invite this user to <strong>{{ orgname }}</strong>
                        {% endblocktrans %}
                    </div>
                </div>
            </div>
            `;
        } else {
            html = `
            <div class="alert alert-danger alert-dismissible show fade">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <div class="row">
                <div class="col-1 alert-icon-col">
                    <span class="oi oi-warning"></span>
                </div>
                <div class="col">
            ` + data.message + "</div></div></div>";
        }
        $("#user_search_result").append(html);
    });
}

$(document).ready(function(){
  $("#invite_user").on("keyup", function() {
   $.ajax({
   url: "{% url "get_user_list" %}?q=" + $("#invite_user").val(),
   dataType: "json",
   }).done(function(data) {
        $("#user_search_result").html("");
        data.values.forEach(function(item, index) {
            $("#user_search_result").append("<a href=\"#\" id=\"addUser"+ item +"\" class=\"list-group-item list-group-item-success list-group-item-action\"><span class=\"oi oi-plus\" title=\"plus\" aria-hidden=\"true\"></span> "+ item +"</a>");
            $("#addUser" + item).on("click", function () {
                addUser(item);
                $("#invite_user").val("");
            });
        });
   });
  });
});

$(function () {
    $('[data-action="delete-member"]').on('click', function () {
       var member_name = $(this).closest("[data-member]").data("member");
       $.ajax("{% url "org_delete_member" org.slugname %}?member=" + member_name).done(function () {
        if (member_name == "{{ user.name }}")
            window.location = "{% url "user_dashboard" %}";
        else
            window.location = window.location.href;
       });
    });
});

{% url "org_dashboard" org.slugname as dashboard_url %}
{% include "petition/generic.js" with dashboard=dashboard_url %}