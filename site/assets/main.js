(function () {
  // Mobilmeny
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

  // Cookie-banner
  var KEY = 'blomsel-cookies-ok';
  var seen = false;
  try { seen = localStorage.getItem(KEY) === '1'; } catch (e) {}
  var bar = document.getElementById('cookie');
  if (bar && !seen) {
    bar.hidden = false;
    bar.querySelector('button').addEventListener('click', function () {
      bar.hidden = true;
      try { localStorage.setItem(KEY, '1'); } catch (e) {}
    });
  }

  // Kontaktformulär: bygger ett mejl till info@blomsel.se
  var form = document.getElementById('kontaktform');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = form.querySelector('.msg');
      var d = new FormData(form);
      if (!d.get('namn') || !d.get('meddelande') || (!d.get('epost') && !d.get('telefon'))) {
        msg.setAttribute('data-err', '');
        msg.textContent = 'Fyll i namn, meddelande och e-post eller telefon så att vi kan svara dig.';
        return;
      }
      msg.removeAttribute('data-err');
      var body = 'Namn: ' + d.get('namn') + '\nE-post: ' + d.get('epost') + '\nTelefon: ' + d.get('telefon') + '\nÄrende: ' + d.get('arende') + '\n\n' + d.get('meddelande');
      var href = 'mailto:info@blomsel.se?subject=' + encodeURIComponent('Förfrågan: ' + d.get('arende')) + '&body=' + encodeURIComponent(body);
      msg.textContent = 'Ditt e-postprogram öppnas med meddelandet ifyllt. Öppnas inget? Mejla info@blomsel.se eller ring 0705-15 02 11.';
      window.location.href = href;
    });
  }
})();

// Herokarusell på startsidan: tio förslag som bläddras i sidled
(function () {
  var track = document.getElementById('hx-track');
  if (!track) return;
  var slides = [].slice.call(track.children);
  var lab = document.getElementById('hx-lab'), dots = document.getElementById('hx-dots');
  var prev = document.querySelector('.hx-prev'), next = document.querySelector('.hx-next');
  var cur = 0;
  slides.forEach(function (s, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = s.id.slice(1);
    b.title = 'Förslag ' + s.id.slice(1) + ' · ' + s.dataset.name;
    b.setAttribute('aria-label', b.title);
    b.addEventListener('click', function () { go(i); });
    dots.appendChild(b);
  });
  function show(i) {
    cur = i;
    var s = slides[i];
    lab.innerHTML = '<b>' + (i + 1) + ' / ' + slides.length + '</b>Förslag ' + s.id.slice(1) + ' · ' + s.dataset.name;
    [].forEach.call(dots.children, function (d, j) { d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    track.style.height = s.offsetHeight + 'px';
    prev.disabled = i === 0;
    next.disabled = i === slides.length - 1;
  }
  function go(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    track.scrollTo({ left: i * track.clientWidth, behavior: 'smooth' });
    show(i);
  }
  var t;
  track.addEventListener('scroll', function () {
    clearTimeout(t);
    t = setTimeout(function () { show(Math.round(track.scrollLeft / track.clientWidth)); }, 60);
  }, { passive: true });
  prev.addEventListener('click', function () { go(cur - 1); });
  next.addEventListener('click', function () { go(cur + 1); });
  document.addEventListener('keydown', function (e) {
    if (e.target.closest && e.target.closest('input,textarea,select')) return;
    var r = track.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
  });
  window.addEventListener('resize', function () { track.style.height = ''; show(cur); });
  show(0);
})();
