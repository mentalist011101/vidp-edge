# Architecture

Vue d'ensemble de l'architecture retenue. Le détail de chaque décision, les options écartées et leurs raisons sont dans le [journal](JOURNAL.md) (section 5).

## Machines et rôles (D2)

| Rôle | Machines | Contenu |
|---|---|---|
| Edge | 2 (Edge A, Edge B), deux sites indépendants | Ingestion, transcodage, transcription, politique adaptative, buffer, envoi, originaux |
| Cloud | 1 | API de réception, base de données, stockage des segments, workers, page web |
| Observation | 1 | Prometheus, Grafana, Loki, scripts de charge et de panne |

Les rôles sont des groupes Ansible : avec 3 machines, l'observation rejoint le Cloud ; le code ne change pas.

## Schéma

```
 Edge A (site 1)                              Edge B (site 2)
 ┌─────────────────────────────────┐          ┌──────────────────┐
 │ source (rejeu) ─► ingestion     │          │ idem             │
 │   ├ image ─► ffmpeg : 360p/480p,│          │                  │
 │   │   segments 6 s, image clé 2s│          │                  │
 │   └ son ──► 16 kHz, VAD,        │          │                  │
 │       faster-whisper, blocs 30 s│          │                  │
 │ politique adaptative (D5)       │          │                  │
 │ ─► buffer : fichiers + SQLite   │          │                  │
 │ ─► envoi HTTP (mTLS, backoff)   │          │                  │
 │ originaux : volume à part       │          │                  │
 └──────────────┬──────────────────┘          └────────┬─────────┘
                │      WAN bridé par tc (mTLS)         │
                └──────────────► Cloud ◄───────────────┘
        Nginx : HTTPS public │ mTLS Edge
        FastAPI ─► PostgreSQL (métadonnées, idempotence, file de travaux)
        segments HLS (fichiers) ─► page web (Tailwind, htmx, hls.js)
        workers : Cloud-only, flux déportés, retranscription

 Observation : Prometheus (agents sur les Edge), Grafana, Loki,
               eBPF (octets par destination), chemin non bridé
```

## Parcours d'un événement

1. La source rejoue une vidéo à vitesse réelle ; l'ingestion l'inspecte et la normalise (ou la met en quarantaine).
2. **Image** : ffmpeg produit des segments HLS de 6 s en 360p et 480p.
3. **Son** : blocs de ~30 s ; le VAD saute les blocs sans voix ; faster-whisper produit langue, sous-titres horodatés et confiance.
4. Les résultats entrent dans le **buffer** (fichier `.tmp`, renommage, inscription SQLite) avec une priorité : métadonnées → 360p → 480p.
5. Le **module d'envoi** transmet en HTTP sur mTLS, avec un identifiant unique ; un élément ne quitte le buffer qu'après confirmation.
6. Le **Cloud** enregistre une seule fois chaque identifiant, met à jour les listes HLS et la base.
7. La **page web** affiche la vidéo (lisible pendant le traitement), la transcription et le retard.

Chaque étape enregistre un horodatage (D8) : c'est ce qui permet de décomposer la latence.

## Modes de fonctionnement

| Mode | Traitement | Ce qui traverse le WAN |
|---|---|---|
| Cloud-only (référence) | Au Cloud, même modèle que l'Edge | Vidéo brute |
| Edge-first | Sur l'Edge | Métadonnées, 360p, 480p |
| Hybride adaptatif (D5) | Selon la politique : paliers, retranscription, déport de flux | Variable |

## Choix tranchés par la mesure

| Sujet | Candidats | Débat |
|---|---|---|
| Orchestrateur | Docker Compose, k3s, KubeEdge | D6 |
| Chiffrement du disque Edge | Avec ou sans LUKS ; emplacement de la clé | D9 |
| Modèle Edge | base ou small (éventuellement small affiné en français) | D7 |
| Seuils de la politique | Paliers, hystérésis | D4, D5 |
| Bascule 360p/480p | Substitution avec discontinuité, ou 480p jusqu'au dernier segment continu | D11 |
