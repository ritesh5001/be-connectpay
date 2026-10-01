"""Builds the Be-Connect homepage: inlines the icon sprite and terminal illustrations.

Outputs:
  <repo>/index.html               full standalone document (open in any browser / hand to WordPress dev)
  <scratch>/artifact/be-connect-home.html   body fragment for the Artifact publish
"""
import re, pathlib

S = pathlib.Path(__file__).parent  # unpack lucide-static to lucide/ and simple-icons to package/ here
REPO = S.parent
LUCIDE = S / 'lucide/package/icons'
SIMPLE = S / 'package/icons'

src = (S / 'homepage.src.html').read_text()

# ---- sprite ----
used_i = sorted(set(re.findall(r'#i-([a-z0-9-]+)', src)))
used_b = sorted(set(re.findall(r'#b-([a-z0-9-]+)', src)))
syms = []
for name in used_i:
    svg = (LUCIDE / f'{name}.svg').read_text()
    inner = re.search(r'>\s*(.*)</svg>', svg, re.S).group(1)
    inner = re.sub(r'\s+/>', '/>', re.sub(r'\s+', ' ', inner)).strip()
    syms.append(f'<symbol id="i-{name}" viewBox="0 0 24 24">{inner}</symbol>')
for name in used_b:
    svg = (SIMPLE / f'{name}.svg').read_text()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    syms.append(f'<symbol id="b-{name}" viewBox="0 0 24 24"><path d="{d}"/></symbol>')
sprite = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
          '<defs>' + ''.join(syms) + '</defs></svg>')
src = src.replace('<!--SPRITE-->', sprite)


# ---- terminal illustrations ----
def contactless(cx, cy, s=1.0):
    return (f'<g class="t-cl" transform="translate({cx} {cy}) scale({s})">'
            '<path d="M0 -6a8 8 0 0 1 0 12"/><path d="M5 -10a14 14 0 0 1 0 20"/><path d="M10 -14a20 20 0 0 1 0 28"/></g>')

def keypad(x0, y0, kw, kh, gx, gy, rows=4):
    out = []
    for r in range(rows):
        for c in range(3):
            out.append(f'<rect class="t-key" x="{x0 + c*(kw+gx)}" y="{y0 + r*(kh+gy)}" width="{kw}" height="{kh}" rx="5"/>')
    y = y0 + rows*(kh+gy)
    for c, cls in enumerate(['t-key-r', 't-key-y', 't-key-g']):
        out.append(f'<rect class="{cls}" x="{x0 + c*(kw+gx)}" y="{y}" width="{kw}" height="{kh}" rx="5"/>')
    return ''.join(out)

def screen(x, y, w, h, amount='£24.50'):
    cx = x + w/2
    return (f'<rect class="t-screen" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
            f'<text class="t-ink" x="{cx}" y="{y + h*0.46}" text-anchor="middle" font-size="{w*0.19:.1f}" font-weight="600">{amount}</text>'
            f'<circle cx="{cx - w*0.27:.1f}" cy="{y + h*0.74:.1f}" r="{w*0.055:.1f}" fill="#16A374"/>'
            f'<path d="M{cx - w*0.3:.1f} {y + h*0.74:.1f}l{w*0.022:.1f} {w*0.022:.1f} {w*0.04:.1f} -{w*0.045:.1f}" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text class="t-ink" x="{cx + w*0.07:.1f}" y="{y + h*0.79:.1f}" text-anchor="middle" font-size="{w*0.105:.1f}" font-weight="600" letter-spacing="1">APPROVED</text>')

def receipt(x, y, w, h):
    lines = ''.join(f'<rect class="t-paper-line" x="{x+10}" y="{y+12+i*9}" width="{w-20 - (i%2)*16}" height="3" rx="1.5"/>' for i in range(int((h-16)/9)))
    return f'<rect class="t-paper" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>{lines}'

def countertop(width):
    body = (receipt(40, 4, 80, 56) +
            '<rect class="t-body" x="12" y="48" width="136" height="246" rx="24"/>'
            '<rect class="t-slot" x="36" y="54" width="88" height="6" rx="3"/>' +
            screen(28, 74, 104, 78) + contactless(80, 168, .8) +
            keypad(32, 186, 26, 13, 9, 6) +
            '<rect class="t-slot" x="50" y="286" width="60" height="4" rx="2"/>')
    return f'<svg viewBox="0 0 160 300" width="{width}" role="img" aria-label="Countertop card machine">{body}</svg>'

def portable(width):
    body = (receipt(30, 4, 70, 50) +
            '<rect class="t-body" x="8" y="42" width="114" height="252" rx="22"/>'
            '<rect class="t-slot" x="28" y="48" width="74" height="6" rx="3"/>' +
            screen(20, 66, 90, 84) + contactless(65, 166, .75) +
            keypad(24, 184, 22, 13, 8, 6) +
            '<rect class="t-slot" x="40" y="286" width="50" height="4" rx="2"/>')
    return f'<svg viewBox="0 0 130 300" width="{width}" role="img" aria-label="Portable card machine">{body}</svg>'

def mobile(width):
    body = ('<rect class="t-body" x="6" y="6" width="98" height="188" rx="20"/>' +
            screen(16, 20, 78, 92, '£9.80') + contactless(55, 128, .65) +
            keypad(20, 144, 18, 6, 11, 4, rows=1) +
            '<rect class="t-key" x="20" y="164" width="70" height="12" rx="6"/>'
            '<rect class="t-slot" x="34" y="186" width="42" height="4" rx="2"/>')
    return f'<svg viewBox="0 0 110 200" width="{width}" role="img" aria-label="Mobile card machine">{body}</svg>'

T = {'countertop': countertop, 'portable': portable, 'mobile': mobile}
src = re.sub(r'<!--T:(\w+):(\d+)-->', lambda m: T[m.group(1)](m.group(2)), src)

assert '<!--' not in src.replace('<!-- ', ''), 'unreplaced marker'

# ---- outputs ----
art = S / 'artifact'
art.mkdir(exist_ok=True)
(art / 'be-connect-home.html').write_text(src)

full = ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + src.split('</style>', 1)[0] + '</style>\n</head>\n<body>\n'
        + src.split('</style>', 1)[1].lstrip() + '\n</body>\n</html>\n')
(REPO / 'index.html').write_text(full)
print('sprite icons:', len(used_i), 'brands:', len(used_b), 'bytes:', len(src))
