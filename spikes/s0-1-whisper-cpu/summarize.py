"""S0-1 — Résume les résultats et applique la règle de décision écrite dans README.md.

Usage :
    python summarize.py --results results/ --reference reference.txt
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import jiwer

# Règle de décision (README.md, écrite avant le test) :
# p95 du rapport temps / durée ≤ 0,5  ET  WER ≤ 20 %.
MAX_RATIO_P95 = 0.5
MAX_WER = 0.20

NORMALIZE = jiwer.Compose(
    [
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
    ]
)


def p95(values: list[float]) -> float:
    """95e percentile (interpolation linéaire)."""
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[94]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--reference", type=Path, default=Path("reference.txt"))
    args = parser.parse_args()

    reference = NORMALIZE(args.reference.read_text(encoding="utf-8"))
    lines = [
        "| Configuration | Blocs | Médiane temps/durée | p95 temps/durée | Max | WER "
        "| Mémoire max | Verdict |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for path in sorted(args.results.glob("*.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        ratios = [b["ratio"] for b in r["blocks"] if not b["warmup"]]
        wer = jiwer.wer(reference, NORMALIZE(r["transcript"]))
        ok = p95(ratios) <= MAX_RATIO_P95 and wer <= MAX_WER
        lines.append(
            f"| {r['config']} | {len(ratios)} | {statistics.median(ratios):.2f} | "
            f"{p95(ratios):.2f} | {max(ratios):.2f} | {wer:.1%} | {r['peak_mem_mb']} Mo | "
            f"{'retenu' if ok else 'non retenu'} |"
        )
    print("\n".join(lines))
    print(
        f"\nRègle : p95 temps/durée ≤ {MAX_RATIO_P95} et WER ≤ {MAX_WER:.0%}. "
        "Chauffe (premier bloc) exclue."
    )


if __name__ == "__main__":
    main()
