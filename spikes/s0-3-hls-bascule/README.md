# S0-3 — Bascule 360p/480p avec hls.js

## Question
Si un segment 480p manque, la lecture peut-elle continuer en remplaçant ce segment par le segment 360p correspondant, dans la liste 480p, avec une marque de discontinuité (`#EXT-X-DISCONTINUITY`) ?

## Contexte (D1 corrigé en D11)
Un lecteur HLS change de qualité selon le débit, pas selon la présence des segments. La bascule automatique n'est donc pas garantie.

## Méthode
1. Produire avec ffmpeg 10 segments de 6 s en 360p et en 480p d'une même vidéo.
2. Écrire une liste 480p où les segments 4 et 5 sont remplacés par les 360p, encadrés de marques de discontinuité.
3. Lire avec hls.js dans Chrome et Firefox (page HTML minimale servie localement) ; tester aussi Safari si possible.
4. Variante : liste qui grandit (type `EVENT`) pour simuler la lecture pendant le traitement.

## Règle de décision (écrite avant le test)
- **Option A retenue** si la lecture est continue (pas d'arrêt de plus de 1 s) dans Chrome et Firefox avec hls.js.
- Sinon **option C** : le 480p n'est proposé que jusqu'au dernier segment 480p continu ; D1 et D11 sont mis à jour.

## Résultat
_À compléter._
