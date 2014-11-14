jQuery(document).ready(function ($) {
    // We want to match from the right to the left.
    var path = document.location.pathname;
    var nav = document.querySelector('nav.header-nav');
    if (!nav) {
	return false;
    }

    var active_tab;
    while (true) {
	active_tab = nav.querySelector("a[href='" + path + "']");
        if (active_tab || path === "/") {
            break;
        }

        path = "/" + path.split("/").slice(-1).join("/");
    }

    $(active_tab).closest("li").addClass("active");

});
