# DEPLOY — Vær-chip + NRK-ticker i bunnlinja (lobbyskjerm)

Bunnlinja på lobbyskjermen fikk to ting:

- **Vær-chip** (venstre, ved klokka): «Selbu» + Yr-ikon + grader. Henter fra
  samme met.no-kall som den eksisterende helskjerm-vær-sliden (som beholdes).
- **Rullende NRK-ticker** (nederst): mikser NRK Trøndelag + nasjonale toppsaker.

NRK setter ikke CORS-headere, så den statiske Pages-siden kan ikke hente RSS-en
selv. En **GitHub Action** henter i stedet server-side hvert kvarter og committer
`nyheter.json`, som skjermen leser same-origin. Samme mønster som `program.json`.

Merking: **[LOKAL]** = PowerShell på PC-en.

---

## Nye/endra filer (repo `mikalmo1/lobbyskjerm`)

- `.github/workflows/nyheter.yml` — planlagt jobb (`*/15 * * * *` + manuell start).
- `scripts/hent_nyheter.py` — henter/mikser feedene, skriver `nyheter.json`.
- `index.html` — vær-chip + ticker (markup, CSS, JS). Tickeren vises kun når
  `nyheter.json` har saker; mangler fila, faller bunnlinja tilbake til før.

## 1. Push

```powershell
# [LOKAL]  (i lobbyskjerm-repoet)
git add .github/workflows/nyheter.yml scripts/hent_nyheter.py index.html DEPLOY-nyheter.md
git commit -m "Bunnlinje: vaer-chip + rullende NRK-ticker (nyheter.json via Action)"
git push
```

## 2. Kjør Action-en én gang manuelt (seeder nyheter.json)

GitHub → repoet → **Actions** → evt. «I understand… enable workflows» →
velg **Hent NRK-nyheter** → **Run workflow** (branch `main`).

Deretter går den av seg selv hvert kvarter.

## 3. Verifiser

- I repoet skal `nyheter.json` dukke opp (commit av `nyheter-bot`).
- `https://mikalmo1.github.io/lobbyskjerm/nyheter.json` skal gi JSON med `saker`.
- På skjermen (eller nettleser mot Pages-URL-en): vær-chip nede til venstre,
  gull «NRK»-merke og rullende saker langs bunnen. Skjermen henter nye saker
  hvert 15. min; en reload viser dem umiddelbart.

## Verdt å vite

- **Action-logg:** åpne siste kjøring. `OK Trøndelag …` / `OK NRK …` = feed hentet.
  Ser du `FEIL … 403`, blokkerer NRK runner-IP-en — da bytter vi tickeren til å
  hente via en CORS-proxy i stedet (liten endring i `index.html`). Skriptet
  overskriver aldri en god `nyheter.json` med tomt resultat.
- **Planlagte Actions** kan settes på pause etter 60 dager uten aktivitet i
  repoet. `program.json`-pushene holder det aktivt, men verdt å vite.
- **Justering:** rullefart = `TICKER_PX_PER_SEK` i `index.html`; antall saker =
  `PER_FEED` / `MAKS_TOTALT` i `scripts/hent_nyheter.py`; feed-valg = `FEEDS`
  samme sted.
