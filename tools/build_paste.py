"""Builds elementor/be-connect-home-paste.html: the homepage as plain HTML that survives
WordPress's content filter (wp_kses_post).

Elementor runs every widget through wp_kses_post when the editing account doesn't have the
`unfiltered_html` permission. That removes <style>, <script>, <link>, <svg>, <input> and
any inline CSS it doesn't allow (display, transform, rgba(), ...). So this version uses
only what survives:

- inline style="" attributes with allowed properties only,
- float / position / aspect-ratio for layout (display:flex/grid are stripped),
- "switch" expressions instead of media queries, e.g.
  clamp(calc(25% - 24px), calc((1000px - 100%) * 999), calc(100% - 24px))
  is 25% wide when the container is wider than 1000px and 100% when it is narrower,
- container query units (cqi) measured against the outer wrapper,
- icons as <img> SVG files, the slider as a swipeable strip with anchor-link arrows/dots,
- no JavaScript: the calculators become worked repayment / savings tables.

Run: python3 tools/build_paste.py
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = 'https://cdn.jsdelivr.net/gh/ritesh5001/be-connectpay@main/assets/'
ICON = IMG + 'icons/'

BLUE, BLUE_D, BLUE_L, BLUE_50, BLUE_100 = '#00a5ea', '#008ccb', '#5cc8f5', '#edf8fe', '#d6effd'
ROYAL, NAVY, NAVY_2, NAVY_D = '#1857c9', '#0a1f4e', '#102b66', '#061538'
TEXT, MUTED, LINE, SOFT, STAR = '#4a5674', '#7a86a1', '#e3eaf3', '#f3f9fd', '#ffb400'
FH = 'Montserrat,Poppins,Segoe UI,Roboto,Arial,sans-serif'
FB = 'Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif'
SH = '0 12px 34px -14px #0a1f4e38'
SH_LG = '0 30px 60px -24px #0a1f4e59'


def s(**kw):
    """style dict -> 'a-b:c;...' (underscores become hyphens)"""
    return ';'.join(f"{k.replace('_', '-')}:{v}" for k, v in kw.items())


def cols(*steps, g=24):
    """Float width that switches column count by container width, no media queries.
    cols((4, 1000), (2, 620)) -> 4 columns above 1000px, 2 above 620px, else 1."""
    expr = f'calc(100% - {g}px)'
    for n, bp in reversed(steps):
        pct = f'{100 / n:.4f}'.rstrip('0').rstrip('.') + '%'
        expr = f'clamp(calc({pct} - {g}px), calc(({bp}px - 100%) * 999), {expr})'
    return expr


def when_wide(bp, value, narrow='0px'):
    """`value` when the outer wrapper is wider than bp, else `narrow` (lengths only)."""
    return f'clamp({narrow}, calc((100cqi - {bp}px) * 999), {value})'


def when_narrow(bp, value, wide='0px'):
    return f'clamp({wide}, calc(({bp}px - 100cqi) * 999), {value})'


def esc(t):
    return html.escape(t, quote=False)


def icon(name, color, size, style=''):
    return f'<img src="{ICON}{name}-{color}.svg" alt="" width="{size}" height="{size}" style="{s(width=f"{size}px", height=f"{size}px", max_width="none", margin="0", padding="0", border="0", border_radius="0", box_shadow="none", vertical_align="middle")}{";" + style if style else ""}">'


def img(src, alt, w, h, style, lazy=True):
    base = s(max_width='100%', margin='0', padding='0', border='0', box_shadow='none', vertical_align='top')
    lz = ' loading="lazy"' if lazy else ''
    return f'<img src="{IMG}{src}" alt="{html.escape(alt)}" width="{w}" height="{h}"{lz} style="{base};{style}">'


# ---------- shared pieces ----------
T_RESET = s(margin='0', padding='0', border='0', background='none', text_transform='none', text_decoration='none', letter_spacing='normal')


def eyebrow(text, center=False):
    line = f'<span style="{s(padding="0 14px", margin="0 10px 0 0", border_bottom=f"2px solid {BLUE}", font_size="0", line_height="0", vertical_align="middle")}"></span>'
    line_r = line.replace('margin:0 10px 0 0', 'margin:0 0 0 10px')
    return (f'<div style="{s(margin="0 0 14px", padding="0", font_family=FH, font_size="13.5px", font_weight="700", letter_spacing=".12em", text_transform="uppercase", color=BLUE, line_height="1.4", text_align="center" if center else "left")}">'
            f'{line}{esc(text)}{line_r if center else ""}</div>')


def title(html_text, center=False, color=NAVY, size='clamp(28px,3.6cqi,44px)'):
    return f'<h2 style="{T_RESET};{s(font_family=FH, font_size=size, font_weight="800", line_height="1.18", color=color, text_align="center" if center else "left")}">{html_text}</h2>'


def hl(t):
    return f'<span style="{s(color=BLUE)}">{esc(t)}</span>'


def lead(t, center=False, color=TEXT):
    return f'<p style="{T_RESET};{s(margin="16px auto 0" if center else "16px 0 0", max_width="64ch", font_family=FB, font_size="clamp(16px,1.3cqi,17.5px)", line_height="1.7", color=color, text_align="center" if center else "left")}">{esc(t)}</p>'


def head(sub, h2, ld=None, center=True):
    return (f'<div style="{s(margin="0 auto clamp(36px,4.5cqi,56px)", max_width="780px" if center else "none", text_align="center" if center else "left")}">'
            + eyebrow(sub, center) + title(h2, center) + (lead(ld, center) if ld else '') + '</div>')


def btn(label, href, kind='primary', arrow=True, ic=None, style=''):
    bg, fg, bd = {'primary': (BLUE, '#fff', BLUE), 'navy': (NAVY, '#fff', NAVY), 'outline': ('#fff', NAVY, LINE),
                  'white': ('#fff', NAVY, '#fff'), 'ghost': ('transparent', '#fff', '#ffffff73')}[kind]
    shadow = '0 12px 24px -12px #00a5eae6' if kind == 'primary' else 'none'
    arrow_c = 'white' if fg == '#fff' else 'navy'
    inner = (icon(ic, arrow_c, 18, s(margin='0 8px 0 0', vertical_align='-3px')) if ic else '') + esc(label) + \
            (icon('arrow', arrow_c, 18, s(margin='0 0 0 10px', vertical_align='-3px')) if arrow else '')
    return (f'<a href="{href}" style="{s(float="left", margin="0", padding="15px 28px", border=f"2px solid {bd}", border_radius="999px", background=bg, color=fg, font_family=FH, font_size="15px", font_weight="700", line_height="1.2", text_decoration="none", text_transform="none", letter_spacing="normal", box_shadow=shadow, cursor="pointer")}{";" + style if style else ""}">{inner}</a>')


def row(inner, margin='0'):
    """left-aligned group of floated buttons"""
    return f'<div style="{s(margin=margin, padding="0", overflow="hidden")}">{inner}</div>'


def center(inner, margin='0 auto'):
    """shrink-to-fit wrapper: centres floated buttons/chips when they fit on one line"""
    return f'<div style="{s(width="max-content", max_width="100%", margin=margin, padding="0", overflow="hidden")}">{inner}</div>'


def link(label, href, color=BLUE):
    return (f'<a href="{href}" style="{s(margin="0", padding="0", color=color, font_family=FH, font_size="14.5px", font_weight="700", text_decoration="none", border="0", background="none", line_height="1.4")}">{esc(label)}'
            + icon('arrow', 'blue' if color == BLUE else 'white', 16, s(margin='0 0 0 8px', vertical_align='-3px')) + '</a>')


def iconrow(ic_html, body_html, pad=34, top='2px'):
    """icon on the left, text on the right (position:absolute instead of flex)"""
    return (f'<div style="{s(position="relative", margin="0", padding=f"0 0 0 {pad}px", min_height="22px")}">'
            f'<span style="{s(position="absolute", left="0", top=top, margin="0", padding="0", line_height="0")}">{ic_html}</span>{body_html}</div>')


def check_badge(size=22):
    return f'<span style="{s(float="left", width=f"{size}px", height=f"{size}px", margin="0", padding="4px", border_radius="50%", background=BLUE, line_height="0")}">{icon("check", "white", size - 8)}</span>'


def wrap(inner, pad='0 20px'):
    return f'<div style="{s(max_width="1240px", margin="0 auto", padding=pad)}">{inner}</div>'


def grid(items):
    """floats in a container that clears them; negative margins give the gutters"""
    return f'<div style="{s(margin="0 -12px", padding="0", overflow="hidden")}">{"".join(items)}</div>'


def section(inner, bg='#fff', id_=None, pad='clamp(64px,8cqi,110px) 0'):
    idattr = f' id="{id_}"' if id_ else ''
    return f'<section{idattr} style="{s(margin="0", padding=pad, background=bg, border="0")}">{inner}</section>'


# ---------- 1. Hero slider ----------
SLIDES = [
    ('banner-card-machines.webp', 1916, '/card-machines/', '89.2%', 'Card Machines for Every Business. We arrange reliable card machines for UK small businesses by partnering with trusted providers and financial institutions.'),
    ('banner-business-funding.webp', 1916, '/business-funding/', '92.2%', 'Business Funding for UK Small Business Owners. Flexible, unsecured funding solutions with easy documentation, fast pay out and no security or mortgage required.'),
    ('banner-pos-system.webp', 1916, '/pos-system/', '89.6%', 'POS System for Modern Businesses. All-in-one POS to manage sales and stock, improve customer experience and accept multiple payment options.'),
    ('banner-online-payments.webp', 1915, '/online-payments/', '92.2%', 'Online Payment Solutions for UK Small Businesses: order and pay at table, payment app, payment link, phone payment and payment gateway.'),
]


def hero():
    n = len(SLIDES)
    slides = []
    for i, (src, w, href, top, alt) in enumerate(SLIDES):
        prev_i, next_i = (i - 1) % n, (i + 1) % n
        arrow_box = s(position='absolute', top='50%', width='clamp(28px,3.2cqi,46px)', height='clamp(28px,3.2cqi,46px)', margin='calc(clamp(28px,3.2cqi,46px) / -2) 0 0', padding='0', border_radius='50%', background='#ffffffeb', box_shadow=SH, text_align='center', line_height='0', text_decoration='none', z_index='3')
        arrow_img = lambda nm: f'<img src="{ICON}{nm}-navy.svg" alt="" width="20" height="20" style="{s(width="50%", height="50%", max_width="none", margin="25%", padding="0", border="0", box_shadow="none", vertical_align="top")}">'
        dots = ''.join(
            f'<a href="#bcpay-s{k + 1}" aria-label="Show slide {k + 1}" style="{s(float="left", width="clamp(14px,1.5cqi,28px)" if k == i else "clamp(6px,.55cqi,10px)", height="clamp(6px,.55cqi,10px)", margin="0 3px", padding="0", border_radius="999px", background=BLUE if k == i else "#9fb4d3", border="0", text_decoration="none")}"></a>'
            for k in range(n))
        slides.append(
            f'<div role="group" aria-label="Slide {i + 1} of {n}" style="{s(float="left", width=f"{100 / n}%", height="100%", position="relative", margin="0", padding="0")}">'
            f'<span id="bcpay-s{i + 1}" style="{s(position="absolute", top="-130px", left="0", width="100%", height="1px")}"></span>'
            + img(src, alt, w, 821, s(width="100%", height="100%", object_fit="cover", border_radius="0"), lazy=False) +
            # "Explore More": in the empty strip under each banner's icon row; shrinks to nothing on phones
            f'<a href="{href}" style="{s(position="absolute", left="4.65%", top=top, margin="0", padding=".85em 1.7em", border="0", border_radius="999px", background=BLUE, color="#fff", font_family=FH, font_size=when_wide(600, "clamp(10px,.86cqi,17px)"), font_weight="700", line_height="1", text_decoration="none", box_shadow="0 14px 26px -12px #0078bee6", z_index="3")}">Explore More'
            f'<img src="{ICON}arrow-white.svg" alt="" width="16" height="16" style="{s(width="1.15em", height="1.15em", max_width="none", margin="0 0 0 .6em", padding="0", border="0", box_shadow="none", vertical_align="-.2em")}"></a>'
            f'<a href="#bcpay-s{prev_i + 1}" aria-label="Previous slide" style="{arrow_box};left:1.2%">{arrow_img("left")}</a>'
            f'<a href="#bcpay-s{next_i + 1}" aria-label="Next slide" style="{arrow_box};right:1.2%">{arrow_img("right")}</a>'
            f'<div style="{s(position="absolute", right="2.6%", bottom="3.4%", margin="0", padding="clamp(4px,.4cqi,7px) clamp(5px,.5cqi,8px)", border_radius="999px", background="#ffffffbf", overflow="hidden", z_index="3")}">{dots}</div>'
            '</div>')
    # scroller is 40px taller than the frame so its scrollbar is hidden below the banner
    return (f'<section id="bcpay-hero" aria-label="Our services" style="{s(margin="0", padding="0", background="#fff")}">'
            f'<div style="{s(position="relative", max_width="1920px", margin="0 auto", padding="0", aspect_ratio="1916/821", overflow="hidden", background=BLUE_50)}">'
            f'<div style="{s(width="100%", height="calc(100% + 40px)", margin="0", padding="0", overflow="auto")}">'
            f'<div style="{s(width=f"{n * 100}%", height="calc(100% - 40px)", margin="0", padding="0", overflow="hidden")}">{"".join(slides)}</div>'
            '</div></div>'
            # phones: banner text is tiny, so a full-width button sits underneath instead
            f'<div style="{s(max_height=when_narrow(600, "120px"), overflow="hidden", margin="0", padding="0")}">'
            f'<div style="{s(padding="16px 20px 4px", text_align="center")}">{center(btn("Explore Our Services", "#bcpay-services"))}'
            f'<div style="{s(margin="10px 0 0", font_size="13px", color=MUTED, font_family=FB, line_height="1.4")}">Swipe the banner to see all our services</div></div></div>'
            '</section>')


# ---------- 2. About ----------
def about():
    media = (f'<div style="{s(float="left", width=cols((2, 900), g=60), margin="0 30px 40px", padding="0")}">'
             f'<div style="{s(position="relative", max_width="560px", margin="0 auto", padding="0 13% 15% 0")}">'
             + img('team-welcome.jpg', 'Be-Connect Pay team member helping a business owner', 1024, 682, s(width='100%', aspect_ratio='4/4.3', object_fit='cover', object_position='50% 30%', border_radius='24px', box_shadow=SH_LG)) +
             img('owners-bakery.jpg', 'Small business owners behind their counter', 1400, 933, s(position='absolute', right='0', bottom='0', width='52%', aspect_ratio='1', object_fit='cover', border_radius='24px', border='8px solid #fff', box_shadow=SH_LG)) +
             f'<div style="{s(position="absolute", left="0", bottom="22%", margin="0", padding="18px 22px", border_radius="16px", background=BLUE, color="#fff", box_shadow="0 20px 40px -18px #00a5eae6")}">'
             f'<div style="{s(margin="0", font_family=FH, font_size="clamp(26px,3cqi,38px)", font_weight="800", line_height="1", color="#fff")}">24/7</div>'
             f'<div style="{s(margin="4px 0 0", font_family=FB, font_size="13.5px", font_weight="600", line_height="1.35", color="#e6f6fe")}">UK-based<br>support team</div></div>'
             '</div></div>')
    checks = ''.join(
        f'<div style="{s(float="left", width=cols((2, 480), g=20), margin="0 10px 12px", padding="0")}">'
        + iconrow(check_badge(), f'<span style="{s(font_family=FB, font_weight="600", font_size="15px", color=NAVY, line_height="1.5")}">{esc(t)}</span>', pad=32, top='1px') + '</div>'
        for t in ['Lower transaction fees', 'Simple, quick application', 'Fast setup and pay out', 'Trusted UK partners'])
    boxes = ''.join(
        f'<div style="{s(float="left", width=cols((2, 520), g=16), margin="0 8px 16px", padding="0")}">'
        f'<div style="{s(position="relative", margin="0", padding="18px 18px 18px 84px", min_height="96px", border_radius="16px", background=SOFT, border=f"1px solid {LINE}")}">'
        f'<span style="{s(position="absolute", left="18px", top="18px", width="52px", height="52px", border_radius="14px", background="#fff", box_shadow=SH, line_height="0", text_align="center")}">{icon(ic, "royal", 24, s(margin="14px"))}</span>'
        f'<div style="{s(margin="0 0 4px", font_family=FH, font_weight="700", font_size="16px", color=NAVY, line_height="1.3")}">{t}</div>'
        f'<div style="{s(margin="0", font_family=FB, font_size="14px", line_height="1.55", color=TEXT)}">{d}</div></div></div>'
        for ic, t, d in [('target', 'Our Mission', 'Make payments and funding simple, fair and fast for every UK small business.'),
                         ('eye', 'Our Vision', 'To be the partner local businesses trust to help them grow. Together for good.')])
    para = lambda t: f'<p style="{T_RESET};{s(margin="18px 0 0", font_family=FB, font_size="16px", line_height="1.7", color=TEXT)}">{t}</p>'
    copy = (f'<div style="{s(float="left", width=cols((2, 900), g=60), margin="0 30px 40px", padding="0")}">'
            + eyebrow('About Us') + title('Your Trusted Partner for ' + hl('Payments & Business Funding')) +
            para('Be-Connect Pay helps UK small businesses take payments and access finance with confidence. We partner with trusted providers, lenders and financial institutions to arrange reliable card machines, modern POS systems, secure online payments and flexible unsecured business funding.') +
            para('From independent cafés and salons to busy restaurants and retail stores, our UK team handles the comparison, paperwork and setup for you, so you can get back to running your business.') +
            f'<div style="{s(margin="22px -10px 0", padding="0", overflow="hidden")}">{checks}</div>'
            f'<div style="{s(margin="10px -8px 0", padding="0", overflow="hidden")}">{boxes}</div>'
            f'<div style="{s(margin="18px 0 0", padding="0", overflow="hidden")}">{btn("More About Us", "/about-us/", style="margin:0 18px 10px 0")}'
            f'<a href="tel:+442070527978" style="{s(float="left", margin="0 0 10px", padding="17px 0", color=NAVY, font_family=FH, font_weight="700", font_size="15px", text_decoration="none", line_height="1.3")}">{icon("phone", "blue", 18, s(margin="0 8px 0 0", vertical_align="-3px"))}020 7052 7978</a></div>'
            '</div>')
    return section(wrap(f'<div style="{s(margin="0 -30px", padding="0", overflow="hidden")}">{media}{copy}</div>'), id_='bcpay-about')


# ---------- 3. Calculators (worked tables; no JavaScript allowed) ----------
def repayment(p, rate, n):
    r = rate / 100 / 12
    return p * r / (1 - (1 + r) ** -n)


def table(caption, cols_, rows, note):
    th = s(margin='0', padding='12px 10px', background=NAVY, color='#fff', font_family=FH, font_size='13px', font_weight='700', text_align='right', border='0', line_height='1.3')
    th0 = th.replace('text-align:right', 'text-align:left')
    head_ = ''.join(f'<th style="{th0 if k == 0 else th}">{esc(c)}</th>' for k, c in enumerate(cols_))
    body = ''
    for ri, r in enumerate(rows):
        bg = '#fff' if ri % 2 == 0 else SOFT
        td = s(margin='0', padding='12px 10px', background=bg, color=NAVY, font_family=FB, font_size='clamp(13px,1.2cqi,14.5px)', font_weight='600', text_align='right', border='0', border_bottom=f'1px solid {LINE}', line_height='1.3')
        td0 = td.replace('text-align:right', 'text-align:left').replace('font-weight:600', 'font-weight:700')
        body += '<tr>' + ''.join(f'<td style="{td0 if k == 0 else td}">{esc(c)}</td>' for k, c in enumerate(r)) + '</tr>'
    return (f'<div style="{s(margin="0", padding="0", overflow="auto", border_radius="14px", border=f"1px solid {LINE}")}">'
            f'<table style="{s(width="100%", min_width="420px", margin="0", padding="0", border="0", border_collapse="collapse", border_spacing="0", background="#fff")}">'
            f'<caption style="{s(caption_side="bottom", margin="0", padding="10px 12px", text_align="left", font_family=FB, font_size="12.5px", color=MUTED, line_height="1.5", background="#fff")}">{esc(note)}</caption>'
            f'<thead><tr>{head_}</tr></thead><tbody>{body}</tbody></table></div>')


def calcs():
    gbp = lambda v: f'£{v:,.0f}'
    rate = 12
    terms = [6, 12, 24, 36]
    amounts = [10000, 25000, 50000, 100000, 250000]
    fund_rows = [[gbp(a)] + [gbp(repayment(a, rate, t)) for t in terms] for a in amounts]
    fund = table('', ['Amount', '6 months', '12 months', '24 months', '36 months'], fund_rows,
                 f'Monthly repayment at an example rate of {rate}% a year. Illustration only, not an offer of finance; your rate depends on the lender and your eligibility.')
    takings = [5000, 10000, 20000, 50000, 100000]
    cuts = [0.2, 0.5, 1.0]
    fee_rows = [[gbp(t)] + [gbp(t * c / 100 * 12) for c in cuts] for t in takings]
    fees = table('', ['Card takings / month', '0.2% lower', '0.5% lower', '1% lower'], fee_rows,
                 'Yearly saving if your card fee rate drops by that much. Illustration only, not a quote.')

    def card(ic, h, p, tbl, cta, href):
        return (f'<div style="{s(float="left", width=cols((2, 960), g=28), margin="0 14px 28px", padding="0")}">'
                f'<div style="{s(margin="0", padding="clamp(20px,3cqi,32px)", border_radius="24px", background="#fff", border=f"1px solid {LINE}", box_shadow=SH)}">'
                + iconrow(f'<span style="{s(float="left", width="48px", height="48px", border_radius="14px", background=BLUE_100, line_height="0", text_align="center")}">{icon(ic, "royal", 24, s(margin="12px"))}</span>',
                          f'<h3 style="{T_RESET};{s(font_family=FH, font_size="20px", font_weight="800", color=NAVY, line_height="1.3", padding="2px 0 0")}">{h}</h3>'
                          f'<p style="{T_RESET};{s(margin="4px 0 0", font_family=FB, font_size="14.5px", line_height="1.6", color=TEXT)}">{p}</p>', pad=64, top='0') +
                f'<div style="{s(margin="22px 0 20px", padding="0")}">{tbl}</div>'
                + row(btn(cta, href)) +
                '</div></div>')
    inner = (head('Business Calculators', 'Plan Smarter With Our ' + hl('Quick Guides'),
                  'See typical monthly funding repayments, and how much a lower card fee rate could save you each year. Ask us for an exact figure.')
             + f'<div style="{s(margin="0 -14px", padding="0", overflow="hidden")}">'
             + card('pound', 'Business Funding Repayments', 'What you might repay each month, by amount and term.', fund, 'Apply for Funding', '/business-funding/')
             + card('card', 'Card Fee Savings', 'What you could save a year by switching to a lower rate.', fees, 'Get a Free Fee Review', '/contact-us/')
             + '</div>')
    return section(wrap(inner), bg=SOFT, id_='bcpay-calculator')


# ---------- 4. Numbers ----------
def stats():
    items = [('store', '1,500+', 'UK businesses supported'), ('coins', '£10M+', 'Funding arranged'),
             ('handshake', '25+', 'Trusted providers & lenders'), ('headset', '24/7', 'UK-based customer support')]
    cells = ''.join(
        f'<div style="{s(float="left", width=cols((4, 1000), (2, 520), g=24), margin="12px", padding="0")}">'
        f'<div style="{s(position="relative", margin="0", padding="4px 0 4px 84px", min_height="64px")}">'
        f'<span style="{s(position="absolute", left="0", top="0", width="62px", height="62px", border_radius="50%", background="#00a5ea29", border="1px solid #00a5ea73", line_height="0", text_align="center")}">{icon(ic, "light", 28, s(margin="17px"))}</span>'
        f'<div style="{s(margin="0", font_family=FH, font_size="clamp(30px,3cqi,40px)", font_weight="800", color="#fff", line_height="1.05")}">{esc(n)}</div>'
        f'<div style="{s(margin="4px 0 0", font_family=FB, font_size="15px", color="#b9c7e2", line_height="1.4")}">{esc(t)}</div></div></div>'
        for ic, n, t in items)
    return section(wrap(grid([cells])), bg=f'linear-gradient(120deg,{NAVY_D} 0%,{NAVY} 55%,#0e3c86 100%)', pad='clamp(48px,6cqi,76px) 0')


# ---------- 5. Featured services ----------
SERVICES = [
    ('service-card-machines.jpg', 'Portable, mobile and countertop card machines', 'Most popular', 'card', 'Card Machines', 'Portable, mobile and countertop card machines that accept chip & PIN, contactless, Apple Pay and Google Pay.', ['Lower transaction fees', 'Simple application', 'Fast setup'], '/card-machines/'),
    ('service-business-funding.jpg', 'Smiling café owner', 'Unsecured', 'pound', 'Business Funding', 'Flexible, unsecured funding for eligible UK small businesses, arranged with trusted lenders and financial institutions.', ['Easy documentation', 'Fast pay out', 'No security or mortgage required'], '/business-funding/'),
    ('service-pos-system.jpg', 'POS system with receipt printer and card machine', None, 'monitor', 'POS System', 'An all-in-one POS solution to run your counter, suitable for retail, hospitality and more.', ['Manage sales & stock', 'Multiple payment options', 'Better customer experience'], '/pos-system/'),
    ('service-online-payments.jpg', 'Order and pay at table, payment link and payment app', None, 'globe', 'Online Payments', 'Secure, flexible ways to get paid online, over the phone and at the table.', ['Payment gateway & links', 'Phone payment & app', 'Order and pay at table'], '/online-payments/'),
]


def services():
    cards = []
    for src, alt, tag, ic, h, d, bullets, href in SERVICES:
        lis = ''.join(f'<li style="{s(margin="0 0 8px", padding="0", list_style_type="none", background="none")}">'
                      + iconrow(icon('check', 'blue', 16), f'<span style="{s(font_family=FB, font_size="14px", font_weight="600", color=NAVY, line_height="1.45")}">{esc(b)}</span>', pad=26, top='2px') + '</li>'
                      for b in bullets)
        cards.append(
            f'<div style="{s(float="left", width=cols((4, 1060), (2, 620), g=24), margin="0 12px 24px", padding="0")}">'
            # equal heights in the 2-column layout so floats line up
            f'<div style="{s(position="relative", margin="0", padding="0 0 76px", min_height=when_wide(600, "600px"), border_radius="24px", background="#fff", border=f"1px solid {LINE}", overflow="hidden", box_shadow=SH)}">'
            f'<a href="{href}" style="{s(position="relative", float="left", width="100%", margin="0", padding="0", line_height="0", border="0")}">'
            + img(src, alt, 720, 480, s(width='100%', aspect_ratio='3/2', object_fit='cover', border_radius='0')) +
            (f'<span style="{s(position="absolute", left="14px", top="14px", margin="0", padding="5px 12px", border_radius="999px", background=NAVY, color="#fff", font_family=FB, font_size="12px", font_weight="700", letter_spacing=".04em", line_height="1.4")}">{esc(tag)}</span>' if tag else '') +
            '</a>'
            f'<div style="{s(clear="both", position="relative", margin="0", padding="44px 24px 0")}">'
            f'<span style="{s(position="absolute", top="-30px", left="24px", width="60px", height="60px", border_radius="18px", background=BLUE, box_shadow="0 14px 26px -12px #00a5eae6", line_height="0", text_align="center")}">{icon(ic, "white", 28, s(margin="16px"))}</span>'
            f'<h3 style="{T_RESET};{s(font_family=FH, font_size="20px", font_weight="800", color=NAVY, line_height="1.25")}">{esc(h)}</h3>'
            f'<p style="{T_RESET};{s(margin="10px 0 14px", font_family=FB, font_size="15px", line_height="1.6", color=TEXT)}">{esc(d)}</p>'
            f'<ul style="{s(margin="0", padding="0", list_style_type="none")}">{lis}</ul></div>'
            f'<div style="{s(position="absolute", left="24px", right="24px", bottom="22px", margin="0", padding="16px 0 0", border_top=f"1px dashed {LINE}")}">{link("Explore More", href)}</div>'
            '</div></div>')
    chip = lambda ic, t, h: (f'<a href="{h}" style="{s(float="left", margin="0 8px 10px 0", padding="9px 16px", border_radius="999px", background="#fff", border=f"1px solid {LINE}", color=NAVY, font_family=FB, font_size="14px", font_weight="600", text_decoration="none", line_height="1.3")}">'
                             + icon(ic, 'blue', 16, s(margin='0 8px 0 0', vertical_align='-3px')) + esc(t) + '</a>')
    also = center(f'<span style="{s(float="left", margin="0 10px 10px 0", padding="10px 0", font_family=FB, font_weight="600", font_size="15px", color=NAVY, line_height="1.3")}">Also available:</span>'
                  + chip('lock', 'Payment Gateway', '/payment-gateway/') + chip('link', 'Payment Link', '/pay-by-link/') + chip('mobile', 'Payment App', '/payment-app/')
                  + chip('phone', 'Phone Payment', '/phone-payment/') + chip('utensils', 'Order & Pay at Table', '/order-and-pay-at-table/'), margin='16px auto 0')
    inner = head('Our Services', 'Featured Services for ' + hl('Growing Businesses'),
                 'Everything you need to take payments and fund your next step, arranged through trusted UK providers and financial institutions.') + grid(cards) + also
    return section(wrap(inner), id_='bcpay-services')


# ---------- 6. Why choose us ----------
WHY_L = [('trend', 'Lower Transaction Fees', 'We compare trusted providers to find competitive rates for the way you trade.'),
         ('file', 'Simple Application', 'Easy documentation and a short application. We guide you through every step.'),
         ('zap', 'Fast Setup & Pay Out', "Quick card machine setup and fast funding pay outs once you're approved.")]
WHY_R = [('shield', 'No Security Required', 'Unsecured funding with no security or mortgage required for eligible businesses.'),
         ('handshake', 'Partnered With Trusted Providers', 'We work with established payment providers, lenders and financial institutions.'),
         ('headset', 'Dedicated UK Support', 'A friendly UK team that stays with you, from application to aftercare.')]


def why():
    def feat(ic, t, d):
        return (f'<div style="{s(position="relative", margin="0 0 20px", padding="22px 22px 22px 98px", min_height="74px", border_radius="16px", background="#fff", border=f"1px solid {LINE}")}">'
                f'<span style="{s(position="absolute", left="22px", top="22px", width="60px", height="60px", border_radius="50%", background=BLUE_100, line_height="0", text_align="center")}">{icon(ic, "royal", 28, s(margin="16px"))}</span>'
                f'<h3 style="{T_RESET};{s(font_family=FH, font_weight="700", font_size="17px", color=NAVY, line_height="1.3")}">{esc(t)}</h3>'
                f'<p style="{T_RESET};{s(margin="6px 0 0", font_family=FB, font_size="14.5px", line_height="1.6", color=TEXT)}">{esc(d)}</p></div>')
    col = lambda inner, w: f'<div style="{s(float="left", width=w, margin="0 16px", padding="0")}">{inner}</div>'
    w_side = cols((100 / 35, 1000), g=32)
    w_mid = cols((100 / 30, 1000), g=32)
    media = (f'<div style="{s(position="relative", max_width="420px", margin="0 auto 30px", padding="16px", border="2px dashed #5cc8f5b3", border_radius="210px 210px 30px 30px")}">'
             + img('hero-terminal.jpg', 'Customer paying by contactless card on a card machine', 1501, 1159, s(width='100%', aspect_ratio='3/4', object_fit='cover', object_position='46% 50%', border_radius='190px 190px 22px 22px', box_shadow=SH_LG)) +
             f'<div style="{s(position="absolute", left="50%", bottom="-8px", width="250px", margin="0 0 0 -125px", padding="10px 14px 10px 62px", border_radius="999px", background="#fff", box_shadow=SH_LG, text_align="left")}">'
             f'<span style="{s(position="absolute", left="10px", top="10px", width="42px", height="42px", border_radius="50%", background=BLUE, line_height="0", text_align="center")}">{icon("award", "white", 20, s(margin="11px"))}</span>'
             f'<div style="{s(margin="0", font_family=FH, font_weight="700", font_size="14px", color=NAVY, line_height="1.3")}">Trusted Partners</div>'
             f'<div style="{s(margin="0", font_family=FB, font_size="12.5px", color=MUTED, line_height="1.3")}">Providers &amp; financial institutions</div></div></div>')
    inner = (head('Why Choose Us', 'Why UK Businesses Choose ' + hl('Be\u2011Connect Pay'),
                  'We do the legwork with trusted providers and lenders, so you get the right solution at the right price, with people you can actually talk to.')
             + f'<div style="{s(margin="0 -16px", padding="0", overflow="hidden")}">'
             + col(''.join(feat(*f) for f in WHY_L), w_side) + col(media, w_mid) + col(''.join(feat(*f) for f in WHY_R), w_side) + '</div>')
    return section(wrap(inner), bg=SOFT, id_='bcpay-why')


# ---------- 7. Industries ----------
INDUSTRIES = [('sector-restaurant.jpg', 'utensils', 'Restaurants & Pubs', 'POS, pay at table and portable card machines.'),
              ('sector-beauty.jpg', 'scissors', 'Salons & Beauty', 'Take deposits by payment link.'),
              ('sector-cafe.jpg', 'coffee', 'Cafés & Coffee Shops', 'Fast contactless payments.'),
              ('sector-retail.jpg', 'bag', 'Retail Shops', 'Countertop terminals and POS.'),
              ('sector-takeaway.jpg', 'pizza', 'Takeaways', 'Counter, phone and online orders.'),
              ('owners-bakery.jpg', 'cake', 'Bakeries & Delis', 'Quick payments and equipment funding.'),
              ('sector-trades.jpg', 'wrench', 'Trades & Services', 'Get paid on the job over 4G.'),
              ('sector-gym.jpg', 'dumbbell', 'Gyms & Fitness', 'Memberships, classes and kit sales.')]


def industries():
    tiles = ''.join(
        f'<a href="/industries/" style="{s(float="left", position="relative", width=cols((4, 1000), (2, 1), g=22), height="clamp(220px,26cqi,330px)", margin="0 11px 22px", padding="0", border_radius="24px", overflow="hidden", text_decoration="none", color="#fff", border="0", background=NAVY)}">'
        + img(src, '', 900, 900, s(position='absolute', left='0', top='0', width='100%', height='100%', max_width='none', object_fit='cover', border_radius='0'))
        + f'<span style="{s(position="absolute", left="0", top="0", width="100%", height="100%", background="linear-gradient(180deg,#06153880 0%,#06153800 32%,#06153814 50%,#061538e6 100%)")}"></span>'
        f'<span style="{s(position="absolute", left="clamp(14px,2cqi,22px)", top="clamp(14px,2cqi,22px)", width="48px", height="48px", border_radius="14px", background="#ffffff29", border="1px solid #ffffff40", line_height="0", text_align="center")}">{icon(ic, "white", 22, s(margin="13px"))}</span>'
        f'<span style="{s(position="absolute", left="clamp(14px,2cqi,22px)", right="clamp(14px,2cqi,22px)", bottom="clamp(14px,2cqi,22px)")}">'
        f'<span style="{s(float="left", width="100%", margin="0", font_family=FH, font_size="clamp(15px,1.7cqi,20px)", font_weight="800", color="#fff", line_height="1.25")}">{esc(t)}</span>'
        f'<span style="{s(float="left", width="100%", margin="6px 0 0", font_family=FB, font_size="13.5px", color="#dce6f5", line_height="1.45", max_height=when_wide(560, "60px"), overflow="hidden")}">{esc(d)}</span>'
        f'<span style="{s(float="left", margin="10px 0 0", font_family=FB, font_size="13.5px", font_weight="700", color="#fff", line_height="1.4")}">Learn more{icon("arrow", "white", 15, s(margin="0 0 0 6px", vertical_align="-3px"))}</span></span>'
        '</a>'
        for src, ic, t, d in INDUSTRIES)
    inner = (head('Industries We Serve', 'Payment Solutions for ' + hl('Every Industry'),
                  'Card machines, POS systems, online payments and funding set up around the way your business trades.')
             + f'<div style="{s(margin="0 -11px", padding="0", overflow="hidden")}">{tiles}</div>'
             + center(btn("View All Industries", "/industries/", "navy"), margin='20px auto 0'))
    return section(wrap(inner), id_='bcpay-industries')


# ---------- 8. Testimonials ----------
REVIEWS = [('D', 'Dhayalan', 'Be-Connect customer', "I have been with Be-Connect for 2 years now and never disappointed. Very reliable and good customer service. I'll recommend it."),
           ('GM', 'Gowtham Manikkam', 'Card machine customer', 'I signed up for a card machine with Be-Connect. Anushka Banerjee helped me with the process. Great service and help by her.'),
           ('DS', 'Denislav Shanov', 'Be-Connect customer', 'Customer care executive Mr. Jason is very helpful and trustworthy. Overall very good experience.')]


def testimonials():
    stars = ''.join(icon('star', 'gold', 18, s(margin='0 3px 0 0')) for _ in range(5))
    cards = ''.join(
        f'<div style="{s(float="left", width=cols((3, 900), g=24), margin="0 12px 24px", padding="0")}">'
        f'<figure style="{s(position="relative", margin="0", padding="30px 28px 26px", min_height=when_wide(900, "330px"), border_radius="24px", background="#fff", border=f"1px solid {LINE}")}">'
        f'{icon("quote", "pale", 48, s(position="absolute", right="24px", top="22px"))}'
        f'<div style="{s(margin="0", line_height="0")}">{stars}</div>'
        f'<p style="{T_RESET};{s(margin="18px 0 0", padding="0 40px 0 0", border="0", font_family=FB, font_style="normal", font_size="16.5px", line_height="1.7", color=NAVY)}">{esc(q)}</p>'
        f'<figcaption style="{s(position="relative", margin="20px 0 0", padding="20px 0 0 66px", min_height="52px", border_top=f"1px solid {LINE}")}">'
        f'<span style="{s(position="absolute", left="0", top="20px", width="52px", height="52px", border_radius="50%", background=f"linear-gradient(135deg,{BLUE},{ROYAL})", color="#fff", font_family=FH, font_weight="800", font_size="17px", line_height="52px", text_align="center")}">{av}</span>'
        f'<span style="{s(float="left", width="100%", margin="5px 0 0", font_family=FH, font_weight="700", color=NAVY, line_height="1.3", font_size="16px")}">{esc(n)}</span>'
        f'<span style="{s(float="left", width="100%", font_family=FB, font_size="13.5px", color=MUTED, line_height="1.4")}">{esc(r)}</span></figcaption>'
        '</figure></div>'
        for av, n, r, q in REVIEWS)
    inner = (head('Testimonials', 'What Our ' + hl('Clients Say'), 'Real words from Be-Connect customers about the service and support they get.') + grid([cards])
             + f'<p style="{T_RESET};{s(margin="10px 0 0", text_align="center", font_family=FB, font_size="15px", color=TEXT, line_height="1.6")}">Read more reviews on '
               f'<span style="{s(font_weight="700", color=NAVY)}">{icon("star", "green", 18, s(margin="0 4px 0 2px", vertical_align="-3px"))}Trustpilot</span></p>')
    return section(wrap(inner), bg=SOFT, id_='bcpay-testimonials')


# ---------- 9. Blog ----------
POSTS = [('hero-terminal.jpg', 1501, 1159, 'Customer tapping a card on a card machine', '22', 'Sep', 'card', 'Card Machines', 'How to Choose the Right Card Machine for Your Small Business', 'Portable, mobile or countertop? What to compare before you sign, from fees to connectivity.'),
         ('service-business-funding.jpg', 720, 480, 'Small business owner in his café', '10', 'Sep', 'pound', 'Business Funding', 'Unsecured Business Funding Explained: A Guide for UK Owners', "How unsecured funding works, who is eligible and what documents you'll need to apply."),
         ('service-pos-system.jpg', 720, 480, 'Restaurant POS system with receipt printer', '28', 'Aug', 'monitor', 'POS Systems', '5 Ways a Modern POS System Can Help Your Restaurant Grow', "From faster table turns to smarter stock control, here's what a good POS can do for you.")]


def blog():
    cards = ''.join(
        f'<div style="{s(float="left", width=cols((3, 900), g=26), margin="0 13px 26px", padding="0")}">'
        f'<article style="{s(position="relative", margin="0", padding="0 0 64px", min_height=when_wide(900, "520px"), border_radius="24px", background="#fff", border=f"1px solid {LINE}", overflow="hidden", box_shadow=SH)}">'
        f'<a href="/blog/" style="{s(position="relative", float="left", width="100%", margin="0", padding="0", line_height="0", border="0")}">'
        + img(src, alt, w, h, s(width='100%', aspect_ratio='16/10', object_fit='cover', border_radius='0')) +
        f'<span style="{s(position="absolute", left="18px", bottom="0", margin="0", padding="10px 14px 8px", border_radius="12px 12px 0 0", background=BLUE, color="#fff", text_align="center", line_height="1.1")}">'
        f'<span style="{s(float="left", width="100%", font_family=FH, font_size="22px", font_weight="800")}">{d}</span>'
        f'<span style="{s(float="left", width="100%", font_family=FB, font_size="12px", font_weight="600", letter_spacing=".06em", text_transform="uppercase")}">{m}</span></span></a>'
        f'<div style="{s(clear="both", margin="0", padding="22px 24px 0")}">'
        f'<div style="{s(margin="0 0 10px", font_family=FB, font_size="13.5px", color=MUTED, line_height="1.5")}">{icon("user", "blue", 15, s(margin="0 6px 0 0", vertical_align="-2px"))}Be-Connect Team'
        f'<span style="{s(margin="0 0 0 16px")}">{icon(ic, "blue", 15, s(margin="0 6px 0 0", vertical_align="-2px"))}{esc(cat)}</span></div>'
        f'<h3 style="{T_RESET};{s(font_family=FH, font_size="19px", font_weight="700", line_height="1.35", color=NAVY)}"><a href="/blog/" style="{s(color=NAVY, text_decoration="none", border="0", background="none")}">{esc(t)}</a></h3>'
        f'<p style="{T_RESET};{s(margin="10px 0 0", font_family=FB, font_size="15px", line_height="1.6", color=TEXT)}">{esc(ex)}</p></div>'
        f'<div style="{s(position="absolute", left="24px", bottom="24px", margin="0", padding="0")}">{link("Read More", "/blog/")}</div>'
        '</article></div>'
        for src, w, h, alt, d, m, ic, cat, t, ex in POSTS)
    inner = (head('Our Blog', 'Latest News &amp; ' + hl('Insights'), 'Practical guides on payments, POS and funding for UK small business owners.') + grid([cards])
             + center(btn("View All Posts", "/blog/", "outline"), margin='16px auto 0'))
    return section(wrap(inner), id_='bcpay-blog')


# ---------- CTA ----------
def cta():
    inner = (f'<div style="{s(position="relative", margin="0", padding="clamp(32px,5cqi,56px) clamp(24px,5cqi,64px)", border_radius="28px", overflow="hidden", background=f"linear-gradient(115deg,{BLUE} 0%,#0a86d6 45%,{NAVY} 100%)")}">'
             f'<h2 style="{T_RESET};{s(font_family=FH, font_size="clamp(24px,3cqi,36px)", font_weight="800", line_height="1.2", color="#fff")}">Ready to Grow Your Business?</h2>'
             f'<p style="{T_RESET};{s(margin="10px 0 0", max_width="60ch", font_family=FB, font_size="16.5px", line_height="1.65", color="#e1f2fc")}">Talk to our UK team about card machines, POS systems, online payments or business funding. No obligation.</p>'
             + row(btn("Get a Free Quote", "/contact-us/", "white", style="margin:0 12px 12px 0") + btn("020 7052 7978", "tel:+442070527978", "ghost", arrow=False, ic="phone", style="margin:0 0 12px"), margin='22px 0 0') +
             '</div>')
    return section(wrap(inner), pad='clamp(56px,7cqi,96px) 0')


page = (f'<div id="bcpay-home" style="{s(container_type="inline-size", width="100%", margin="0", padding="0", background="#fff", color=TEXT, font_family=FB, font_size="16px", font_weight="400", line_height="1.7", text_align="left", overflow="hidden")}">'
        + hero() + about() + calcs() + stats() + services() + why() + industries() + testimonials() + blog() + cta() + '</div>')

assert '<style' not in page and '<script' not in page and '<svg' not in page and 'display:' not in page

# icons: SVG files built from the sprite in index.html, one file per colour used
COLORS = {'blue': BLUE, 'royal': ROYAL, 'white': '#ffffff', 'navy': NAVY, 'light': BLUE_L, 'gold': STAR, 'pale': BLUE_100, 'green': '#00b67a'}
FILLED = {'star', 'quote'}
ALIAS = {'arrow': 'arrow', 'trend': 'trend', 'card': 'card', 'bag': 'bag'}
sprite = (ROOT / 'index.html').read_text()
syms = dict(re.findall(r'<symbol id="bcpay-i-([\w-]+)" viewBox="0 0 24 24">(.*?)</symbol>', sprite, re.S))
icon_dir = ROOT / 'assets' / 'icons'
icon_dir.mkdir(exist_ok=True)
for old in icon_dir.glob('*.svg'):
    old.unlink()
used = sorted(set(re.findall(r'icons/([a-z-]+?)-([a-z]+)\.svg', page)))
for name, color in used:
    c = COLORS[color]
    paint = f'fill="{c}" stroke="none"' if name in FILLED else f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    (icon_dir / f'{name}-{color}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {paint}>{syms[name]}</svg>\n')
print(f'{len(used)} icon files in assets/icons/')
dest = ROOT / 'elementor' / 'be-connect-home-paste.html'
dest.write_text(page + '\n')
print(f'wrote {dest.relative_to(ROOT)}: {len(page):,} bytes')
