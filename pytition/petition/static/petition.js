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


    /* handle sticky form */
    function handle_scroll(a, b, c) {
      function d() {
          var a = !1,
              b = g.offset().top;
          b = window_width < mobile_breakpoint ? b + f.height() - g.height() : b - l - 15, m > b && (a = !0), window_width >= mobile_breakpoint ? a ? (l = m - b, f.css("transform", "translate3d(0," + l + "px,0)")) : f.css("transform", "translate3d(0,0,0)") : (f.css("transform", "translate3d(0,0,0)"), a ? i.addClass("fixed") : i.removeClass("fixed"))
      }

      function e() {
          window_width = j.width(), d()
      }
      var f, g, h, i, j = a(b),
          k = b.document,
          l = 0,
          m = 0;
      window_width = 0, mobile_breakpoint = 768, j.on("scroll", function() {
          m = j.scrollTop(), d()
      }).on("resize", e), a(k).ready(function() {
          f = a("#form-sticky"), g = f.find(".eaFullWidthContent:first"), h = a("#show-form"), i = a("body"), h.on("click", function() {
              a("html,body").animate({
                  scrollTop: a("#intro").offset().top
              }, .5 * m)
          }), e()
      })
    };
    handle_scroll(jQuery, window);
});