odoo.define('website_ecom_custom.header_custom', function (require) {
    "use strict";

    var affix1 = function (i, n) {
        var o = $(this);
        return (
            o.each(function () {
                var t = $(this);
                t.bind("affix", function (t, o) {
                    var s = $(this);
                    ("function" == typeof i ? i.apply(this) : i) <= o ? s.addClass("affix").css(n || {}) : s.removeClass("affix").removeAttr("style");
                }),
                    t.trigger("affix");
            }),
            $(t)
                .scroll(function () {
                    var t = $(this).scrollTop();
                    o.trigger("affix", [t]);
                })
                .trigger("scroll"),
            this
        );
    }
    $(document).ready(function(){
        var aa = affix1(("#header"), 0.5)
    });


});