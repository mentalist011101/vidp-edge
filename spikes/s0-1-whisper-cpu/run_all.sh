#!/usr/bin/env bash
# S0-1 — Prépare l'audio puis mesure toutes les configurations, une par processus.
# Usage : ./run_all.sh ma_video.mp4
set -euo pipefail

SRC="${1:?Donner le chemin de la vidéo ou de l'audio de test}"
cd "$(dirname "$0")"

echo "== Machine"
nproc
lscpu | grep -E "Model name|^CPU\(s\)"
free -h | head -2

echo "== Découpage en blocs de 30 s, 16 kHz mono"
rm -rf blocks && mkdir -p blocks
ffmpeg -loglevel error -i "$SRC" -vn -ac 1 -ar 16000 -c:a pcm_s16le \
  -f segment -segment_time 30 blocks/block_%03d.wav
ls blocks | wc -l

mkdir -p results
for model in base small; do
  for beam in 5 1; do
    echo "== $model, beam $beam"
    python bench.py --model "$model" --beam "$beam" --blocks blocks --out results
  done
done

echo "== Résumé"
python summarize.py --results results --reference reference.txt
