# Infoskjerm – Servicetorget Selbu

Én HTML-side som vises på lobbyskjermen via MagicInfo (web-innhold i spillelisten).
Innholdet henter seg selv:

- **Tælet Kultursal** – kommende arrangementer hentes automatisk fra det åpne
  events-API-et på taletkultursal.no. Null vedlikehold.
- **Bygdekinoen** – plakatbilder som ligger i `plakater/`-mappa i dette repoet.
  Oppdateres med `git push` – ingen MagicInfo-innlogging.

## Førstegangsoppsett

1. Opprett et **offentlig** repo på github.com, f.eks. `infoskjerm` (uten README).
2. Push innholdet i denne mappa:

   **[LOKAL]**
   ```powershell
   cd <denne mappa>
   git init
   git add .
   git commit -m "Infoskjerm v1"
   git branch -M main
   git remote add origin git@github.com:<BRUKER>/infoskjerm.git
   git push -u origin main
   ```

3. På github.com: **Settings → Pages → Source: Deploy from a branch → main / (root) → Save.**
   Etter et par minutter ligger siden på `https://<BRUKER>.github.io/infoskjerm/`.
4. Åpne URL-en i en nettleser og sjekk at kultursal-programmet vises.
5. I MagicInfo: legg URL-en inn som web-innhold og bytt den inn i spillelisten
   (erstatter taletkultursal.no/infoskjerm2/). Dette gjøres **én gang**.

Siden finner selv ut hvilket repo den ligger i (via github.io-adressen), så det
er ingenting å konfigurere i `index.html`. (Ved behov kan `GITHUB_USER`/`GITHUB_REPO`
overstyres øverst i script-delen.)

## Legge ut nye kinoplakater

Lagre plakatene som **JPG/PNG** (ikke PDF) i `plakater/`-mappa, og push:

**[LOKAL]**
```powershell
cd <denne mappa>
copy "C:\Users\...\plakat.jpg" "plakater\2026-09-15 1800 En nasjon i sjakk.jpg"
git add plakater
git commit -m "Nye kinoplakater"
git push
```

Skjermen viser de nye plakatene innen ca. et minutt (senest ved neste
30-minutters oppdatering).

### Filnavn-konvensjon (valgfri, men lur)

| Filnavn | Vises som |
|---|---|
| `2026-09-15 1800 En nasjon i sjakk.jpg` | «En nasjon i sjakk» + *tirsdag 15. september kl. 18:00* |
| `2026-09-15 En nasjon i sjakk.jpg` | tittel + dato uten klokkeslett |
| `En nasjon i sjakk.jpg` | bare tittel |

Plakater med dato **som er passert, forsvinner automatisk** fra skjermen –
men rydd gjerne i mappa av og til likevel.

## Slik virker det (teknisk)

- Kultursal: `GET https://www.taletkultursal.no/wp-json/tribe/events/v1/events`
  (The Events Calendar REST API, åpent). Kun framtidige arrangementer vises.
- Bygdekino: `GET https://api.github.com/repos/<bruker>/<repo>/contents/plakater`
  (offentlig GitHub-API) → bildene lastes fra `download_url`.
- Rotasjon hvert 12. sekund; posisjonen huskes (localStorage) så neste visning i
  MagicInfo-rotasjonen fortsetter der forrige slapp.
- Data hentes på nytt hvert 30. minutt; siden laster seg selv helt på nytt kl. 04.
- Hvis begge kilder er tomme/feiler vises en nøytral «Selbu kommune»-side.
