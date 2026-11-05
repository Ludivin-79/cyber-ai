---
name: backend-engineering
description: Guide le développement du backend FastAPI de CYBER AI — structure des routes, schémas Pydantic, async, accès base de données, gestion d'erreurs, tests. À utiliser pour tout ajout ou modification d'endpoint, de service ou de modèle de données côté backend.
---

# backend-engineering

## 1. Objectif
Produire un backend FastAPI propre, testé, asynchrone et cohérent, où chaque endpoint
a un contrat clair, une gestion d'erreurs explicite et des tests.

## 2. Périmètre
- **Couvre** : routes FastAPI, schémas Pydantic, services métier, accès Postgres/Redis/
  Qdrant/MinIO, auth, validation, gestion d'erreurs, tests backend.
- **Ne couvre pas** : l'abstraction des fournisseurs LLM (→ `llm-integration`), le frontend,
  les décisions d'architecture globale (→ `architecture-design`).

## 3. Compétences
- Routes `async` avec `APIRouter`, regroupées par domaine dans `app/api/`.
- Séparation **route ↔ service** : la route valide/sérialise, le service porte la logique.
- Schémas Pydantic distincts pour l'entrée (`...Create`) et la sortie (`...Read`).
- Accès DB asynchrone (SQLAlchemy async + asyncpg), migrations via Alembic.
- Tâches longues (OSINT) déportées vers un worker (Redis + arq/Celery), jamais dans la requête HTTP.

## 4. Outils utilisables
- `fastapi`, `pydantic`, `pydantic-settings`, `uvicorn`
- `sqlalchemy[asyncio]`, `asyncpg`, `alembic` (à ajouter en Phase 2)
- `pytest`, `httpx`/`TestClient`, `ruff`

## 5. Méthodes de travail
1. Définir le schéma Pydantic avant la route.
2. Écrire la route mince → déléguer au service.
3. Écrire au moins un test par endpoint (succès + un cas d'erreur).
4. `ruff check .` et `pytest -q` doivent passer avant commit.

## 6. Règles de sécurité
- **Aucun secret en dur** : tout via `app.core.config.get_settings()`.
- Valider et typer toutes les entrées (Pydantic) ; ne jamais faire confiance au client.
- Pas de SQL concaténé : requêtes paramétrées / ORM uniquement.
- Erreurs : ne jamais renvoyer de stack trace au client ; logger côté serveur, renvoyer
  un message neutre + code HTTP approprié.
- Endpoints sensibles protégés par auth + RBAC (dès la Phase 2).
- Fichiers uploadés : vérifier type/taille, traiter en zone isolée, jamais exécuter.

## 7. Procédures
### Ajouter un endpoint
1. Schéma(s) Pydantic dans `app/<domaine>/schemas.py`.
2. Logique dans `app/<domaine>/service.py`.
3. Route dans `app/api/<domaine>.py`, incluse via `app.include_router(...)` dans `main.py`.
4. Test dans `tests/test_<domaine>.py`.

### Ajouter une table
1. Modèle SQLAlchemy dans `app/<domaine>/models.py`.
2. `alembic revision --autogenerate -m "..."` puis `alembic upgrade head`.
3. Tester la migration sur une base jetable.

## 8. Exemples d'utilisation
- « Endpoint pour lister les conversations » → `ConversationRead`, service `list_conversations`,
  route `GET /conversations`, test succès + test non authentifié → 401.
- « Lancer une investigation OSINT » → la route crée une tâche (202 + id), le worker exécute,
  un endpoint `GET /investigations/{id}` renvoie l'état/résultat.

## 9. Références documentaires
- https://fastapi.tiangolo.com/
- https://docs.pydantic.dev/
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://owasp.org/API-Security/

## 10. Tests de validation
- [ ] `ruff check .` passe.
- [ ] `pytest -q` passe (≥ 1 test succès + 1 cas d'erreur par endpoint).
- [ ] Aucun secret ni requête SQL concaténée dans le diff.
- [ ] Les entrées sont validées par Pydantic ; les erreurs ne fuient pas de détails internes.
- [ ] Les tâches longues sont déportées hors de la requête HTTP.
