# Offres d'emploi & bourses — Bénin & International

Site statique généré automatiquement, agrégeant des offres d'emploi, de
stages et de bourses d'études pertinentes pour le Bénin et à l'international.

**⚡ Commence par lire `GUIDE_DEPLOIEMENT.md`** pour mettre ce projet en ligne.

## Structure du projet

```
emploi-benin-site/
├── scraper.py              # Récupère les offres depuis plusieurs sources
├── build_site.py           # Génère docs/index.html à partir des données
├── requirements.txt        # Dépendances Python
├── .github/workflows/
│   └── update.yml           # Automatisation quotidienne (GitHub Actions)
├── data/
│   └── offres.json          # Base de données cumulée (générée automatiquement)
└── docs/
    └── index.html            # Le site final (servi par GitHub Pages)
```

## Sources actuellement couvertes

| Source | Type | Fiabilité |
|---|---|---|
| ReliefWeb | Emplois ONG/humanitaire | Élevée (API officielle) |
| UNjobs | Emplois agences ONU | Élevée (flux RSS stable) |
| EmploiBenin.com | Emplois tous secteurs, Bénin | Moyenne (scraping HTML) |
| PagesHumanitaires | Emplois ONG, Afrique de l'Ouest | Moyenne (scraping HTML) |
| Campus France | Bourses d'études | Moyenne (flux RSS) |
| AEFE | Postes enseignants réseau français | Moyenne (scraping HTML) |

## Lancer en local (pour tester avant de déployer)

```bash
pip install -r requirements.txt
python scraper.py       # récupère les offres → data/offres.json
python build_site.py    # génère → docs/index.html
```

Ouvre ensuite `docs/index.html` dans ton navigateur pour prévisualiser.

## Automatisation

Le fichier `.github/workflows/update.yml` fait tourner `scraper.py` puis
`build_site.py` chaque jour à 6h UTC via GitHub Actions, et republie le
site automatiquement. Aucune action manuelle requise une fois déployé.
