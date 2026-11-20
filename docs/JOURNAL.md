# Journal de suivi — Projet VidP-Edge

Projet Cloud (Djob Mvondo), projet 1 : pipeline vidéo adaptatif Edge–Cloud.
Sources : `projet/Projet_Cloud_Edge_dark_v4.pdf`, `projet/Projet Cloud (2).pdf` (ancienne version), notes orales de Luciano, cours du dépôt `cloud_course_resources`.

Méthode : chaque choix structurant passe par un débat (options, arguments pour/contre, décision, raison). Rien n'est « décidé » tant que ce n'est pas écrit dans la section 5. Les notions sont expliquées au fil des débats. Exigences de Luciano : ne pas se contenter de la solution que tout le monde fera ; réfléchir aux cas limites ; regarder comment font les solutions existantes ; être robuste à la source des vidéos ; ne refuser une solution moderne éprouvée que si le gain de l'alternative est démontré par la mesure.

Dernière mise à jour : 2026-11-20 (séance 3 — toutes les décisions d'architecture prises ; D6 et le chiffrement de D9 tranchés par mesure ; D1 corrigé).

---

## 1. Ce que le projet demande

### 1.1 En une phrase
Des vidéos arrivent en flux sur des nœuds Edge aux ressources limitées ; on les analyse localement dans des conteneurs, on n'envoie au Cloud que les métadonnées et les extraits utiles, et le Cloud agrège, stocke et expose le tout sur une page web publique — le système devant rester utile quand le lien WAN se dégrade ou tombe.

### 1.2 Architecture actuelle (après D1 à D7)
```
 Edge A (site 1)                              Edge B (site 2)
 ┌─────────────────────────────────┐          ┌──────────────────┐
 │ source ─► ingestion (ffprobe,   │          │ idem             │
 │   normalisation, quarantaine)   │          │                  │
 │   ├ image ─► ffmpeg : 360p/480p,│          │                  │
 │   │   segments 6 s, image clé 2s│          │                  │
 │   └ son ──► 16 kHz mono, VAD    │          │                  │
 │       Silero, faster-whisper    │          │                  │
 │       (base ou small), blocs 30s│          │                  │
 │ politique adaptative (D5)       │          │                  │
 │ ─► buffer : fichiers + SQLite   │          │                  │
 │ ─► module d'envoi (HTTP,        │          │                  │
 │     backoff, envois limités)    │          │                  │
 │ originaux : volume à part       │          │                  │
 │ [orchestrateur : banc d'essai D6│          │                  │
 │  agents D8, sécurité D9]        │          │                  │
 └──────────────┬──────────────────┘          └────────┬─────────┘
                │        WAN bridé par tc              │
                └──────────────► Cloud ◄───────────────┘
            API de réception (idempotente) ─► stockage ─► web public
            traitement Cloud-only (même modèle que l'Edge) /
            flux déportés / retranscription (medium ou distil-large-v3-fr)
            [à décider : base de données et serveur web D11, sécurité D9]

 Observation (Prometheus, Grafana, eBPF, scripts de charge et de panne)
   reliée aux trois autres machines par un chemin non bridé
   [à décider : méthode énergie D8, protocole D10]

 Déploiement : Terraform + Ansible, rôles = groupes ; images construites
   par GitHub Actions, registre GitHub, modèles inclus ; orchestrateur
   choisi après banc d'essai (Compose, k3s, KubeEdge) ; signature D9
```

- Les deux Edge ne se connaissent pas et ne se synchronisent pas : chacun traite sa source, le Cloud rassemble.
- Style par événements à l'intérieur de l'Edge (traitement → buffer), requête/réponse sur le WAN (module d'envoi → Cloud).

### 1.3 Autour du pipeline
- **Déploiement automatisé** : Terraform (créer l'infrastructure) + Ansible (configurer et lancer), depuis une machine vierge.
- **Observabilité** : eBPF / Prometheus / Grafana ; CPU, mémoire, réseau de chaque machine.
- **Injection de pannes** : scripts de charge et de panne versionnés.
- **Sécurité** : identité des nœuds, secrets hors des images, moindre privilège, images vérifiées.

### 1.4 Scénarios obligatoires
| # | Scénario | Ce que ça implique |
|---|---|---|
| 1 | Baseline Cloud-only | L'Edge envoie la vidéo brute, tout le traitement se fait au Cloud |
| 2 | Edge-first | Tout le traitement sur l'Edge, seuls les résultats partent |
| 3 | Hybride adaptatif | Le système choisit dynamiquement selon l'état du WAN / de l'Edge (D5) |
| 4 | Coupure WAN de 2 min | Buffer, zéro perte, reprise mesurée |
| 5 | Débit limité à 5 ou 10 Mbit/s | Comportement sous contrainte réseau |

### 1.5 Mesures à remettre
- **Latence** : p50, p95, p99 de l'événement au résultat.
- **Réseau** : octets WAN envoyés et volume évité (par rapport au Cloud-only).
- **Résilience** : pertes, backlog, temps de reprise.
- **Ressources** : WSS, CPU, énergie par résultat utile.
- Bonus : réduire l'énergie sans dégrader le p99 ni le taux de résultats corrects.

### 1.6 Barème
Mesures et méthodologie 20 % · Déploiement reproductible 15 % · Architecture Edge–Cloud 15 % · Résilience et mode déconnecté 15 % · Sécurité 10 % · Énergie et efficacité réseau 10 % · Observabilité et diagnostic 10 % · Démonstration 5 %.

Lecture : la qualité du modèle d'IA n'est notée nulle part. La note porte sur l'infrastructure, la résilience et la mesure. Principe retenu : le travail bien fait passe avant la chasse au bonus énergie.

### 1.7 Livrables
- Dépôt Git : code + historique, README de redéploiement, Infrastructure as Code, scripts de charge et de panne.
- Rapport : architecture et modèle de menace, protocole et données brutes, percentiles et intervalles, limites et risques résiduels.
- Vidéo de présentation + démo live : redéployer en quelques minutes sur des IP fournies, régime nominal, perturbation, violation observée, récupération.

### 1.8 Contraintes de travail
- Équipe : 2 personnes aujourd'hui, peut-être 4, peut-être 1 → ne pas dimensionner le projet sur la taille de l'équipe.
- Machine de développement : Windows, 8 Go de RAM. Conteneurs possibles (WSL2), plusieurs VM en parallèle non.
- GitHub Codespaces : utilisable pour développer. À tester : `tc` et eBPF. Pas pour les mesures finales.
- Clés d'accès à un cloud fournies par le prof quand l'équipe est prête.
- Vidéos de test : en français.
- Document « point d'étape » (LaTeX/PDF, 8 pages) produit le 2026-11-19 pour le second membre du groupe.

---

## 2. Difficultés identifiées

1. ~~Définitions manquantes~~ → D1.
2. ~~Politique adaptative~~ → D5 ; seuils à mesurer.
3. ~~Mode déconnecté~~ → D3 et D4.
4. **IA sur un Edge limité** : le français exclut tiny ; base ou small à valider sur la vraie VM.
5. **Énergie** : dans une VM, les compteurs matériels (RAPL) ne sont en général pas accessibles → estimation probable.
6. **Rigueur statistique** : 120 événements « sous-titres » par heure de vidéo et par Edge → tests longs.
7. **Redéploiement en quelques minutes sur des IP imposées** : images pré-construites, plan B par copie locale.
8. **Sécurité** : 10 % du barème.
9. **Observer pendant la coupure** : conservation locale des métriques.
10. **Lien plus lent que la production** : cas le plus probable de saturation du buffer.
11. **Écrire soi-même le buffer** : risque de bugs → tests de panne systématiques.
12. **Débit WAN disponible inconnu** → autonomie du buffer comme signal principal.
13. **Sources vidéo imprévisibles** → étape d'ingestion.
14. **Choix de l'orchestrateur** : Kubernetes moderne et éprouvé, mais coûteux sur l'Edge et risqué pendant les coupures → tranché par banc d'essai.

---

## 3. Notions (glossaire vivant)

| Notion | Définition courte | Statut |
|---|---|---|
| Edge | Machine proche de la source des données, attachée à un lieu, ressources limitées | vu |
| WAN | Réseau longue distance entre Edge et Cloud ; lent, instable | vu |
| Buffer / file locale | Stockage tampon où les données attendent d'être envoyées | vu |
| Store-and-forward | « Stocker puis transmettre » : nom du principe de notre buffer | vu |
| p50 / p95 / p99 | Valeur sous laquelle tombent 50/95/99 % des mesures ; un p99 fiable exige des milliers de points | vu |
| Transcodage | Réencoder une vidéo dans une autre qualité pour réduire son poids | vu |
| HLS | Streaming par segments + liste de lecture ; la liste peut grandir ; le lecteur choisit la qualité segment par segment | vu |
| Image clé (GOP) | Image complète à partir de laquelle on peut décoder ; on ne peut couper un segment que sur une image clé | vu |
| Débit plafonné | Limite maximale du débit vidéo ; rend la taille des segments prévisible | vu |
| Granularité | Taille des morceaux dans lesquels on découpe un flux | vu |
| Whisper | Modèle de transcription ; fenêtres de 30 s ; score de confiance ; tailles tiny à large | vu |
| faster-whisper | Moteur qui fait tourner Whisper plus vite sur CPU (CTranslate2) | vu |
| Quantification (int8) | Stocker les poids du modèle sur 8 bits au lieu de 32 : plus léger et plus rapide | vu |
| WER | Taux d'erreur sur les mots ; mesure standard de la qualité d'une transcription | vu |
| VAD | Détecteur de parole (Silero : ~2 Mo, < 1 ms par morceau de 30 ms) | vu |
| Ingestion / normalisation | Inspecter chaque source (`ffprobe`) et la ramener à un format interne unique, ou la rejeter proprement | vu |
| VM | Ordinateur complet simulé, avec son propre système ; bien isolé, lourd | vu |
| Conteneur | Programme isolé qui partage le système de la machine hôte ; léger, démarre vite | vu |
| Groupes Ansible | Rôles (`edge`, `cloud`, `observation`) auxquels on affecte les IP disponibles | vu (principe) |
| tc / netem | Outil Linux pour brider débit, ajouter délai et pertes ; peut cibler une destination | vu (principe) |
| Requête/réponse | Appel téléphonique : l'appelant attend la réponse, l'autre doit être joignable | vu |
| Par événements / broker | Boîte aux lettres : on dépose un message et on repart | vu |
| MQTT, NATS JetStream | Brokers ; NATS est pensé pour l'Edge (leaf nodes) | vu |
| Idempotence / déduplication | Rejouer un envoi ne change pas le résultat ; repose sur un identifiant unique par envoi | vu |
| Backoff exponentiel | Espacer les nouvelles tentatives pour ne pas bombarder un service en panne | vu |
| Famine | Un élément jamais servi parce que d'autres, plus prioritaires, arrivent sans cesse | vu |
| Buffer : pic vs déséquilibre | Un buffer absorbe un pic passager, pas un déséquilibre durable | vu |
| Autonomie du buffer | Espace libre ÷ (débit entrant − débit sortant) | vu |
| SQLite | Base de données qui est un simple fichier, sans serveur | vu |
| fsync / durabilité | `fsync` force l'inscription physique sur disque | vu |
| Renommage atomique | Écrire dans un `.tmp` puis renommer : le fichier visible est toujours complet | vu |
| Somme de contrôle | Empreinte calculée sur le contenu ; permet de détecter un fichier abîmé | vu |
| Envois en vol | Envois partis mais pas encore confirmés ; à limiter sur un lien lent | vu |
| Déport (offloading) | Faire traiter par le Cloud un flux que l'Edge ne peut plus suivre | vu |
| Hystérésis | Deux seuils différents pour entrer et sortir d'un état, plus une durée minimale | vu |
| Contrôle de congestion | Sonder prudemment la capacité d'un lien (principe de TCP) | vu (principe) |
| Orchestration | Choisir où placer les conteneurs, les déployer, les surveiller, les relancer (cours « Orchestration et automatisation ») | vu |
| Docker Compose | Fichier qui décrit les conteneurs d'une machine ; relance les conteneurs arrêtés, mais pas ceux qui sont « unhealthy » | vu |
| Kubernetes / k3s | Orchestrateur multi-machines (état désiré, réconciliation, relance, passage à l'échelle) ; k3s = version allégée (~1,6 Go pour un serveur avec charge) ; par défaut, un nœud injoignable voit ses conteneurs expulsés au bout d'environ 5 min | vu |
| KubeEdge | Extension de Kubernetes pour l'Edge : agent EdgeCore ~70 Mo, autonomie hors ligne (état en cache SQLite), contrôle centralisé au Cloud | vu |
| Service indépendant de l'orchestrateur | Configuration par variables d'environnement, `/healthz`, journaux sur la sortie standard, état dans des volumes : tourne sous Compose comme sous Kubernetes | vu |
| IaC, Terraform, Ansible | Infrastructure décrite dans du code ; Terraform crée, Ansible configure | à approfondir |
| Métriques / journaux / traces | Combien / quoi / où passe le temps pour un même événement | vu |
| eBPF | Petits programmes exécutés dans le noyau ; chez nous : octets par destination, retransmissions TCP | vu |
| Prometheus / Grafana | Collecte de métriques / tableaux de bord | vu (principe) |
| Prometheus en mode agent | Collecte locale + journal sur disque + envoi différé (remote write) ; rétention par défaut 5 min à 4 h (v3.13) | vu |
| node_exporter / cAdvisor | Métriques par machine / par conteneur (dont le working set, notre WSS) | vu |
| Fluent Bit / Loki | Acheminement des journaux avec buffer disque / stockage des journaux | vu |
| chrony | Synchronisation des horloges ; l'écart résiduel est une incertitude sur les latences | vu |
| RAPL | Compteurs d'énergie du processeur ; en général inaccessibles dans une VM | vu |
| Scaphandre | Mesure d'énergie par RAPL ; dans une VM seulement s'il tourne sur l'hyperviseur (exportateur QEMU) | vu |
| Kepler | Exporteur d'énergie de la CNCF (eBPF) ; sans RAPL, estimation peu fiable (étude : RMSE 11,9 W, surestimation ~15×) | vu |
| SCI (ISO/IEC 21031:2024) | Norme : SCI = ((E × I) + M) par R, R = unité fonctionnelle (chez nous : un résultat utile) | vu |
| Cloud Carbon Footprint | Méthode publiée : puissance = min + utilisation × (max − min), coefficients par vCPU issus de SPECpower | vu |
| Boavizta | Profils de consommation non linéaires par CPU ; utilisés par Scaleway pour ses instances | vu |
| Modèle de menace | Ce qu'on protège, contre qui, avec quelles conséquences ; exigé dans le rapport | vu |
| mTLS | TLS mutuel : chaque côté présente un certificat ; identité forte + chiffrement | vu |
| Autorité de certification (CA) | Entité qui signe les certificats ; chez nous, la nôtre, générée par Ansible | vu |
| Ansible Vault | Secrets chiffrés dans le dépôt, déchiffrés au déploiement | vu |
| Moindre privilège | Chaque composant n'a que les droits nécessaires (non-root, lecture seule, droits noyau retirés) | vu |
| SBOM / Trivy | Liste des composants d'une image / analyse de ses vulnérabilités | vu |
| cosign (Sigstore) | Signature et vérification des images de conteneurs | vu |
| Digest | Empreinte d'une image ; contrairement à une étiquette, ne peut pas être déplacée vers une autre image | vu |
| LUKS | Chiffrement de disque sous Linux ; inutile si la clé est stockée sur la même machine | vu |
| Proxy (Nginx) | Serveur placé devant les services : reçoit les connexions, gère TLS, sert les fichiers statiques, redirige vers l'API | vu |
| FastAPI | Framework Python pour écrire des API web ; documentation de l'API générée automatiquement | vu |
| PostgreSQL | Base de données serveur conçue pour plusieurs écrivains et lecteurs simultanés | vu |
| File de travaux SKIP LOCKED | Table PostgreSQL utilisée comme file : `FOR UPDATE SKIP LOCKED` évite que deux workers prennent le même travail ; prévoir une durée limite pour les travaux abandonnés | vu |
| Liste maîtresse HLS | Liste qui regroupe les listes de chaque résolution ; le lecteur choisit la qualité selon le débit | vu |
| Discontinuité HLS / GAP | Balises pour signaler un changement de flux ou un segment manquant ; prise en charge inégale selon les lecteurs | vu |
| Tailwind CSS / htmx | Style moderne par classes utilitaires / mise à jour partielle d'une page sans la recharger | vu |
| Certificat Let's Encrypt pour IP | Certificat public pour une adresse IP sans nom de domaine ; valable 160 h, renouvellement automatique obligatoire | vu |
| SLI / SLO / SLA | Indicateur / objectif / contrat ; nos SLO seront fixés après le régime nominal | vu |
| Bootstrap par essai | Rééchantillonner des essais entiers (et non des événements corrélés) pour obtenir l'intervalle d'un percentile | vu |
| Pré-enregistrement | Écrire définitions et règles de décision avant de mesurer | vu |
| WSS | Mémoire réellement touchée par un processus sur une période | à approfondir |

---

## 4. Débats

| # | Question | Statut |
|---|---|---|
| D1 | Qu'est-ce qu'un événement, un résultat utile, un extrait utile ? | **clos** (révisé le 2026-11-18) |
| D2 | Topologie : combien de machines, quel rôle, VM ou conteneur ? | **clos** |
| D3 | Communication Edge→Cloud : requête/réponse (HTTP) ou événements (broker) ? | **clos** |
| D4 | Buffer Edge : politique, technologie, conservation des originaux | **clos** |
| D5 | Politique hybride adaptative : quels signaux, quelles règles ? | **clos** (seuils à mesurer) |
| D7 | Traitement : modèles et outils | **clos** |
| D6 | Orchestration des conteneurs ; images et registre | **décidé par expérience** (images et registre clos ; orchestrateur après banc d'essai) |
| D8 | Observabilité et mesure d'énergie | **clos** |
| D9 | Sécurité : identité des nœuds, secrets, chiffrement, images vérifiées | **clos** (chiffrement du disque Edge décidé par mesure) |
| D11 | Pile du Cloud : base de données, stockage des vidéos, serveur web | **clos** |
| D10 | Protocole expérimental : charge, durée, répétitions, statistiques | **clos** |

**Toutes les décisions d'architecture sont prises (2026-11-20).** Restent des choix tranchés par mesure : orchestrateur (D6), chiffrement du disque Edge (D9), tailles de modèle et seuils (D5, D7), bascule 360p/480p (D11).

### Idées en réserve
- **Pour le bonus énergie** : VAD ; paliers ; réglage `synchronous` de SQLite ; préréglage ffmpeg ; énergie « Edge » vs « brut + Cloud » ; énergie au repos de l'orchestrateur (banc d'essai D6).
- **Pour D10** : comparer trois politiques d'ordre d'envoi ; coût du réglage de durabilité ; tests de coupure brutale ; seuils de D5 ; matrice de test des sources ; WER par taille de modèle sur nos vidéos ; banc d'essai des orchestrateurs.
- **À débattre** : ignorer les passages immobiles de l'image, en tension avec la lecture complète.
- **Rapport — état de l'art** : Greengrass, Azure IoT Edge, Fluent Bit, NATS JetStream, Kafka ; API de transcription (Groq, Azure, Google) ; orchestrateurs (Compose, k3s, KubeEdge) avec chiffres du banc d'essai.
- **Rapport — limites** : Edge débordé + lien mauvais ; changement de langue au milieu d'un bloc ; référence imparfaite si produite par large-v3.
- **Écarté, à citer dans le rapport** : lien de secours, débord vers un voisin, compression supplémentaire, modèle appris pour la politique, API externe de transcription, Kubernetes complet sur l'Edge.

---

## 5. Décisions prises

### D1 — Définitions (2026-11-13, révisé le 2026-11-18)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Source | Flux continu, simulé par rejeu de fichiers à vitesse réelle ; fichiers importés possibles | Fichier entier traité d'un bloc ; webcam réelle | Plus représentatif ; les VM de démo n'ont pas de caméra ; mesures reproductibles |
| Segment vidéo | 6 s | 10 s | Recommandation HLS d'Apple ; à confirmer par test |
| Transcription | Branche séparée, blocs audio d'environ 30 s | Morceaux de 6 s ; transcrire avant de découper | Whisper travaille par fenêtres de 30 s |
| Extrait utile | Métadonnées + 360p + 480p ; l'original reste sur l'Edge | Abandonner la notion ; transférer l'original | « Volume évité » est une mesure exigée |
| Priorité d'envoi | Métadonnées → 360p → 480p | File unique | Sous débit limité, le plus léger passe d'abord |
| Lecture web (révisé) | Pendant le traitement, depuis le début, jusqu'au dernier segment arrivé dans l'ordre ; choix 360p/480p. **Corrigé le 2026-11-20 (D11)** : la bascule automatique en 360p là où le 480p manque n'est pas garantie (un lecteur HLS change de qualité selon le débit, pas selon la présence des segments) ; à prototyper avec hls.js (segment 360p substitué dans la liste 480p avec marque de discontinuité), repli : 480p proposé seulement jusqu'au dernier segment 480p continu | Lecture seulement quand une résolution est complète | HLS gère une liste qui grandit |
| Résultat utile | Arrivé au Cloud, une seule fois, conforme à une référence ; pas d'échéance | Échéance | Une échéance rendrait « inutile » tout résultat suivant une coupure |

### D1 bis — Cas limites du son (2026-11-13)

| Cas | Comportement |
|---|---|
| Pas de piste audio | Branche son non lancée |
| Silence / pas de voix | VAD ; Whisper sauté |
| Son peu audible | Bloc marqué « incertain » |
| Deux langues | Langue détectée par bloc ; liste horodatée |

Limite assumée : changement de langue au milieu d'un bloc → langue dominante retenue.

### D1 ter — Interface web (2026-11-18)

| Point | Décision | Raison |
|---|---|---|
| Progression | % pour les fichiers ; retard affiché pour les flux en direct | Le retard rend la récupération visible en démo |
| Sous-titres avant la vidéo | Stockés dès leur arrivée, affichés quand la vidéo arrive | Indépendants de la vidéo |
| Transcription sans vidéo | Texte affiché à côté du lecteur | Ne pas faire sentir la panne |
| Plusieurs flux | Oui | Capacité par Edge mesurée par les scripts de charge |

### D2 — Topologie (2026-11-13)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Nombre d'Edge | Deux | Un seul | Réalisme ; agrégation et identité des nœuds |
| Rôles | Edge, Cloud, Observation | Observation sur le Cloud par défaut | Ne pas perturber les mesures ni dépendre du Cloud |
| Machines pour les mesures | 4 | 3 avec deux Edge sur la même machine | Deux Edge sur un processeur faussent les mesures |
| Repli | 3 machines, voire 2, sans changer le code | Architecture figée | Rôles = groupes Ansible |
| Machines et conteneurs | VM avec conteneurs dedans | — | Imposé par l'énoncé |
| Chemin d'observation | `tc` ne bride que le trafic vers le Cloud ; métriques conservées localement | Réseau d'administration séparé | Une seule carte réseau suffit |
| Développement | Conteneurs sur le poste ou Codespaces ; mesures sur les vraies VM | VM locales | 8 Go de RAM |

### D3 — Communication Edge→Cloud (2026-11-18)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Protocole | HTTP, à l'initiative de l'Edge | Broker MQTT/NATS ; mixte | Un broker ne remplace pas le buffer ; un composant de moins ; MQTT non exigé |
| Déduplication | Identifiant unique par envoi (nœud, vidéo, segment, résolution) ; le Cloud répond « déjà reçu » | — | Cas de la confirmation perdue |
| Sortie du buffer | Après confirmation du Cloud seulement | Supprimer à l'envoi | Zéro perte |
| Échecs | Délai d'attente, nouvelles tentatives avec backoff exponentiel plafonné | Réessai immédiat | Ne pas surcharger un Cloud en difficulté |
| Panne du Cloud | Traitée comme une coupure WAN | — | Indiscernables pour l'Edge |
| Suivi web | Interrogation régulière par le navigateur ; coût à mesurer | Diffusion temps réel | Hors WAN bridé |

### D4 — Buffer (2026-11-18)

**Politique**

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Principe | « Ne pas produire ce qu'on ne pourra pas envoyer » ; rien n'est jeté | Jeter les plus anciens ; ralentir un flux en direct | Jeter rend le traitement vain ; une caméra ne ralentit pas |
| Paliers (direct) | Normal : tout ; palier 1 (~50 %) : métadonnées + 360p ; palier 2 (~80 %) : métadonnées ; rattrapage depuis l'original après la crise | — | Seuils à régler par test |
| Fichiers importés | Ralentir la lecture du fichier | Paliers | On peut produire au rythme de l'envoi |
| Volume | Espace dédié avec plafond | Disque principal | Un buffer plein ne doit pas faire planter la machine |
| Ordre : sous-titres | Le plus récent d'abord | — | Page vite à jour |
| Ordre : vidéo | Priorité au direct, part fixe (ex. 30 %) au rattrapage | Récent d'abord pur | Lecture depuis le début ; éviter la famine |

Ordres de grandeur (hypothèses : 360p ≈ 0,8 Mbit/s, 480p ≈ 1,5 Mbit/s) : coupure de 2 min ≈ 35 Mo ; rattrapage ≈ 100 s à 5 Mbit/s, ≈ 36 s à 10 Mbit/s ; lien < 2,3 Mbit/s → buffer qui grossit sans fin.

**Technologie**

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Support | Segments en fichiers + index SQLite (priorité, état, empreinte) | Fichiers seuls ; Redis/RabbitMQ ; NATS JetStream ; Greengrass/Azure IoT Edge | Nos besoins ne sont couverts par aucun outil ; pas de service en plus ; pas de dépendance à un fournisseur |
| Écriture | Fichier `.tmp` → renommage atomique → inscription dans SQLite | Écriture directe | Jamais de fichier à moitié écrit (leçon NATS) |
| Durabilité | Réglage `synchronous` de SQLite choisi et mesuré ; risque résiduel documenté | Implicite | NATS ne force l'écriture qu'aux 2 min par défaut |
| Redémarrage | Vérifier existence et empreinte de chaque segment ; pertes comptées dans une métrique | Reprise aveugle | Prouver le zéro perte (leçon NATS) |
| Déduplication côté Cloud | Identifiants gardés sans limite de temps, contrainte d'unicité | Fenêtre de temps | La fenêtre par défaut de NATS (2 min) égale notre coupure |
| Envois simultanés | Nombre limité (ex. 2 ou 3, à mesurer) | Sans limite | Sur un lien lent, trop d'envois en parallèle finissent tous en retard |

**Conservation des originaux**

| Point | Décision | Raison |
|---|---|---|
| Protection | Protégé tant que toutes ses versions ne sont pas confirmées par le Cloud | Nécessaire au rattrapage |
| Suppression | Ensuite supprimable, les plus anciens d'abord quand l'espace atteint son plafond | Espace disque |
| Cas limite | Espace des originaux protégés plein : refuser les nouvelles vidéos et l'afficher | Perte visible plutôt que silencieuse. Risque résiduel |

### D5 — Politique hybride adaptative (2026-11-18)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Leviers | (1) paliers ; (2) retranscription au Cloud d'un bloc douteux ; (3) déport d'un flux entier vers le Cloud | Traitement toujours au même endroit | Couvre le lien et la capacité de l'Edge |
| Signaux | Autonomie du buffer (principal), retard de traitement, confiance de Whisper | Mesure active du débit WAN | Sonder le lien consomme la ressource rare |
| Grille | Edge à l'aise : tout sur l'Edge (+ paliers si lien mauvais). Edge débordé + lien bon : déporter certains flux. Edge débordé + lien mauvais : paliers, retard assumé | — | Dernière case = limite du rapport |
| Granularité | Décisions par flux, valables pour une période | Par segment | Plus simple à coder, observer et expliquer |
| Stabilité | Hystérésis + durée minimale entre deux décisions | Seuil unique | Éviter les oscillations |
| Forme | Règles simples et lisibles | Modèle appris | Explicable et mesurable |
| Énergie | Comparer « Edge » vs « brut + Cloud » ; critère possible après D8 | — | Inconnu sans mesure |

### D7 — Traitement : modèles et outils (2026-11-18)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Moteur de transcription | faster-whisper en int8 ; whisper.cpp en alternative si la mémoire limite | openai/whisper | Benchmark du projet (small, 13 min d'audio, 8 threads) : 2 min 04 s et 995 Mo contre 10 min 31 s et 3,1 Go ; à revérifier sur nos VM |
| Modèle Edge | base au minimum, small si la VM le permet (critère : transcription d'un bloc ≤ ~50 % de sa durée) | tiny | En français, audio long (Common Voice 17) : tiny ≈ 28 % de WER, base ≈ 19 %, small ≈ 12,5 % |
| Variante française | Tester un small affiné en français (≈ 11,8 % de WER sur Common Voice 11), en vérifiant la détection de langue | — | Même coût CPU, meilleure qualité |
| Modèle Cloud | medium ou distil-large-v3-fr (≈ 11 % de WER en audio long) | — | Flux déportés et retranscription |
| Comparaison juste | Cloud-only utilise le même modèle que l'Edge-first | Gros modèle au Cloud pour la baseline | Comparer des architectures, pas des modèles |
| Langues | Modèle multilingue obligatoire | Variantes `.en` | Détection de langue |
| Seuil de qualité | WER ≤ 20 % sur l'Edge, mesuré sur nos vidéos ; ajustable | — | Blocs à faible confiance retranscrits au Cloud |
| VAD | Silero, via le filtre intégré de faster-whisper | WebRTC VAD | ~2 Mo, < 1 ms par morceau |
| Transcodage | Une commande ffmpeg, un décodage, deux sorties (360p, 480p) ; image clé toutes les 2 s (en temps) ; débit plafonné ; préréglage choisi par mesure | Deux commandes ; qualité constante sans plafond | Éviter le double décodage ; segments réguliers ; débit prévisible |
| API externes | Pas dans le pipeline ; Groq éventuellement pour produire des références hors ligne | Groq / Azure / Google dans le pipeline | Indisponible pendant la coupure ; énergie non mesurable ; données sensibles ; limites de requêtes ; dépendance en démo |
| Ingestion | `ffprobe` puis normalisation : résolutions ≤ source ; petit côté à 360/480 ; rotation appliquée ; images/s variables gérées, plafond 30 ; audio 16 kHz mono, piste par défaut ; fichiers illisibles en quarantaine, comptés | Supposer un format de source | Robustesse à la source |
| Vidéos de test | Enregistrées par nous à partir d'un texte écrit, conditions variées ; plus des vidéos libres de formats variés | Vidéos tierces seules | Référence exacte pour le WER ; matrice de test présentable |

### D6 — Orchestration ; images et registre (2026-11-20)

**Décidé**

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Méthode | Orchestrateur choisi **par expérience** (banc d'essai), pas par raisonnement | Trancher maintenant | Exigence de Luciano : ne refuser une solution moderne éprouvée que si le gain de l'alternative est démontré |
| Services | Écrits **indépendants de l'orchestrateur** : configuration par variables d'environnement, point `/healthz`, journaux sur la sortie standard, état (buffer, originaux) dans des volumes | Code lié à un orchestrateur | Basculer ne coûte que des fichiers de déploiement ; on peut implémenter sans avoir tranché |
| Images | Construites par GitHub Actions, stockées sur le registre GitHub (GHCR), étiquetées par version de code (jamais `latest`) | Construction sur les machines à la démo | Redéploiement rapide et reproductible |
| Modèles | Inclus dans les images | Téléchargement au démarrage | Démo indépendante de Hugging Face ; reproductibilité |
| Découpage | Une image par rôle (traitement Edge avec petit modèle, API Cloud, traitement Cloud avec gros modèle, web) | Image unique | L'Edge ne télécharge pas le gros modèle |
| Plan B | Ansible peut copier les images exportées depuis notre ordinateur | Registre seul | Débit Internet de la démo inconnu ; chronométrer les deux voies |

**Banc d'essai (à mener dès qu'on a les VM)**

Candidats : (1) Docker Compose + Ansible ; (2) k3s en cluster (serveur au Cloud, agents sur les Edge) ; (3) KubeEdge (EdgeCore ~70 Mo sur les Edge, CloudCore + k3s au Cloud).

| Critère | Mesure |
|---|---|
| Coût sur l'Edge | Mémoire et CPU au repos de l'orchestrateur |
| Trafic de contrôle | Octets par heure sur le WAN bridé |
| Coupures | Survie des conteneurs Edge pendant et après une coupure de 2 min et de 15 min |
| Conteneur bloqué | Temps avant relance automatique |
| Redéploiement | Durée depuis une machine vierge, chronométrée |
| Énergie au repos | Selon la méthode de D8 |
| Complexité | Fichiers de configuration à maintenir, étapes du README |

Règle de décision, fixée **avant** la mesure : on retient la solution Kubernetes la plus légère si elle survit aux deux coupures sans perte, si son trafic de contrôle reste sous 1 % du débit bridé à 5 Mbit/s, et si le redéploiement tient dans le budget de la démo ; sinon, Docker Compose. Seuils discutables, mais à écrire avant le test.

Si Compose est retenu : prévoir explicitement la relance des conteneurs « unhealthy » (arrêt volontaire du service quand il se détecte bloqué, ou petit service de surveillance), car Docker seul ne relance que les conteneurs arrêtés.

Analyse ayant mené à ce choix :
- Avantages réels de Kubernetes chez nous : relance des conteneurs malades, gestion des secrets et règles réseau (D9), écosystème, attente probable du cours. Avantages sans objet à notre échelle : replacement sur un autre nœud (traitement Edge lié à sa source), mises à jour progressives (sujet du projet 2), gestion de flotte (2 Edge seulement).
- Le placement Edge/Cloud de D5 n'est pas une réécriture de Kubernetes : il serait à écrire dans tous les cas.
- Risques de Kubernetes chez nous : trafic de contrôle sur le WAN mesuré ; expulsion des conteneurs d'un nœud injoignable après ~5 min par défaut ; ~1,6 Go pour un serveur k3s.
- Le banc d'essai devient une section du rapport (mesures et méthodologie).

### D8 — Observabilité et énergie (2026-11-20)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Métriques machine et conteneur | node_exporter (par VM), cAdvisor (par conteneur, working set = WSS) | — | Mesures « ressources » exigées |
| Métriques applicatives | Exposées par nos services : latences par étape, buffer, palier actif, décisions D5, pertes, rejets à l'ingestion | — | Relier les métriques aux SLO et aux incidents |
| eBPF | Exporteur eBPF : octets envoyés **par destination** (WAN vs observation), retransmissions TCP, temps d'aller-retour | eBPF décoratif | Mesurer les octets WAN sans le trafic de supervision ; expliquer la latence sous `tc` |
| Collecte | Prometheus en mode agent sur chaque Edge (journal sur disque, envoi différé) vers la machine d'observation ; débit d'envoi limité ; octets comptés à part | Prometheus central qui interroge les Edge | Sans agent, aucune métrique pendant la coupure ; même principe que notre buffer |
| Journaux | Fluent Bit avec buffer disque → Loki ; identifiant d'événement dans chaque message | — | Survivre à la coupure ; relier journaux et traces |
| Traces | **Horodatages maison** à chaque étape (capture, ingestion, transcodage/transcription, entrée buffer, chaque tentative d'envoi, réception Cloud, disponibilité web), plus palier et nombre de tentatives, transportés avec l'événement ; durées par étape exposées en métriques ; vue Grafana du parcours | OpenTelemetry + Tempo/Jaeger | Choix de Luciano : un composant de moins ; les horodatages traversent naturellement le buffer et la coupure ; export vers OpenTelemetry possible plus tard |
| Horloges | chrony sur toutes les machines ; écart résiduel mesuré et reporté comme incertitude | Supposer les horloges justes | Une latence Edge → Cloud dépend de deux horloges |
| Énergie : cadre | Norme SCI (ISO/IEC 21031:2024) : E par R, avec R = résultat utile (D1) | Définition maison | Exigence de Luciano : méthode reconnue |
| Énergie : estimation | E estimée par **deux** modèles reconnus, Cloud Carbon Footprint (linéaire, SPECpower) et Boavizta (profils non linéaires), à partir du CPU par conteneur et des coefficients du vrai processeur (`lscpu`) ; résultats présentés en encadrement ; conclusions retenues si les deux modèles classent les configurations dans le même ordre | Kepler (peu fiable sans RAPL, pensé pour Kubernetes) ; un seul modèle | Dans une VM, toute méthode reconnue est une estimation ; deux modèles concordants rendent les comparaisons robustes |
| Énergie : mesure réelle | Vérifier `/sys/class/powercap` sur les VM ; si les VM tournent sur un QEMU/KVM accessible, Scaphandre sur l'hyperviseur avec l'exportateur QEMU | — | Seule voie vers une vraie mesure ; dépend du prof |
| Périmètre énergie | Edge + Cloud ; machine d'observation mesurée mais exclue de l'énergie par résultat ; énergie du réseau non mesurée (limite déclarée) | — | L'observation est un coût de mesure, pas du système |
| Tableaux de bord | Grafana pensé pour la démo : retard par flux, buffer, palier actif, octets WAN, énergie par résultat | — | Rendre la perturbation et la récupération visibles |

### D9 — Sécurité (2026-11-20)

**Modèle de menace** (à reprendre dans le rapport)

Actifs : vidéos et transcriptions (« données sensibles ») ; intégrité des résultats ; secrets ; intégrité des mesures.

| Menace | Exemple | Parade |
|---|---|---|
| Écoute sur le WAN | Interception Edge → Cloud | mTLS (chiffrement) |
| Faux Edge | Une machine se fait passer pour Edge A | mTLS (certificat par Edge) + correspondance nœud / certificat |
| Edge compromis | Vol ou piratage d'un Edge exposé | Révocation de son certificat ; chiffrement du disque (selon mesure) |
| Image piégée | Image modifiée entre construction et déploiement | Signature cosign vérifiée, désignation par empreinte |
| Abus de la page publique | Requêtes massives, accès aux fonctions internes | Lecture seule, limitation des requêtes, pare-feu |
| Conteneur détourné | Faille dans ffmpeg ou Whisper | Non-root, lecture seule, droits noyau retirés |

**Décisions**

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Identité des nœuds | **mTLS** : notre autorité de certification générée par Ansible, un certificat par Edge, vérification dans les deux sens | Jeton secret par Edge | Choix de Luciano : « pour la sécurité, on ne lésine pas » ; identité forte, chiffrement du WAN, révocation individuelle |
| Cohérence identité / données | Le Cloud vérifie que le nœud nommé dans l'identifiant d'envoi (D3) correspond au certificat présenté | — | Edge A ne peut pas envoyer au nom d'Edge B |
| Coût du mTLS | Octets supplémentaires comptés dans les octets WAN ; CPU mesuré | Supposer le coût négligeable | Méthode : mesurer |
| Secrets | Ansible Vault dans le dépôt ; secrets montés comme fichiers au démarrage ; jamais dans les images ni en clair dans Git ; secrets de GitHub Actions pour le registre ; certificats créés au déploiement | Secrets dans les images | Exigence « secrets externes » ; redéploiement sur les IP du prof |
| Conteneurs | Utilisateur non-root, système de fichiers en lecture seule sauf volumes prévus, droits noyau retirés | — | Contenir une faille de ffmpeg ou Whisper |
| Droits élevés | `tc` et eBPF dans des conteneurs dédiés avec seulement les droits nécessaires | Donner ces droits à tout le pipeline | Moindre privilège |
| Réseau | Pare-feu par machine : Cloud expose seulement HTTPS ; Edge n'accepte que la machine d'observation (métriques) ; SSH par clé uniquement | — | Réduire la surface d'attaque |
| Page publique | Lecture seule, aucune fonction d'administration ni d'envoi de fichier, limitation des requêtes par client | — | Page publique imposée par l'énoncé |
| Images | Analyse de vulnérabilités (Trivy) et SBOM dans GitHub Actions ; signature cosign ; vérification de la signature par Ansible avant lancement ; image désignée par son empreinte | Étiquette seule, sans vérification | Exigence « images vérifiées » |
| Chiffrement du disque des Edge | **Décidé par mesure**, comme D6 : mesurer le coût CPU, énergie et latence du chiffrement (LUKS) des seuls volumes sensibles (originaux, buffer) ; règle de décision à fixer avant la mesure | Décider sans mesurer | Choix de Luciano : mesurer d'abord |
| Vie privée | Vidéos de test enregistrées par nous, avec consentement ; limite déclarée pour un usage réel d'une page publique de vidéos | — | Page publique imposée |

### D11 — Pile du Cloud (2026-11-20)

| Point | Décision | Options écartées | Raison |
|---|---|---|---|
| Entrées | Proxy Nginx avec deux entrées séparées : HTTPS public (page, lecture HLS) et mTLS (API de réception des Edge) | Une seule entrée | Séparer le public des Edge (D9) |
| API | Python, FastAPI | Go | Même langage que le reste du projet ; quelques requêtes par seconde ; documentation automatique |
| Base de données | **PostgreSQL** : métadonnées, sous-titres, horodatages (D8), identifiants d'envoi avec contrainte d'unicité (D3) | SQLite au Cloud | Validé par Luciano : plusieurs écrivains simultanés (API, workers) ; outil standard adapté |
| File de travaux | Table PostgreSQL avec `FOR UPDATE SKIP LOCKED` ; durée limite par travail, puis remise en file | Redis, RabbitMQ | Pas de composant de plus ; un worker qui plante laisse sinon un travail « en cours » indéfiniment |
| Stockage des vidéos | Segments HLS sur un volume de fichiers servi par le proxy, derrière une couche d'accès au stockage dans le code | MinIO / S3 d'emblée | Pas de service de plus ; passage à S3 possible sans réécriture (piste pour Terraform si le prof fournit AWS) |
| Listes HLS | Construites par le Cloud au fil de l'eau : une par résolution + une liste maîtresse ; seulement la suite continue de segments depuis le début ; ligne de fin à la fin de la vidéo | — | Lecture pendant le traitement (D1) |
| Bascule 360p/480p | **Correction de D1 validée** : prototyper tôt avec hls.js la substitution du segment 360p dans la liste 480p (marque de discontinuité) ; repli : 480p proposé jusqu'au dernier segment 480p continu | Supposer la bascule automatique ; balise GAP | Un lecteur change de qualité selon le débit, pas selon la présence des segments ; prise en charge inégale des discontinuités (bug WebKit sur plusieurs résolutions dans une liste) et de GAP |
| Export | Sous-titres en SRT et WebVTT générés depuis la base | — | Fonction demandée |
| HTTPS public | Certificat Let's Encrypt pour adresse IP (160 h, renouvellement automatique) ; à vérifier sur les machines de démo (joignables depuis Internet ?) ; repli : certificat auto-signé | Certificat auto-signé d'emblée | Pas de nom de domaine à la démo ; éviter l'avertissement du navigateur |
| Workers | Conteneurs séparés de l'API, alimentés par la file PostgreSQL : Cloud-only, flux déportés, retranscription ; nombre et limites CPU par configuration | Traitement dans l'API | Capacité mesurable ; l'API reste réactive |
| Envoi brut | Pour Cloud-only et déport, l'Edge envoie les segments bruts par la même API, mêmes identifiants et confirmations | Canal séparé | Un seul mécanisme |
| Interface web | Pages générées par le serveur (FastAPI) + **Tailwind CSS** (exécutable autonome, sans Node.js) + **htmx** (mises à jour partielles, interrogation régulière) + hls.js | React ou équivalent | Validé par Luciano : la beauté dépend du design, pas de l'outil ; nos besoins sont une liste, un état, un lecteur, une transcription ; pas de chaîne Node.js ni d'image de plus. Risque : le soin du design repose sur nous → maquette des écrans possible avant le code |

### D10 — Protocole expérimental (2026-11-20)

| Point | Décision | Raison |
|---|---|---|
| Chronologie d'un essai | Chauffe (exclue) → régime nominal → perturbation → récupération → retour au nominal ; heures de chaque phase et de `tc` enregistrées | Chronologie des incidents exigée ; la chauffe gonflerait les premières latences |
| Perturbations | Celles de l'énoncé (coupure de 2 min, 5 et 10 Mbit/s) + balayage du débit (10, 5, 3, 2, 1 Mbit/s) + **délai de 100 ms, 1 % de pertes, et leur combinaison** (ajout validé par Luciano, repris de la liste du projet 3) | Le prof fera varier le débit ; sous 2,3 Mbit/s les paliers entrent en jeu ; délai et pertes enrichissent le rapport |
| Taille des échantillons | p99 rapporté seulement avec au moins ~1 000 événements ; sinon dit explicitement, intervalle large ; pas de flux ajoutés pour gonfler les nombres | Segments : ~1 000 en 50 min ; sous-titres : ~1 000 en 4 h par configuration ; ajouter des flux changerait le régime mesuré |
| Répétitions | Au moins 5 essais indépendants par configuration | Variabilité des VM |
| Intervalles | Bootstrap **par essai entier** (pas par événement) | Les événements d'un même essai sont corrélés (tous en retard pendant la coupure) ; un bootstrap par événement donnerait des intervalles trop étroits |
| Comparaisons | Mêmes vidéos, mêmes machines, essais alternés (A, B, A, B…) ; intervalle de la **différence** | Neutraliser la dérive des VM dans le temps |
| Pré-enregistrement | Définitions et règles de décision écrites avant la mesure : pertes = produits − reçus une seule fois (cible 0) ; backlog = taille du buffer dans le temps (octets, éléments) ; temps de reprise = du rétablissement du lien jusqu'à un retard < p95 nominal pendant ≥ 60 s ; volume évité = octets Cloud-only − octets de la configuration, mêmes vidéos | Ne pas ajuster les règles selon les résultats |
| SLO | Fixés après la mesure du régime nominal (ex. p99 nominal + marge), puis figés ; ex. « 99 % des sous-titres visibles en moins de X s » | Une violation n'existe que par rapport à un objectif ; nécessaire pour la démo |
| Automatisation | Un script unique par essai : applique `tc`, lance la charge, horodate les phases, exporte les données | Reproductibilité ; essais de nuit |
| Données brutes | Un dossier par essai (horodatages par événement, export des métriques, journaux, configuration, version du code et empreintes des images), versionné dans le dépôt | Exigé par l'énoncé |
| Menaces sur la validité | Listées dans le rapport : variabilité des VM, écart d'horloge, `tc` sur VM ≠ vrai WAN, coût de l'observation (mesuré une fois avec et sans monitoring) | Honnêteté méthodologique |
| Budget de temps | Inconnu → **« faire avec ce qu'on a »** (choix de Luciano) : commencer à mesurer tôt sur les moyens disponibles (poste, Codespace) pour la mise au point ; mesures finales sur les vraies VM ; exécution par ordre de priorité | Machines et date limite inconnues |

Ordre de priorité des mesures :
1. Les 5 scénarios obligatoires, 5 répétitions.
2. Balayage du débit, délai, pertes et combinaison.
3. Comparaisons : orchestrateurs (D6), chiffrement (D9), VAD et énergie, tailles de modèle et WER (D7), politiques d'ordre d'envoi (D4), coût du mTLS.

Ordre de grandeur : 3 modes × 3 perturbations × 5 répétitions × 25 min ≈ 19 h de machines pour le seul premier niveau.

Point à trancher avant la mesure du chiffrement : **où est la clé**. Sur le même disque, le chiffrement ne protège pas d'un vol. Avec une clé fournie par le réseau au démarrage (principe Clevis/Tang), un Edge qui redémarre pendant une coupure WAN ne peut plus déverrouiller ses données : conflit avec la résilience. Avec une puce TPM (ou vTPM de la VM, si disponible), la clé reste locale mais liée à la machine. À examiner avec la mesure.

---

## 6. Questions ouvertes

Pour le prof :
- Les trois traitements (langue, sous-titres, 360p/480p) sont-ils imposés, ou la « détection locale » est-elle libre ?
- Lecture limitée à 360p/480p sans transfert de l'original : acceptable ?
- Qui applique `tc` pendant la démo, sur quelle machine, et sur toute la carte réseau ou vers une destination ?
- Énergie : les VM tournent-elles sur un hyperviseur QEMU/KVM où Scaphandre pourrait être installé ? Sinon, une estimation selon la norme SCI avec les modèles Cloud Carbon Footprint et Boavizta est-elle acceptée ?
- Démo : combien de machines fournies, caractéristiques (vCPU, RAM), OS, accès root, accès Internet ?
- Terraform le jour de la démo : les machines existent déjà, donc à quoi sert-il ?
- Kubernetes est-il attendu, ou un orchestrateur plus léger justifié par la mesure est-il accepté ?

Résolu : « vidéo 360 » = résolution 360p (et 480p). MQTT n'est pas exigé par l'énoncé du projet 1. Vidéos de test en français.

À tester / mesurer : `tc` et eBPF dans un Codespace ; durée des segments et des blocs audio ; débits réels ; seuils des paliers et de D5 ; flux simultanés par Edge ; coût de l'interrogation de la page web ; réglage de durabilité SQLite ; envois simultanés ; énergie Edge vs Cloud ; vitesse et WER de base / small / small français sur la VM Edge ; préréglage ffmpeg ; utilité de la normalisation du volume ; banc d'essai des orchestrateurs ; durée de redéploiement par registre et par copie locale ; coût du mTLS (octets WAN, CPU) ; coût du chiffrement LUKS des volumes sensibles de l'Edge ; présence d'un vTPM sur les VM.

---

## 7. Historique des séances

- **2026-11-13 — Séance 1** : lecture de l'énoncé et du cours. D1 clos (définitions, cas limites du son). D2 clos (deux Edge, quatre machines, chemin d'observation).
- **2026-11-16 / 2026-11-18 — Séance 2** : D3 clos (HTTP, idempotence, backoff, pas de broker). D1 révisé (lecture pendant le traitement, interface). D4 clos (politique, état de l'art, lecture du code de NATS JetStream, fichiers + SQLite, originaux). D5 clos (leviers, signaux, hystérésis, règles simples). Schéma « décidé / à décider ». D11 ajouté. D7 clos (faster-whisper, base/small en français, seuil WER 20 %, ffmpeg, ingestion robuste, vidéos enregistrées par nous, pas d'API externe).
- **2026-11-19** : document « point d'étape » (LaTeX/PDF) pour le second membre du groupe.
- **2026-11-20 — Séance 3** : D6 — comparaison Kubernetes / Compose, découverte de KubeEdge ; décision de trancher l'orchestrateur par banc d'essai avec règle fixée à l'avance ; services indépendants de l'orchestrateur ; images et registre décidés. D8 clos (agents Prometheus sur les Edge, eBPF par destination, Fluent Bit/Loki, traces par horodatages maison, chrony, énergie selon SCI avec deux modèles reconnus, Scaphandre si hyperviseur accessible). D9 clos (modèle de menace, mTLS, secrets par Ansible Vault, moindre privilège, images signées et vérifiées ; chiffrement du disque Edge décidé par mesure). D11 clos (interface : pages serveur + Tailwind + htmx + hls.js ; Nginx, FastAPI, PostgreSQL avec file SKIP LOCKED, fichiers, listes HLS, certificat IP Let's Encrypt, workers) ; correction de D1 sur la bascule 360p/480p. D10 clos (chronologie, balayage du débit + délai et pertes, bootstrap par essai, pré-enregistrement, SLO fixés après le nominal, données brutes versionnées, priorités). Toutes les décisions d'architecture sont prises.
