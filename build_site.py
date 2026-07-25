#!/usr/bin/env python3
"""
Génère docs/index.html à partir de data/offres.json.
Site statique pur (HTML/CSS/JS vanilla), servi gratuitement par GitHub Pages.
Aucune dépendance externe au runtime (tout est en ligne dans le fichier).
"""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "offres.json"
DOCS_DIR = ROOT / "docs"
OUTPUT_FILE = DOCS_DIR / "index.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google-site-verification" content="6Ielhh4Jl6872Ui1OPTWZs8RHVRGmWTxQrzYjSZQD-A" />
<title>Offres d'emploi &amp; bourses -- Bénin &amp; International</title>
<style>
  :root {{
    --accent: #2563eb;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text: #1e293b;
    --muted: #64748b;
    --border: #e2e8f0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 0;
  }}
  header {{
    background: var(--accent);
    color: white;
    padding: 2rem 1rem;
    text-align: center;
  }}
  header h1 {{ margin: 0 0 0.5rem; font-size: 1.6rem; }}
  header p {{ margin: 0; opacity: 0.9; font-size: 0.95rem; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 1.5rem 1rem; }}
  .controls {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    position: sticky;
    top: 0;
    background: var(--bg);
    padding: 0.75rem 0;
    z-index: 10;
  }}
  .controls input, .controls select {{
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    border: 1px solid var(--border);
    font-size: 0.9rem;
  }}
  .controls input {{ flex: 1; min-width: 150px; }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
  }}
  .card h3 {{ margin: 0 0 0.35rem; font-size: 1.05rem; }}
  .card h3 a {{ color: var(--text); text-decoration: none; }}
  .card h3 a:hover {{ color: var(--accent); }}
  .meta {{ font-size: 0.85rem; color: var(--muted); display: flex; gap: 0.75rem; flex-wrap: wrap; }}
  .tag {{
    display: inline-block;
    background: #eff6ff;
    color: var(--accent);
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }}
  .tag.bourse {{ background: #fef3c7; color: #92400e; }}
  footer {{
    text-align: center;
    padding: 2rem 1rem;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  .empty {{ text-align: center; color: var(--muted); padding: 3rem 1rem; }}
  .count {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem; }}
</style>
</head>
<body>
<header>
  <h1>Offres d'emploi &amp; bourses -- Bénin &amp; International</h1>
  <p>Mis à jour automatiquement -- dernière actualisation : {last_update}</p>
</header>
<div class="container">
  <div class="controls">
    <input type="text" id="search" placeholder="Rechercher (ex. anglais, éducation, ONG...)">
    <select id="filterCategorie">
      <option value="">Toutes catégories</option>
      <option value="emploi">Emploi</option>
      <option value="bourse">Bourse d'études</option>
    </select>
    <select id="filterSource">
      <option value="">Toutes sources</option>
      {source_options}
    </select>
  </div>
  <div class="count" id="count"></div>
  <div id="list"></div>
</div>
<footer>
  Généré automatiquement via GitHub Actions. Vérifiez toujours les offres directement sur le site source avant de postuler.
</footer>
<script>
const OFFRES = {offres_json};

const list = document.getElementById('list');
const search = document.getElementById('search');
const filterCategorie = document.getElementById('filterCategorie');
const filterSource = document.getElementById('filterSource');
const countEl = document.getElementById('count');

function render() {{
  const q = search.value.toLowerCase();
  const cat = filterCategorie.value;
  const src = filterSource.value;

  const filtered = OFFRES.filter(o => {{
    const matchQ = !q || (o.titre + ' ' + o.organisation + ' ' + o.localisation).toLowerCase().includes(q);
    const matchCat = !cat || o.categorie === cat;
    const matchSrc = !src || o.source === src;
    return matchQ && matchCat && matchSrc;
  }});

  countEl.textContent = filtered.length + ' offre(s) affichée(s) sur ' + OFFRES.length + ' au total';

  if (filtered.length === 0) {{
    list.innerHTML = '<div class="empty">Aucune offre ne correspond à ta recherche.</div>';
    return;
  }}

  list.innerHTML = filtered.map(o => `
    <div class="card">
      <h3><a href="${{o.lien}}" target="_blank" rel="noopener">${{o.titre}}</a></h3>
      <div class="meta">
        <span class="tag ${{o.categorie === 'bourse' ? 'bourse' : ''}}">${{o.categorie === 'bourse' ? 'Bourse' : 'Emploi'}}</span>
        <span>${{o.organisation || ''}}</span>
        <span>📍 ${{o.localisation || ''}}</span>
        <span>🗓️ ${{o.date_publication || ''}}</span>
        <span>via ${{o.source}}</span>
      </div>
    </div>
  `).join('');
}}

search.addEventListener('input', render);
filterCategorie.addEventListener('change', render);
filterSource.addEventListener('change', render);
render();
</script>
</body>
</html>
"""


def build():
    if not DATA_FILE.exists():
        offres = []
    else:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        offres = list(raw.values())
        # Tri par date décroissante (les plus récentes en premier)
        offres.sort(key=lambda o: o.get("date_publication", ""), reverse=True)

    sources = sorted(set(o.get("source", "") for o in offres if o.get("source")))
    source_options = "\n".join(f'<option value="{s}">{s}</option>' for s in sources)

    html = TEMPLATE.format(
        last_update=datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
        source_options=source_options,
        offres_json=json.dumps(offres, ensure_ascii=False),
    )

    DOCS_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Site généré : {OUTPUT_FILE} ({len(offres)} offres)")


if __name__ == "__main__":
    build()
