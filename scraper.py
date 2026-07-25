#!/usr/bin/env python3
"""
Scraper d'offres d'emploi, de stages et de bourses -- Bénin, Afrique & International.

Sources agrégées via flux RSS/pages publiques. Conçu pour tourner sur GitHub
Actions une fois par jour. Écrit un fichier data/offres.json (historique cumulé)
et régénère docs/index.html (site statique servi par GitHub Pages).

IMPORTANT (à lire avant de modifier) :
- Chaque source a son propre parseur car chaque site a une structure différente.
- Si un site change sa structure HTML, seul le parseur correspondant cassera --
  les autres continueront de fonctionner (chaque parseur est protégé par un
  try/except et logue l'erreur au lieu de faire planter tout le script).
- Respecte un délai entre requêtes (voir SLEEP_BETWEEN_REQUESTS) pour rester
  poli avec les serveurs cibles.
"""

import json
import re
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
import feedparser
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scraper")

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "offres.json"
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EmploiBeninBot/1.0; +https://github.com/)"
}
SLEEP_BETWEEN_REQUESTS = 2  # secondes, politesse envers les serveurs
REQUEST_TIMEOUT = 15
MAX_AGE_DAYS = 60  # on ne garde pas d'offres plus vieilles que ça dans le site final


def make_id(*parts) -> str:
    """ID stable basé sur le contenu, pour dédupliquer entre exécutions."""
    raw = "|".join(str(p) for p in parts if p)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def safe_get(url, **kwargs):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception as e:
        log.warning(f"Échec requête {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# SOURCE 1 : ReliefWeb (ONG / humanitaire / international) -- a une vraie API
# ---------------------------------------------------------------------------
def scrape_reliefweb(country="Benin", limit=40):
    """
    ReliefWeb expose une API JSON publique et stable -- source la plus fiable
    du script. Documentation : https://apidoc.reliefweb.int/
    """
    offres = []
    url = "https://api.reliefweb.int/v1/jobs"
    params = {
        "appname": "emploi-benin-site",
        "profile": "list",
        "preset": "latest",
        "limit": limit,
        "filter[field]": "country.name",
        "filter[value]": country,
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            fields = item.get("fields", {})
            title = fields.get("title", "Sans titre")
            link = fields.get("url_alias") or fields.get("url") or ""
            date_created = fields.get("date", {}).get("created", "")
            source_names = [s.get("name") for s in fields.get("source", [])]
            offres.append({
                "id": make_id("reliefweb", item.get("id"), title),
                "titre": title,
                "organisation": ", ".join(source_names) if source_names else "ReliefWeb",
                "lien": link,
                "date_publication": date_created[:10] if date_created else "",
                "localisation": country,
                "categorie": "emploi",
                "source": "ReliefWeb",
            })
    except Exception as e:
        log.warning(f"ReliefWeb ({country}) a échoué : {e}")
    return offres


# ---------------------------------------------------------------------------
# SOURCE 2 : UN Jobs / agences onusiennes -- flux RSS
# ---------------------------------------------------------------------------
def scrape_unjobs_rss(query="Benin"):
    offres = []
    url = f"https://unjobs.org/rss/duty_stations/{query.lower()}"
    feed = feedparser.parse(url)
    for entry in feed.entries:
        offres.append({
            "id": make_id("unjobs", entry.get("link")),
            "titre": entry.get("title", "Sans titre"),
            "organisation": "Agences ONU / UNjobs",
            "lien": entry.get("link", ""),
            "date_publication": entry.get("published", "")[:10] if entry.get("published") else "",
            "localisation": query,
            "categorie": "emploi",
            "source": "UNjobs",
        })
    return offres


# ---------------------------------------------------------------------------
# SOURCE 3 : EmploiBenin.com -- scraping HTML (structure susceptible de changer)
# ---------------------------------------------------------------------------
def scrape_emploibenin():
    offres = []
    resp = safe_get("https://www.emploibenin.com/")
    if not resp:
        return offres
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        # Les annonces sont généralement dans des blocs <a> pointant vers /offre-emploi-benin/
        links = soup.find_all("a", href=re.compile(r"/offre-emploi-benin/"))
        seen = set()
        for a in links:
            href = a.get("href", "")
            if href in seen:
                continue
            seen.add(href)
            titre = a.get_text(strip=True)
            if not titre or len(titre) < 3:
                continue
            full_url = href if href.startswith("http") else f"https://www.emploibenin.com{href}"
            offres.append({
                "id": make_id("emploibenin", full_url),
                "titre": titre,
                "organisation": "Voir annonce",
                "lien": full_url,
                "date_publication": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "localisation": "Bénin",
                "categorie": "emploi",
                "source": "EmploiBenin.com",
            })
    except Exception as e:
        log.warning(f"Parsing EmploiBenin échoué : {e}")
    return offres


# ---------------------------------------------------------------------------
# SOURCE 4 : PagesHumanitaires -- scraping HTML
# ---------------------------------------------------------------------------
def scrape_pageshumanitaires():
    offres = []
    resp = safe_get("https://www.pageshumanitaires.com/recrutements")
    if not resp:
        return offres
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=re.compile(r"/recrutements-1/"))
        seen = set()
        for a in links:
            href = a.get("href", "")
            if href in seen or not href:
                continue
            seen.add(href)
            titre = a.get_text(strip=True)
            if not titre or len(titre) < 3:
                continue
            full_url = href if href.startswith("http") else f"https://www.pageshumanitaires.com{href}"
            offres.append({
                "id": make_id("pageshumanitaires", full_url),
                "titre": titre,
                "organisation": "ONG (voir annonce)",
                "lien": full_url,
                "date_publication": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "localisation": "Afrique / International",
                "categorie": "emploi",
                "source": "PagesHumanitaires",
            })
    except Exception as e:
        log.warning(f"Parsing PagesHumanitaires échoué : {e}")
    return offres


# ---------------------------------------------------------------------------
# SOURCE 5 : Bourses d'études -- Campus France / flux génériques bourses Afrique
# ---------------------------------------------------------------------------
def scrape_bourses_campusfrance():
    """
    Campus France n'a pas d'API publique stable ; on tente un flux RSS
    connu pour les actualités bourses. Si indisponible, retourne une liste vide
    sans casser le script.
    """
    offres = []
    feed = feedparser.parse("https://www.campusfrance.org/fr/rss.xml")
    for entry in feed.entries[:20]:
        title = entry.get("title", "")
        if re.search(r"bourse|scholarship", title, re.IGNORECASE):
            offres.append({
                "id": make_id("campusfrance", entry.get("link")),
                "titre": title,
                "organisation": "Campus France",
                "lien": entry.get("link", ""),
                "date_publication": entry.get("published", "")[:10] if entry.get("published") else "",
                "localisation": "France / International",
                "categorie": "bourse",
                "source": "Campus France",
            })
    return offres


# ---------------------------------------------------------------------------
# SOURCE 6 : AEFE (postes enseignants réseau français international)
# ---------------------------------------------------------------------------
def scrape_aefe_benin():
    offres = []
    resp = safe_get("https://talents.aefe.fr/fr/offres?q=Benin")
    if not resp:
        return offres
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=re.compile(r"/fr/annonce/"))
        seen = set()
        for a in links:
            href = a.get("href", "")
            if href in seen or not href:
                continue
            seen.add(href)
            titre = a.get_text(strip=True)
            if not titre or len(titre) < 3:
                continue
            full_url = href if href.startswith("http") else f"https://talents.aefe.fr{href}"
            offres.append({
                "id": make_id("aefe", full_url),
                "titre": titre,
                "organisation": "AEFE (enseignement français à l'étranger)",
                "lien": full_url,
                "date_publication": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "localisation": "Bénin",
                "categorie": "emploi",
                "source": "AEFE",
            })
    except Exception as e:
        log.warning(f"Parsing AEFE échoué : {e}")
    return offres


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
SCRAPERS = [
    ("ReliefWeb Bénin", lambda: scrape_reliefweb("Benin")),
    ("UNjobs Bénin", lambda: scrape_unjobs_rss("Benin")),
    ("EmploiBenin.com", scrape_emploibenin),
    ("PagesHumanitaires", scrape_pageshumanitaires),
    ("Campus France (bourses)", scrape_bourses_campusfrance),
    ("AEFE Bénin", scrape_aefe_benin),
]


def load_existing():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def run_all():
    existing = load_existing()  # dict id -> offre, sert d'historique cumulé
    total_new = 0

    for name, fn in SCRAPERS:
        log.info(f"--- Source : {name} ---")
        try:
            results = fn()
            log.info(f"{name} : {len(results)} offres trouvées")
            for offre in results:
                if offre["id"] not in existing:
                    total_new += 1
                existing[offre["id"]] = offre
        except Exception as e:
            log.error(f"Source '{name}' a échoué entièrement : {e}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # Purge des offres trop anciennes pour garder le fichier propre
    cutoff = datetime.now(timezone.utc).timestamp() - MAX_AGE_DAYS * 86400
    cleaned = {}
    for oid, offre in existing.items():
        try:
            d = datetime.strptime(offre["date_publication"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if d.timestamp() >= cutoff:
                cleaned[oid] = offre
        except Exception:
            cleaned[oid] = offre  # si date illisible, on garde par prudence

    DATA_FILE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(f"Total : {len(cleaned)} offres en base, {total_new} nouvelles cette exécution")
    return cleaned


if __name__ == "__main__":
    run_all()
