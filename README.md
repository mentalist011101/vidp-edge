# VidP-Edge

Pipeline vidéo adaptatif entre l'Edge et le Cloud — projet du cours Cloud Computing (ENSPY, 2026/2027, Djob Mvondo), projet 1 de l'énoncé `Projet_Cloud_Edge_dark_v4.pdf`.

Des vidéos arrivent en flux continu sur deux nœuds Edge aux ressources limitées. Chaque Edge les analyse sur place (langue, sous-titres, versions 360p et 480p), garde l'original, et n'envoie au Cloud que l'utile. Le Cloud agrège, stocke et expose le tout sur une page web publique. Le système doit rester utile quand le lien WAN ralentit ou coupe.

```
 Edge A ─┐                                   ┌─► page web publique
 Edge B ─┼── WAN (bridé par tc, mTLS) ──► Cloud
         │                                   └─► stockage + workers
 Observation (Prometheus, Grafana, eBPF) ◄── chemin non bridé
```

## État du projet

| Phase | État |
|---|---|
| Conception (11 débats d'architecture) | Terminée — voir [`docs/JOURNAL.md`](docs/JOURNAL.md) |
| Levée des risques (sprint 0) | En cours |
| Implémentation, mesures, rapport | À venir — voir [`docs/SPRINTS.md`](docs/SPRINTS.md) |

## Documentation

| Document | Contenu |
|---|---|
| [`docs/JOURNAL.md`](docs/JOURNAL.md) | Journal de suivi : toutes les décisions, les options écartées et leurs raisons, le glossaire des notions |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Vue d'ensemble de l'architecture retenue |
| [`docs/PROTOCOLE.md`](docs/PROTOCOLE.md) | Protocole expérimental : comment on mesure et on prouve |
| [`docs/SPRINTS.md`](docs/SPRINTS.md) | Plan de travail par sprint, avec les responsables |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Méthode de travail : branches, PR, relecture, commits |
| [`CLAUDE.md`](CLAUDE.md) | Instructions pour l'assistant de code (contexte, règles, conventions) |

## Arborescence

```
edge/              Services du nœud Edge (ingestion, transcodage, transcription, buffer, envoi, politique)
cloud/             Services du Cloud (API de réception, workers, page web)
deploy/ansible/    Configuration et déploiement des machines
deploy/terraform/  Création de l'infrastructure
observability/     Prometheus, Grafana, eBPF, Fluent Bit, Loki
experiments/       Scripts d'essai, injection de pannes, analyse, données brutes
spikes/            Tests rapides du sprint 0 (levée des risques)
tests/             Tests automatisés
docs/              Documentation et journal de décisions
```

## Redéploiement

Le README de redéploiement (depuis une machine vierge, sur des adresses IP fournies) sera écrit au sprint 5. Il doit permettre un redéploiement complet en quelques minutes.

## Équipe

| Membre | GitHub |
|---|---|
| FOKOUO SAADIE Luciano | [mentalist011101](https://github.com/mentalist011101) |
| Binôme | [esmirida](https://github.com/esmirida) |
