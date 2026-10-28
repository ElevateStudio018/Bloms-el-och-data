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

- Logga in med användarnamn och lösenord. Konton finns i `site/admin/users.json`.
- Under **Användare** kan administratörer lägga till och ta bort användare (roller: administratör, redaktör),
  och alla kan byta sitt lösenord. Eftersom sajten är statisk laddas en ny `users.json` ner vid ändring;
  lägg den i `site/admin/` på sajten.
- Lösenord sparas aldrig. `users.json` innehåller en PBKDF2-härledning (SHA-256, 210 000 iterationer, unikt salt).
- Fem felaktiga försök ger en spärr som växer från 30 sekunder upp till 15 minuter.
- Inloggningen varar 12 timmar, eller 14 dagar med "Håll mig inloggad".

### AI-assistent

Chatt med Claude (Opus 5.5) som känner till företagets fakta och sajtens sidor. Välj en sida som sammanhang
för att låta den läsa sidans text. Kräver en API-nyckel från console.anthropic.com som sparas i webbläsaren;
anropet går direkt från webbläsaren till Anthropic.

### Typsnitt

Välj typsnitt för rubriker och brödtext bland 20 Google Fonts. Valet sparas i `content.json` och sajten laddar
typsnitten när sidan öppnas.

### Spara ändringar

**Publicera → Ladda ner content.json** och lägg filen i `site/` på sajten (ersätt den gamla).
Under *Avancerat* går det att publicera direkt till GitHub med en token, men det behövs inte.

Inloggningen hindrar att obehöriga kommer åt panelen i webbläsaren. Eftersom sajten är statisk kan den inte
ändra något på servern av sig själv: ändringar blir synliga först när den nya filen läggs upp.
