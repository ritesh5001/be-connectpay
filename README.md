# Be-Connect Pay – homepage redesign

Proposed new homepage for https://be-connectpay.co.uk/, for client approval before the WordPress build.

- **`index.html`** + **`assets/`** – the homepage. Open `index.html` in a browser.
- `tools/homepage.src.html` + `tools/build.py` + `tools/images/` – source, original images, and the script that inlines the icon sprite (Lucide + Simple Icons) and copies images into `assets/`.

## Design

Premium fintech direction (in the spirit of Stripe / Dojo / Revolut Business) built on the reference sites' structure:

1. Transparent header over a dark hero; turns white on scroll. Full-screen mobile menu.
2. Hero: headline, CTAs, customer avatars + Trustpilot stars, terminal photo with floating "payment approved", "paid out tomorrow" and "welcome team" cards. Payment logos in white.
3. Solutions bento: card machines (cut-out product shots), online / Pay by Link (checkout mock-up), POS, phone payments (photo), business funding.
4. Card machine showcase (dark): switch between Mobile 4G, Smart terminal and Countertop.
5. Industries: photo cards (retail, cafés, restaurants & pubs, hair & beauty, takeaways, trades, gyms). Swipeable carousel on phones.
6. Next-day settlement story with a phone app mock-up and timeline.
7. Why Be-Connect: welcome-team photo + six benefits.
8. Fee checker: sliders → effective rate, yearly fees, savings per 0.1%.
9. How it works (3 steps), customer reviews (the three on the current site), funding CTA with photo, FAQ, footer.
10. "Get a free quote" opens a 3-step quote dialog everywhere. Sticky call/quote bar on phones.

## Images

- `assets/hero-terminal.jpg`, `terminal-*.png`, `pos-system.png`, logos: from the current be-connectpay.co.uk homepage (cut out / recoloured).
- Sector, team, bakery, phone and avatar photos: royalty-free stock (Pexels / Unsplash / CC0) taken from open-source WordPress themes in github.com/Automattic/themes and github.com/woocommerce/woocommerce. Swap for the client's own or licensed photos before launch if preferred.

## Notes for the WordPress build

- Colours are CSS variables at the top of the `<style>` block: `--sky` (#00A0DC, Be-Connect blue) and the `--navy-*` scale.
- Fonts: Plus Jakarta Sans (everything) and JetBrains Mono (times in the settlement timeline) from Google Fonts.
- Each `<section>` maps to an Elementor/Gutenberg section.
- Product images were cut from a screenshot of the current homepage. Use the original high-resolution files from the WordPress media library for the live build.
- The quote dialog, machine switcher and fee checker are front-end JavaScript only. Connect the quote dialog to Gravity Forms / WPForms / the CRM.
- Links to existing pages (`/pos-system/`, `/payment-gateway/`, `/pay-by-link/`, `/payment-app/`, `/about-us/`) are kept. Careers, blog, contact, privacy, terms and social links are `#` placeholders.
