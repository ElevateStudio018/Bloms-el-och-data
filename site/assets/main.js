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
