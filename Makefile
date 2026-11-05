.PHONY: help up down logs backend-dev backend-test frontend-dev lint

help:
	@echo "CYBER AI — commandes"
	@echo "  make up            Démarre toute l'infra (docker compose)"
	@echo "  make down          Arrête l'infra"
	@echo "  make logs          Suit les logs"
	@echo "  make backend-dev   Lance le backend en local (hors Docker)"
	@echo "  make backend-test  Lance les tests backend"
	@echo "  make frontend-dev  Lance le frontend en local"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && pytest -q

frontend-dev:
	cd frontend && npm run dev
