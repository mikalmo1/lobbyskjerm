#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Henter NRK-RSS (Trøndelag + nasjonale toppsaker), mikser dem og skriver
nyheter.json i repo-roten. Kjøres av .github/workflows/nyheter.yml.

Hvorfor server-side: NRK setter ikke CORS-headere, så lobbyskjermen (statisk
GitHub Pages) kan ikke hente RSS-en selv. Denne jobben henter i stedet på
GitHub sin runner og committer en same-origin nyheter.json som skjermen leser.

Robusthet: feiler én feed, brukes den andre. Feiler begge, skrives ingenting
(forrige nyheter.json beholdes). Ingen tredjepartsavhengighet.
"""

import json
import os
import sys
import html
import datetime
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = [
    ("Trøndelag", "https://www.nrk.no/trondelag/toppsaker.rss"),
    ("NRK",       "https://www.nrk.no/toppsaker.rss"),
]

PER_FEED = 8      # maks saker hentet fra hver feed
MAKS_TOTALT = 16  # maks saker i miksen
UA = "Mozilla/5.0 (lobbyskjerm Selbu kommune; +https://github.com/mikalmo1/lobbyskjerm)"


def hent_feed(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def parse_rss(raw):
    """Returnerer liste av {tittel, lenke} fra en RSS 2.0-payload."""
    root = ET.fromstring(raw)
    saker = []
    for item in root.iter("item"):
        tittel_el = item.find("title")
        lenke_el = item.find("link")
        if tittel_el is None or not (tittel_el.text or "").strip():
            continue
        tittel = html.unescape(tittel_el.text).strip()
        tittel = " ".join(tittel.split())  # normaliser mellomrom/linjeskift
        lenke = (lenke_el.text or "").strip() if lenke_el is not None else ""
        saker.append({"tittel": tittel, "lenke": lenke})
    return saker


def miks(feeds_saker):
    """Fletter listene annenhver (Trøndelag, NRK, Trøndelag, ...), deduplikerer."""
    sett = set()
    ut = []
    i = 0
    while len(ut) < MAKS_TOTALT:
        la_til = False
        for kilde, saker in feeds_saker:
            if i < len(saker):
                s = saker[i]
                nokkel = s["tittel"].lower()
                if nokkel not in sett:
                    sett.add(nokkel)
                    ut.append({"tittel": s["tittel"], "kilde": kilde, "lenke": s["lenke"]})
                    la_til = True
                    if len(ut) >= MAKS_TOTALT:
                        break
        if not la_til:
            break
        i += 1
    return ut


def main():
    feeds_saker = []
    for kilde, url in FEEDS:
        try:
            raw = hent_feed(url)
            saker = parse_rss(raw)[:PER_FEED]
            if saker:
                feeds_saker.append((kilde, saker))
                print("OK  %-10s %2d saker  %s" % (kilde, len(saker), url))
            else:
                print("TOM %-10s          %s" % (kilde, url))
        except Exception as e:
            print("FEIL %-10s %s  (%s)" % (kilde, url, e), file=sys.stderr)

    if not feeds_saker:
        print("Ingen feeder svarte — beholder forrige nyheter.json.", file=sys.stderr)
        return 0  # ikke overskriv siste gode fil

    saker = miks(feeds_saker)
    data = {
        "oppdatert": datetime.datetime.now(datetime.timezone.utc)
                        .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "saker": saker,
    }

    ut_sti = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nyheter.json")
    with open(ut_sti, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Skrev %d saker til %s" % (len(saker), ut_sti))
    return 0


if __name__ == "__main__":
    sys.exit(main())
