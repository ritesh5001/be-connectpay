=== Be-Connect Pay Homepage ===
Stable tag: 1.1.0

Adds the [bcpay_home] shortcode for the Be-Connect Pay homepage.

== Installation ==
1. Plugins > Add New > Upload Plugin > choose be-connect-home.zip > Install > Activate.
2. Edit the home page with Elementor, add a "Shortcode" widget and enter: [bcpay_home]
   (Page Settings > Page Layout > "Elementor Canvas" if you use the plugin's own header and footer.)

Options:
[bcpay_home header="no"]              use your theme header instead of the plugin's
[bcpay_home footer="no"]              use your theme footer instead of the plugin's
[bcpay_home header="no" footer="no"]  homepage sections only

Every class and id starts with "bcpay-" and all CSS is scoped to .bcpay-home,
so nothing affects the rest of the site.
