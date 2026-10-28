(function () {
  // ---------------------------------------------------------------- mobilmeny
  var nav = document.querySelector('.nav');
  var burger = document.querySelector('.burger');
  if (nav && burger) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); burger.focus(); }
    });
  }

  // ---------------------------------------------------------------- kontaktformulär
  // Skickas till api/ (hamnar i adminpanelens inkorg). Saknas servern öppnas ett ifyllt mejl istället.
  var form = document.getElementById('kontaktform');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = form.querySelector('.msg'), btn = form.querySelector('button[type=submit]');
      var d = new FormData(form);
      if (!d.get('namn') || !d.get('meddelande') || (!d.get('epost') && !d.get('telefon'))) {
        msg.setAttribute('data-err', '');
        msg.textContent = 'Fyll i namn, meddelande och e-post eller telefon så att vi kan svara dig.';
        return;
      }
      msg.removeAttribute('data-err');
      var to = (BC.content.settings && BC.content.settings.email) || 'info@blomsel.se';
      var mailto = function () {
        var body = 'Namn: ' + d.get('namn') + '\nE-post: ' + d.get('epost') + '\nTelefon: ' + d.get('telefon') + '\nÄrende: ' + d.get('arende') + '\n\n' + d.get('meddelande');
        msg.textContent = 'Ditt e-postprogram öppnas med meddelandet ifyllt. Öppnas inget? Mejla ' + to + '.';
        window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent('Förfrågan: ' + d.get('arende')) + '&body=' + encodeURIComponent(body);
      };
      var data = { sida: PAGE };
      d.forEach(function (v, k) { data[k] = v; });
      btn.disabled = true;
      msg.textContent = 'Skickar…';
      fetch('api/?action=lead', { method: 'POST', headers: { 'content-type': 'application/json', 'X-Bloms': '1' }, body: JSON.stringify(data) })
        .then(function (r) {
          var json = /json/.test(r.headers.get('content-type') || '');
          if (!json) throw new Error('ingen server');
          return r.json().then(function (j) {
            if (!r.ok) { msg.setAttribute('data-err', ''); msg.textContent = j.error || 'Något gick fel. Ring oss gärna istället.'; return; }
            form.reset();
            msg.textContent = 'Tack! Vi har fått din förfrågan och återkommer normalt samma arbetsdag.';
          });
        })
        .catch(mailto)
        .then(function () { btn.disabled = false; });
    });
  }

  // ---------------------------------------------------------------- innehållslager (adminpanelen)
  // content.json innehåller ändringar gjorda i /admin. Texter nycklas på sin ursprungliga text,
  // så att ändringen följer med även om sektioner flyttas.
  var PAGE = document.body.getAttribute('data-page') || 'index';
  var EDIT_SEL = 'h1,h2,h3,h4,p,li,.btn,.card .row,.eyebrow,small,.num,.bignum,.tag,.note,.menu a';
  var SKIP = '.hx-bar,.hx-arrow,.burger,#hx-dots,script,style';
  var DEFAULTS = { phone: '0705-15 02 11', email: 'info@blomsel.se', address: 'Blomstergatan 5', city: '411 04 Göteborg', orgnr: '556754-3656' };
  var PHONE_VARIANTS = ['0705-15 02 11', '0705-150211', '0705 - 15 02 11'];

  function hash(s) { var x = 5381; for (var i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) | 0; return (x >>> 0).toString(36); }
  function norm(s) { return (s || '').replace(/\s+/g, ' ').trim(); }
  function scopeOf(el) { return el.closest('header,footer,#cookie') ? 'alla' : PAGE; }

  var ALLOWED = { STRONG: 1, EM: 1, B: 1, I: 1, BR: 1, SPAN: 1, A: 1, SMALL: 1 };
  function sanitize(html) {
    var t = document.createElement('template');
    t.innerHTML = html;
    (function walk(n) {
      [].slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType === 1) {
          if (!ALLOWED[c.tagName]) { c.replaceWith(document.createTextNode(c.textContent)); return; }
          [].slice.call(c.attributes).forEach(function (a) {
            var ok = (a.name === 'href' && c.tagName === 'A' && !/^\s*javascript:/i.test(a.value)) || a.name === 'class' || a.name === 'aria-hidden';
            if (!ok) c.removeAttribute(a.name);
          });
          walk(c);
        } else if (c.nodeType !== 3) c.remove();
      });
    })(t.content);
    return t.innerHTML;
  }

  var texts = [], links = [], imgs = [];
  function collect() {
    var root = document.body;
    [].slice.call(root.querySelectorAll(EDIT_SEL)).forEach(function (el) {
      if (el.closest(SKIP) || el.closest('.nav') && !el.matches('.menu a')) return;
      var p = el.parentElement && el.parentElement.closest(EDIT_SEL);
      if (p && root.contains(p) && !p.closest(SKIP)) return; // bara yttersta redigerbara elementet
      el.dataset.bcOrig = el.innerHTML;
      el.dataset.bcKey = scopeOf(el) + ':' + hash(norm(el.textContent));
      texts.push(el);
    });
    [].slice.call(root.querySelectorAll('main a[href], footer a[href], #cookie a[href]')).forEach(function (a) {
      if (a.closest(SKIP)) return;
      a.dataset.bcHref = a.getAttribute('href');
      a.dataset.bcLkey = scopeOf(a) + ':' + hash(a.getAttribute('href') + '|' + norm(a.textContent));
      links.push(a);
    });
    [].slice.call(root.querySelectorAll('main img, footer img')).forEach(function (im) {
      im.dataset.bcSrc = im.getAttribute('src');
      if (im.hasAttribute('srcset')) im.dataset.bcSrcset = im.getAttribute('srcset');
      im.dataset.bcAlt = im.getAttribute('alt') || '';
      im.dataset.bcIkey = scopeOf(im) + ':' + im.getAttribute('src');
      imgs.push(im);
    });
    var md = document.querySelector('meta[name="description"]');
    BC.orig = { title: document.title, description: md ? md.content : '' };
  }

  function company(str, s) {
    if (!s) return str;
    if (s.phone && s.phone !== DEFAULTS.phone) {
      PHONE_VARIANTS.forEach(function (v) { str = str.split(v).join(s.phone); });
      str = str.replace(/tel:0705150211/g, 'tel:' + s.phone.replace(/[^\d+]/g, ''));
    }
    ['email', 'address', 'city', 'orgnr'].forEach(function (k) {
      if (s[k] && s[k] !== DEFAULTS[k]) str = str.split(DEFAULTS[k]).join(s[k]);
    });
    return str;
  }

  function apply(c) {
    c = c || {};
    BC.content = c;
    var s = c.settings || {};
    var T = c.text || {}, L = c.link || {}, I = c.img || {}, M = (c.meta || {})[PAGE] || {};
    texts.forEach(function (el) {
      if (el === BC.editing) return;
      var v = T[el.dataset.bcKey];
      el.innerHTML = company(v != null ? sanitize(v) : el.dataset.bcOrig, s);
    });
    links.forEach(function (a) {
      var v = L[a.dataset.bcLkey];
      a.setAttribute('href', company(v != null ? v : a.dataset.bcHref, s));
    });
    imgs.forEach(function (im) {
      var v = I[im.dataset.bcIkey] || {};
      var src = v.src || im.dataset.bcSrc;
      if (c.uploads && c.uploads[src]) src = c.uploads[src];
      // utbytt bild: ta bort srcset så att den nya bilden visas, annars återställ originalets varianter
      if (src !== im.dataset.bcSrc) im.removeAttribute('srcset'); else if (im.dataset.bcSrcset) im.setAttribute('srcset', im.dataset.bcSrcset);
      if (im.getAttribute('src') !== src) im.setAttribute('src', src);
      im.setAttribute('alt', v.alt != null ? v.alt : im.dataset.bcAlt);
    });
    document.title = M.title || BC.orig.title;
    var md = document.querySelector('meta[name="description"]');
    if (md) md.content = M.description || BC.orig.description;
    var th = s.theme || {}, r = document.documentElement.style;
    ['red', 'yellow', 'ink'].forEach(function (k) { if (th[k]) r.setProperty('--' + k, th[k]); else r.removeProperty('--' + k); });
    var ck = document.getElementById('cookie');
    if (ck && s.cookie === false) ck.hidden = true;
    fonts(s.fonts);
    if (BC.carousel) BC.carousel.configure(c.hero || {});
  }

  // Typsnitt valda i adminpanelen (Google Fonts)
  var WEIGHTS = { 'Lato': '400;700;900', 'Merriweather': '400;700;900', 'Bebas Neue': '400', 'Oswald': '400;500;600;700', 'Lora': '400;500;600;700' };
  function fonts(f) {
    var r = document.documentElement.style, link = document.getElementById('bc-fonts');
    if (!f || (!f.head && !f.body)) { r.removeProperty('--font'); r.removeProperty('--font-head'); if (link) link.remove(); return; }
    var names = [f.head, f.body].filter(function (n, i, a) { return n && n !== 'Poppins' && a.indexOf(n) === i; });
    if (names.length) {
      var href = 'https://fonts.googleapis.com/css2?' + names.map(function (n) { return 'family=' + n.replace(/ /g, '+') + ':wght@' + (WEIGHTS[n] || '400;500;600;700;800'); }).join('&') + '&display=swap';
      if (!link) { link = document.createElement('link'); link.id = 'bc-fonts'; link.rel = 'stylesheet'; document.head.appendChild(link); }
      if (link.getAttribute('href') !== href) link.setAttribute('href', href);
    }
    var stack = function (n) { return '"' + n + '", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'; };
    if (f.body) r.setProperty('--font', stack(f.body)); else r.removeProperty('--font');
    if (f.head) r.setProperty('--font-head', stack(f.head)); else r.removeProperty('--font-head');
  }

  // Redigeringsläge som adminpanelen slår på i sin förhandsvisning
  var editHandler = null;
  function edit(handler) {
    editHandler = handler;
    var on = !!handler;
    document.documentElement.classList.toggle('bc-edit', on);
    if (!document.getElementById('bc-edit-css')) {
      var st = document.createElement('style');
      st.id = 'bc-edit-css';
      st.textContent = '.bc-edit [data-bc-key]{outline:1.5px dashed transparent;outline-offset:3px;cursor:text;transition:outline-color .15s}' +
        '.bc-edit [data-bc-key]:hover{outline-color:rgba(249,205,25,.95)}.bc-edit [data-bc-key][contenteditable]{outline:2px solid #F9CD19;background:rgba(249,205,25,.08)}' +
        '.bc-edit img[data-bc-ikey]{cursor:pointer}.bc-edit img[data-bc-ikey]:hover{outline:3px solid #F9CD19;outline-offset:-3px}.bc-edit .bc-sel{outline:3px solid #F9CD19!important;outline-offset:-3px}';
      document.head.appendChild(st);
    }
    if (!on && BC.editing) { BC.editing.removeAttribute('contenteditable'); BC.editing = null; }
  }
  document.addEventListener('click', function (e) {
    if (!editHandler) return;
    var im = e.target.closest('img[data-bc-ikey]');
    var el = e.target.closest('[data-bc-key]');
    var a = e.target.closest('a[data-bc-lkey]');
    if (a || el || im) e.preventDefault();
    [].forEach.call(document.querySelectorAll('.bc-sel'), function (x) { x.classList.remove('bc-sel'); });
    if (im && (!el || !el.contains(im))) {
      im.classList.add('bc-sel');
      editHandler({ type: 'img', key: im.dataset.bcIkey, src: im.getAttribute('src'), orig: im.dataset.bcSrc, alt: im.getAttribute('alt') });
      return;
    }
    if (!el) return;
    if (BC.editing && BC.editing !== el) BC.editing.removeAttribute('contenteditable');
    BC.editing = el;
    el.setAttribute('contenteditable', 'true');
    el.focus();
    var link = el.matches('a') ? el : (a && el.contains(a) ? a : el.querySelector('a[data-bc-lkey]'));
    editHandler({ type: 'text', key: el.dataset.bcKey, html: el.innerHTML, orig: el.dataset.bcOrig, tag: el.tagName.toLowerCase(),
      link: link ? { key: link.dataset.bcLkey, href: link.getAttribute('href'), orig: link.dataset.bcHref } : null });
  }, true);
  document.addEventListener('input', function (e) {
    var el = e.target.closest && e.target.closest('[data-bc-key][contenteditable]');
    if (el && editHandler) editHandler({ type: 'input', key: el.dataset.bcKey, html: sanitize(el.innerHTML), orig: el.dataset.bcOrig });
  });

  var BC = window.BlomsContent = { content: {}, apply: apply, edit: edit, sanitize: sanitize, page: PAGE,
    list: function () {
      return { texts: texts.map(function (el) { return { key: el.dataset.bcKey, text: norm(el.textContent), orig: el.dataset.bcOrig, tag: el.tagName.toLowerCase() }; }),
        imgs: imgs.map(function (im) { return { key: im.dataset.bcIkey, src: im.dataset.bcSrc, alt: im.dataset.bcAlt }; }),
        links: links.map(function (a) { return { key: a.dataset.bcLkey, href: a.dataset.bcHref, text: norm(a.textContent) }; }) };
    } };

  // ---------------------------------------------------------------- herokarusell (startsidan)
  var track = document.getElementById('hx-track');
  if (track) {
    var all = [].slice.call(track.children), slides = all.slice();
    var lab = document.getElementById('hx-lab'), dots = document.getElementById('hx-dots');
    var prev = document.querySelector('.hx-prev'), next = document.querySelector('.hx-next');
    var cur = 0;
    var show = function (i) {
      cur = i;
      var s = slides[i];
      if (!s) return;
      lab.textContent = (i + 1) + ' / ' + slides.length + ' · Förslag ' + s.id.slice(1) + ' · ' + s.dataset.name;
      [].forEach.call(dots.children, function (d, j) { d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
      track.style.height = s.offsetHeight + 'px';
      prev.disabled = i === 0;
      next.disabled = i === slides.length - 1;
    };
    var go = function (i, instant) {
      i = Math.max(0, Math.min(slides.length - 1, i));
      track.scrollTo({ left: i * track.clientWidth, behavior: instant ? 'auto' : 'smooth' });
      show(i);
    };
    var t;
    track.addEventListener('scroll', function () {
      clearTimeout(t);
      t = setTimeout(function () { show(Math.round(track.scrollLeft / track.clientWidth)); }, 60);
    }, { passive: true });
    prev.addEventListener('click', function () { go(cur - 1); });
    next.addEventListener('click', function () { go(cur + 1); });
    document.addEventListener('keydown', function (e) {
      if (editHandler || (e.target.closest && e.target.closest('input,textarea,select,[contenteditable]'))) return;
      var r = track.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    });
    window.addEventListener('resize', function () { track.style.height = ''; go(cur, true); });
    BC.carousel = {
      configure: function (h) {
        var order = (h.order && h.order.length ? h.order : all.map(function (s) { return s.id; }));
        var hidden = h.hidden || [];
        slides = order.map(function (id) { return document.getElementById(id); })
          .filter(function (s) { return s && all.indexOf(s) >= 0 && hidden.indexOf(s.id) < 0; });
        all.forEach(function (s) { if (order.indexOf(s.id) < 0 && hidden.indexOf(s.id) < 0) slides.push(s); });
        if (!slides.length) slides = [all[0]];
        if (h.mode === 'single') slides = [document.getElementById(h.start) || slides[0]];
        all.forEach(function (s) { s.hidden = slides.indexOf(s) < 0; });
        slides.forEach(function (s) { track.appendChild(s); });
        dots.innerHTML = '';
        slides.forEach(function (s, i) {
          var b = document.createElement('button');
          b.type = 'button';
          b.setAttribute('aria-label', 'Förslag ' + s.id.slice(1) + ' · ' + s.dataset.name);
          b.addEventListener('click', function () { go(i); });
          dots.appendChild(b);
        });
        document.querySelector('.hx-bar').hidden = slides.length < 2;
        var start = Math.max(0, slides.indexOf(document.getElementById(h.start)));
        go(start, true);
      }
    };
    BC.carousel.configure({});
  }

  // ---------------------------------------------------------------- start
  collect();
  var inAdmin = false;
  try { inAdmin = window.parent !== window && !!window.parent.BlomsAdmin; } catch (e) {}
  if (inAdmin) {
    window.parent.BlomsAdmin.frameReady(window);
  } else {
    fetch('content.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; })
      .then(apply).catch(function () {});
  }

  // ---------------------------------------------------------------- cookie-banner
  var KEY = 'blomsel-cookies-ok';
  var seen = false;
  try { seen = localStorage.getItem(KEY) === '1'; } catch (e) {}
  var bar = document.getElementById('cookie');
  if (bar && !seen && !inAdmin) {
    bar.hidden = false;
    bar.querySelector('button').addEventListener('click', function () {
      bar.hidden = true;
      try { localStorage.setItem(KEY, '1'); } catch (e) {}
    });
  }
})();
