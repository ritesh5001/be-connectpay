"""Builds elementor/be-connect-home.html: the homepage as one block to paste into an
Elementor HTML widget.

- Every class and id is prefixed with `bcp-`, every element gets a `bcp-t-<tag>` class,
  and all CSS is scoped under `.bcp-home`. There are no bare tag selectors, so the theme
  can't restyle the page and the page can't restyle the rest of the site.
- Images load from IMG_BASE. Change it (or find/replace it) once the images are in the
  WordPress media library.

Run after tools/build.py:  python3 tools/build_elementor.py
"""
import html, pathlib, re
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_BASE = 'https://raw.githubusercontent.com/ritesh5001/be-connectpay/claude/be-connectpay-homepage-redesign-5wiwc8/assets/'
P = 'bcp-'

page = (ROOT / 'index.html').read_text()
head = page.split('<head>', 1)[1].split('</head>', 1)[0]
body = page.split('<body>', 1)[1].rsplit('</body>', 1)[0]
css = re.search(r'<style>(.*?)</style>', head, re.S).group(1)
fonts = re.search(r'<link rel="stylesheet" href="(https://fonts[^"]+)"', head).group(1)
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)

# ---------- CSS ----------
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
tokens = re.search(r':root\{(.*?)\n\}', css, re.S).group(1)
css = css.replace(':root{' + tokens + '\n}', '')
base_start = css.index('*,*::before,*::after{box-sizing:border-box}')
base_end = css.index('\n', css.index(':focus-visible{'))
css = css[:base_start] + css[base_end:]

def sel(s):
    out = []
    for part in s.split(','):
        part = part.strip()
        part = re.sub(r'\.([A-Za-z_][\w-]*)', lambda m: '.' + P + m.group(1), part)
        part = re.sub(r'(^|[\s>+~])([a-z][a-z0-9]*)(?=[\s.:\[>+~]|$)', lambda m: m.group(1) + '.' + P + 't-' + m.group(2), part)
        part = re.sub(r'(^|[\s>+~])\*', r'\1[class*="bcp-"]', part)
        if part.startswith('.bcp-js '):
            part = '.bcp-home.bcp-js ' + part[len('.bcp-js '):]
        else:
            part = '.bcp-home ' + part
        out.append(part)
    return ','.join(out)

def walk(text):
    res, i = [], 0
    while i < len(text):
        j = text.find('{', i)
        if j < 0:
            break
        prelude = text[i:j].strip()
        depth, k = 1, j + 1
        while depth:
            depth += {'{': 1, '}': -1}.get(text[k], 0); k += 1
        inner = text[j + 1:k - 1]
        if prelude.startswith('@keyframes'):
            res.append(prelude.replace('@keyframes ', '@keyframes bcp-') + '{' + inner + '}')
        elif prelude.startswith('@media'):
            res.append(prelude + '{' + walk(inner) + '}')
        else:
            inner = re.sub(r'animation:float\b', 'animation:bcp-float', inner)
            res.append(sel(prelude) + '{' + inner.strip() + '}')
        i = k
    return '\n'.join(res)

scoped = walk(css)

base = f""".bcp-home{{{tokens}
  position:relative;display:block;width:100%;margin:0;padding:0;background:var(--bg);color:var(--text);font-family:var(--f);font-size:16.5px;font-weight:400;font-style:normal;line-height:1.65;letter-spacing:normal;text-transform:none;text-align:left;-webkit-font-smoothing:antialiased;-webkit-text-size-adjust:100%;overflow-x:hidden;overflow-x:clip}}
.bcp-home [class*="bcp-"],.bcp-home [class*="bcp-"]::before,.bcp-home [class*="bcp-"]::after{{box-sizing:border-box}}
.bcp-home [class*="bcp-"]{{margin:0;padding:0;border:0 solid transparent;border-radius:0;background:none;box-shadow:none;outline:0;font:inherit;color:inherit;letter-spacing:inherit;line-height:inherit;text-transform:inherit;text-align:inherit;text-decoration:none;text-shadow:none;list-style:none;min-width:0;float:none;vertical-align:baseline}}
.bcp-home [class*="bcp-"]:hover,.bcp-home [class*="bcp-"]:focus{{text-decoration:none}}
.bcp-home [hidden]{{display:none!important}}
.bcp-home .bcp-t-img{{max-width:100%;height:auto;display:block}}
.bcp-home .bcp-t-svg{{display:inline-block;overflow:visible}}
.bcp-home .bcp-t-h1,.bcp-home .bcp-t-h2,.bcp-home .bcp-t-h3,.bcp-home .bcp-t-h4,.bcp-home .bcp-t-h5{{font-family:var(--f)!important;color:var(--ink);line-height:1.1;letter-spacing:-.025em;font-weight:700;text-wrap:balance}}
.bcp-home .bcp-t-b,.bcp-home .bcp-t-strong{{font-weight:700}}
.bcp-home .bcp-t-small{{font-size:inherit}}
.bcp-home .bcp-t-a{{cursor:pointer}}
.bcp-home .bcp-t-button{{cursor:pointer;-webkit-appearance:none;appearance:none}}
.bcp-home .bcp-t-input{{-webkit-appearance:none;appearance:none}}
.bcp-home .bcp-t-input[type=checkbox],.bcp-home .bcp-t-input[type=radio]{{-webkit-appearance:auto;appearance:auto}}
.bcp-home .bcp-t-ol,.bcp-home .bcp-t-ul{{list-style:none}}
.bcp-home [class*="bcp-"]:focus-visible{{outline:3px solid var(--sky);outline-offset:3px;border-radius:8px}}
@media (prefers-reduced-motion: reduce){{ .bcp-home [class*="bcp-"],.bcp-home [class*="bcp-"]::before,.bcp-home [class*="bcp-"]::after{{animation:none!important;transition:none!important}} }}
body.admin-bar .bcp-home .bcp-header{{top:32px}}
@media (max-width:782px){{ body.admin-bar .bcp-home .bcp-header{{top:46px}} }}
"""
scoped = base + scoped

# ---------- HTML ----------
ids = set(re.findall(r'\sid="([^"]+)"', body))
REF_ATTRS = {'for', 'aria-controls', 'aria-labelledby'}
VOID = {'img', 'input', 'br', 'hr', 'meta', 'link', 'source'}

class Rewriter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out, self.svg = [], 0
    def attrs(self, tag, attrs):
        d, order = {}, []
        for k, v in attrs:
            if k not in d: order.append(k)
            d[k] = v
        if self.svg == 0 or tag == 'svg':
            cls = [P + c for c in (d.get('class') or '').split()]
            cls.append(P + 't-' + tag)
            d['class'] = ' '.join(cls)
            if 'class' not in order: order.insert(0, 'class')
        elif d.get('class'):
            d['class'] = ' '.join(P + c for c in d['class'].split())
        if d.get('id'):
            d['id'] = P + d['id']
        for k in REF_ATTRS:
            if d.get(k) in ids: d[k] = P + d[k]
        if d.get('href', '').startswith('#') and d['href'][1:] in ids:
            d['href'] = '#' + P + d['href'][1:]
        if tag == 'img' and d.get('src', '').startswith('assets/'):
            d['src'] = IMG_BASE + d['src'][len('assets/'):]
        s = []
        for k in order:
            v = d[k]
            s.append(k if v is None else f'{k}="{html.escape(v, quote=True)}"')
        return (' ' + ' '.join(s)) if s else ''
    def handle_starttag(self, tag, attrs):
        a = self.attrs(tag, attrs)
        if tag == 'svg': self.svg += 1
        self.out.append(f'<{tag}{a}>')
        if tag in VOID and tag != 'svg': pass
    def handle_startendtag(self, tag, attrs):
        a = self.attrs(tag, attrs)
        self.out.append(f'<{tag}{a}/>')
    def handle_endtag(self, tag):
        if tag == 'svg': self.svg -= 1
        self.out.append(f'</{tag}>')
    def handle_data(self, data): self.out.append(data)
    def handle_entityref(self, name): self.out.append(f'&{name};')
    def handle_charref(self, name): self.out.append(f'&#{name};')
    def handle_comment(self, data): pass

r = Rewriter(); r.feed(body); r.close()
markup = ''.join(r.out)
markup = re.sub(r'\n\s*\n+', '\n', markup).strip()

# ---------- JS ----------
js = r"""
(function(){
  var root=document.getElementById('bcp-home');
  if(!root||root.getAttribute('data-bcp-ready'))return;
  root.setAttribute('data-bcp-ready','1');
  root.classList.add('bcp-js');
  var IMG='__IMG__';
  function $(id){return document.getElementById('bcp-'+id);}
  function $$(s){return root.querySelectorAll(s);}
  function icon(n){return '<svg class="bcp-ic bcp-arrow bcp-t-svg"><use href="#bcp-i-'+n+'"/></svg>';}

  /* Header + mobile bar */
  var header=$('header'),mbar=$('mbar');
  function onScroll(){var y=window.pageYOffset||document.documentElement.scrollTop;header.classList.toggle('bcp-solid',y>40);mbar.classList.toggle('bcp-show',y>600);}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  /* Smooth scrolling for in-page links */
  $$('a[href^="#bcp-"]').forEach(function(a){if(a.hasAttribute('data-quote'))return;a.addEventListener('click',function(e){var t=document.getElementById(a.getAttribute('href').slice(1));if(!t)return;e.preventDefault();var top=t.getBoundingClientRect().top+window.pageYOffset-(t.id==='bcp-top'?0:70);window.scrollTo({top:top,behavior:'smooth'});});});

  /* Drawer */
  var drawer=$('drawer'),menuBtn=$('menuBtn');
  function setDrawer(o){drawer.classList.toggle('bcp-open',o);drawer.setAttribute('aria-hidden',!o);menuBtn.setAttribute('aria-expanded',o);document.body.style.overflow=o?'hidden':'';}
  menuBtn.addEventListener('click',function(){setDrawer(true);});
  $('closeBtn').addEventListener('click',function(){setDrawer(false);});
  drawer.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setDrawer(false);});});

  /* Reveal on scroll (content stays visible without IntersectionObserver) */
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.remove('bcp-pre');io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px'});
    $$('.bcp-rv').forEach(function(el){if(el.getBoundingClientRect().top>window.innerHeight){el.classList.add('bcp-pre');io.observe(el);}});
  }

  /* Card machine switcher */
  var M=[
    {img:'terminal-a920.png',w:273,h:579,alt:'Be-Connect A920 mobile card machine',label:'Mobile · 4G',s:[['Connection','Built-in GPRS SIM'],['Coverage','Anywhere with 4G'],['Battery','Long battery life']]},
    {img:'terminal-move.png',w:155,h:328,alt:'Be-Connect smart card terminal',label:'Smart terminal',s:[['Speed','Fast, secure payments'],['Reporting','Real time on screen'],['Setup','Easy set up']]},
    {img:'terminal-compact.png',w:135,h:288,alt:'Compact countertop card machine',label:'Countertop',s:[['Design','Small and compact'],['Connection','Broadband or phone'],['Receipts','Fast receipt printing']]}
  ];
  var tabs=$$('.bcp-mtab'),mImg=$('mImg');
  tabs.forEach(function(t){t.addEventListener('click',function(){
    var m=M[+t.getAttribute('data-m')];tabs.forEach(function(x){x.setAttribute('aria-selected',x===t);});
    mImg.classList.add('bcp-swap');
    setTimeout(function(){mImg.src=IMG+m.img;mImg.width=m.w;mImg.height=m.h;mImg.alt=m.alt;mImg.classList.remove('bcp-swap');},220);
    $('mLabel').textContent=m.label;
    m.s.forEach(function(p,i){$('s'+(i+1)+'k').textContent=p[0];$('s'+(i+1)).textContent=p[1];});
  });});

  /* Fee checker */
  var gbp=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}),gbp0=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',maximumFractionDigits:0}),n0=new Intl.NumberFormat('en-GB');
  var sT=$('sTurn'),sX=$('sTx'),sF=$('sFees');
  function set(id,v){$(id).textContent=v;}
  function calc(){
    var t=+sT.value,x=+sX.value,f=+sF.value;
    [sT,sX,sF].forEach(function(r){r.style.setProperty('--p',((r.value-r.min)/(r.max-r.min)*100)+'%');});
    set('oTurn',gbp0.format(t));set('oTx',n0.format(x));set('oFees',gbp0.format(f));
    set('rRate',(f/t*100).toFixed(2)+'%');set('rYear',gbp0.format(f*12));set('rPer',gbp.format(f/x));set('rAvg',gbp.format(t/x));set('rTenth',gbp0.format(t*.001*12));
  }
  [sT,sX,sF].forEach(function(r){r.addEventListener('input',calc);});calc();

  /* Quote dialog */
  var q=$('quote'),form=$('qForm'),steps=form.querySelectorAll('[data-s]'),prog=form.querySelectorAll('.bcp-q-prog .bcp-t-i'),cur=1;
  var back=$('qBack'),next=$('qNext'),msg=$('qMsg'),nav=$('qNav'),last=null;
  function show(n){cur=n;steps.forEach(function(s){s.hidden=+s.getAttribute('data-s')!==n;});prog.forEach(function(p,i){p.classList.toggle('bcp-on',i<n);});back.hidden=n===1||n>3;nav.hidden=n>3;msg.textContent='';
    next.innerHTML=(n===3?'Get my quote':'Continue')+' '+icon('arrow-right');}
  function open(e){if(e)e.preventDefault();last=document.activeElement;show(1);q.classList.add('bcp-open');q.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';setTimeout(function(){next.focus();},50);}
  function close(){q.classList.remove('bcp-open');q.setAttribute('aria-hidden','true');document.body.style.overflow='';if(last)last.focus();}
  $$('[data-quote]').forEach(function(a){a.addEventListener('click',open);});
  $('qClose').addEventListener('click',close);
  q.addEventListener('click',function(e){if(e.target===q)close();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&q.classList.contains('bcp-open'))close();});
  back.addEventListener('click',function(){show(cur-1);});
  form.addEventListener('submit',function(e){
    e.preventDefault();
    if(cur===1&&!form.querySelector('[name=need]:checked')){msg.textContent='Choose at least one option to continue.';return;}
    if(cur===3){var nm=$('qn').value.trim(),ct=$('qp').value.trim();
      if(!nm){msg.textContent='Add your name so we know who to ask for.';$('qn').focus();return;}
      if(!ct){msg.textContent='Add a phone number or email so we can send your quote.';$('qp').focus();return;}
      $('qDoneTitle').textContent='Thanks, '+nm.split(' ')[0]+'. You’re all set.';}
    show(cur+1);
  });
})();
""".replace('__IMG__', IMG_BASE)

out = f"""<!-- ============================================================
  Be-Connect Pay homepage for Elementor
  Paste all of this into ONE Elementor "HTML" widget.
  Everything is scoped under .bcp-home and prefixed bcp-, so it
  won't change any other page or element on the site.
  Images load from:
  {IMG_BASE}
  To host them yourself, upload the files in /assets to the media
  library and replace that address everywhere in this code.
============================================================ -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<style>
{scoped}
</style>
<div class="bcp-home" id="bcp-home">
{markup}
</div>
<script>{js}</script>
"""
dest = ROOT / 'elementor' / 'be-connect-home.html'
dest.parent.mkdir(exist_ok=True)
dest.write_text(out)

# sanity checks
bare = [s for s in re.findall(r'(?:^|\})\s*([^{}@]+)\{', scoped) if not s.strip().startswith(('.bcp-home', 'body.admin-bar', 'from', 'to')) and not re.match(r'^[\d%,\s]+$', s.strip())]
assert not bare, bare[:5]
missing = sorted(set(re.findall(r'#(bcp-[\w-]+)', markup + js)) - set(re.findall(r'id="(bcp-[\w-]+)"', markup)))
print('wrote', dest.relative_to(ROOT), len(out), 'bytes; unresolved #refs:', missing)
