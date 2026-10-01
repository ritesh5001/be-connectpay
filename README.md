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
- Links to existing pages (POS system, payment gateway, Pay by Link, payment app, About us) point at https://be-connectpay.co.uk/... so they work from the preview. Make them relative in WordPress. Careers, blog, contact, privacy, terms and social links are `#` placeholders.

## Live preview (GitHub Pages)

In the repo: Settings → Pages → Source "Deploy from a branch" → pick the branch → folder `/ (root)` → Save. The site is then at https://ritesh5001.github.io/be-connectpay/.

## Elementor version

`elementor/be-connect-home.html` is the whole homepage as one block for an Elementor **HTML** widget.

- All classes and ids start with `bcp-` and every CSS rule is scoped under `.bcp-home`. There are no styles on bare tags (h1, p, a, img…), so it won't affect other pages or widgets.
- Images load from this repo on GitHub. To host them in WordPress, upload `assets/` to the media library and find/replace the GitHub address in the code.
- Rebuild after editing the source: `python3 tools/build.py && python3 tools/build_elementor.py`.
