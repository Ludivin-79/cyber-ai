# ADR 0001 — Choix de stack et d'architecture initiale

- **Statut** : accepté
- **Date** : 2026-11-05

## Contexte

Construire CYBER AI, plateforme IA cybersécurité/OSINT, déployable sur Proxmox,
infra de départ 24 Go RAM sans GPU, développée par une seule personne.

## Décisions

1. **Monolithe modulaire** (backend FastAPI) plutôt que microservices.
   Raison : complexité des microservices injustifiée pour un dev solo ; la
   modularité est assurée au niveau des packages Python. Réversible plus tard.

2. **Routeur + catalogue de compétences + sous-agents à la demande** plutôt que
   20 agents permanents concurrents. Raison : coût tokens/latence et complexité
   de coordination. L'esprit « spécialisation » est conservé.

3. **LLM : local (Ollama) pour le simple/confidentiel + API distante pour le
   raisonnement complexe**, via une couche d'abstraction unique (LiteLLM).
   Raison : 24 Go sans GPU ne permettent pas un grand modèle local performant ;
   l'abstraction garantit l'indépendance vis-à-vis d'un fournisseur unique.

4. **Capacités externes optionnelles et explicites** (`feature_flags`).
   Raison : exigence de ne jamais simuler une capacité indisponible.

## Conséquences

- MVP livrable rapidement, extensible par phases.
- SOCMINT restera limité (API fermées des plateformes ; pas de contournement).
- « Evolution Engine » = veille + éval + propositions sous validation humaine,
  pas d'auto-modification du modèle ni de la production.
