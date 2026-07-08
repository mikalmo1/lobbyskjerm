# Infoskjerm – Servicetorget Selbu

Én HTML-side som vises på lobbyskjermen via MagicInfo (web-innhold i spillelisten).
Innholdet henter seg selv:

- **Tælet Kultursal** – kommende arrangementer hentes automatisk fra det åpne
  events-API-et på taletkultursal.no. Null vedlikehold.
- **Bygdekinoen** – plakatbilder som ligger i `plakater/`-mappa i dette repoet.
  Oppdateres med `git push` – ingen MagicInfo-innlogging.
- **«Selbu i dag»-sliden** – dashboard med fire felt, alt henter seg selv:
  - *Været i Selbu* – api.met.no (Yr), nå + tre punkter framover.
  - *Neste buss* – de tre neste avgangene fra **Bell skole/Selbu ungdomsskole**
    (Entur JourneyPlanner, åpent API; grønn prikk = sanntid). Oppdateres hvert
    5. minutt.
  - *Beskjeder* – fra `beskjeder.json` i dette repoet (se under). Pushes normalt
    fra Knuten, men kan også redigeres for hånd + `git push`.
  - *Siste fra NRK* – de to øverste sakene fra `nyheter.json` (samme kilde som
    tickeren i bunnlinja). Skjules automatisk hvis tre beskjeder trenger plassen.

## Beskjeder fra kommune og skole (`beskjeder.json`)

```json
{
 "beskjeder": [
  {
   "tittel": "Foreldremøte 8. trinn torsdag kl. 18",
   "tekst": "Møtet holdes i kultursalen. Velkommen!",
   "avsender": "Selbu ungdomsskole",
   "viktig": false,
   "fra": "2026-08-10",
   "til": "2026-08-13"
  }
 ]
}
```

- `tittel` er eneste påkrevde felt.
- `avsender` vises som liten etikett (f.eks. «Selbu kommune» / «Selbu ungdomsskole»).
- `viktig: true` gir rødt, uthevet kort og sorteres først.
- `fra`/`til` er valgfrie ISO-datoer; beskjeden vises kun i intervallet.
  `til` uten klokkeslett gjelder **ut** den dagen. Utløpte beskjeder forsvinner
  av seg selv – fila trenger ikke ryddes for at skjermen skal bli riktig.
- Maks 3 beskjeder vises (viktige først). Skjermen sjekker fila hvert 5. minutt.

## Førstegangsoppsett

1. Opprett et **offentlig** repo på github.com (dette repoet: `lobbyskjerm`).
2. Push innholdet i denne mappa:

   **[LOKAL]**
   ```powershell
   cd <denne mappa>
   git init
   git add .
   git commit -m "Infoskjerm v1"
   git branch -M main
   git remote add origin https://github.com/mikalmo1/lobbyskjerm.git
   git push -u origin main
   ```

3. På github.com: **Settings → Pages → Source: Deploy from a branch → main / (root) → Save.**
   Etter et par minutter ligger siden på `https://mikalmo1.github.io/lobbyskjerm/`.
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
| `2026-09-15 Bygdekino loop.mp4` | video – spilles ferdig én gang per runde, full skjerm |
| `2026-09-15 [skjerm] Bygdekino.png` | bilde i full skjerm **uten** tekstpanel (ferdigdesignet 1920×1080) |

Filer med dato **som er passert, forsvinner automatisk** fra skjermen –
men rydd gjerne i mappa av og til likevel.

### Video

- mp4/webm støttes; spilles av uten lyd (skjermen står i et venterom).
- Siden henter video fra to steder: `plakater/`-mappa (git — hold filer her under
  ~50 MB) og **release-en med tag `infoskjerm`** (assets, tåler store filer —
  det er dit Knutens publiser-knapp legger loop-videoene, komprimert til ~85 MB
  ved behov). Navnekonvensjonen er den samme begge steder.
- Kino-modulen i Knuten har en egen **«Publiser til infoskjerm»**-knapp som legger
  kveldens loop-video (eller lobbyplakat) rett i `plakater/`-mappa her — da trengs
  ikke git i det hele tatt. Jf. `DEPLOY-infoskjerm.md` i portal-repoet.

## Slik virker det (teknisk)

- Kultursal: `GET https://www.taletkultursal.no/wp-json/tribe/events/v1/events`
  (The Events Calendar REST API, åpent). Kun framtidige arrangementer vises.
- Bygdekino: `GET https://api.github.com/repos/<bruker>/<repo>/contents/plakater`
  (offentlig GitHub-API) → bildene lastes fra `download_url`.
- Rotasjon hvert 12. sekund; posisjonen huskes (localStorage) så neste visning i
  MagicInfo-rotasjonen fortsetter der forrige slapp.
- Data hentes på nytt hvert 30. minutt; siden laster seg selv helt på nytt kl. 04.
- Hvis begge kilder er tomme/feiler vises en nøytral «Selbu kommune»-side.
