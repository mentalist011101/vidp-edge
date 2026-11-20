# CLAUDE.md — instructions pour l'assistant de code

Ce fichier est lu automatiquement par Claude Code au début de chaque session dans ce dépôt. Il donne le contexte du projet, les règles à respecter et la manière de travailler.

## 1. Le projet en bref

VidP-Edge est un pipeline vidéo adaptatif Edge–Cloud (projet 1 de l'énoncé du cours Cloud Computing, ENSPY 2026/2027).

- Deux nœuds **Edge** reçoivent chacun un flux vidéo (simulé par rejeu de fichiers à vitesse réelle), l'analysent sur place et gardent l'original.
- Le **Cloud** reçoit les métadonnées et les versions 360p/480p, stocke, et expose une page web publique.
- Une machine d'**observation** collecte métriques, journaux et horodatages.
- Le système doit rester utile quand le WAN se dégrade ou coupe (le professeur bridera le lien avec `tc`).

La note porte surtout sur l'infrastructure, la résilience et **la preuve par la mesure** (20 % pour les mesures et la méthodologie). La qualité du modèle d'IA n'est pas notée. « Une fonctionnalité non mesurée ne constitue pas une preuve de fonctionnement. »

## 2. Source de vérité : le journal

Toutes les décisions d'architecture sont dans [`docs/JOURNAL.md`](docs/JOURNAL.md), avec les options écartées et les raisons. **Avant toute modification structurante, lis la section concernée du journal.**

- Ne contredis pas une décision du journal sans le signaler explicitement.
- Si une décision doit changer, propose-la comme un débat (options, arguments, raison) et mets à jour le journal dans la même PR après accord.
- Plusieurs choix sont volontairement **tranchés par la mesure** (orchestrateur D6, chiffrement du disque Edge D9, taille du modèle D7, seuils D5, bascule 360p/480p D11) : ne les tranche pas par raisonnement.

### Résumé des décisions (détails dans le journal)

| Débat | Décision clé |
|---|---|
| D1 | Flux continu ; segments vidéo de 6 s ; blocs audio de ~30 s ; extrait utile = métadonnées + 360p + 480p ; priorité métadonnées → 360p → 480p ; résultat utile = reçu une fois et conforme à une référence |
| D2 | 2 Edge, 1 Cloud, 1 Observation (4 VM pour les mesures, repli sur 3 ou 2) ; rôles = groupes Ansible |
| D3 | HTTP à l'initiative de l'Edge ; identifiant unique par envoi (nœud, vidéo, segment, résolution) ; suppression du buffer après confirmation ; backoff exponentiel ; pas de broker |
| D4 | Buffer = fichiers + SQLite, volume dédié avec plafond ; écriture `.tmp` puis renommage ; vérification au redémarrage ; paliers de dégradation ; rien n'est jeté ; envois simultanés limités |
| D5 | Politique adaptative par règles lisibles, par flux, avec hystérésis ; signaux : autonomie du buffer, retard de traitement, confiance de Whisper |
| D6 | Services indépendants de l'orchestrateur (env vars, `/healthz`, logs sur stdout, état dans des volumes) ; orchestrateur choisi par banc d'essai (Compose, k3s, KubeEdge) ; images par GitHub Actions, registre GHCR, modèles inclus |
| D7 | faster-whisper int8 ; Edge : base au minimum, small si la VM suit ; VAD Silero ; ffmpeg une commande, deux sorties, image clé toutes les 2 s, débit plafonné ; ingestion robuste ; pas d'API externe |
| D8 | Prometheus en mode agent sur les Edge ; node_exporter, cAdvisor, métriques applicatives, eBPF (octets par destination) ; Fluent Bit → Loki ; traces = horodatages maison par étape ; chrony ; énergie selon SCI (ISO/IEC 21031) avec Cloud Carbon Footprint et Boavizta |
| D9 | mTLS Edge ↔ Cloud (notre CA, un certificat par Edge) ; Ansible Vault ; conteneurs non-root en lecture seule ; `tc`/eBPF isolés ; images signées (cosign) et vérifiées, désignées par empreinte |
| D10 | Protocole : chauffe exclue, ≥ 5 répétitions, bootstrap par essai, essais alternés, définitions écrites avant de mesurer, SLO fixés après le nominal, données brutes versionnées |
| D11 | Nginx (HTTPS public + mTLS) ; FastAPI ; PostgreSQL (métadonnées, idempotence, file de travaux `SKIP LOCKED`) ; segments sur fichiers ; pages serveur + Tailwind + htmx + hls.js |

## 3. Méthode de travail

- **Jamais de commit direct sur `main`.** Tout passe par une branche et une Pull Request vers `main`, relue par l'autre membre.
- Une PR = une tâche (une issue). La description de la PR référence l'issue (`Closes #12`).
- Branches : `<type>/<numéro-issue>-<description-courte>`, par exemple `feat/14-edge-buffer`, `spike/3-hls-bascule`, `docs/20-readme-redeploiement`.
- Commits au format Conventional Commits : `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`, `perf:`, `exp:` (expérience/mesure).
- **N'ajoute pas de ligne `Co-Authored-By` ni de mention de Claude** dans les messages de commit ni dans les descriptions de PR. C'est une consigne explicite de l'équipe.
- Avant d'ouvrir une PR : les vérifications locales passent (`ruff check .` et `pytest`), et la documentation touchée est à jour.

Détails dans [`CONTRIBUTING.md`](CONTRIBUTING.md).

## 4. Conventions de code

- **Langue** : documentation, journal, issues et PR en français ; code, noms de variables, de fonctions et de fichiers en anglais.
- **Python 3.11+**. Style vérifié par `ruff` (configuration dans `pyproject.toml`). Annotations de type sur les fonctions publiques.
- **Services indépendants de l'orchestrateur** (D6) : configuration par variables d'environnement uniquement, point `/healthz`, journaux sur la sortie standard au format JSON, tout état persistant dans un volume.
- **Chaque journal applicatif lié à un événement porte son identifiant** (nœud, vidéo, segment, résolution), pour relier journaux et horodatages (D8).
- **Horodatages** : en UTC, avec la précision de la milliseconde, enregistrés à chaque étape du parcours d'un événement (D8).
- **Aucun secret** dans le code, les images ou le dépôt en clair. Les secrets passent par Ansible Vault et sont montés comme fichiers au démarrage (D9).
- **Écriture de fichiers dans le buffer** : toujours dans un fichier `.tmp` puis renommage, puis inscription dans SQLite (D4).
- Les conteneurs tournent en **utilisateur non-root**, système de fichiers en lecture seule sauf volumes prévus (D9).

## 5. Mesures et expériences

- Les définitions (pertes, backlog, temps de reprise, volume évité, résultat utile) et les règles de décision sont écrites **avant** de mesurer (voir [`docs/PROTOCOLE.md`](docs/PROTOCOLE.md)). Ne les modifie pas après avoir vu les résultats.
- Un essai se lance uniquement par script, jamais à la main.
- Chaque essai produit un dossier de données brutes avec la configuration et la version exacte du code.
- N'annonce jamais un chiffre de performance qui n'a pas été mesuré ; distingue toujours hypothèse et mesure.

## 6. Comment aider l'équipe

- Le porteur principal (Luciano) découvre le cloud computing et veut **comprendre** les notions. Quand tu introduis une notion (outil, mécanisme système, réseau), explique-la en une ou deux phrases simples.
- Pour un choix structurant, présente les options avec leurs avantages et inconvénients, donne ta position, et attends l'accord avant de l'implémenter.
- Préfère un outil éprouvé à du code maison, sauf si le gain du code maison est démontré (principe adopté en D6).
- Signale les cas limites et les risques plutôt que de les passer sous silence.

## 7. Commandes utiles

```bash
ruff check .          # style
pytest                # tests
```

Les commandes de déploiement et d'expérience seront ajoutées ici au fil des sprints.
