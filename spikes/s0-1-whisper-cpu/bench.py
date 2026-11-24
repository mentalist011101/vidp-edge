"""S0-1 — Mesure la vitesse de faster-whisper sur CPU pour UNE configuration.

Usage :
    python bench.py --model base --beam 5 --blocks blocks/ --out results/

Chaque configuration tourne dans son propre processus (voir run_all.sh) pour que
la mémoire maximale mesurée soit bien celle de ce modèle seul.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import time
import wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def load_wav(path: Path) -> tuple[np.ndarray, float]:
    """Lit un WAV 16 kHz mono 16 bits et renvoie (échantillons float32, durée en s).

    On passe un tableau à Whisper plutôt qu'un chemin : la mesure ne compte que la
    transcription, et on évite PyAV (incompatibilité de version avec faster-whisper).
    """
    with wave.open(str(path), "rb") as f:
        if f.getframerate() != 16000 or f.getnchannels() != 1 or f.getsampwidth() != 2:
            raise SystemExit(f"{path.name} : attendu 16 kHz, mono, 16 bits")
        frames = f.readframes(f.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    return audio, len(audio) / 16000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True, help="base, small, ou chemin d'un modèle converti"
    )
    parser.add_argument("--beam", type=int, default=5, help="taille du faisceau de décodage")
    parser.add_argument("--blocks", type=Path, default=Path("blocks"))
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()

    blocks = sorted(args.blocks.glob("block_*.wav"))
    if len(blocks) < 2:
        raise SystemExit("Il faut au moins 2 blocs (le premier sert de chauffe).")

    threads = os.cpu_count() or 1
    t0 = time.perf_counter()
    model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=threads)
    load_s = time.perf_counter() - t0

    rows = []
    texts = []
    for i, block in enumerate(blocks):
        audio, duration = load_wav(block)
        start = time.perf_counter()
        # language=None : on laisse Whisper détecter la langue, comme dans le pipeline.
        segments, info = model.transcribe(audio, beam_size=args.beam, language=None)
        # `segments` est un générateur : la transcription n'a lieu qu'en le parcourant.
        segs = list(segments)
        elapsed = time.perf_counter() - start
        text = " ".join(s.text.strip() for s in segs)
        avg_logprob = sum(s.avg_logprob for s in segs) / len(segs) if segs else None
        rows.append(
            {
                "block": block.name,
                "warmup": i == 0,  # le premier bloc est la chauffe, exclue des statistiques
                "duration_s": round(duration, 3),
                "elapsed_s": round(elapsed, 3),
                "ratio": round(elapsed / duration, 3),
                "language": info.language,
                "language_prob": round(info.language_probability, 3),
                "avg_logprob": round(avg_logprob, 3) if avg_logprob is not None else None,
            }
        )
        texts.append(text)
        print(f"{block.name}: {elapsed:5.1f} s pour {duration:4.1f} s d'audio ({info.language})")

    # ru_maxrss est en kilo-octets sous Linux : mémoire maximale du processus.
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    config = f"{Path(args.model).name}_beam{args.beam}"
    args.out.mkdir(parents=True, exist_ok=True)
    result = {
        "config": config,
        "model": args.model,
        "beam": args.beam,
        "threads": threads,
        "cpu": platform.processor() or platform.machine(),
        "load_s": round(load_s, 2),
        "peak_mem_mb": round(peak_mb),
        "blocks": rows,
        "transcript": " ".join(texts),
    }
    (args.out / f"{config}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n{config} : mémoire max {peak_mb:.0f} Mo, chargement {load_s:.1f} s")


if __name__ == "__main__":
    main()
