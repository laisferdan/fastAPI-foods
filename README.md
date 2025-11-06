# Rango's Week: API de Cardápio Inteligente

API backend (FastAPI) do projeto universitário “Rangos Week: Cardápio Inteligente”, voltado a facilitar o planejamento de marmitas saudáveis semanais, com recomendações personalizadas baseadas em perfil nutricional e histórico de consumo.

## Visão Geral
A plataforma auxilia trabalhadores na organização de refeições saudáveis para o dia a dia. Ela oferece opções de marmitas congeladas semanais, filtros personalizados (vegetariano, vegano, sem glúten, baixo sódio) e integração com IA para recomendações, seguindo boas práticas de UX e segurança (LGPD).

Principais objetivos do backend:
- Expor endpoints REST para usuários, perfis nutricionais e consumo diário.
- Calcular TDEE a partir do perfil (idade, peso, altura, nível de atividade) e sugerir refeições dentro de uma faixa de adequação calórica.
- Realizar recomendações content-based por categorias de consumo e ajustar por feedback (like/dislike).
- Proteger o acesso com JWT.

## Tecnologias
- FastAPI, Uvicorn
- SQLAlchemy 2.x, Alembic (migrations)
- Pydantic e pydantic-settings
- pytest, pytest-cov, taskipy, ruff
- python-jose (JWT)
- loguru (logs)

## Arquitetura (pastas principais)
- `fast_zero/app.py`: app FastAPI e inclusão de routers.
- `fast_zero/routes/`: rotas de usuários, receitas e recomendações.
- `fast_zero/models/`: ORM (Users, Recipes, UserProfile, ConsumptionLog, RecommendationFeedback).
- `fast_zero/schemas/`: contratos Pydantic com exemplos OpenAPI.
- `fast_zero/services/`: TDEE/BMR e recommendation engine.
- `fast_zero/repositories/`: consultas (histórico diário, feedbacks, etc.).
- `fast_zero/migration/`: migrações Alembic.
- `fast_zero/tests/`: testes unitários e de integração.

## Endpoints principais
- Recomendações (JWT obrigatório):
  - `GET /recomendacoes/recommend` → sugestões com adequação percentual.
  - `GET /recomendacoes/profile` → obter perfil.
  - `PUT /recomendacoes/profile` → criar/atualizar perfil.
  - `POST /recomendacoes/consumptions` → registrar consumo.
  - `POST /recomendacoes/feedback` → like/dislike.
- Usuários e receitas: endpoints de estudo já existentes.
- Analytics — Meus Registros (JWT obrigatório):
  - `GET /analytics/me/summary` → total de kcal, nº de refeições, total de alimentos.
  - `GET /analytics/me/calories-by-day` → série de kcal por dia no período.
  - `GET /analytics/me/distribution-by-meal` → kcal e percentual por tipo de refeição.
  - Parâmetros (query): `start_date`, `end_date`, `tz` (opcional; defaults a janela de 7 dias, UTC).

Quando faltar perfil, a API retorna: “Atualize suas informações pessoais para receber recomendações de refeição.”

## Requisitos e configuração
### Dependências de sistema
- Python 3.12+
- pipx (recomendado)

### Instalação
```bash
cd fast_zero
pip install pipx
pipx install poetry
poetry install
```

### Variáveis de ambiente
Crie `.env` em `fast_zero/` (ou defina no ambiente):
```
DATABASE_URL=sqlite:///./database.db
JWT_SECRET_KEY=troque-esta-chave-em-producao
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Banco e migrações
```bash
alembic upgrade head
```

### Executar a aplicação
```bash
poetry run task run
# ou
fastapi dev fast_zero/app.py
```
Docs interativas em `/docs` e `/redoc`.

## Testes e cobertura
```bash
poetry run task test
# ou
pytest -s -x --cov=fast_zero --cov-report=term-missing --cov-fail-under=90 -vv
```

Marcadores úteis:
- Rodar apenas testes rápidos (exclui perf): `pytest -q -m "not slow"`
- Incluir testes de performance: `pytest -q -m slow`

## Autenticação (JWT)
Gere um token com `sub = user_id` (ver `fast_zero/security/auth.py`) e envie:
```
Authorization: Bearer <token>
```

## Recomendações (resumo)
- BMR (Mifflin-St Jeor) e TDEE por perfil.
- Soma de kcal do dia e meta restante.
- Seleção dentro de ±10% da meta restante.
- Sinal por categorias recentes e ajuste por feedback.

## Analytics (resumo)
- Painel "Meus Registros" com métricas por usuário autenticado.
- Resumo do período: total de kcal, número de refeições, total de alimentos.
- Série diária: kcal por dia no intervalo.
- Distribuição por tipo de refeição: kcal e percentuais.

### Machine Learning
- Embeddings por calorias: o motor agora calcula um vetor 2D normalizado a partir de kcal e usa similaridade por cosseno entre a meta restante e as receitas para refinar o ranking. Peso inicial do sinal: `sim * 10.0` (ajustável).
- Implementação: `fast_zero/services/embeddings.py` (normalização, vetor 2D e cosine) e integração no `recommendation_engine.py`.
- Testes: `tests/services/test_embeddings.py` valida normalização, vetor 2D e similaridade.

### Big Data
- O escopo de dados é relacional e leve (SQLAlchemy + Alembic; tabelas: users, recipes, profiles, consumption_logs, feedback).

## Roadmap (resumo)
- Similaridade por ingredientes/embeddings.
- Otimizações de query/paginação.
- Integração com frontend Angular e chatbot.

## Licença
Projeto acadêmico para fins de estudo. Respeite a LGPD.
