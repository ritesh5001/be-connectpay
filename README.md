# Be-Connect Pay – homepage

New homepage for https://be-connectpay.co.uk/, laid out like the reference site (suchitagroup.com) and built around the four Be-Connect banners.

- **`index.html`** + **`assets/`**: the homepage. Open `index.html` in a browser to preview.
- **`elementor/be-connect-home.html`**: the same page as one copy-paste block for an Elementor **HTML** widget.
- `tools/build_elementor.py`: rebuilds the Elementor file from `index.html` (`python3 tools/build_elementor.py`).

## Page sections (top to bottom)

1. **Top bar**: phone, email, 24/7 support, social icons.
2. **Header**: logo, menu (Home, About Us, Services dropdown, Industries, Blog, Contact Us), "Call us" and **Get a Free Quote**. Sticky on scroll. Slide-in menu on mobile.
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

## Using it in Elementor

1. Create or edit the Home page. In **Page Settings → Page Layout**, choose **Elementor Canvas** (the code has its own header and footer). To keep your theme's header/footer instead, delete the `TOP BAR`, `HEADER`, `Mobile menu` and `FOOTER` blocks from the code.
2. Add a section/container set to **Full Width** with **0 padding / 0 gap**, then drag in an **HTML** widget.
3. Open `elementor/be-connect-home.html`, copy everything and paste it into the widget.

**No clashes:** every class and id starts with `bcpay-` and every CSS rule is scoped to `.bcpay-home`, so nothing affects other pages, widgets or the theme. The page also resets its own elements, so theme styles for headings, buttons, links and images don't leak in (tested against Hello-theme style rules).

**Images** load from this repo through jsDelivr (`https://cdn.jsdelivr.net/gh/ritesh5001/be-connectpay@main/assets/`). For production, upload `assets/` to the Media Library and find/replace that address with your uploads URL.

**Links** use WordPress-style paths (`/about-us/`, `/card-machines/`, `/business-funding/`, `/pos-system/`, `/online-payments/`, `/payment-gateway/`, `/pay-by-link/`, `/payment-app/`, `/phone-payment/`, `/order-and-pay-at-table/`, `/industries/`, `/blog/`, `/contact-us/`). Change them if your page slugs differ.

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
