# Protocole expérimental

Ce document fixe **avant toute mesure** les définitions, le déroulé des essais et les règles d'analyse (décision D10 du [journal](JOURNAL.md)). Il ne doit pas être modifié après avoir vu les résultats ; toute modification est datée et justifiée.

## Définitions

| Grandeur | Définition |
|---|---|
| Événement | Un segment vidéo (6 s, par résolution) ou un bloc de sous-titres (~30 s) |
| Résultat utile | Événement arrivé au Cloud, une seule fois, conforme à la référence (sous-titres : WER ≤ 20 % ; vidéo : segment décodable) |
| Latence | Du moment de capture de l'événement à sa disponibilité sur la page web |
| Pertes | Événements produits − événements reçus une seule fois. Cible : 0 |
| Backlog | Taille du buffer au cours du temps, en octets et en nombre d'éléments |
| Temps de reprise | Du rétablissement du lien jusqu'à ce que le retard redevienne inférieur au p95 du régime nominal, et y reste au moins 60 s |
| Volume évité | Octets WAN du Cloud-only − octets WAN de la configuration testée, sur les mêmes vidéos |
| Énergie par résultat utile | E / R selon la norme SCI (ISO/IEC 21031:2024), E estimée par Cloud Carbon Footprint et Boavizta, R = nombre de résultats utiles ; Edge + Cloud, machine d'observation exclue |

## Déroulé d'un essai

```
| chauffe | régime nominal | perturbation | récupération | retour au nominal |
  exclue      mesuré           mesuré          mesuré          mesuré
```

- Lancement uniquement par script ; heures de chaque phase et de `tc` enregistrées.
- Horloges synchronisées par chrony ; écart résiduel mesuré et reporté.

## Perturbations

| Perturbation | Valeurs |
|---|---|
| Coupure WAN | 2 min |
| Débit limité | 10, 5, 3, 2, 1 Mbit/s |
| Délai | 100 ms |
| Pertes de paquets | 1 % |
| Combinaison | Délai + pertes + débit limité |

## Analyse

- Au moins **5 répétitions** indépendantes par configuration.
- p50, p95, p99 ; le p99 n'est rapporté que sur au moins ~1 000 événements, sinon c'est dit explicitement.
- Intervalles de confiance par **bootstrap par essai entier** (les événements d'un même essai sont corrélés).
- Comparaisons : mêmes vidéos, mêmes machines, essais **alternés** ; on rapporte l'intervalle de la **différence**.
- SLO fixés après la mesure du régime nominal, puis figés.

## Priorités

1. Les 5 scénarios obligatoires (Cloud-only, Edge-first, hybride, coupure de 2 min, 5 et 10 Mbit/s).
2. Balayage du débit, délai, pertes, combinaison.
3. Comparaisons : orchestrateurs, chiffrement, VAD et énergie, tailles de modèle et WER, politiques d'ordre d'envoi, coût du mTLS.

## Données brutes

Un dossier par essai dans `experiments/runs/` : horodatages par événement, export des métriques, journaux, configuration, version du code et empreintes des images.

## Menaces sur la validité

Variabilité des VM ; écart d'horloge ; `tc` sur une VM n'est pas un vrai WAN ; coût de l'observation elle-même (mesuré une fois avec et sans monitoring) ; énergie estimée et non mesurée (sauf accès à l'hyperviseur).
