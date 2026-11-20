# S0-2 — `tc` et eBPF dans un Codespace

## Question
Peut-on développer et tester dans un GitHub Codespace la partie réseau : brider le débit, couper le lien, compter les octets par destination avec eBPF ?

## Méthode
1. `tc qdisc add dev eth0 root netem rate 5mbit` puis mesurer le débit réel (par exemple avec `iperf3` vers un conteneur local ou un téléchargement).
2. Coupure : `netem loss 100%`, puis rétablissement.
3. Filtrer par destination (bridage seulement vers une adresse) avec `tc filter`.
4. eBPF : `bpftrace` (ou bcc) pour compter les octets envoyés par adresse de destination.
5. Noter ce qui échoue et pourquoi (droits, noyau, conteneur).

## Règle de décision (écrite avant le test)
- Si les points 1 à 4 fonctionnent : la partie réseau se développe dans le Codespace.
- Si `tc` fonctionne mais pas eBPF : développer `tc` dans le Codespace, eBPF sur une vraie VM dès qu'elle est disponible.
- Si `tc` ne fonctionne pas : il faut une VM Linux (fournie par le prof ou gratuite) dès le sprint 1.

## Résultat
_À compléter._
