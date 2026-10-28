// Gör PDF:er av info.html och offert.html. Kör: node design/offert/render.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [src, out] of [['info.html', 'Bloms-El-och-Data-forslag-Elevate-Studio.pdf'], ['offert.html', 'Offert-Bloms-El-och-Data-Elevate-Studio.pdf']]) {
    await p.goto('file://' + path.join(__dirname, src), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: path.join(__dirname, out), format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log(out);
  }
  await b.close();
})();
