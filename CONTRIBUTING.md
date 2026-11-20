# Méthode de travail

## Principe

`main` contient toujours une version qui fonctionne. **Personne ne pousse directement sur `main`** : chaque changement passe par une Pull Request (PR) relue par l'autre membre de l'équipe.

## Le cycle d'une tâche

1. **Prendre une issue** du sprint en cours (voir [`docs/SPRINTS.md`](docs/SPRINTS.md) et l'onglet *Issues*). S'assurer qu'elle vous est assignée.
2. **Créer une branche** depuis `main` à jour :
   ```bash
   git switch main && git pull
   git switch -c feat/14-edge-buffer
   ```
   Format : `<type>/<numéro-issue>-<description-courte>`. Types : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `perf`, `exp`, `spike`.
3. **Travailler par petits commits** au format Conventional Commits :
   ```
   feat(edge): écrire les segments dans le buffer via .tmp puis renommage
   fix(cloud): rejeter un envoi dont le nœud ne correspond pas au certificat
   docs: compléter le protocole de mesure
   ```
   Pas de ligne `Co-Authored-By` ni de mention d'un assistant d'IA dans les commits ou les PR.
4. **Vérifier localement** avant d'ouvrir la PR :
   ```bash
   ruff check .
   pytest
   ```
5. **Ouvrir la PR** vers `main` en remplissant le modèle (ce qui change, comment tester, issue liée avec `Closes #14`).
6. **Relecture** : l'autre membre relit, pose ses questions et approuve. La relecture est une vraie contribution : c'est le moyen pour chacun de comprendre tout le système.
7. **Fusion** par l'auteur une fois la PR approuvée et l'intégration continue verte (« Squash and merge » pour garder un historique lisible).

## Règles de la branche `main`

- PR obligatoire, au moins une approbation.
- Intégration continue verte obligatoire.
- Pas de force-push.

## Décisions d'architecture

Une PR qui change une décision du journal ([`docs/JOURNAL.md`](docs/JOURNAL.md)) doit :
- l'annoncer dans sa description ;
- mettre à jour le journal (décision, option écartée, raison, date) dans la même PR.

## Données et fichiers lourds

- Les vidéos de test et les modèles ne vont **pas** dans Git : trop lourds. Ils sont stockés à part (Releases GitHub ou espace partagé) et référencés par leur empreinte SHA-256 dans `experiments/videos.md`.
- Les données brutes d'expérience (CSV, JSON, exports de métriques) vont dans `experiments/runs/`, une fois compressées si besoin.
- Jamais de secret, de clé ou de certificat privé dans le dépôt.
