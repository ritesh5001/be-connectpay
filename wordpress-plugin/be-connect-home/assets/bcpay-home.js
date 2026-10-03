(function(){
  var root=document.getElementById('bcpay-home');
  if(!root||root.getAttribute('data-bcpay-ready'))return;
  root.setAttribute('data-bcpay-ready','1');
  root.classList.add('bcpay-js');
  function $(id){return document.getElementById('bcpay-'+id);}
  function $$(sel,ctx){return Array.prototype.slice.call((ctx||root).querySelectorAll(sel));}
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Header shadow + back to top (header/footer can be switched off in the plugin) */
  var header=$('header'),totop=$('totop');
  function onScroll(){var y=window.pageYOffset||document.documentElement.scrollTop;if(header)header.classList.toggle('bcpay-is-stuck',y>60);totop.classList.toggle('bcpay-show',y>700);}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  totop.addEventListener('click',function(e){e.preventDefault();window.scrollTo({top:root.getBoundingClientRect().top+window.pageYOffset,behavior:reduce?'auto':'smooth'});});
  var yr=$('year');if(yr)yr.textContent=new Date().getFullYear();

  /* Menu dropdowns: hover on desktop, tap to open on touch screens */
  var dds=$$('.bcpay-has-dd');
  function closeDd(except){dds.forEach(function(d){if(d!==except){d.classList.remove('bcpay-is-open');d.querySelector('.bcpay-nav-link').setAttribute('aria-expanded','false');}});}
  dds.forEach(function(d){
    var link=d.querySelector('.bcpay-nav-link');
    link.addEventListener('click',function(e){
      if(window.matchMedia('(hover: none)').matches&&!d.classList.contains('bcpay-is-open')){e.preventDefault();closeDd(d);d.classList.add('bcpay-is-open');link.setAttribute('aria-expanded','true');}
    });
    d.addEventListener('keydown',function(e){if(e.key==='Escape'){closeDd();link.focus();}});
  });
  document.addEventListener('click',function(e){if(!e.target.closest||!e.target.closest('.bcpay-has-dd'))closeDd();});

  /* Mobile drawer */
  var burger=$('burger'),drawer=$('drawer');
  if(burger&&drawer){
    var setMenu=function(open){root.classList.toggle('bcpay-menu-open',open);drawer.setAttribute('aria-hidden',!open);burger.setAttribute('aria-expanded',open);document.documentElement.style.overflow=open?'hidden':'';if(open)$('close').focus();};
    burger.addEventListener('click',function(){setMenu(true);});
    $('close').addEventListener('click',function(){setMenu(false);burger.focus();});
    $('overlay').addEventListener('click',function(){setMenu(false);});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&root.classList.contains('bcpay-menu-open'))setMenu(false);});
    $$('.bcpay-msub-btn').forEach(function(btn){var sub=document.getElementById(btn.getAttribute('aria-controls'));btn.addEventListener('click',function(){var o=sub.hidden;sub.hidden=!o;btn.setAttribute('aria-expanded',o);});});
  }

  /* Hero slider */
  (function(){
    var track=$('hero-track'),slides=$$('.bcpay-slide',track),dots=$$('.bcpay-hero-dot',track),mcta=$('hero-mcta'),cur=0,timer=null,DELAY=6000;
    function go(n){
      cur=(n+slides.length)%slides.length;
      slides.forEach(function(s,i){var on=i===cur;s.classList.toggle('bcpay-is-active',on);s.setAttribute('aria-hidden',!on);var a=s.querySelector('.bcpay-hero-cta');if(a)a.tabIndex=on?0:-1;});
      dots.forEach(function(d,i){d.setAttribute('aria-current',i===cur?'true':'false');});
      var link=slides[cur].querySelector('.bcpay-hero-cta');if(link&&mcta)mcta.href=link.getAttribute('href');
    }
    function play(){if(reduce)return;stop();timer=setInterval(function(){go(cur+1);},DELAY);}
    function stop(){if(timer){clearInterval(timer);timer=null;}}
    $('hero-prev').addEventListener('click',function(){go(cur-1);play();});
    $('hero-next').addEventListener('click',function(){go(cur+1);play();});
    dots.forEach(function(d,i){d.addEventListener('click',function(){go(i);play();});});
    track.addEventListener('mouseenter',stop);track.addEventListener('mouseleave',play);
    track.addEventListener('focusin',stop);track.addEventListener('focusout',play);
    track.addEventListener('keydown',function(e){if(e.key==='ArrowLeft'){go(cur-1);}else if(e.key==='ArrowRight'){go(cur+1);}});
    var sx=null,sy=0;
    track.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;stop();},{passive:true});
    track.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy))go(dx<0?cur+1:cur-1);sx=null;play();},{passive:true});
    document.addEventListener('visibilitychange',function(){document.hidden?stop():play();});
    go(0);play();
  })();

  /* Calculators */
  var gbp0=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',maximumFractionDigits:0}),
      gbp2=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',minimumFractionDigits:2,maximumFractionDigits:2}),
      n0=new Intl.NumberFormat('en-GB');
  function set(id,v){$(id).textContent=v;}
  function fill(r){r.style.setProperty('--bcpay-p',((r.value-r.min)/(r.max-r.min)*100)+'%');}
  /* keeps a range slider and its number box in sync, then recalculates */
  function pair(id,cb){
    var r=$(id),n=$(id+'-n');
    r.addEventListener('input',function(){n.value=r.value;fill(r);cb();});
    n.addEventListener('input',function(){var v=parseFloat(n.value);if(isNaN(v))return;r.value=Math.min(Math.max(v,+r.min),+r.max);fill(r);cb();});
    n.addEventListener('change',function(){var v=parseFloat(n.value);if(isNaN(v))v=+r.value;v=Math.min(Math.max(v,+r.min),+r.max);n.value=v;r.value=v;fill(r);cb();});
    fill(r);
    return function(){var v=parseFloat(n.value);return isNaN(v)?+r.value:Math.min(Math.max(v,+r.min),+r.max);};
  }
  var fAmt=pair('f-amt',fund),fTerm=pair('f-term',fund),fRate=pair('f-rate',fund);
  var donut=$('f-donut'),C=2*Math.PI*50;
  function fund(){
    var p=fAmt(),n=Math.round(fTerm()),r=fRate()/100/12;
    var m=r>0?p*r/(1-Math.pow(1+r,-n)):p/n,total=m*n,interest=total-p;
    set('f-month',gbp0.format(m));set('f-p',gbp0.format(p));set('f-i',gbp0.format(interest));set('f-t',gbp0.format(total));
    donut.setAttribute('stroke-dasharray',(C*p/total).toFixed(1)+' '+C.toFixed(1));
  }
  var cTurn=pair('c-turn',fees),cTx=pair('c-tx',fees),cFee=pair('c-fee',fees);
  function fees(){
    var t=cTurn(),x=cTx(),f=cFee();
    set('c-rate',(f/t*100).toFixed(2)+'%');set('c-year',gbp0.format(f*12));set('c-per',gbp2.format(f/x));set('c-avg',gbp2.format(t/x));set('c-tenth',gbp0.format(t*0.001*12));
  }
  fund();fees();

  /* Calculator tabs */
  var tabs=$$('.bcpay-tab');
  function selectTab(t){tabs.forEach(function(x){var on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});}
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){selectTab(t);});
    t.addEventListener('keydown',function(e){var k=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(!k)return;var nt=tabs[(i+k+tabs.length)%tabs.length];selectTab(nt);nt.focus();});
  });

  /* Testimonials slider */
  (function(){
    var track=$('t-track'),cards=$$('.bcpay-testi',track),dotsBox=$('t-dots'),prev=$('t-prev'),next=$('t-next'),dots=[];
    function step(){return cards.length>1?cards[1].offsetLeft-cards[0].offsetLeft:track.clientWidth;}
    function idx(){return Math.round(track.scrollLeft/step());}
    cards.forEach(function(c,i){var b=document.createElement('button');b.type='button';b.className='bcpay-dot';b.setAttribute('aria-label','Show testimonial '+(i+1));b.addEventListener('click',function(){track.scrollTo({left:i*step()});});dotsBox.appendChild(b);dots.push(b);});
    function update(){var i=idx(),max=track.scrollWidth-track.clientWidth-4,fits=max<=0;$('t-arrows').hidden=fits;dotsBox.hidden=fits;dots.forEach(function(d,k){d.setAttribute('aria-current',k===i?'true':'false');});prev.disabled=track.scrollLeft<=4;next.disabled=track.scrollLeft>=max;}
    prev.addEventListener('click',function(){track.scrollBy({left:-step()});});
    next.addEventListener('click',function(){track.scrollBy({left:step()});});
    track.addEventListener('scroll',function(){window.requestAnimationFrame(update);},{passive:true});
    window.addEventListener('resize',update);update();
  })();

  /* Count-up numbers + reveal on scroll */
  function countUp(el){
    var end=+el.getAttribute('data-bcpay-count'),pre=el.getAttribute('data-bcpay-prefix')||'',suf=el.getAttribute('data-bcpay-suffix')||'',t0=null,dur=1600;
    if(reduce){el.textContent=pre+n0.format(end)+suf;return;}
    function tick(ts){if(!t0)t0=ts;var k=Math.min((ts-t0)/dur,1),e=1-Math.pow(1-k,3);el.textContent=pre+n0.format(Math.round(end*e))+suf;if(k<1)requestAnimationFrame(tick);}
    requestAnimationFrame(tick);
  }
  var counters=$$('[data-bcpay-count]');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target;if(el.hasAttribute('data-bcpay-count'))countUp(el);else el.classList.remove('bcpay-pre');io.unobserve(el);});},{rootMargin:'0px 0px -8% 0px'});
    counters.forEach(function(el){io.observe(el);});
    $$('.bcpay-rv').forEach(function(el){if(el.getBoundingClientRect().top>window.innerHeight){el.classList.add('bcpay-pre');io.observe(el);}});
  }
})();
