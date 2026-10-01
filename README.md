# Be-Connect Pay – homepage redesign

Proposed new homepage for https://be-connectpay.co.uk/, for client approval before the WordPress build.

- **`index.html`** + **`assets/`** – the homepage. Open `index.html` in a browser.
- `tools/homepage.src.html` + `tools/build.py` – source and the script that inlines the icon sprite (Lucide + Simple Icons) and copies images into `assets/`.

## Layout

Follows the three references:

- **merchantbusinessloans.co.uk** – split hero with photo, numbered sections, cost calculator with receipt, stats row, FAQ list, "Ready to get started?" CTA
- **knowyourbusiness.co.uk** – solution finder (tabs + "Which best describes your business?" pills), Trustpilot-style reviews row, brand-colour footer
- **merchantsavvy.co.uk** – payment logo band, in-person / online / phone channel cards with product images

## Sections (top to bottom)

1. Header: logo, nav (Card Machine, Online Payment, Business Funding, Sectors, About), phone/email icons, Get a Free Quote
2. Hero with the current site's terminal photo
3. Payment logos band
4. Solution finder (Card machines / POS / Online / Phone / Funding × business type)
5. 01 Sales channels: Card Machines, POS Systems, Online Payments, Phone Payments
6. 02 Why Be-Connect (content from the current site)
7. 03 Card machines (the three current machines and their bullet points)
8. 04 Sectors
9. 05 Three steps
10. 06 Fee checker calculator with receipt
11. Stats + 07 Business funding
12. Customer reviews (the three reviews on the current site)
13. 08 FAQs
14. CTA
15. Footer: contact details, links, card logos, Trustpilot, company no. 15411775

## Notes for the WordPress build

- Colours are CSS variables at the top of the `<style>` block: `--sky` (#00A0DC, Be-Connect blue) and `--navy`.
- Fonts: Poppins (headings), DM Sans (body), Space Mono (labels) from Google Fonts.
- Each `<section>` maps to an Elementor/Gutenberg section.
- Images in `assets/` were cropped from a screenshot of the current homepage. Use the original high-resolution files from the WordPress media library for the live build.
- Sector tiles use gradients and icons. Replace them with sector photos if the client has any.
- The solution finder and fee checker are front-end JavaScript only. Point quote buttons at the real quote form (Gravity Forms / WPForms / CRM).
- Links to existing pages (`/pos-system/`, `/payment-gateway/`, `/pay-by-link/`, `/payment-app/`, `/about-us/`) are kept. Careers, blog, contact, privacy, terms and social links are `#` placeholders.
