# CYBER AI

Plateforme d'intelligence artificielle conversationnelle, spécialisée en
**cybersécurité, OSINT, CTI, systèmes, réseaux, DevOps & Cloud**, déployable
sur infrastructure privée (Proxmox).

> État actuel : **Phase 0 — socle**. L'infrastructure, le backend FastAPI et
> le socle frontend sont en place et fonctionnels. Les modules métier (AI Core,
> OSINT, CTI, SOC…) sont développés dans les phases suivantes (voir la roadmap).

## Architecture (résumé)

- **Frontend** : Next.js + React + TypeScript + Tailwind
- **Backend** : Python + FastAPI (monolithe modulaire)
- **Données** : PostgreSQL · Redis · Qdrant (vectoriel) · MinIO (S3)
- **LLM** : abstraction multi-fournisseur — Ollama (local) + API distante (optionnelle)
- **Infra** : Docker Compose, reverse proxy HTTPS, déployable Proxmox

Le dossier d'architecture complet (14 points) se trouve dans l'espace projet.

## Démarrage rapide

### Prérequis
- Docker + Docker Compose
- (optionnel) [Ollama](https://ollama.com) sur l'hôte pour le LLM local

### Lancer
```bash
cp .env.example .env          # puis éditer si besoin (clés optionnelles)
docker compose up -d --build
```

- API : http://localhost:8000  (doc interactive : http://localhost:8000/docs)
- Front : http://localhost:3000
- Console MinIO : http://localhost:9001

### Développement backend (hors Docker)
```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest -q          # tests
ruff check .       # lint
```

### Développement frontend
```bash
cd frontend
npm install
npm run dev
```

## Principe de transparence des capacités

L'endpoint `GET /capabilities` et la page d'accueil affichent **uniquement**
ce qui est réellement activable selon les clés présentes. Aucune capacité
nécessitant une API/licence absente n'est présentée comme opérationnelle
(aucun résultat simulé).

## Roadmap

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Socle : infra, backend health, front | ✅ |
| 2 | Auth/MFA, chat multi-LLM, streaming, RAG, mémoire | à venir |
| 3 | AI Core, orchestrateur, compétences, recherche web | à venir |
| 4 | OSINT (domaines/IP/certs), CTI, logs, corrélation, rapports | à venir |
| 5 | AI Evolution Engine (veille, éval, dashboard) | à venir |
| 6 | Industrialisation : tests, hardening, monitoring, Proxmox | à venir |

## Sécurité

Conçu « security by design » : authentification + MFA, RBAC, secrets hors code,
exécution des outils en sandbox, contenu externe traité comme donnée non fiable
(protection contre l'injection de prompt). Les fonctions offensives sont
strictement encadrées (autorisation + périmètre explicites).

## Licence

Projet personnel — à définir.
