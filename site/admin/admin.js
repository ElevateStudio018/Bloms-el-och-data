/* Bloms admin: redigerar site/content.json och publicerar via GitHub. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var clone = function (o) { return JSON.parse(JSON.stringify(o)); };
  var strip = function (html) { var d = document.createElement('div'); d.innerHTML = html || ''; return d.textContent.replace(/\s+/g, ' ').trim(); };
  var store = {
    get: function (k, area) { try { return JSON.parse((area || localStorage).getItem(k)); } catch (e) { return null; } },
    set: function (k, v, area) { try { (area || localStorage).setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
    del: function (k, area) { try { (area || localStorage).removeItem(k); } catch (e) {} }
  };

  var DEFAULTS = { phone: '0705-15 02 11', email: 'info@blomsel.se', address: 'Blomstergatan 5', city: '411 04 Göteborg', orgnr: '556754-3656' };
  var THEME = { red: '#8B0000', yellow: '#F9CD19', ink: '#303030' };
  var GH_DEFAULT = { owner: 'ElevateStudio018', repo: 'Bloms-el-och-data', branch: 'claude/dazzling-fermi-wmmmt5', path: 'site' };
  var VIEWS = { oversikt: 'Översikt', innehall: 'Sidor & innehåll', hero: 'Herokarusell', seo: 'SEO', media: 'Mediabibliotek', installningar: 'Företag & tema', publicera: 'Publicera', historik: 'Historik', anvandare: 'Användare', ai: 'AI-assistent', typsnitt: 'Typsnitt' };

  var S = { manifest: null, published: null, draft: null, log: [], undo: [], gh: {}, token: '', page: 'index', frameWin: null, heroWin: null, sel: null, picking: null };

  function blank() { return { version: 1, updated: null, text: {}, link: {}, img: {}, meta: {}, hero: {}, settings: {}, uploads: {} }; }
  function normal(c) {
    var b = blank();
    c = c && typeof c === 'object' ? c : {};
    Object.keys(b).forEach(function (k) { if (c[k] == null || (Array.isArray(c[k]) && k !== 'updated')) c[k] = b[k]; });
    return c;
  }

  // ---------------------------------------------------------------- toast och status
  var toastT;
  function toast(msg, err) {
    var t = $('#toast');
    t.textContent = msg;
    t.className = 'toast' + (err ? ' err' : '');
    t.hidden = false;
    clearTimeout(toastT);
    toastT = setTimeout(function () { t.hidden = true; }, 3200);
  }

  // ---------------------------------------------------------------- ändringar (diff mot publicerat)
  function pageOf(key) { return key.split(':')[0]; }
  function pageName(slug) {
    if (slug === 'alla') return 'Alla sidor (navbar, sidfot)';
    var p = (S.manifest.pages || []).filter(function (x) { return x.slug === slug; })[0];
    return p ? (p.name || p.title.split('|')[0].trim()) : slug;
  }
  function changes() {
    var out = [], d = S.draft, p = S.published;
    ['text', 'link', 'img'].forEach(function (area) {
      var keys = {};
      Object.keys(d[area]).concat(Object.keys(p[area])).forEach(function (k) { keys[k] = 1; });
      Object.keys(keys).forEach(function (k) {
        var a = JSON.stringify(p[area][k]), b = JSON.stringify(d[area][k]);
        if (a !== b) out.push({ area: area, key: k, page: pageOf(k), before: p[area][k], after: d[area][k] });
      });
    });
    var mk = {};
    Object.keys(d.meta).concat(Object.keys(p.meta)).forEach(function (k) { mk[k] = 1; });
    Object.keys(mk).forEach(function (k) {
      ['title', 'description'].forEach(function (f) {
        var a = (p.meta[k] || {})[f] || '', b = (d.meta[k] || {})[f] || '';
        if (a !== b) out.push({ area: 'meta', key: k + '.' + f, page: k, field: f, before: a, after: b });
      });
    });
    if (JSON.stringify(d.hero) !== JSON.stringify(p.hero)) out.push({ area: 'hero', key: 'hero', page: 'index', before: p.hero, after: d.hero });
    if (JSON.stringify(d.settings) !== JSON.stringify(p.settings)) out.push({ area: 'settings', key: 'settings', page: 'alla', before: p.settings, after: d.settings });
    Object.keys(d.uploads).forEach(function (k) { if (!p.uploads[k]) out.push({ area: 'uploads', key: k, page: 'alla', after: k }); });
    return out;
  }
  function describe(c) {
    var v = function (x) {
      if (c.area === 'text') return x == null ? '(original)' : strip(x);
      if (c.area === 'img') return x == null ? '(original)' : (x.src || '') + (x.alt != null ? ' · alt: ' + x.alt : '');
      if (c.area === 'link') return x == null ? '(original)' : x;
      if (c.area === 'meta') return x || '(original)';
      if (c.area === 'uploads') return 'Ny bild: ' + c.key;
      if (!x || !Object.keys(x).length) return '(standard)';
      if (c.area === 'hero') {
        var parts = [];
        if (x.mode === 'single') parts.push('Bara ett förslag');
        if (x.order && x.order.length) parts.push('Ordning: ' + x.order.map(function (i) { return i.slice(1); }).join(', '));
        if (x.hidden && x.hidden.length) parts.push('Dolda: ' + x.hidden.map(function (i) { return i.slice(1); }).join(', '));
        if (x.start) parts.push('Start: ' + x.start.slice(1));
        return parts.join(' · ') || '(standard)';
      }
      var names = { phone: 'Telefon', email: 'E-post', address: 'Adress', city: 'Ort', orgnr: 'Org.nr' };
      var out = Object.keys(names).filter(function (k) { return x[k]; }).map(function (k) { return names[k] + ': ' + x[k]; });
      if (x.theme) out.push('Tema: ' + Object.keys(x.theme).map(function (k) { return x.theme[k]; }).join(', '));
      if (x.cookie === false) out.push('Cookie-banner av');
      if (x.fonts) out.push('Typsnitt: ' + (x.fonts.head || 'Poppins') + ' / ' + (x.fonts.body || 'Poppins'));
      return out.join(' · ');
    };
    var label = { text: 'Text', img: 'Bild', link: 'Länk', meta: c.field === 'title' ? 'SEO-titel' : 'SEO-beskrivning', hero: 'Herokarusell', settings: 'Företag & tema', uploads: 'Uppladdning' }[c.area];
    return { label: label, before: v(c.before), after: v(c.after) };
  }
  function revert(c) {
    snapshot();
    var d = S.draft, p = S.published;
    if (c.area === 'meta') { d.meta[c.page] = d.meta[c.page] || {}; if (p.meta[c.page] && p.meta[c.page][c.field] != null) d.meta[c.page][c.field] = p.meta[c.page][c.field]; else delete d.meta[c.page][c.field]; }
    else if (c.area === 'hero' || c.area === 'settings') d[c.area] = clone(p[c.area]);
    else if (c.area === 'uploads') delete d.uploads[c.key];
    else if (p[c.area][c.key] != null) d[c.area][c.key] = clone(p[c.area][c.key]); else delete d[c.area][c.key];
    commit('Återställde ' + describe(c).label.toLowerCase(), c.page, true);
  }

  // ---------------------------------------------------------------- utkast, ångra, logg
  function snapshot() { S.undo.push(JSON.stringify(S.draft)); if (S.undo.length > 60) S.undo.shift(); $('#undo').disabled = false; }
  function persist() {
    var ok = store.set('bloms-admin-draft', { draft: S.draft, log: S.log.slice(-80) });
    if (!ok) toast('Utkastet är för stort för webbläsarens lagring. Publicera eller ta bort uppladdade bilder.', true);
  }
  var renderT;
  function commit(what, page, reapply) {
    var now_ = JSON.stringify(S.draft);
    if (S.undo.length && S.undo[S.undo.length - 1] === now_) { S.undo.pop(); $('#undo').disabled = !S.undo.length; if (what) return; }
    if (what) {
      var last = S.log[S.log.length - 1];
      var now = Date.now();
      if (last && last.what === what && last.page === page && now - last.t < 15000) last.t = now;
      else S.log.push({ t: now, what: what, page: page });
    }
    persist();
    status();
    if (reapply) applyFrames();
    clearTimeout(renderT);
    renderT = setTimeout(function () { renderPageChanges(); if (current() === 'oversikt') renderOverview(); if (current() === 'publicera') renderPublish(); }, 120);
  }
  function undo() {
    if (!S.undo.length) return;
    S.draft = normal(JSON.parse(S.undo.pop()));
    $('#undo').disabled = !S.undo.length;
    commit(null, null, true);
    render(current());
    toast('Ångrat');
  }
  function status() {
    var n = changes().length;
    var st = $('#status');
    st.textContent = n ? n + (n === 1 ? ' ändring' : ' ändringar') + ' inte publicerade' : 'Allt publicerat';
    st.classList.toggle('dirty', n > 0);
    var b = $('#nav-badge');
    b.hidden = !n;
    b.textContent = n;
  }

  // ---------------------------------------------------------------- förhandsvisning (iframe)
  window.BlomsAdmin = {
    frameReady: function (win) {
      if ($('#hero-frame').contentWindow === win) {
        S.heroWin = win;
        win.BlomsContent.apply(clone(S.draft));
        return;
      }
      S.frameWin = win;
      win.BlomsContent.apply(clone(S.draft));
      if ($('#ed-mode').checked) win.BlomsContent.edit(onFrame);
      renderPageChanges();
      runSearch();
    }
  };
  function applyFrames() {
    [S.frameWin, S.heroWin].forEach(function (w) { try { if (w && w.BlomsContent) w.BlomsContent.apply(clone(S.draft)); } catch (e) {} });
  }
  function loadPage(slug) {
    S.page = slug;
    S.sel = null;
    $('#ed-page').value = slug;
    $('#insp-body').hidden = true;
    $('#insp-empty').hidden = false;
    var p = S.manifest.pages.filter(function (x) { return x.slug === slug; })[0];
    $('#frame').src = '../' + (p ? p.file : 'index.html');
  }

  function onFrame(ev) {
    if (ev.type === 'input') {
      if (!S.sel || S.sel.key !== ev.key) return;
      if (!S.sel.snapshotted) { snapshot(); S.sel.snapshotted = true; }
      if (ev.html === ev.orig) delete S.draft.text[ev.key]; else S.draft.text[ev.key] = ev.html;
      commit('Ändrade text', pageOf(ev.key));
      return;
    }
    S.sel = ev;
    renderInspector();
  }

  function renderInspector() {
    var ev = S.sel, box = $('#insp-body');
    $('#insp-empty').hidden = !!ev;
    box.hidden = !ev;
    if (!ev) return;
    if (ev.type === 'text') {
      var scope = pageOf(ev.key) === 'alla' ? '<span class="pill edit">Gäller alla sidor</span>' : '';
      box.innerHTML = '<div class="insp-card"><span class="kind">Text · &lt;' + esc(ev.tag) + '&gt; ' + scope + '</span>' +
        '<p class="muted">Skriv direkt i förhandsvisningen.</p>' +
        '<div class="fmt"><button type="button" data-cmd="bold" title="Fet"><b>B</b></button><button type="button" data-cmd="italic" title="Kursiv"><i>I</i></button><button type="button" data-cmd="removeFormat" title="Rensa formatering">⌫</button></div>' +
        (ev.link ? '<label for="i-href">Länkar till<input id="i-href" value="' + esc(S.draft.link[ev.link.key] != null ? S.draft.link[ev.link.key] : ev.link.orig) + '"></label>' +
          '<label for="i-hrefsel">…eller välj sida<select id="i-hrefsel"><option value="">Välj sida</option>' + S.manifest.pages.map(function (p) { return '<option value="' + esc(p.file) + '">' + esc(pageName(p.slug)) + '</option>'; }).join('') + '</select></label>' : '') +
        '<div><span class="muted">Original</span><div class="orig">' + esc(strip(ev.orig)) + '</div></div>' +
        '<button class="btn ghost sm" type="button" id="i-reset">Återställ texten</button></div>';
      $$('.fmt button', box).forEach(function (b) {
        b.addEventListener('mousedown', function (e) { e.preventDefault(); });
        b.addEventListener('click', function () {
          try { S.frameWin.document.execCommand(b.dataset.cmd); } catch (e) {}
          var el = S.frameWin.document.querySelector('[data-bc-key][contenteditable]');
          if (el) el.dispatchEvent(new Event('input', { bubbles: true }));
        });
      });
      var setHref = function (v) {
        snapshot();
        if (!v || v === ev.link.orig) delete S.draft.link[ev.link.key]; else S.draft.link[ev.link.key] = v;
        commit('Ändrade länk', pageOf(ev.link.key), true);
      };
      if (ev.link) {
        $('#i-href').addEventListener('change', function () { setHref(this.value.trim()); });
        $('#i-hrefsel').addEventListener('change', function () { if (this.value) { $('#i-href').value = this.value; setHref(this.value); } });
      }
      $('#i-reset').addEventListener('click', function () {
        snapshot();
        delete S.draft.text[ev.key];
        var el = S.frameWin && S.frameWin.document.querySelector('[data-bc-key][contenteditable]');
        if (el) { el.removeAttribute('contenteditable'); S.frameWin.BlomsContent.editing = null; }
        commit('Återställde text', pageOf(ev.key), true);
      });
    } else if (ev.type === 'img') {
      var cur = S.draft.img[ev.key] || {};
      var src = cur.src || ev.orig;
      box.innerHTML = '<div class="insp-card"><span class="kind">Bild</span><img src="' + esc(previewSrc(src)) + '" alt="">' +
        '<p class="muted" style="overflow-wrap:anywhere">' + esc(src) + '</p>' +
        '<button class="btn primary sm" type="button" id="i-pick">Byt bild från mediabiblioteket</button>' +
        '<label for="i-alt">Alt-text (beskrivning för skärmläsare och Google)<input id="i-alt" value="' + esc(ev.alt || '') + '"></label>' +
        '<button class="btn ghost sm" type="button" id="i-ireset">Återställ bilden</button></div>';
      $('#i-pick').addEventListener('click', function () { S.picking = { key: ev.key }; go('media'); });
      $('#i-alt').addEventListener('change', function () {
        snapshot();
        var o = S.draft.img[ev.key] || {};
        o.alt = this.value;
        S.draft.img[ev.key] = o;
        commit('Ändrade alt-text', pageOf(ev.key), true);
      });
      $('#i-ireset').addEventListener('click', function () {
        snapshot();
        delete S.draft.img[ev.key];
        commit('Återställde bild', pageOf(ev.key), true);
        S.sel = null;
        renderInspector();
      });
    }
  }
  // Förhandsvisningen renderas i verklig bredd och skalas ner så att den får plats
  function fitFrame() {
    var wrap = $('#frame-wrap'), f = $('#frame');
    var w = parseInt(S.device || '1440', 10);
    var avail = wrap.clientWidth - 32, h = wrap.clientHeight - 32;
    if (avail <= 0) return;
    var k = Math.min(1, avail / w);
    f.style.width = w + 'px';
    f.style.height = (h / k) + 'px';
    f.style.transform = 'scale(' + k + ')';
  }
  function previewSrc(src) { return S.draft.uploads[src] || '../' + src; }

  function renderPageChanges() {
    var ul = $('#page-changes');
    if (!ul) return;
    var list = changes().filter(function (c) { return c.page === S.page || c.page === 'alla'; });
    ul.innerHTML = list.length ? '' : '<li class="empty">Inga ändringar ännu.</li>';
    list.forEach(function (c) {
      var d = describe(c);
      var li = document.createElement('li');
      li.className = 'chg';
      li.innerHTML = '<span><b>' + esc(d.label) + ':</b> ' + esc(d.after) + '</span><button class="link" type="button">Ångra</button>';
      li.querySelector('button').addEventListener('click', function () { revert(c); });
      ul.appendChild(li);
    });
  }

  function runSearch() {
    var q = $('#ed-search').value.trim().toLowerCase(), box = $('#search-results');
    if (!q || !S.frameWin) { box.hidden = true; return; }
    var hits = S.frameWin.BlomsContent.list().texts.filter(function (t) { return t.text.toLowerCase().indexOf(q) >= 0; }).slice(0, 30);
    box.hidden = false;
    box.innerHTML = '<h3>' + hits.length + ' träffar</h3><ul></ul>';
    hits.forEach(function (h) {
      var li = document.createElement('li');
      li.innerHTML = '<button class="hit" type="button">' + esc(h.text.slice(0, 120)) + '</button>';
      li.firstChild.addEventListener('click', function () {
        var el = S.frameWin.document.querySelector('[data-bc-key="' + h.key + '"]');
        if (!el) return;
        el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        setTimeout(function () { el.click(); }, 350);
      });
      box.querySelector('ul').appendChild(li);
    });
  }

  // ---------------------------------------------------------------- vyer
  function current() { return (location.hash.slice(1) || 'oversikt'); }
  function go(v) { if (location.hash.slice(1) === v) render(v); else location.hash = v; }
  function render(v) {
    if (!VIEWS[v]) v = 'oversikt';
    $$('.view').forEach(function (s) { s.hidden = s.id !== 'v-' + v; });
    $$('#side-nav a').forEach(function (a) { if (a.dataset.view === v) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    $('#view-title').textContent = VIEWS[v];
    $('#app').classList.remove('nav-open');
    if (v !== 'media') S.picking = null;
    ({ oversikt: renderOverview, innehall: renderEditor, hero: renderHero, seo: renderSeo, media: renderMedia, installningar: renderSettings, publicera: renderPublish, historik: function () {}, anvandare: renderUsers, ai: renderAi, typsnitt: renderFonts })[v]();
  }

  function seoIssues() {
    var out = [];
    S.manifest.pages.forEach(function (p) {
      var m = S.draft.meta[p.slug] || {};
      var t = m.title || p.title, d = m.description || p.description;
      if (t.length > 60) out.push({ page: p.slug, msg: 'Titeln är ' + t.length + ' tecken (max 60)' });
      if (!d || d === '-' || d.length < 70) out.push({ page: p.slug, msg: 'Beskrivningen är för kort (' + (d === '-' ? 0 : d.length) + ' tecken)' });
      else if (d.length > 160) out.push({ page: p.slug, msg: 'Beskrivningen är ' + d.length + ' tecken (max 160)' });
    });
    return out;
  }
  function fmtTime(t) { var d = new Date(t); return d.toLocaleString('sv-SE', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); }

  function renderOverview() {
    var ch = changes(), issues = seoIssues();
    $('#kpis').innerHTML =
      '<div class="kpi"><b>' + S.manifest.pages.length + '</b><span>Sidor på sajten</span></div>' +
      '<div class="kpi' + (ch.length ? ' dirty' : '') + '"><b>' + ch.length + '</b><span>Ändringar i utkast</span></div>' +
      '<div class="kpi"><b>' + (S.published.updated ? esc(fmtTime(S.published.updated)) : 'Aldrig') + '</b><span>Senast publicerad</span></div>' +
      '<div class="kpi' + (issues.length ? ' warn' : '') + '"><b>' + issues.length + '</b><span>SEO-varningar</span></div>';
    var log = S.log.slice(-8).reverse();
    $('#log').innerHTML = log.length ? log.map(function (l) {
      return '<li><time>' + esc(new Date(l.t).toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })) + '</time><span class="what">' + esc(l.what) + '<small>' + esc(pageName(l.page || 'alla')) + '</small></span></li>';
    }).join('') : '<li class="empty">Inga ändringar ännu. Börja under Sidor &amp; innehåll.</li>';
    var todo = [];
    if (ch.length) todo.push('<li><span class="what">' + ch.length + ' ändringar är inte sparade på sajten. Ladda ner content.json och lägg upp den.</span><a href="#publicera">Spara</a></li>');
    issues.slice(0, 6).forEach(function (i) { todo.push('<li><span class="what">' + esc(pageName(i.page)) + ': ' + esc(i.msg) + '</span><a href="#seo">Åtgärda</a></li>'); });
    if (issues.length > 6) todo.push('<li><span class="what">…och ' + (issues.length - 6) + ' till.</span><a href="#seo">Visa</a></li>');
    $('#todo').innerHTML = todo.join('') || '<li class="ok"><span class="what">Allt ser bra ut.</span></li>';
    var counts = {};
    ch.forEach(function (c) { counts[c.page] = (counts[c.page] || 0) + 1; });
    $('#page-grid').innerHTML = '';
    S.manifest.pages.forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'page-card';
      b.innerHTML = '<b>' + esc(pageName(p.slug)) + '</b><small>' + esc(p.file) + '</small>' + (counts[p.slug] ? '<span><span class="pill edit">' + counts[p.slug] + ' ändringar</span></span>' : '');
      b.addEventListener('click', function () { S.page = p.slug; go('innehall'); });
      $('#page-grid').appendChild(b);
    });
  }

  function renderEditor() {
    var sel = $('#ed-page');
    if (!sel.options.length) {
      sel.innerHTML = S.manifest.pages.map(function (p) { return '<option value="' + esc(p.slug) + '">' + esc(pageName(p.slug)) + '</option>'; }).join('');
    }
    var want = '../' + (S.manifest.pages.filter(function (x) { return x.slug === S.page; })[0] || { file: 'index.html' }).file;
    setTimeout(fitFrame, 0);
    if (!$('#frame').getAttribute('src') || $('#frame').getAttribute('src') !== want) loadPage(S.page);
    else { applyFrames(); renderPageChanges(); }
  }

  function heroOrder() {
    var ids = S.manifest.heroes.map(function (h) { return h.id; });
    var o = (S.draft.hero.order || []).filter(function (id) { return ids.indexOf(id) >= 0; });
    ids.forEach(function (id) { if (o.indexOf(id) < 0) o.push(id); });
    return o;
  }
  function setHero(patch, what) {
    snapshot();
    var h = clone(S.draft.hero);
    Object.keys(patch).forEach(function (k) { h[k] = patch[k]; });
    S.draft.hero = h;
    commit(what, 'index', true);
    renderHero();
  }
  function renderHero() {
    if (!$('#hero-frame').getAttribute('src')) $('#hero-frame').src = '../index.html';
    var h = S.draft.hero, hidden = h.hidden || [], order = heroOrder();
    var start = h.start || order.filter(function (id) { return hidden.indexOf(id) < 0; })[0];
    $('#h-mode').value = h.mode || 'carousel';
    var list = $('#hero-list');
    list.innerHTML = '';
    var name = function (id) { return (S.manifest.heroes.filter(function (x) { return x.id === id; })[0] || {}).name || id; };
    order.forEach(function (id, i) {
      var li = document.createElement('li');
      li.className = 'hero-item' + (hidden.indexOf(id) >= 0 ? ' off' : '');
      li.draggable = true;
      li.dataset.id = id;
      li.innerHTML = '<span class="handle" aria-hidden="true">⋮⋮</span><span class="num">' + (i + 1) + '</span>' +
        '<span><b>Förslag ' + esc(id.slice(1)) + '</b> · ' + esc(name(id)) + '</span>' +
        '<span class="row"><label><input type="checkbox" class="h-vis"' + (hidden.indexOf(id) < 0 ? ' checked' : '') + '> Visa</label>' +
        '<label><input type="radio" name="h-start" class="h-start"' + (id === start ? ' checked' : '') + '> Start</label></span>' +
        '<span class="arrows"><button type="button" class="h-up" aria-label="Flytta upp">↑</button><button type="button" class="h-down" aria-label="Flytta ner">↓</button></span>';
      var move = function (to) {
        var o = order.slice();
        o.splice(i, 1);
        o.splice(Math.max(0, Math.min(o.length, to)), 0, id);
        setHero({ order: o }, 'Ändrade ordning i herokarusellen');
      };
      li.querySelector('.h-up').addEventListener('click', function () { move(i - 1); });
      li.querySelector('.h-down').addEventListener('click', function () { move(i + 1); });
      li.querySelector('.h-vis').addEventListener('change', function () {
        var hd = hidden.filter(function (x) { return x !== id; });
        if (!this.checked) hd.push(id);
        if (hd.length >= order.length) { this.checked = true; toast('Minst ett förslag måste visas.', true); return; }
        setHero({ hidden: hd }, (this.checked ? 'Visar ' : 'Döljer ') + 'förslag ' + id.slice(1));
      });
      li.querySelector('.h-start').addEventListener('change', function () { setHero({ start: id }, 'Startförslag: ' + id.slice(1)); });
      li.addEventListener('dragstart', function (e) { li.classList.add('drag'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', id); });
      li.addEventListener('dragend', function () { li.classList.remove('drag'); });
      li.addEventListener('dragover', function (e) { e.preventDefault(); li.classList.add('over'); });
      li.addEventListener('dragleave', function () { li.classList.remove('over'); });
      li.addEventListener('drop', function (e) {
        e.preventDefault();
        var from = e.dataTransfer.getData('text/plain');
        if (!from || from === id) return;
        var o = order.filter(function (x) { return x !== from; });
        o.splice(o.indexOf(id), 0, from);
        setHero({ order: o }, 'Ändrade ordning i herokarusellen');
      });
      list.appendChild(li);
    });
  }

  function renderSeo() {
    var box = $('#seo-list');
    box.innerHTML = '';
    S.manifest.pages.forEach(function (p) {
      var m = S.draft.meta[p.slug] || {};
      var el = document.createElement('div');
      el.className = 'seo-item';
      el.innerHTML = '<h3>' + esc(pageName(p.slug)) + ' <span class="muted">' + esc(p.file) + '</span></h3>' +
        '<div class="stack"><label for="seo-t-' + p.slug + '">Titel <span class="count" data-c="t"></span><input id="seo-t-' + p.slug + '" data-f="title"></label>' +
        '<label for="seo-d-' + p.slug + '">Beskrivning <span class="count" data-c="d"></span><textarea id="seo-d-' + p.slug + '" data-f="description" rows="3"></textarea></label></div>' +
        '<div class="serp"><div class="u">blomsel.se › ' + esc(p.slug === 'index' ? '' : p.slug) + '</div><div class="t"></div><div class="d"></div></div>';
      var ti = el.querySelector('[data-f=title]'), de = el.querySelector('[data-f=description]');
      ti.value = m.title || p.title;
      de.value = m.description || (p.description === '-' ? '' : p.description);
      var upd = function () {
        el.querySelector('.serp .t').textContent = ti.value;
        el.querySelector('.serp .d').textContent = de.value || 'Ingen beskrivning, Google väljer en text från sidan.';
        var ct = el.querySelector('[data-c=t]'), cd = el.querySelector('[data-c=d]');
        ct.textContent = ti.value.length + ' / 60';
        ct.classList.toggle('bad', ti.value.length > 60);
        cd.textContent = de.value.length + ' / 160';
        cd.classList.toggle('bad', de.value.length > 160 || de.value.length < 70);
      };
      var save = function (f, val, orig) {
        snapshot();
        var mm = clone(S.draft.meta[p.slug] || {});
        if (!val || val === orig) delete mm[f]; else mm[f] = val;
        if (Object.keys(mm).length) S.draft.meta[p.slug] = mm; else delete S.draft.meta[p.slug];
        commit('Ändrade SEO-' + (f === 'title' ? 'titel' : 'beskrivning'), p.slug);
      };
      ti.addEventListener('input', upd);
      de.addEventListener('input', upd);
      ti.addEventListener('change', function () { save('title', ti.value.trim(), p.title); });
      de.addEventListener('change', function () { save('description', de.value.trim(), p.description); });
      upd();
      box.appendChild(el);
    });
  }

  function renderMedia() {
    $('#m-pick-hint').hidden = !S.picking;
    var q = $('#m-search').value.trim().toLowerCase();
    var used = {};
    Object.keys(S.draft.img).forEach(function (k) { if (S.draft.img[k].src) used[S.draft.img[k].src] = 1; });
    var all = Object.keys(S.draft.uploads).concat(S.manifest.images.filter(function (i) { return !/logo|\.ico$/.test(i); }));
    var grid = $('#media-grid');
    grid.innerHTML = '';
    all.filter(function (i) { return i.toLowerCase().indexOf(q) >= 0; }).forEach(function (src) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'media-item';
      b.innerHTML = '<img src="' + esc(previewSrc(src)) + '" alt="" loading="lazy"><div>' + esc(src.replace(/^img\//, '')) +
        (S.draft.uploads[src] ? '<span class="pill edit">Ny</span>' : '') + (used[src] ? '<span class="pill">Använd</span>' : '') + '</div>';
      b.addEventListener('click', function () {
        if (S.picking) {
          snapshot();
          var o = S.draft.img[S.picking.key] || {};
          o.src = src;
          S.draft.img[S.picking.key] = o;
          var key = S.picking.key;
          S.picking = null;
          commit('Bytte bild', pageOf(key), true);
          go('innehall');
          setTimeout(function () { if (S.sel && S.sel.key === key) { S.sel.orig = S.sel.orig; renderInspector(); } }, 50);
          toast('Bilden är bytt');
        } else {
          copy(src);
        }
      });
      grid.appendChild(b);
    });
  }
  function copy(text) {
    var done = function () { toast('Sökväg kopierad: ' + text); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { toast(text); });
    else toast(text);
  }
  function upload(files) {
    [].slice.call(files).forEach(function (f) {
      if (!/^image\//.test(f.type)) return;
      var r = new FileReader();
      r.onload = function () {
        var im = new Image();
        im.onload = function () {
          var max = 2000, w = im.width, h = im.height, k = Math.min(1, max / Math.max(w, h));
          var c = document.createElement('canvas');
          c.width = Math.round(w * k);
          c.height = Math.round(h * k);
          c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
          var name = 'img/uploads/' + f.name.toLowerCase().replace(/\.[a-z0-9]+$/, '').replace(/[^a-z0-9åäö]+/g, '-').replace(/[åä]/g, 'a').replace(/ö/g, 'o').replace(/^-|-$/g, '') + '.jpg';
          snapshot();
          S.draft.uploads[name] = c.toDataURL('image/jpeg', 0.82);
          commit('Laddade upp ' + name.replace('img/uploads/', ''), 'alla');
          renderMedia();
          toast('Uppladdad: ' + name.replace('img/uploads/', ''));
        };
        im.src = r.result;
      };
      r.readAsDataURL(f);
    });
  }

  function renderSettings() {
    var s = S.draft.settings, th = s.theme || {};
    Object.keys(DEFAULTS).forEach(function (k) { var i = $('#s-' + k); i.placeholder = DEFAULTS[k]; i.value = s[k] || DEFAULTS[k]; });
    ['red', 'yellow', 'ink'].forEach(function (k) { $('#t-' + k).value = th[k] || THEME[k]; });
    $('#s-cookie').checked = s.cookie !== false;
    themePreview();
  }
  function themePreview() {
    var p = $('#t-preview');
    ['red', 'yellow', 'ink'].forEach(function (k) { p.style.setProperty('--t-' + k, $('#t-' + k).value); });
  }
  function saveSettings(what) {
    snapshot();
    var s = {};
    Object.keys(DEFAULTS).forEach(function (k) { var v = $('#s-' + k).value.trim(); if (v && v !== DEFAULTS[k]) s[k] = v; });
    var th = {};
    ['red', 'yellow', 'ink'].forEach(function (k) { var v = $('#t-' + k).value; if (v.toLowerCase() !== THEME[k].toLowerCase()) th[k] = v; });
    if (Object.keys(th).length) s.theme = th;
    if (!$('#s-cookie').checked) s.cookie = false;
    if (S.draft.settings.fonts) s.fonts = S.draft.settings.fonts;
    S.draft.settings = s;
    commit(what, 'alla', true);
  }

  function renderPublish() {
    var ch = changes(), box = $('#p-diff');
    var g = S.gh;
    $('#g-owner').value = g.owner; $('#g-repo').value = g.repo; $('#g-branch').value = g.branch;
    $('#g-token').value = S.token;
    if (!ch.length) { box.innerHTML = '<p class="empty">Inga ändringar. Allt är publicerat.</p>'; return; }
    var groups = {};
    ch.forEach(function (c) { (groups[c.page] = groups[c.page] || []).push(c); });
    box.innerHTML = '';
    Object.keys(groups).forEach(function (pg) {
      var gdiv = document.createElement('div');
      gdiv.className = 'diff-group';
      gdiv.innerHTML = '<h3>' + esc(pageName(pg)) + ' <span class="pill">' + groups[pg].length + '</span></h3>';
      groups[pg].forEach(function (c) {
        var d = describe(c), row = document.createElement('div');
        row.className = 'diff';
        row.innerHTML = '<div><span class="muted">' + esc(d.label) + '</span><br><del>' + esc(d.before).slice(0, 300) + '</del></div><div><br><ins>' + esc(d.after).slice(0, 300) + '</ins></div><button class="link" type="button">Ångra</button>';
        if (c.area === 'uploads') row.querySelector('del').remove();
        row.querySelector('button').addEventListener('click', function () { revert(c); renderPublish(); });
        gdiv.appendChild(row);
      });
      box.appendChild(gdiv);
    });
  }

  // ---------------------------------------------------------------- GitHub
  function readGh() {
    S.gh = { owner: $('#g-owner').value.trim() || GH_DEFAULT.owner, repo: $('#g-repo').value.trim() || GH_DEFAULT.repo, branch: $('#g-branch').value.trim() || GH_DEFAULT.branch, path: GH_DEFAULT.path };
    store.set('bloms-admin-gh', S.gh);
  }
  function setToken(t) {
    S.token = t;
    var c = $('#conn');
    c.textContent = t ? 'GitHub ansluten' : 'Lokalt läge';
    c.classList.toggle('on', !!t);
  }
  function gh(path, opts) {
    opts = opts || {};
    return fetch('https://api.github.com/repos/' + S.gh.owner + '/' + S.gh.repo + path, {
      method: opts.method || 'GET',
      headers: Object.assign({ Accept: 'application/vnd.github+json' }, S.token ? { Authorization: 'Bearer ' + S.token } : {}),
      body: opts.body ? JSON.stringify(opts.body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw new Error((j && j.message) || ('HTTP ' + r.status));
        return j;
      });
    });
  }
  var b64 = function (str) { return btoa(unescape(encodeURIComponent(str))); };
  var unb64 = function (s) { return decodeURIComponent(escape(atob(s.replace(/\n/g, '')))); };
  function putFile(path, base64, msg) {
    var full = S.gh.path + '/' + path;
    return gh('/contents/' + encodeURI(full) + '?ref=' + encodeURIComponent(S.gh.branch)).then(function (f) { return f.sha; }, function () { return null; })
      .then(function (sha) {
        var body = { message: msg, content: base64, branch: S.gh.branch };
        if (sha) body.sha = sha;
        return gh('/contents/' + encodeURI(full), { method: 'PUT', body: body });
      });
  }
  function publish() {
    readGh();
    if (!S.token) { toast('Lägg in en GitHub-token under Avancerat, eller ladda ner content.json.', true); return; }
    var ch = changes();
    if (!ch.length) { toast('Inget att publicera.'); return; }
    var msg = $('#p-msg').value.trim() || 'Uppdaterade innehåll via adminpanelen';
    var st = $('#p-status'), btn = $('#p-publish');
    btn.disabled = true;
    var ups = Object.keys(S.draft.uploads).filter(function (k) { return !S.published.uploads[k]; });
    var chain = Promise.resolve();
    ups.forEach(function (k, i) {
      chain = chain.then(function () {
        st.textContent = 'Laddar upp bild ' + (i + 1) + ' av ' + ups.length + '…';
        return putFile(k, S.draft.uploads[k].split(',')[1], 'Admin: laddade upp ' + k);
      });
    });
    chain.then(function () {
      st.textContent = 'Sparar innehåll…';
      var out = clone(S.draft);
      out.uploads = {};
      out.updated = new Date().toISOString();
      return putFile('content.json', b64(JSON.stringify(out, null, 1)), msg).then(function () { return out; });
    }).then(function (out) {
      S.published = normal(clone(out));
      S.draft = normal(clone(out));
      $('#p-msg').value = '';
      commit('Publicerade: ' + msg, 'alla', true);
      st.textContent = 'Publicerat ' + new Date().toLocaleTimeString('sv-SE') + '. Sajten visar ändringarna inom några minuter.';
      toast('Publicerat!');
      renderPublish();
    }).catch(function (e) {
      st.textContent = 'Kunde inte publicera: ' + e.message;
      toast('Publiceringen misslyckades: ' + e.message, true);
    }).then(function () { btn.disabled = false; });
  }
  function testGh() {
    readGh();
    $('#g-msg').textContent = 'Testar…';
    gh('/branches/' + encodeURIComponent(S.gh.branch)).then(function (b) {
      return gh('').then(function (r) {
        var can = r.permissions && r.permissions.push;
        $('#g-msg').textContent = 'Ansluten till ' + r.full_name + ' (' + b.name + ')' + (can === false ? ', men token saknar skrivrätt' : '') + '.';
      });
    }).catch(function (e) { $('#g-msg').textContent = 'Fel: ' + e.message; });
  }
  function loadHistory() {
    readGh();
    var msg = $('#hi-msg'), ol = $('#history');
    msg.textContent = 'Hämtar…';
    gh('/commits?path=' + encodeURIComponent(S.gh.path + '/content.json') + '&sha=' + encodeURIComponent(S.gh.branch) + '&per_page=25').then(function (list) {
      msg.textContent = list.length ? list.length + ' versioner' : 'Inga publicerade versioner ännu.';
      ol.innerHTML = '';
      list.forEach(function (c) {
        var li = document.createElement('li');
        li.innerHTML = '<span class="what"><b>' + esc(c.commit.message.split('\n')[0]) + '</b><small>' + esc((c.commit.author || {}).name || '') + ' · ' + esc(fmtTime(c.commit.author.date)) + ' · ' + esc(c.sha.slice(0, 7)) + '</small></span><button class="btn ghost sm" type="button">Läs in som utkast</button>';
        li.querySelector('button').addEventListener('click', function () {
          gh('/contents/' + encodeURI(S.gh.path + '/content.json') + '?ref=' + c.sha).then(function (f) {
            snapshot();
            S.draft = normal(JSON.parse(unb64(f.content)));
            commit('Läste in version ' + c.sha.slice(0, 7), 'alla', true);
            toast('Versionen är inläst som utkast. Publicera för att återställa den.');
          }).catch(function (e) { toast('Kunde inte läsa versionen: ' + e.message, true); });
        });
        ol.appendChild(li);
      });
    }).catch(function (e) { msg.textContent = 'Fel: ' + e.message + (S.token ? '' : ' (privat repo kräver token)'); });
  }

  function download(name, text) {
    var blob = new Blob([text], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function exportJson() {
    var out = clone(S.draft);
    out.updated = new Date().toISOString();
    if (Object.keys(out.uploads).length) toast('Obs: uppladdade bilder ligger inbäddade i filen. Publicera via GitHub för att spara dem som egna filer.');
    download('content.json', JSON.stringify(out, null, 1));
    S.published = normal(clone(out));
    commit('Laddade ner content.json', 'alla');
    renderPublish();
  }
  function importJson(file) {
    var r = new FileReader();
    r.onload = function () {
      try {
        var c = JSON.parse(r.result);
        if (typeof c !== 'object' || !c.text) throw new Error('fel format');
        snapshot();
        S.draft = normal(c);
        commit('Importerade ' + file.name, 'alla', true);
        render(current());
        toast('Importerat');
      } catch (e) { toast('Filen är inte en giltig content.json.', true); }
    };
    r.readAsText(file);
  }

  // ---------------------------------------------------------------- start
  function boot() {
    Promise.all([
      fetch('../assets/manifest.json', { cache: 'no-store' }).then(function (r) { return r.json(); }),
      fetch(rawUrl('content.json'), { cache: 'no-store' }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .catch(function () { return fetch('../content.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }); }).catch(function () { return {}; })
    ]).then(function (res) {
      S.manifest = res[0];
      S.published = normal(res[1]);
      var saved = store.get('bloms-admin-draft');
      S.draft = normal(saved && saved.draft ? saved.draft : clone(S.published));
      S.log = (saved && saved.log) || [];
      wire();
      status();
      render(current());
    }).catch(function (e) {
      document.body.innerHTML = '<p style="padding:40px">Kunde inte läsa sajtens manifest (' + esc(e.message) + '). Kör <code>python3 site/build.py</code>.</p>';
    });
  }
  function wire() {
    window.addEventListener('hashchange', function () { render(current()); });
    $('#menu-btn').addEventListener('click', function () { $('#app').classList.toggle('nav-open'); });
    $('#undo').addEventListener('click', undo);
    $('#top-publish').addEventListener('click', function () { go('publicera'); });
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey && !e.target.closest('input,textarea,[contenteditable]')) { e.preventDefault(); undo(); }
    });
    $('#logout').addEventListener('click', function () {
      endSession();
      location.hash = '';
      location.reload();
    });
    $('#u-add').addEventListener('submit', addUser);
    $('#u-pw').addEventListener('submit', changePassword);
    $('#u-gen').addEventListener('click', function () {
      var pw = genPassword();
      $('#u-pass').value = pw; $('#u-pass2').value = pw;
      $('#u-msg').innerHTML = 'Förslag: <code style="user-select:all">' + esc(pw) + '</code> (skicka det säkert till personen)';
    });
    $('#ed-page').addEventListener('change', function () { loadPage(this.value); });
    $$('#ed-device button').forEach(function (b) {
      b.addEventListener('click', function () {
        $$('#ed-device button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        S.device = b.dataset.w;
        fitFrame();
      });
    });
    window.addEventListener('resize', fitFrame);
    S.device = '1440px';
    fitFrame();
    $('#ed-mode').addEventListener('change', function () {
      if (!S.frameWin) return;
      S.frameWin.BlomsContent.edit(this.checked ? onFrame : null);
      if (!this.checked) { S.sel = null; renderInspector(); }
    });
    $('#ed-search').addEventListener('input', runSearch);
    $('#h-mode').addEventListener('change', function () { setHero({ mode: this.value }, this.value === 'single' ? 'Visar bara ett heroförslag' : 'Visar herokarusell'); });
    $('#h-reset').addEventListener('click', function () { setHero({ order: [], hidden: [], start: undefined }, 'Återställde herokarusellen'); });
    $('#m-search').addEventListener('input', renderMedia);
    $('#m-upload').addEventListener('change', function () { upload(this.files); this.value = ''; });
    $('#s-company').addEventListener('change', function () { saveSettings('Ändrade företagsuppgifter'); });
    $('#s-company').addEventListener('submit', function (e) { e.preventDefault(); });
    $('#s-theme').addEventListener('input', themePreview);
    $('#s-theme').addEventListener('change', function () { saveSettings('Ändrade tema'); });
    $('#t-reset').addEventListener('click', function () { ['red', 'yellow', 'ink'].forEach(function (k) { $('#t-' + k).value = THEME[k]; }); themePreview(); saveSettings('Återställde tema'); });
    $('#p-publish').addEventListener('click', publish);
    $('#g-test').addEventListener('click', testGh);
    ['#g-owner', '#g-repo', '#g-branch'].forEach(function (s) { $(s).addEventListener('change', readGh); });
    $('#g-token').addEventListener('change', function () { setToken(this.value.trim()); updateSessionToken(S.token); });
    $('#p-export').addEventListener('click', exportJson);
    $('#p-import').addEventListener('change', function () { if (this.files[0]) importJson(this.files[0]); this.value = ''; });
    $('#p-discard').addEventListener('click', function () {
      var b = this;
      if (b.dataset.confirm !== '1') { b.dataset.confirm = '1'; b.textContent = 'Klicka igen för att slänga'; setTimeout(function () { b.dataset.confirm = ''; b.textContent = 'Släng utkast'; }, 3000); return; }
      snapshot();
      S.draft = normal(clone(S.published));
      commit('Slängde utkastet', 'alla', true);
      render('publicera');
      b.dataset.confirm = ''; b.textContent = 'Släng utkast';
    });
    $('#hi-load').addEventListener('click', loadHistory);
    $('#f-head').addEventListener('change', function () { setFont('head', this.value); });
    $('#f-body').addEventListener('change', function () { setFont('body', this.value); });
    $('#f-reset').addEventListener('click', function () { snapshot(); var st = clone(S.draft.settings); delete st.fonts; S.draft.settings = st; commit('Återställde typsnitt', 'alla', true); renderFonts(); });
  }


  // ---------------------------------------------------------------- typsnitt
  // Google Fonts som sajten kan använda. Vikterna måste finnas i respektive familj.
  var FONTS = [
    ['Poppins', 'Geometrisk', '400;500;600;700;800'], ['Montserrat', 'Geometrisk', '400;500;600;700;800'],
    ['Outfit', 'Geometrisk', '400;500;600;700;800'], ['DM Sans', 'Rak och modern', '400;500;600;700;800'],
    ['Manrope', 'Rak och modern', '400;500;600;700;800'], ['Plus Jakarta Sans', 'Rak och modern', '400;500;600;700;800'],
    ['Work Sans', 'Rak och modern', '400;500;600;700;800'], ['Inter', 'Neutral', '400;500;600;700;800'],
    ['Open Sans', 'Neutral', '400;500;600;700;800'], ['Lato', 'Neutral', '400;700;900'],
    ['Nunito', 'Rundad', '400;500;600;700;800'], ['Rubik', 'Rundad', '400;500;600;700;800'],
    ['Barlow', 'Teknisk', '400;500;600;700;800'], ['Archivo', 'Teknisk', '400;500;600;700;800'],
    ['Oswald', 'Smal rubrik', '400;500;600;700'], ['Bebas Neue', 'Smal rubrik', '400'],
    ['Playfair Display', 'Serif', '400;500;600;700;800'], ['Merriweather', 'Serif', '400;700;900'],
    ['Source Serif 4', 'Serif', '400;500;600;700;800'], ['Lora', 'Serif', '400;500;600;700']
  ];
  var fontCss = function (names) {
    var fams = names.filter(Boolean).filter(function (n, i, a) { return a.indexOf(n) === i; });
    return 'https://fonts.googleapis.com/css2?' + fams.map(function (n) {
      var f = FONTS.filter(function (x) { return x[0] === n; })[0];
      return 'family=' + n.replace(/ /g, '+') + ':wght@' + (f ? f[2] : '400;700');
    }).join('&') + '&display=swap';
  };
  function loadFontsInAdmin() {
    if (document.getElementById('admin-font-gallery')) return;
    for (var i = 0; i < FONTS.length; i += 10) {
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.id = i ? '' : 'admin-font-gallery';
      l.href = fontCss(FONTS.slice(i, i + 10).map(function (f) { return f[0]; }));
      document.head.appendChild(l);
    }
  }
  function curFonts() { var f = S.draft.settings.fonts || {}; return { head: f.head || 'Poppins', body: f.body || 'Poppins' }; }
  function setFont(which, name) {
    snapshot();
    var f = curFonts();
    f[which] = name;
    var st = clone(S.draft.settings);
    if (f.head === 'Poppins' && f.body === 'Poppins') delete st.fonts; else st.fonts = f;
    S.draft.settings = st;
    commit('Bytte typsnitt för ' + (which === 'head' ? 'rubriker' : 'brödtext') + ' till ' + name, 'alla', true);
    renderFonts();
  }
  function renderFonts() {
    loadFontsInAdmin();
    var f = curFonts();
    var opts = FONTS.map(function (x) { return '<option value="' + esc(x[0]) + '">' + esc(x[0]) + ' · ' + esc(x[1]) + '</option>'; }).join('');
    ['head', 'body'].forEach(function (k) { var sel = $('#f-' + k); if (!sel.options.length) sel.innerHTML = opts; sel.value = f[k]; });
    var pv = $('#f-preview');
    pv.style.setProperty('--fp-head', '"' + f.head + '", system-ui, sans-serif');
    pv.style.setProperty('--fp-body', '"' + f.body + '", system-ui, sans-serif');
    var grid = $('#f-grid');
    grid.innerHTML = '';
    FONTS.forEach(function (x) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'font-card' + (x[0] === f.head ? ' is-head' : '') + (x[0] === f.body ? ' is-body' : '');
      b.innerHTML = '<span class="aa" style="font-family:\'' + esc(x[0]) + '\',sans-serif;font-weight:700">Elektriker Aa</span><b style="font-family:\'' + esc(x[0]) + '\',sans-serif">' + esc(x[0]) + '</b><small>' + esc(x[1]) + '</small>' +
        '<span class="tags">' + (x[0] === f.head ? '<span class="pill edit">Rubriker</span>' : '') + (x[0] === f.body ? '<span class="pill">Brödtext</span>' : '') + '</span>';
      b.addEventListener('click', function (e) { setFont(e.shiftKey ? 'body' : 'head', x[0]); });
      grid.appendChild(b);
    });
  }

  // ---------------------------------------------------------------- AI-assistent (Claude via Messages API)
  var AI = { msgs: [], ctrl: null, busy: false };
  var AI_KEY = 'bloms-admin-ai-key';
  var AI_CHIPS = ['Skriv en kort säljande text om laddboxar för startsidan', 'Förbättra SEO-beskrivningen för sidan Solceller',
    'Svara en kund som frågar om ROT-avdrag gäller byte av elcentral', 'Skriv ett inlägg till Facebook om golvvärme inför vintern',
    'Vad får en privatperson göra själv med elen?'];
  function aiSystem() {
    var pages = S.manifest.pages.map(function (p) { return '- ' + (p.name || p.slug) + ' (' + p.file + ')'; }).join('\n');
    var tone = { vardaglig: 'vardaglig, tydlig och personlig', formell: 'formell och saklig', saljande: 'säljande men trovärdig' }[$('#ai-tone').value];
    return 'Du är en skrivassistent för redaktörerna på webbplatsen för Bloms El & Data AB, en elfirma i Göteborg. ' +
      'Svara på svenska. Tonen ska vara ' + tone + '.\n\nFakta om företaget (använd bara dessa när du skriver om företaget):\n' +
      '- Certifierade elektriker i Göteborg sedan 2008. Kontor och lager på Blomstergatan 5, 411 04 Göteborg.\n' +
      '- Telefon 0705-15 02 11, e-post info@blomsel.se, org.nr 556754-3656.\n' +
      '- Alla montörer har ABL- eller BB1-behörighet. Registrerade hos Elsäkerhetsverket. Ansvarsförsäkrade. Garanti på alla arbeten. CE-märkt material.\n' +
      '- Kunder: privatpersoner, bostadsrättsföreningar, fastighetsägare, restauranger, butiker, kontor, industri, lantbrukare, kommuner, byggföretag.\n' +
      '- Område: Falkenberg i söder till Uddevalla i norr, Ulricehamn och Borås. Materialdepåer i Mölndal, Partille, Hisingen, Västra Frölunda, Lindholmen, Kungsbacka, Kungälv och Borås.\n' +
      '- ROT-avdrag upp till 30 % av arbetskostnaden. Grön teknik: 20 % för solceller, 50 % för batterilager och laddbox, max 50 000 kr per person och år. Bloms sköter avdragen på fakturan.\n' +
      '- Återkommer normalt samma arbetsdag med bedömning och offert.\n\nSajtens sidor:\n' + pages + '\n\n' +
      'Hitta inte på priser, kundomdömen, siffror eller tjänster som inte står ovan. Om något är osäkert, till exempel regler som kan ha ändrats, säg det och föreslå att kontrollera med Elsäkerhetsverket eller Skatteverket. ' +
      'När du skriver texter till sajten: skriv färdig text utan rubriker som "Här är texten", använd korta stycken och ingen markdown-formatering om användaren inte ber om det. ' +
      'För SEO-titlar gäller max 60 tecken och för beskrivningar 70–160 tecken.';
  }
  function aiBubble(role, text) {
    var hello = $('#ai-hello');
    if (hello) hello.remove();
    var d = document.createElement('div');
    d.className = 'msg ' + role;
    d.textContent = text;
    $('#ai-msgs').appendChild(d);
    $('#ai-msgs').scrollTop = 1e9;
    return d;
  }
  function aiTools(d, text) {
    var t = document.createElement('div');
    t.className = 'tools';
    t.innerHTML = '<button type="button">Kopiera</button>';
    t.firstChild.addEventListener('click', function () { copy(text); });
    d.appendChild(t);
  }
  function pageText(slug) {
    var p = S.manifest.pages.filter(function (x) { return x.slug === slug; })[0];
    if (!p) return Promise.resolve('');
    return fetch('../' + p.file, { cache: 'no-store' }).then(function (r) { return r.text(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var m = doc.querySelector('main');
      return (p.name || slug) + ' (' + p.file + ')\nSEO-titel: ' + p.title + '\nSEO-beskrivning: ' + p.description + '\n\n' + (m ? m.innerText || m.textContent : '').replace(/\n\s*\n+/g, '\n').trim();
    });
  }
  function aiSend(text) {
    if (AI.busy || !text.trim()) return;
    var key = $('#ai-key').value.trim();
    if (!key) { toast('Lägg in en API-nyckel från Anthropic först.', true); $('#ai-key').focus(); return; }
    var slug = $('#ai-page').value;
    aiBubble('user', text);
    $('#ai-text').value = '';
    var bot = aiBubble('bot typing', '');
    AI.busy = true; $('#ai-send').disabled = true; $('#ai-stop').hidden = false;
    $('#ai-status').textContent = 'Skriver…';
    (slug ? pageText(slug) : Promise.resolve('')).then(function (ctx) {
      var content = ctx ? 'Text från sidan som frågan gäller:\n<sida>\n' + ctx.slice(0, 60000) + '\n</sida>\n\n' + text : text;
      AI.msgs.push({ role: 'user', content: content });
      AI.ctrl = new AbortController();
      return fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST', signal: AI.ctrl.signal,
        headers: { 'content-type': 'application/json', 'x-api-key': key, 'anthropic-version': '2026-10-21',
          'anthropic-beta': 'server-side-fallback-2026-07-01', 'anthropic-dangerous-direct-browser-access': 'true' },
        body: JSON.stringify({ model: 'claude-opus-5-5', max_tokens: 16000, stream: true, fallbacks: 'default',
          output_config: { effort: 'medium' }, system: aiSystem(), messages: AI.msgs })
      });
    }).then(function (r) {
      if (!r.ok) return r.json().catch(function () { return {}; }).then(function (j) {
        var m = (j.error && j.error.message) || ('HTTP ' + r.status);
        if (r.status === 401) m = 'API-nyckeln är ogiltig.';
        if (r.status === 429) m = 'För många frågor just nu. Vänta en stund och försök igen.';
        throw new Error(m);
      });
      var reader = r.body.getReader(), dec = new TextDecoder(), buf = '', out = '', stop = null;
      var pump = function () {
        return reader.read().then(function (res) {
          if (res.done) return;
          buf += dec.decode(res.value, { stream: true });
          var parts = buf.split('\n\n');
          buf = parts.pop();
          parts.forEach(function (chunk) {
            var line = chunk.split('\n').filter(function (l) { return l.indexOf('data:') === 0; })[0];
            if (!line) return;
            var ev; try { ev = JSON.parse(line.slice(5)); } catch (e) { return; }
            if (ev.type === 'content_block_delta' && ev.delta && ev.delta.type === 'text_delta') { out += ev.delta.text; bot.textContent = out; $('#ai-msgs').scrollTop = 1e9; }
            else if (ev.type === 'message_delta' && ev.delta) stop = ev.delta.stop_reason;
            else if (ev.type === 'error') throw new Error((ev.error && ev.error.message) || 'Fel i svaret');
          });
          return pump();
        });
      };
      return pump().then(function () {
        if (stop === 'refusal' && !out) out = 'Assistenten kunde inte svara på den frågan. Försök formulera den på ett annat sätt.';
        if (stop === 'max_tokens') out += '\n\n(Svaret blev för långt och kortades av.)';
        bot.classList.remove('typing');
        bot.textContent = out;
        aiTools(bot, out);
        AI.msgs.push({ role: 'assistant', content: out || '(tomt svar)' });
        store.set('bloms-admin-ai-chat', AI.msgs.slice(-30), sessionStorage);
        $('#ai-status').textContent = '';
      });
    }).catch(function (e) {
      bot.classList.remove('typing');
      if (e.name === 'AbortError') { bot.textContent = (bot.textContent || '') + '\n(Stoppad)'; AI.msgs.pop(); }
      else { bot.classList.add('err'); bot.textContent = 'Kunde inte få svar: ' + e.message; AI.msgs.pop(); }
      $('#ai-status').textContent = '';
    }).then(function () { AI.busy = false; $('#ai-send').disabled = false; $('#ai-stop').hidden = true; AI.ctrl = null; });
  }
  var aiWired = false;
  function renderAi() {
    if (aiWired) return;
    aiWired = true;
    $('#ai-key').value = store.get(AI_KEY) || store.get(AI_KEY, sessionStorage) || '';
    $('#ai-remember').checked = !!store.get(AI_KEY);
    var saveKey = function () {
      var k = $('#ai-key').value.trim();
      store.del(AI_KEY); store.del(AI_KEY, sessionStorage);
      if (k) store.set(AI_KEY, k, $('#ai-remember').checked ? localStorage : sessionStorage);
    };
    $('#ai-key').addEventListener('change', saveKey);
    $('#ai-remember').addEventListener('change', saveKey);
    $('#ai-page').innerHTML = '<option value="">Ingen sida</option>' + S.manifest.pages.map(function (p) { return '<option value="' + esc(p.slug) + '">' + esc(p.name || p.slug) + '</option>'; }).join('');
    AI_CHIPS.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = c;
      b.addEventListener('click', function () {
        if (/Solceller/.test(c)) $('#ai-page').value = 'solceller';
        aiSend(c);
      });
      $('#ai-chips').appendChild(b);
    });
    $('#ai-form').addEventListener('submit', function (e) { e.preventDefault(); aiSend($('#ai-text').value); });
    $('#ai-text').addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); aiSend(this.value); } });
    $('#ai-stop').addEventListener('click', function () { if (AI.ctrl) AI.ctrl.abort(); });
    $('#ai-clear').addEventListener('click', function () {
      if (AI.busy) return;
      AI.msgs = [];
      store.del('bloms-admin-ai-chat', sessionStorage);
      $('#ai-msgs').innerHTML = '';
      toast('Ny konversation');
    });
    var saved = store.get('bloms-admin-ai-chat', sessionStorage) || [];
    saved.forEach(function (m) {
      var shown = m.role === 'user' ? m.content.replace(/^Text från sidan[\s\S]*?<\/sida>\n\n/, '') : m.content;
      var d = aiBubble(m.role === 'user' ? 'user' : 'bot', shown);
      if (m.role !== 'user') aiTools(d, m.content);
    });
    AI.msgs = saved;
  }

  // ---------------------------------------------------------------- inloggning
  // Användare sparas i site/admin/users.json. Lösenord lagras aldrig, bara en PBKDF2-härledning.
  // Samma härledning ger en AES-nyckel som krypterar användarens GitHub-token.
  var AUTH = { users: [], me: null };
  var ITER = 210000, MIN_PW = 12;
  var te = new TextEncoder();
  var hex = function (buf) { return [].map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); };
  var unhex = function (h) { return new Uint8Array(h.match(/../g).map(function (x) { return parseInt(x, 16); })); };
  var b64e = function (buf) { var s = ''; new Uint8Array(buf).forEach(function (b) { s += String.fromCharCode(b); }); return btoa(s); };
  var b64d = function (str) { var s = atob(str), a = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a; };
  var rand = function (n) { var a = new Uint8Array(n); crypto.getRandomValues(a); return a; };

  function rawUrl(path) {
    var g = S.gh.owner ? S.gh : GH_DEFAULT;
    return 'https://raw.githubusercontent.com/' + g.owner + '/' + g.repo + '/' + g.branch + '/' + g.path + '/' + path + '?t=' + Date.now();
  }
  function derive(pass, saltHex, iter) {
    return crypto.subtle.importKey('raw', te.encode(pass), 'PBKDF2', false, ['deriveBits'])
      .then(function (k) { return crypto.subtle.deriveBits({ name: 'PBKDF2', salt: unhex(saltHex), iterations: iter, hash: 'SHA-256' }, k, 512); })
      .then(function (bits) {
        return crypto.subtle.importKey('raw', bits.slice(32), 'AES-GCM', false, ['encrypt', 'decrypt'])
          .then(function (key) { return { verifier: hex(bits.slice(0, 32)), key: key }; });
      });
  }
  function makeUser(name, pass, role, token, created) {
    var salt = hex(rand(16));
    return derive(pass, salt, ITER).then(function (d) {
      var iv = rand(12);
      var done = function (ct) {
        return { username: name, role: role, salt: salt, iterations: ITER, verifier: d.verifier,
          token: ct ? { iv: b64e(iv), data: b64e(ct) } : null, created: created || new Date().toISOString() };
      };
      return token ? crypto.subtle.encrypt({ name: 'AES-GCM', iv: iv }, d.key, te.encode(token)).then(done) : done(null);
    });
  }
  function unlock(u, pass) {
    return derive(pass, u.salt, u.iterations || ITER).then(function (d) {
      if (d.verifier !== u.verifier) throw new Error('auth');
      if (!u.token) return '';
      return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64d(u.token.iv) }, d.key, b64d(u.token.data))
        .then(function (pt) { return new TextDecoder().decode(pt); });
    });
  }
  function findUser(name) {
    name = (name || '').trim().toLowerCase();
    return AUTH.users.filter(function (u) { return u.username.toLowerCase() === name; })[0];
  }
  function loadUsers() {
    return fetch(rawUrl('admin/users.json'), { cache: 'no-store' }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .catch(function () { return fetch('users.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }); })
      .catch(function () { return {}; })
      .then(function (j) { AUTH.users = (j && j.users) || []; return AUTH.users; });
  }
  function saveUsers(msg) {
    readGhSafe();
    var body = JSON.stringify({ version: 1, users: AUTH.users }, null, 1);
    if (S.token) return putFile('admin/users.json', b64(body), 'Admin: ' + msg);
    download('users.json', body);
    toast('users.json laddades ner. Lägg den i site/admin/ på sajten så att ändringen gäller överallt.');
    return Promise.resolve();
  }
  function readGhSafe() { if ($('#g-owner') && $('#g-owner').value) readGh(); }
  function tokenCanPush(token) {
    var old = S.token;
    S.token = token;
    return gh('').then(function (r) {
      S.token = old;
      if (r.permissions && r.permissions.push === false) throw new Error('Token saknar skrivrätt till ' + r.full_name);
      return r;
    }, function (e) { S.token = old; throw new Error('Token fungerar inte: ' + e.message); });
  }

  // session
  var SESSION = 'bloms-admin-session';
  function startSession(u, token, remember) {
    var s = { user: u.username, role: u.role, token: token, exp: Date.now() + (remember ? 14 * 864e5 : 12 * 36e5) };
    store.del(SESSION); store.del(SESSION, sessionStorage);
    store.set(SESSION, s, remember ? localStorage : sessionStorage);
  }
  function getSession() {
    var s = store.get(SESSION, sessionStorage) || store.get(SESSION);
    if (!s || !s.exp || s.exp < Date.now()) { endSession(); return null; }
    return s;
  }
  function endSession() { store.del(SESSION); store.del(SESSION, sessionStorage); }
  function updateSessionToken(token) {
    var s = getSession(); if (!s) return;
    s.token = token;
    var remember = !!store.get(SESSION);
    store.set(SESSION, s, remember ? localStorage : sessionStorage);
  }

  // spärr efter för många felaktiga försök
  var FAILS = 'bloms-admin-fails';
  function lockedFor() { var f = store.get(FAILS) || {}; return f.until && f.until > Date.now() ? Math.ceil((f.until - Date.now()) / 1000) : 0; }
  function failed() {
    var f = store.get(FAILS) || { n: 0 };
    f.n = (f.n || 0) + 1;
    if (f.n >= 5) { f.until = Date.now() + Math.min(15 * 60, 30 * Math.pow(2, f.n - 5)) * 1000; }
    store.set(FAILS, f);
  }

  function enterApp(sess) {
    AUTH.me = findUser(sess.user);
    setToken(sess.token || '');
    $('#login').hidden = true;
    $('#app').hidden = false;
    $('#who').textContent = 'Inloggad som ' + sess.user;
    $('#side-nav a[data-view=anvandare]').hidden = false;
    boot();
  }
  function showLogin() {
    $('#login-loading').hidden = true;
    var setup = !AUTH.users.length;
    $('#setup-form').hidden = !setup;
    $('#login-form').hidden = setup;
    (setup ? $('#su-user') : $('#l-user')).focus();
  }

  $('#login-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var err = $('#l-err'), btn = $('#l-submit');
    var wait = lockedFor();
    if (wait) { err.textContent = 'För många försök. Vänta ' + wait + ' sekunder.'; return; }
    var u = findUser($('#l-user').value), pass = $('#l-pass').value;
    btn.disabled = true; btn.textContent = 'Loggar in…'; err.textContent = '';
    (u ? unlock(u, pass) : Promise.reject(new Error('auth'))).then(function (token) {
      store.del(FAILS);
      startSession(u, token, $('#l-remember').checked);
      enterApp(getSession());
    }).catch(function () {
      failed();
      $('#l-pass').value = '';
      err.textContent = 'Fel användarnamn eller lösenord.';
    }).then(function () { btn.disabled = false; btn.textContent = 'Logga in'; });
  });

  $('#setup-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var err = $('#su-err'), btn = $('#su-submit');
    var name = $('#su-user').value.trim(), pass = $('#su-pass').value;
    if (!/^[\w.\-@]{3,40}$/.test(name)) { err.textContent = 'Användarnamnet ska vara 3–40 tecken: bokstäver, siffror, punkt, bindestreck eller @.'; return; }
    if (pass.length < MIN_PW) { err.textContent = 'Lösenordet måste vara minst ' + MIN_PW + ' tecken.'; return; }
    if (pass !== $('#su-pass2').value) { err.textContent = 'Lösenorden är inte lika.'; return; }
    btn.disabled = true; btn.textContent = 'Skapar konto…'; err.textContent = '';
    makeUser(name, pass, 'admin', null).then(function (u) {
      return loadUsers().then(function (list) {
        if (list.length) throw new Error('Det finns redan användare. Ladda om sidan och logga in.');
        AUTH.users = [u];
        return saveUsers('skapade administratör ' + name);
      }).then(function () {
        startSession(u, '', false);
        enterApp(getSession());
      });
    }).catch(function (x) { err.textContent = x.message || String(x); })
      .then(function () { btn.disabled = false; btn.textContent = 'Skapa konto och logga in'; });
  });

  // användarhantering
  function isAdmin() { return AUTH.me && AUTH.me.role === 'admin'; }
  function renderUsers() {
    var ul = $('#u-list');
    ul.innerHTML = '';
    $('#u-count').textContent = AUTH.users.length + (AUTH.users.length === 1 ? ' användare' : ' användare');
    AUTH.users.forEach(function (u) {
      var li = document.createElement('li');
      var me = AUTH.me && u.username === AUTH.me.username;
      li.innerHTML = '<span class="av">' + esc(u.username.slice(0, 1)) + '</span><span class="what"><b>' + esc(u.username) + (me ? ' (du)' : '') + '</b><small>' +
        (u.role === 'admin' ? 'Administratör' : 'Redaktör') + ' · skapad ' + esc(new Date(u.created).toLocaleDateString('sv-SE')) + '' + '</small></span>' +
        (isAdmin() && !me ? '<button class="link danger" type="button">Ta bort</button>' : '');
      var b = li.querySelector('button');
      if (b) b.addEventListener('click', function () {
        if (b.dataset.confirm !== '1') { b.dataset.confirm = '1'; b.textContent = 'Klicka igen för att ta bort'; return; }
        var keep = AUTH.users.filter(function (x) { return x !== u; });
        if (!keep.some(function (x) { return x.role === 'admin'; })) { toast('Minst en administratör måste finnas.', true); return; }
        var before = AUTH.users;
        AUTH.users = keep;
        saveUsers('tog bort användare ' + u.username).then(function () { toast(u.username + ' är borttagen.'); renderUsers(); })
          .catch(function (x) { AUTH.users = before; toast('Kunde inte spara: ' + x.message, true); renderUsers(); });
      });
      ul.appendChild(li);
    });
    $('#u-add').hidden = !isAdmin();
  }
  function genPassword() {
    var cs = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789-_!?';
    return [].map.call(rand(16), function (b) { return cs[b % cs.length]; }).join('');
  }
  function addUser(e) {
    e.preventDefault();
    var msg = $('#u-msg'), name = $('#u-name').value.trim(), pass = $('#u-pass').value;
    if (!isAdmin()) return;
    if (!/^[\w.\-@]{3,40}$/.test(name)) { msg.textContent = 'Användarnamnet ska vara 3–40 tecken.'; return; }
    if (findUser(name)) { msg.textContent = 'Användarnamnet finns redan.'; return; }
    if (pass.length < MIN_PW) { msg.textContent = 'Lösenordet måste vara minst ' + MIN_PW + ' tecken.'; return; }
    if (pass !== $('#u-pass2').value) { msg.textContent = 'Lösenorden är inte lika.'; return; }
    msg.textContent = 'Sparar…';
    makeUser(name, pass, $('#u-role').value, null).then(function (u) {
      AUTH.users = AUTH.users.concat([u]);
      return saveUsers('lade till användare ' + name);
    }).then(function () {
      $('#u-add').reset(); msg.textContent = name + ' är tillagd.'; renderUsers();
    }).catch(function (x) { AUTH.users = AUTH.users.filter(function (u) { return u.username !== name; }); msg.textContent = 'Kunde inte spara: ' + x.message; });
  }
  function replaceMe(u) {
    AUTH.users = AUTH.users.map(function (x) { return x.username === AUTH.me.username ? u : x; });
    AUTH.me = u;
  }
  function changePassword(e) {
    e.preventDefault();
    var msg = $('#pw-msg'), np = $('#pw-new').value;
    if (np.length < MIN_PW) { msg.textContent = 'Minst ' + MIN_PW + ' tecken.'; return; }
    if (np !== $('#pw-new2').value) { msg.textContent = 'Lösenorden är inte lika.'; return; }
    msg.textContent = 'Sparar…';
    var before = AUTH.users, beforeMe = AUTH.me;
    unlock(AUTH.me, $('#pw-old').value).then(function (token) {
      return makeUser(AUTH.me.username, np, AUTH.me.role, token || null, AUTH.me.created);
    }, function () { throw new Error('Nuvarande lösenord stämmer inte.'); }).then(function (u) {
      replaceMe(u);
      return saveUsers('bytte lösenord för ' + u.username);
    }).then(function () { $('#u-pw').reset(); msg.textContent = 'Lösenordet är bytt.'; })
      .catch(function (x) { AUTH.users = before; AUTH.me = beforeMe; msg.textContent = x.message; });
  }
  // start: läs användare och kontrollera session
  if (!window.crypto || !crypto.subtle) {
    $('#login-loading').textContent = 'Adminpanelen kräver en säker anslutning (https).';
  } else {
    S.gh = Object.assign({}, GH_DEFAULT, store.get('bloms-admin-gh') || {});
    loadUsers().then(function () {
      var sess = getSession();
      if (sess && findUser(sess.user)) enterApp(sess);
      else { endSession(); showLogin(); }
    });
  }
})();
