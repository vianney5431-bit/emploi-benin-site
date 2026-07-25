# Guide de déploiement — Site d'offres d'emploi & bourses (Bénin & International)

Ce guide t'explique comment mettre ce projet en ligne, étape par étape, sans
connaissances techniques préalables. Compte environ 20-30 minutes.

## Ce que tu vas obtenir à la fin

Un site web public, gratuit, à une adresse du type :
`https://TON_PSEUDO.github.io/emploi-benin-site/`

Il se mettra à jour **automatiquement chaque jour à 6h UTC** (7h ou 8h heure
du Bénin selon la saison), sans que tu aies besoin de rien faire.

---

## Étape 1 — Créer un compte GitHub

1. Va sur https://github.com/signup
2. Crée un compte avec ton adresse email (vianney5431@gmail.com par exemple)
3. Choisis un nom d'utilisateur simple (ex. `vianney43` ou `jjotolorin`)
4. Confirme ton email

## Étape 2 — Créer un nouveau dépôt (« repository »)

1. Une fois connecté, clique sur le bouton vert **"New"** (ou va sur
   https://github.com/new)
2. Nom du dépôt : `emploi-benin-site`
3. Coche **"Public"**
4. Ne coche PAS "Add a README" (on va importer nos propres fichiers)
5. Clique sur **"Create repository"**

## Étape 3 — Envoyer les fichiers du projet sur GitHub

Le plus simple sans ligne de commande :

1. Sur la page de ton nouveau dépôt (vide), clique sur le lien
   **"uploading an existing file"**
2. Fais glisser TOUS les fichiers et dossiers que je t'ai fournis
   (scraper.py, build_site.py, requirements.txt, le dossier `.github/`,
   le dossier `data/`, le dossier `docs/`)
3. ⚠️ Important : glisse les dossiers en entier (pas juste les fichiers à
   l'intérieur) pour que GitHub garde la structure des sous-dossiers.
   Si le glisser-déposer "aplati" les dossiers, utilise plutôt GitHub
   Desktop (voir Étape 3 bis ci-dessous).
4. En bas de page, clique sur **"Commit changes"**

### Étape 3 bis (recommandée) — GitHub Desktop, plus fiable pour les dossiers

1. Télécharge GitHub Desktop : https://desktop.github.com/
2. Installe-le et connecte-toi avec ton compte GitHub
3. Clique "File" → "Add local repository" → sélectionne le dossier
   `emploi-benin-site` sur ton ordinateur (celui que je t'ai fourni)
4. Clique "Publish repository", décoche "Keep this code private"
5. Clique "Publish"

## Étape 4 — Activer GitHub Pages (pour que le site soit visible)

1. Sur la page de ton dépôt, va dans **"Settings"** (en haut)
2. Dans le menu de gauche, clique **"Pages"**
3. Sous "Build and deployment" → "Source", choisis **"Deploy from a branch"**
4. Branche : `main`, dossier : `/docs`
5. Clique **"Save"**
6. Attends 1-2 minutes, actualise la page : l'URL de ton site apparaît en haut
   (ex. `https://tonpseudo.github.io/emploi-benin-site/`)

## Étape 5 — Lancer la première mise à jour manuellement

Le site est en ligne mais vide tant que le scraper n'a pas tourné une fois.

1. Sur la page de ton dépôt, clique sur l'onglet **"Actions"**
2. Clique sur le workflow **"Mise à jour quotidienne des offres"** (colonne
   de gauche)
3. Clique sur le bouton **"Run workflow"** (à droite) → **"Run workflow"**
4. Attends 1-2 minutes, actualise la page : tu dois voir un ✅ vert
5. Va sur ton site (`https://tonpseudo.github.io/emploi-benin-site/`) —
   les offres doivent maintenant apparaître

Après ça, le site se mettra à jour **tout seul chaque jour**. Tu n'as plus
rien à faire.

---

## Comment vérifier que tout va bien, dans le temps

- Onglet **"Actions"** de ton dépôt : chaque exécution quotidienne apparaît
  avec une coche verte (✅ succès) ou une croix rouge (❌ échec)
- Si tu vois une croix rouge plusieurs jours de suite, clique dessus pour
  voir le message d'erreur — le plus souvent, ça veut dire qu'un site
  cible a changé sa structure et qu'un parseur doit être ajusté

## Limites à connaître

- **Le scraping n'est jamais garanti à 100%.** Certains sites (EmploiBenin,
  PagesHumanitaires, AEFE) n'ont pas d'API officielle — le script lit
  directement leur page HTML. Si ces sites changent de design, le parseur
  correspondant peut cesser de fonctionner jusqu'à ce qu'il soit corrigé.
- **ReliefWeb et UNjobs sont les sources les plus fiables** (API officielle
  ou flux RSS stable) — elles continueront de fonctionner même si les
  autres sources changent.
- Le site garde seulement les offres des 60 derniers jours (réglable dans
  `scraper.py`, variable `MAX_AGE_DAYS`) pour rester pertinent.
- Vérifie toujours l'offre directement sur le site source avant de
  postuler — le scraper peut occasionnellement mal extraire une date ou
  un titre.

## Pour ajouter d'autres sources plus tard

Reviens me voir avec le nom du site que tu veux ajouter (ex. Indeed Bénin,
un site de bourses précis) — je t'écrirai le parseur correspondant à
ajouter dans `scraper.py`.
