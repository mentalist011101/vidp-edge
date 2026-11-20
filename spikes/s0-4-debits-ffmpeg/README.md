# S0-4 — Débits réels du 360p et du 480p

## Question
Quels débits et tailles de segments obtient-on avec la commande ffmpeg de D7, et l'hypothèse « ≈ 2,3 Mbit/s par Edge » (360p ≈ 0,8 ; 480p ≈ 1,5) tient-elle ?

## Méthode
- Une commande ffmpeg : un décodage, deux sorties (360p et 480p, petit côté), image clé toutes les 2 s imposée en temps, débit plafonné, segments HLS de 6 s.
- Tester 2 ou 3 préréglages (`veryfast`, `faster`, `medium`) : débit moyen, débit maximal par segment, taille des segments, temps CPU par minute de vidéo.
- Sur au moins 2 vidéos de test différentes (une calme, une avec beaucoup de mouvement).

## Règle de décision (écrite avant le test)
- Retenir le préréglage le moins coûteux en CPU dont le débit réel reste sous le plafond fixé.
- Remplacer l'hypothèse de D4 par les chiffres mesurés et recalculer : volume d'une coupure de 2 min, temps de rattrapage à 5 et 10 Mbit/s.

## Résultat
_À compléter._
