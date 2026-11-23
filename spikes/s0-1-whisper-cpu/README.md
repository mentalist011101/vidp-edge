# S0-1 — faster-whisper sur 2 cœurs, en français

## Question
Le modèle **base** ou **small** de faster-whisper (int8) suit-il un flux en direct sur une machine à 2 cœurs, avec une qualité acceptable en français ?

## Hypothèses (D7)
- small : ~12,5 % de WER en audio long (Common Voice 17), base : ~19 %.
- Sur 2 cœurs, small risque de ne pas laisser de marge à ffmpeg.

## Méthode
- Machine : GitHub Codespace à 2 cœurs (noter le modèle de CPU avec `lscpu`).
- Audio : une vidéo de test en français (S0-7), découpée en blocs de 30 s, 16 kHz mono.
- Pour chaque modèle (base, small, et si possible un small affiné en français) : temps de transcription par bloc, mémoire maximale, WER contre le texte lu.
- Au moins 20 blocs par modèle ; rapporter médiane et maximum.

## Règle de décision (écrite avant le test)
- Un modèle est **retenu pour l'Edge** si le temps de transcription d'un bloc reste ≤ 50 % de sa durée (≤ 15 s pour 30 s) au p95 **et** si son WER ≤ 20 %.
- Si les deux passent : prendre le plus précis (small).
- Si aucun ne passe : rapporter les chiffres et rouvrir D7 (blocs plus courts, whisper.cpp, ou déport plus fréquent).

## Comment lancer

Dans un Codespace à 2 cœurs, depuis ce dossier :

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
pip install -r requirements.txt
# déposer la vidéo de test (hors Git) et le texte lu dans reference.txt
./run_all.sh /chemin/vers/video_test.mp4
```

- `run_all.sh` découpe l'audio en blocs de 30 s (16 kHz mono), puis mesure 4 configurations : base et small, avec un faisceau de décodage de 5 (valeur par défaut) et de 1 (décodage glouton, plus rapide).
- `bench.py` mesure une configuration dans son propre processus (pour isoler la mémoire maximale) et écrit `results/<configuration>.json`.
- `summarize.py` calcule médiane, p95 et maximum du rapport temps de transcription / durée du bloc, le WER contre `reference.txt`, et applique la règle de décision ci-dessus.

Les fichiers `results/*.json` sont les données brutes : ils sont versionnés. Les blocs audio ne le sont pas.

## Résultat
_À compléter._
