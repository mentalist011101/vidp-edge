# Énoncé du projet

## Sources

| Document | Lien |
|---|---|
| Dépôt du cours (Djob Mvondo) | https://github.com/djobiii2078/cloud_course_resources |
| Énoncé officiel (version 4) | [`Projet_Cloud_Edge_dark_v4.pdf`](Projet_Cloud_Edge_dark_v4.pdf) — original : https://github.com/djobiii2078/cloud_course_resources/blob/main/projet/Projet_Cloud_Edge_dark_v4.pdf |
| Ancienne version de l'énoncé | [`Projet_Cloud_ancienne_version.pdf`](Projet_Cloud_ancienne_version.pdf) — original : `projet/Projet Cloud (2).pdf` dans le dépôt du cours |
| Règles du projet (délai, démo, bonus) | https://github.com/djobiii2078/cloud_course_resources/blob/main/projet/readme.md |

Copies faites le 20 novembre 2026, depuis la version du dépôt du cours du 10 novembre 2026 (commit `1613918`). En cas de différence, **le dépôt du cours fait foi**.

## Projet choisi : 1 — VidP-Edge, pipeline vidéo adaptatif

Chaîne : caméra / fichiers → détection locale → buffer Edge → WAN → agrégation Cloud → web public.

**Décision locale** : traiter la vidéo sur l'Edge, envoyer les métadonnées, transférer seulement les extraits utiles.

**Déploiement demandé** : conteneurs sur le nœud Edge ; VM ou services dans le Cloud ; Ansible et Terraform ; monitoring eBPF / Prometheus / Grafana.

**Scénarios obligatoires** : baseline Cloud-only ; traitement Edge-first ; politique hybride adaptative ; coupure WAN de 2 minutes ; débit limité à 5 ou 10 Mbit/s.

**Mesures à remettre** : latence p50, p95 et p99 de l'événement au résultat ; octets WAN et volume évité ; pertes, backlog et temps de reprise ; WSS, CPU et énergie par résultat utile.

**Bonus** : réduire l'énergie sans dégrader le p99 ni le taux de résultats corrects.

## Exigences communes aux trois projets

| Axe | Exigence |
|---|---|
| Automatisation | Un déploiement depuis une machine vierge, avec configuration versionnée |
| Observabilité | Métriques, logs et traces reliés aux SLO et à la chronologie des incidents |
| Résilience | Mode déconnecté, file locale, déduplication et reprise contrôlée |
| Sécurité | Identité des nœuds, secrets externes, moindre privilège et images vérifiées |

« Une fonctionnalité non mesurée ne constitue pas une preuve de fonctionnement. »

## Livrables

- **Dépôt Git** : code source et historique, README de redéploiement, Infrastructure as Code, scripts de charge et de panne.
- **Rapport technique** : architecture et modèle de menace, protocole et données brutes, percentiles et intervalles, limites et risques résiduels.
- **Vidéo de présentation** où les membres expliquent leur design et réalisent une démo (règles du projet).
- **Démo live** : redéployer en quelques minutes sur les adresses IP fournies, présenter le régime nominal, provoquer une perturbation, observer la violation et démontrer la récupération.

Date limite : non communiquée à ce jour (« xx/xx/2026 à 23h59 » dans l'énoncé ; après ce délai, la note est 0).

## Barème proposé

| Critère | Poids |
|---|---|
| Mesures et méthodologie | 20 % |
| Déploiement reproductible | 15 % |
| Architecture Edge–Cloud | 15 % |
| Résilience et mode déconnecté | 15 % |
| Sécurité | 10 % |
| Énergie et efficacité réseau | 10 % |
| Observabilité et diagnostic | 10 % |
| Démonstration | 5 % |

Bonus énergie : seulement si la réduction ne dégrade ni le p99, ni la fiabilité, ni la qualité du résultat.

## Notes prises pendant l'explication orale du professeur

Notes de Luciano, transcrites telles quelles (à confirmer avec le professeur quand elles diffèrent du PDF) :

- Détection : langue, sous-titres, qualité de la vidéo (le professeur a parlé de **360 et 480**, c'est-à-dire des résolutions 360p et 480p), exécutée dans un conteneur.
- Puis passage dans le Cloud : agrégation (vidéos et sous-titres), interface web pour visualiser chaque vidéo en cours de traitement, voir les vidéos déjà traitées et leurs métadonnées, et choisir de lire ou d'exporter les sous-titres.
- Le système doit fonctionner quel que soit le réseau : le professeur utilisera `tc` pour brider la connexion (débit, taux de pertes de paquets) et fera varier ces paramètres pour vérifier la disponibilité.
- Des flux de vidéos arrivent en continu.
- Déploiement automatisable : Ansible, Terraform ; monitorer la consommation CPU et autres ressources des différentes machines ; monitoring eBPF.
- Viser la plus petite consommation d'énergie avec de bonnes performances.
- Le professeur fournira les machines et un accès au cloud (clés) quand l'équipe sera prête.
- Mesures : latence, réseau, résilience, ressources.
- Démo live : redéployer en quelques minutes sur les adresses IP fournies, présenter le régime nominal, provoquer une perturbation, observer la violation et démontrer la récupération.

Les questions encore ouvertes pour le professeur sont listées dans [`../JOURNAL.md`](../JOURNAL.md), section 6.
