# Plan de travail par sprint

Sprints d'une semaine, à partir du lundi 23 novembre 2026. La date limite du projet n'est pas encore connue : **les dates sont indicatives, l'ordre des sprints fait foi.**

Répartition : **Luciano** ([mentalist011101](https://github.com/mentalist011101)) porte les tâches complexes ; **esmirida** ([esmirida](https://github.com/esmirida)) prend des tâches plus légères et relit les PR de Luciano. La relecture est une vraie tâche : c'est ce qui permet à chacun de comprendre tout le système et de le présenter à la démo.

Chaque ligne correspond à une issue GitHub, rangée dans le jalon du sprint.

## Vue d'ensemble

| Sprint | Dates | Objectif | Livrable de fin de sprint |
|---|---|---|---|
| S0 | 23 – 29 nov. | Fondations et levée des risques | Hypothèses critiques vérifiées ; squelette du dépôt et CI ; premières vidéos de test |
| S1 | 30 nov. – 6 déc. | Tranche verticale en régime nominal | Une vidéo traverse tout le pipeline (un Edge → Cloud → page web) |
| S2 | 7 – 13 déc. | Buffer et mode déconnecté | Coupure de 2 min sans perte, prouvée par un test |
| S3 | 14 – 20 déc. | Politique adaptative et traitement au Cloud | Les 3 modes (Cloud-only, Edge-first, hybride) fonctionnent |
| S4 | 21 – 27 déc. | Observabilité et énergie | Métriques, journaux, horodatages et énergie visibles dans Grafana |
| S5 | 28 déc. – 3 janv. | Sécurité et déploiement automatisé | Redéploiement complet depuis une machine vierge, chronométré |
| S6 | 4 – 10 janv. | Campagnes de mesure | Données brutes et résultats des scénarios obligatoires |
| S7 | 11 – 17 janv. | Rapport et démo | Rapport technique, vidéo, démo répétée |

## Détail des tâches

### Sprint 0 — Fondations et levée des risques

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S0-1 | Spike : vitesse et WER de faster-whisper base et small sur 2 cœurs (Codespace), audio français | Luciano | D7 | Temps de transcription par bloc de 30 s et WER mesurés ; recommandation base/small notée dans le journal |
| S0-2 | Spike : `tc`/netem et eBPF dans un Codespace (brider à 5 Mbit/s, couper, compter les octets par destination) | Luciano | D2, D8 | Faisabilité documentée ; si impossible, plan B pour développer la partie réseau |
| S0-3 | Spike : bascule 360p/480p avec hls.js (segment 360p substitué dans la liste 480p, marque de discontinuité) | Luciano | D1, D11 | Option A validée ou repli C adopté ; journal mis à jour |
| S0-4 | Spike : débits réels du 360p et du 480p avec la commande ffmpeg de D7 (débit plafonné, image clé toutes les 2 s) | Luciano | D4, D7 | Débits et tailles de segments mesurés ; l'hypothèse « 2,3 Mbit/s par Edge » est confirmée ou corrigée |
| S0-5 | Squelette technique : paquets `edge` et `cloud`, `pyproject.toml`, CI verte, environnement de développement en conteneurs | Luciano | D6 | `ruff` et `pytest` passent en CI ; un service vide répond sur `/healthz` |
| S0-6 | Écrire le texte de lecture des vidéos de test (~3 min en français + ~30 s en anglais) et la matrice des conditions d'enregistrement | esmirida | D7 | Fichier `experiments/videos.md` avec le texte et la matrice |
| S0-7 | Enregistrer les 3 premières vidéos de test (pièce calme à la webcam, téléphone vertical, pièce bruyante) et calculer leur empreinte SHA-256 | esmirida | D7 | Vidéos déposées hors Git, empreintes listées dans `experiments/videos.md` |

### Sprint 1 — Tranche verticale en régime nominal

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S1-1 | Edge : source par rejeu à vitesse réelle + ingestion (`ffprobe`, normalisation, quarantaine des fichiers illisibles) | Luciano | D1, D7 | Les vidéos de la matrice sont acceptées ou rejetées proprement ; test automatisé |
| S1-2 | Edge : branche image (une commande ffmpeg, segments HLS 360p et 480p de 6 s) | Luciano | D7 | Segments réguliers produits pour un flux en direct simulé |
| S1-3 | Edge : branche son (16 kHz mono, VAD, faster-whisper, blocs de 30 s, langue, confiance) | Luciano | D1, D7 | Sous-titres horodatés produits ; blocs sans voix sautés |
| S1-4 | Cloud : API FastAPI + PostgreSQL (schéma, identifiants uniques, réponse « déjà reçu ») + construction des listes HLS | Luciano | D3, D11 | Un envoi rejoué ne crée pas de doublon ; listes HLS valides |
| S1-5 | Edge : envoi HTTP simple vers le Cloud (sans buffer avancé) pour relier la chaîne de bout en bout | Luciano | D3 | Une vidéo traverse le pipeline et devient lisible |
| S1-6 | Page web v0 : gabarits HTML avec Tailwind (liste des vidéos, page de lecture avec hls.js et transcription à côté), sur données d'exemple | esmirida | D11 | Pages statiques propres, prêtes à être branchées sur l'API |
| S1-7 | Enregistrer les vidéos de test restantes (voix lointaine, passage en anglais, longs silences) | esmirida | D7 | Matrice complète, empreintes listées |

### Sprint 2 — Buffer et mode déconnecté

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S2-1 | Buffer : fichiers + SQLite, écriture `.tmp` puis renommage, priorités, vérification au redémarrage, métrique de pertes | Luciano | D4 | Redémarrage brutal de l'Edge sans perte ni fichier corrompu |
| S2-2 | Module d'envoi : confirmations, backoff exponentiel, envois simultanés limités, partage du débit direct / rattrapage | Luciano | D3, D4 | Coupure simulée : reprise automatique, ordre respecté |
| S2-3 | Paliers de dégradation, rattrapage depuis l'original, conservation des originaux (protection, suppression, refus visible) | Luciano | D4 | Lien plus lent que la production : paliers activés puis rattrapage |
| S2-4 | Tests de panne : coupure de 2 min, confirmation perdue, coupure pendant une écriture | Luciano | D4, D10 | Tests automatisés verts ; pertes = 0 |
| S2-5 | Export des sous-titres en SRT et WebVTT (point d'API + bouton sur la page) | esmirida | D11 | Fichiers exportés valides, lus par un lecteur vidéo |

### Sprint 3 — Politique adaptative et traitement au Cloud

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S3-1 | Workers Cloud + file PostgreSQL `SKIP LOCKED` avec durée limite ; mode Cloud-only ; envoi de segments bruts | Luciano | D5, D11 | Mode Cloud-only fonctionnel avec le même modèle que l'Edge |
| S3-2 | Politique adaptative : signaux, règles, hystérésis, déport d'un flux, retranscription des blocs douteux | Luciano | D5 | Décisions visibles et stables sous variation du débit |
| S3-3 | Lecture pendant le traitement et bascule 360p/480p selon le résultat de S0-3 | Luciano | D1, D11 | Une vidéo en cours se lit depuis le début |
| S3-4 | Page web : retard affiché et transcription rafraîchis avec htmx | esmirida | D1, D11 | Le retard évolue en direct pendant une coupure simulée |

### Sprint 4 — Observabilité et énergie

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S4-1 | Horodatages par étape et métriques applicatives (latences par étape, buffer, palier, décisions, pertes) | Luciano | D8 | Durée de chaque étape disponible en métrique |
| S4-2 | Prometheus en mode agent sur les Edge, node_exporter, cAdvisor, exporteur eBPF (octets par destination), chrony | Luciano | D8 | Aucune métrique perdue pendant une coupure ; écart d'horloge mesuré |
| S4-3 | Fluent Bit → Loki ; identifiant d'événement dans chaque journal | Luciano | D8 | Recherche des journaux d'un événement par son identifiant |
| S4-4 | Énergie selon SCI : modèles Cloud Carbon Footprint et Boavizta par conteneur ; énergie par résultat utile | Luciano | D8 | Énergie par résultat calculée avec les deux modèles |
| S4-5 | Tableaux de bord Grafana de la démo (retard par flux, buffer, palier, octets WAN, énergie), à partir de la liste de métriques fournie par Luciano | esmirida | D8 | Tableau lisible qui montre une perturbation et la récupération |

### Sprint 5 — Sécurité et déploiement automatisé

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S5-1 | mTLS : autorité de certification et certificats par Edge générés par Ansible, vérification nœud / certificat ; secrets avec Ansible Vault | Luciano | D9 | Un faux Edge est refusé ; aucun secret en clair dans le dépôt |
| S5-2 | Durcissement : conteneurs non-root en lecture seule, `tc`/eBPF isolés, pare-feu, SSH par clé | Luciano | D9 | Vérification des droits de chaque conteneur documentée |
| S5-3 | GitHub Actions : construction des images, Trivy, SBOM, signature cosign ; vérification au déploiement, images par empreinte | Luciano | D6, D9 | Une image non signée est refusée au déploiement |
| S5-4 | Ansible (rôles edge, cloud, observation, inventaire quelconque), Terraform, plan B de copie des images | Luciano | D2, D6 | Déploiement sur 4, 3 ou 2 machines sans changer le code |
| S5-5 | README de redéploiement : rédaction, puis test sur une machine vierge en suivant uniquement le README (chronométré) | esmirida | Livrables | Redéploiement réussi par quelqu'un qui n'a pas écrit le code |

### Sprint 6 — Campagnes de mesure

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S6-1 | Script d'essai unique (phases, `tc`, charge, export) et analyse (percentiles, bootstrap par essai, différences) | Luciano | D10 | Un essai complet se lance et s'analyse en une commande |
| S6-2 | Bancs d'essai des orchestrateurs (D6) et du chiffrement (D9) ; fixation des SLO après le nominal | Luciano | D6, D9, D10 | Décisions tranchées selon les règles écrites à l'avance |
| S6-3 | Lancer et surveiller les campagnes selon le script ; tenir le cahier d'essais (dates, incidents, anomalies) | esmirida | D10 | Campagnes de priorité 1 complètes, cahier à jour |
| S6-4 | WER par taille de modèle sur nos vidéos ; effet du VAD sur l'énergie | Luciano | D7, D8 | Résultats avec intervalles |

### Sprint 7 — Rapport et démo

| ID | Tâche | Responsable | Lien | Critère de fin |
|---|---|---|---|---|
| S7-1 | Rapport technique : architecture, modèle de menace, protocole, résultats, limites et risques résiduels | Luciano | Livrables | Rapport complet |
| S7-2 | Répétition de la démo : redéploiement chronométré, régime nominal, perturbation, violation du SLO, récupération | Luciano | Livrables | Deux répétitions réussies |
| S7-3 | Vidéo de présentation (enregistrement et montage) et relecture du rapport | esmirida | Livrables | Vidéo finale ; relecture faite |

### Tâche permanente

| ID | Tâche | Responsable | Critère de fin |
|---|---|---|---|
| R-1 | Relire chaque PR de Luciano : poser des questions, tester la branche, approuver | esmirida | Aucune PR fusionnée sans relecture |
