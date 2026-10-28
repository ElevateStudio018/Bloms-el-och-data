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

## Adminpanel (`/admin`)

Öppna `site/admin/index.html` på den publicerade sajten (t.ex. via githack eller er webbhost).

- **Sidor & innehåll**: klicka på en text i förhandsvisningen och skriv direkt. Klicka på en bild för att byta den
  eller ändra alt-text. Länkar på knappar kan pekas om. Sök efter text på sidan.
- **Herokarusell**: dra för att ändra ordning, dölj förslag, välj startförslag eller visa bara ett.
- **SEO**: titel och beskrivning per sida med teckenräknare och Google-förhandsvisning.
- **Mediabibliotek**: alla bilder, uppladdning (skalas ner till max 2000 px).
- **Företag & tema**: telefon, e-post, adress och org.nr byts på alla sidor. Färger och cookie-banner.
- **Publicera**: lista över alla ändringar med ångra per rad. Publicerar `site/content.json` och uppladdade
  bilder till GitHub med en fine-grained token (behörighet *Contents: Read and write* för repot).
  Export/import av JSON som säkerhetskopia.
- **Historik**: tidigare publicerade versioner, kan läsas in och återställas.

Ändringar sparas som utkast i webbläsaren tills de publiceras. Sajten läser `content.json` när sidan laddas.

### Inloggning

- Första gången visas **Skapa första administratören**: användarnamn, lösenord (minst 12 tecken) och en GitHub-token.
  Kontot sparas i `site/admin/users.json` i repot.
- Därefter loggar man in med användarnamn och lösenord. Under **Användare** kan administratörer lägga till och ta bort
  användare (roller: administratör, redaktör), och alla kan byta sitt lösenord och sin token.
- Lösenord sparas aldrig. `users.json` innehåller en PBKDF2-härledning (SHA-256, 210 000 iterationer, unikt salt per
  användare) och användarens GitHub-token krypterad med AES-GCM och en nyckel från lösenordet.
- Fem felaktiga försök ger en spärr som växer från 30 sekunder upp till 15 minuter.

Sajten är statisk, så filerna (även `users.json`) går att läsa för den som letar. Skyddet är att token bara kan
låsas upp med rätt lösenord. Använd därför långa lösenord och en fine-grained token som bara har
*Contents: Read and write* för det här repot och ett utgångsdatum.
