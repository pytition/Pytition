var $ = jQuery;
$(document).ready(function() {

    /* progress bar loading */
    var l = 1e3;
    var m = "linear";
    var counter = $("#counter");
    var signature_number = counter.find("#nb-signatures");
    var progressbar = counter.find("#progress-bar");
    var target = parseInt(progressbar.data('target'));
    var signatures = parseInt(signature_number.text());
    var q = Math.floor(signatures/target*100);
    counter.addClass("show");
    progressbar.animate({width:q+"%"},l,m, function() {
        $(window).trigger("counter.displayed");
    });
});
$(function() {
   $('[data-action="petition-report"]').on("click", function() {
       var report_url = $("#reason_selector option:selected").data("url");
       var report_success = $(this).closest("[data-report-success]").data("report-success");
       var report_failure = $(this).closest("[data-report-failure]").data("report-failure");
       $.ajax(report_url).done(function() {
           alert(report_success);
       }).fail(function () {
           alert(report_failure);
       })
   });
});
