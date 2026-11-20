# spikes/ — levée des risques (sprint 0)

Un *spike* est un test court et jetable qui répond à une question précise avant de construire. Chaque dossier contient la question, l'hypothèse, la méthode, **la règle de décision écrite avant le test**, puis le résultat.

| Spike | Question | Débat |
|---|---|---|
| [s0-1-whisper-cpu](s0-1-whisper-cpu/README.md) | base ou small tient-il sur un Edge à 2 cœurs, en français ? | D7 |
| [s0-2-tc-ebpf-codespace](s0-2-tc-ebpf-codespace/README.md) | Peut-on développer la partie réseau (`tc`, eBPF) dans un Codespace ? | D2, D8 |
| [s0-3-hls-bascule](s0-3-hls-bascule/README.md) | hls.js lit-il une liste 480p où un segment manquant est remplacé par un 360p ? | D1, D11 |
| [s0-4-debits-ffmpeg](s0-4-debits-ffmpeg/README.md) | Quels débits réels pour le 360p et le 480p ? | D4, D7 |

Le code d'un spike n'a pas vocation à être réutilisé tel quel : seule la conclusion compte, reportée dans `docs/JOURNAL.md`.
