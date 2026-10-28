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
  var VIEWS = { oversikt: 'Översikt', innehall: 'Sidor & innehåll', hero: 'Herokarusell', seo: 'SEO', media: 'Mediabibliotek', installningar: 'Företag & tema', publicera: 'Publicera', historik: 'Historik' };

  var S = { manifest: null, published: null, draft: null, log: [], undo: [], gh: {}, token: '', page: 'index', frameWin: null, heroWin: null, sel: null, picking: null };

  function blank() { return { version: 1, updated: null, text: {}, link: {}, img: {}, meta: {}, hero: {}, settings: {}, uploads: {} }; }
  function normal(c) {
    var b = blank();
    c = c && typeof c === 'object' ? c : {};
    Object.keys(b).forEach(function (k) { if (c[k] == null) c[k] = b[k]; });
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
    ({ oversikt: renderOverview, innehall: renderEditor, hero: renderHero, seo: renderSeo, media: renderMedia, installningar: renderSettings, publicera: renderPublish, historik: function () {} })[v]();
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
    if (!S.token) todo.push('<li><span class="what">Ingen GitHub-token. Ändringar kan bara exporteras, inte publiceras.</span><a href="#publicera">Anslut</a></li>');
    if (ch.length) todo.push('<li><span class="what">' + ch.length + ' ändringar väntar på publicering.</span><a href="#publicera">Publicera</a></li>');
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
    S.draft.settings = s;
    commit(what, 'alla', true);
  }

  function renderPublish() {
    var ch = changes(), box = $('#p-diff');
    var g = S.gh;
    $('#g-owner').value = g.owner; $('#g-repo').value = g.repo; $('#g-branch').value = g.branch; $('#g-token').value = S.token;
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
    var t = $('#g-token').value.trim();
    if (t !== S.token) setToken(t, !!store.get('bloms-admin-token'));
    store.set('bloms-admin-gh', S.gh);
  }
  function setToken(t, remember) {
    S.token = t;
    store.del('bloms-admin-token'); store.del('bloms-admin-token', sessionStorage);
    if (t) store.set('bloms-admin-token', t, remember ? localStorage : sessionStorage);
    var c = $('#conn');
    c.textContent = t ? 'GitHub ansluten' : 'Inte ansluten';
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
    if (!S.token) { toast('Lägg in en GitHub-token först, eller exportera JSON.', true); return; }
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

  function exportJson() {
    var blob = new Blob([JSON.stringify(S.draft, null, 1)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'content.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    toast('content.json exporterad');
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
      fetch('../content.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
    ]).then(function (res) {
      S.manifest = res[0];
      S.published = normal(res[1]);
      var saved = store.get('bloms-admin-draft');
      S.draft = normal(saved && saved.draft ? saved.draft : clone(S.published));
      S.log = (saved && saved.log) || [];
      S.gh = Object.assign({}, GH_DEFAULT, store.get('bloms-admin-gh') || {});
      setToken(store.get('bloms-admin-token') || store.get('bloms-admin-token', sessionStorage) || '', !!store.get('bloms-admin-token'));
      wire();
      status();
      render(current());
    }).catch(function (e) {
      document.body.innerHTML = '<p style="padding:40px">Kunde inte läsa sajtens manifest (' + esc(e.message) + '). Kör <code>python3 site/build.py</code>.</p>';
    });
  }
  function enter(token, remember) {
    if (token) setToken(token, remember);
    store.set('bloms-admin-session', 1, sessionStorage);
    $('#login').hidden = true;
    $('#app').hidden = false;
    boot();
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
      setToken('', false);
      store.del('bloms-admin-session', sessionStorage);
      location.hash = '';
      location.reload();
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
    ['#g-owner', '#g-repo', '#g-branch', '#g-token'].forEach(function (s) { $(s).addEventListener('change', readGh); });
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
  }

  $('#login-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var t = $('#l-token').value.trim();
    if (!t) { $('#l-err').textContent = 'Klistra in en token, eller fortsätt utan.'; return; }
    enter(t, $('#l-remember').checked);
  });
  $('#l-demo').addEventListener('click', function () { enter('', false); });
  if (store.get('bloms-admin-session', sessionStorage) || store.get('bloms-admin-token')) enter('', false);
})();
