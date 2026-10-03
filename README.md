# Be-Connect Pay – homepage

New homepage for https://be-connectpay.co.uk/, laid out like the reference site (suchitagroup.com) and built around the four Be-Connect banners.

- **`elementor/be-connect-home-paste.html`**: **copy-paste version.** Paste it into one Elementor **HTML** widget and it works for any account, including ones without the `unfiltered_html` permission.
- `wordpress-plugin/be-connect-home.zip`: plugin version with `[bcpay_home]` shortcode, including the autoplay slider, live calculators and animations.
- `elementor/be-connect-home.html`: full version for an HTML widget. Only works for accounts with the `unfiltered_html` permission.
- **`index.html`** + **`assets/`**: the homepage as a static page for previewing.
- `tools/build_paste.py`: rebuilds the copy-paste version. `tools/build_elementor.py`: rebuilds the plugin and full HTML version.

## Copy-paste version (recommended for this site)

1. Edit the home page with Elementor. Set **Page Settings → Page Layout → Elementor Full Width** (keeps your theme header and footer).
2. Add a section/container set to **Full Width** with **0 padding**, then drag in an **HTML** widget.
3. Open `elementor/be-connect-home-paste.html`, copy everything and paste it into the widget. **Update**.

This version has no `<style>` or `<script>`. Everything is inline styles that WordPress's content filter keeps, checked by running it through `wp_kses_post` (the same filter Elementor applies) with nothing removed. Layout uses floats plus `clamp()` breakpoints, so it switches between 4, 2 and 1 columns without media queries.

Because WordPress removes all JavaScript in this mode:
- The **banner slider** works by swipe/trackpad and by its arrows and dots, but doesn't autoplay.
- The **calculators** become worked tables: monthly funding repayments by amount and term at an example 12% rate, and yearly savings from a lower card fee rate.
- There are no hover animations or count-up numbers.

For those extras, use the plugin version.

**Fonts:** headings use Montserrat and body text uses Inter, if your site loads them. Otherwise they fall back to Segoe UI/Roboto/Arial. To load them, pick Montserrat and Inter in **Elementor → Site Settings → Global Fonts**.

## Page sections (top to bottom)

1. **Top bar**: phone, email, 24/7 support, social icons.
2. **Header**: logo, menu (Home, Card Machine ▾, Online Payment ▾, Business Funding, About ▾), "Call us" and **Get a Free Quote**. Sticky on scroll. Slide-in menu on mobile. Can be switched off with `header="no"`.
3. **Banner slider**: the 4 banners (Card Machines, Business Funding, POS System, Online Payments). Autoplays every 6s, with arrows, dots and swipe. Each slide has an **Explore More** button in the empty strip under the banner's icon row, linking to that service. On phones the button sits under the banner.
4. **About Us**: image collage, 24/7 badge, text, checklist, mission/vision, More About Us button.
5. **Calculators**: tabbed **Business Funding Calculator** (amount, term, rate → monthly repayment, total interest, total repayable, chart) and **Card Fee Calculator** (takings, transactions, fees → effective rate, yearly fees, savings per 0.1%).
6. **Numbers**: 4 animated counters.
7. **Featured Services**: Card Machines, Business Funding, POS System, Online Payments cards, plus "Also available" links.
8. **Why Choose Us**: 6 reasons around a central image.
9. **Industries We Serve**: Restaurants & Pubs, Salons & Beauty, Cafés, Retail, Takeaways, Bakeries & Delis, Trades, Gyms.
10. **Testimonials**: the 3 real customer reviews (slider on smaller screens).
11. **Blog**: 3 latest-post cards.
12. **Call to action** and **footer**.

## Installing on WordPress (plugin – recommended)

1. **Plugins → Add New → Upload Plugin**, choose `wordpress-plugin/be-connect-home.zip`, **Install**, **Activate**.
2. Edit the home page with Elementor. Add a section/container set to **Full Width** with **0 padding**, then drag in a **Shortcode** widget.
3. Enter one of:
   - `[bcpay_home header="no" footer="no"]`: keep your theme's header and footer. Set **Page Settings → Page Layout → Elementor Full Width**.
   - `[bcpay_home]`: use this page's own top bar, header and footer. Set **Page Layout → Elementor Canvas**.
4. **Update** the page.

The plugin loads its CSS/JS as files and its images from the plugin folder, so WordPress can't strip anything and no CDN is needed.

### Why the HTML widget showed the CSS as text

WordPress removes `<style>` and `<script>` tags from content saved by accounts without the **`unfiltered_html`** permission, but leaves the CSS inside as plain text. Hosts and security plugins often remove that permission from admins (`define('DISALLOW_UNFILTERED_HTML', true);` in `wp-config.php`, or a "disable unfiltered HTML" setting in a security plugin). It was reproduced on a clean WordPress install: the `<style>`/`<script>` tags were removed and the CSS was printed on the page. The plugin avoids this entirely.

If you'd rather use the HTML widget, re-enable `unfiltered_html` for your account first, then paste `elementor/be-connect-home.html` into an **HTML** widget.

**No clashes:** every class and id starts with `bcpay-` and every CSS rule is scoped to `.bcpay-home`, so nothing affects other pages, widgets or the theme, and theme styles for headings, buttons, links and images don't leak in.

**Menu** matches the live header: Home, Card Machine (Portable, Mobile, Countertop, POS System), Online Payment (Payment Gateway, Payment Link, Payment App, Phone Payment, Order & Pay at Table), Business Funding, About (About Us, Industries, Blog, Contact Us). The dropdown page addresses are guesses (`/portable-card-machine/`, `/mobile-card-machine/`, `/countertop-card-machine/`, `/payment-gateway/`, `/pay-by-link/`, `/payment-app/`, `/phone-payment/`, `/order-and-pay-at-table/`, …). Correct them in `index.html` and rebuild, or ask for them to be updated.

## SEO (set in Yoast / Rank Math, not in the widget)

- **Meta title:** Card Machines, POS & Business Funding for UK Businesses | Be-Connect Pay
- **Meta description:** Be-Connect Pay arranges card machines, POS systems, online payments and flexible unsecured business funding for UK small businesses, with trusted providers and UK support.

## Placeholder content to replace

- **Numbers** (1,500+ businesses, £10M+ funding, 25+ partners): placeholders. Edit the text and the `data-bcpay-count` value in the NUMBERS block.
- **About Us** text, mission and vision: written as a starting point.
- **Blog cards**: sample posts. Swap in real posts, or use Elementor's Posts widget for an auto-updating list.
- **Social links** in the top bar and footer are `#`.
- **Calculators** are illustrations only, and the page says so. The funding calculator assumes a standard repayment loan.

## Images

- `banner-*.webp`: the four supplied banners. `service-*.jpg`: crops from those banners.
- `logo-dark.png`: from the current site.
- Industry, team, bakery and terminal photos: royalty-free stock carried over from the previous draft. Replace with the client's own photos if preferred.
