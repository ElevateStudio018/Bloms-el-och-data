# Nya blomsel.se

Statisk webbplats i stil med heroförslag 15 (fotohero med överlappande tjänstekort, original-röd navbar, Poppins).
Allt innehåll är hämtat från blomsel.se (se `../scrape/`).

- `build.py` genererar alla sidor: `python3 site/build.py`
- `assets/style.css` designsystemet, `assets/main.js` mobilmeny, cookie-banner och kontaktformulär
- `img/` optimerade bilder från originalsajten

Sidorna har samma namn som på originalet med `.html` (t.ex. `tjanster.html`). Wix-mallsidan
`inquiry-services-page` var tom och är inte med.

Kontaktformuläret öppnar ett ifyllt mejl till info@blomsel.se. Vill ni ta emot förfrågningar direkt
behövs en formulärtjänst (t.ex. Formspree eller Netlify Forms) när sajten publiceras.
