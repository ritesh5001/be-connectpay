"""Builds elementor/be-connect-home.html from index.html.

The output is the whole homepage as one block for an Elementor "HTML" widget:
fonts + <style> + markup + <script>, with image paths pointed at IMG_BASE.
Everything in index.html is already prefixed "bcpay-" and scoped to .bcpay-home,
so no class rewriting is needed here.

Run after editing index.html:  python3 tools/build_elementor.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_BASE = 'https://cdn.jsdelivr.net/gh/ritesh5001/be-connectpay@main/assets/'

page = (ROOT / 'index.html').read_text()
head = page.split('<!--BCPAY:START-->', 1)[1].split('<!--BCPAY:HEAD-END-->', 1)[0].strip()
body = page.split('<!--BCPAY:BODY-START-->', 1)[1].split('<!--BCPAY:BODY-END-->', 1)[0].strip()
code = (head + '\n' + body).replace('src="assets/', 'src="' + IMG_BASE)

out = f"""<!-- ==========================================================================
  Be-Connect Pay homepage for Elementor
  1. Page settings > Page Layout: "Elementor Canvas" (this code has its own
     header and footer). Or keep your theme layout and delete the TOP BAR,
     HEADER, Mobile menu and FOOTER blocks below.
  2. Add ONE section/container set to Full Width with 0 padding and 0 gap,
     drop in an "HTML" widget and paste everything in this file.
  All classes and ids start with "bcpay-" and every CSS rule is scoped to
  .bcpay-home, so nothing here affects other pages or widgets.
  Images load from: {IMG_BASE}
  To host them in WordPress, upload /assets to the Media Library and
  find/replace that address with your uploads folder URL.
=========================================================================== -->
{code}
"""
dest = ROOT / 'elementor' / 'be-connect-home.html'
dest.parent.mkdir(exist_ok=True)
dest.write_text(out)

# sanity checks: every rule scoped, every #ref resolvable, every image present
css = re.search(r'<style>(.*?)</style>', out, re.S).group(1)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
sels = [s.strip() for s in re.findall(r'(?:^|[{}])\s*([^{}@]+?)\s*\{', css)]
bad = [s for s in sels if not all(p.strip().startswith(('.bcpay-home', 'body.admin-bar .bcpay-home')) or re.fullmatch(r'[\d.%\s,]+|from|to', p.strip()) for p in s.split(','))]
assert not bad, bad[:5]
ids = set(re.findall(r'\sid="([^"]+)"', out))
refs = set(re.findall(r'href="#([^"]+)"', out)) | {'bcpay-' + x for x in re.findall(r"\$\('([\w-]+)'\)", out)}
assert refs <= ids, sorted(refs - ids)
assert all(i.startswith('bcpay-') for i in ids), [i for i in ids if not i.startswith('bcpay-')]
classes = {c for v in re.findall(r'\sclass="([^"]+)"', out) for c in v.split()}
assert all(c.startswith('bcpay-') for c in classes), sorted(c for c in classes if not c.startswith('bcpay-'))
imgs = set(re.findall(re.escape(IMG_BASE) + r'([\w.-]+)', out))
missing = [i for i in imgs if not (ROOT / 'assets' / i).exists()]
assert not missing, missing
print(f'wrote {dest.relative_to(ROOT)}: {len(out):,} bytes, {len(classes)} classes, {len(ids)} ids, {len(imgs)} images')
