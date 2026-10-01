"""Builds the Be-Connect homepage: inlines the icon sprite, copies image assets.

Outputs  <repo>/index.html + <repo>/assets/   and   <scratch>/site/index.html + site/assets/ (artifact)
"""
import re, pathlib, shutil
S = pathlib.Path(__file__).parent  # put lucide/ (lucide-static) and package/ (simple-icons) next to this file
REPO = S.parent
LUCIDE, SIMPLE = S / 'lucide/package/icons', S / 'package/icons'
src = (S / 'homepage.src.html').read_text()
DYNAMIC = ['x', 'menu']
used_i = sorted(set(re.findall(r'#i-([a-z0-9-]+)', src)) - {''} | set(DYNAMIC))
used_b = sorted(set(re.findall(r'#b-([a-z0-9-]+)', src)))
syms = []
for n in used_i:
    inner = re.search(r'<svg[^>]*>\s*(.*)</svg>', (LUCIDE / f'{n}.svg').read_text(), re.S).group(1)
    syms.append(f'<symbol id="i-{n}" viewBox="0 0 24 24">' + re.sub(r'\s+/>', '/>', re.sub(r'\s+', ' ', inner)).strip() + '</symbol>')
for n in used_b:
    d = re.search(r'<path d="([^"]+)"', (SIMPLE / f'{n}.svg').read_text()).group(1)
    syms.append(f'<symbol id="b-{n}" viewBox="0 0 24 24"><path d="{d}"/></symbol>')
src = src.replace('<!--SPRITE-->', '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>' + ''.join(syms) + '</defs></svg>')

for out in (REPO,):
    if (out / 'assets').exists(): shutil.rmtree(out / 'assets')
    shutil.copytree(S / 'images', out / 'assets')
head, body = src.split('</style>', 1)
(REPO / 'index.html').write_text('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + head + '</style>\n</head>\n<body>\n' + body.lstrip() + '\n</body>\n</html>\n')
print('icons', len(used_i), 'brands', len(used_b), 'bytes', len(src))
