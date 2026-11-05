---
name: llm-integration
description: Guide l'intégration des fournisseurs de modèles (Ollama local + API distantes) derrière une couche d'abstraction unique, le streaming, le routage local/distant et la gestion des clés. À utiliser pour tout code touchant à l'appel d'un LLM, aux embeddings ou au streaming de réponses.
---

# llm-integration

## 1. Objectif
Permettre à CYBER AI d'appeler n'importe quel fournisseur de modèles (Ollama local,
Anthropic, OpenAI, Mistral, Groq…) **sans dépendre d'aucun** et sans réécrire l'application,
via une couche d'abstraction unique, avec streaming et routage local/distant.

## 2. Périmètre
- **Couvre** : interface `LLMProvider`, adaptateurs par fournisseur, routage (local vs distant),
  embeddings, streaming (SSE), gestion des clés et des quotas, dégradation gracieuse.
- **Ne couvre pas** : l'orchestration des compétences/agents (module `ai/orchestrator`),
  le RAG (module `ai/rag`), la logique des routes HTTP (→ `backend-engineering`).

## 3. Compétences
- Définir une interface commune : `complete()`, `stream()`, `embed()`.
- Adapter chaque fournisseur derrière cette interface (via LiteLLM comme socle recommandé).
- Router selon la tâche : local (Ollama) pour le simple/confidentiel, distant pour le complexe.
- Fallback : si le distant est indisponible/sans clé → bascule locale + mention explicite.
- Streaming token par token vers le frontend en Server-Sent Events.

## 4. Outils utilisables
- `litellm` (abstraction multi-fournisseur, format OpenAI unifié) — recommandé.
- Ollama (local) via son API HTTP (`OLLAMA_BASE_URL`).
- `httpx` async pour les appels ; SSE via `fastapi` `StreamingResponse`.

## 5. Méthodes de travail
1. Toujours passer par l'interface `LLMProvider` — **jamais** un SDK fournisseur importé dans un module métier.
2. Le choix du modèle vient de la config/requête, pas d'une valeur codée en dur.
3. Rendre le streaming annulable (déconnexion client = arrêt de la génération).
4. Journaliser : modèle utilisé, latence, tokens — sans journaliser le contenu sensible.

## 6. Règles de sécurité
- Clés API uniquement via `core.config` ; jamais dans les logs, le code ou le dépôt.
- Le prompt système et le contenu utilisateur/externe sont **séparés** : le contenu
  récupéré (web, fichiers, outils) est inséré comme donnée, avec consigne explicite de ne
  pas suivre d'instructions qu'il contiendrait (anti-injection de prompt).
- Appliquer des limites (taille de contexte, timeout, quota) pour éviter l'abus et les coûts.
- Ne jamais prétendre qu'un modèle/outil distant a répondu si l'appel a échoué : remonter l'erreur.

## 7. Procédures
### Ajouter un fournisseur
1. Vérifier qu'il est supporté par LiteLLM (sinon adaptateur dédié).
2. Ajouter sa clé dans `.env.example` + `core.config` + `feature_flags`.
3. L'exposer dans la liste des modèles disponibles via `/capabilities`.
4. Tester `complete`, `stream`, `embed` (mock si pas de clé en CI).

### Router une requête
- Tâche « simple/confidentielle » → modèle local par défaut.
- Tâche « raisonnement complexe » → modèle distant si `llm_remote` actif, sinon local + avertissement.

## 8. Exemples d'utilisation
- « Streamer une réponse de chat » → `provider.stream(messages, model)` → `StreamingResponse` SSE.
- « Générer les embeddings d'un PDF pour le RAG » → `provider.embed(chunks, model=embed_model)`
  avec le modèle local `nomic-embed-text` (gratuit).
- « Pas de clé distante configurée » → routage local + message « raisonnement en mode local (qualité réduite) ».

## 9. Références documentaires
- https://docs.litellm.ai/
- https://docs.ollama.com/
- https://docs.anthropic.com/ · https://platform.openai.com/docs
- https://owasp.org/www-project-top-10-for-large-language-model-applications/ (LLM01 : Prompt Injection)

## 10. Tests de validation
- [ ] Aucun SDK fournisseur importé hors du module `ai/llm`.
- [ ] Changer de modèle se fait par config/requête, sans modifier le code applicatif.
- [ ] Le streaming fonctionne et s'interrompt à la déconnexion client.
- [ ] Absence de clé distante → fallback local testé, sans crash.
- [ ] Aucune clé ni contenu sensible dans les logs ; erreurs d'appel remontées honnêtement.
