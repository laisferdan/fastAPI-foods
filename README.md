# Rango's Week: API de Cardápio Inteligente

API backend (FastAPI) do projeto universitário “Rangos Week: Cardápio Inteligente”, voltado a facilitar o planejamento de marmitas saudáveis semanais, com recomendações personalizadas baseadas em perfil nutricional e histórico de consumo.

## Visão Geral
A plataforma auxilia trabalhadores na organização de refeições saudáveis para o dia a dia. Ela oferece opções de marmitas congeladas semanais, filtros personalizados (vegetariano, vegano, sem glúten, baixo sódio) e integração com IA para recomendações, seguindo boas práticas de UX e segurança (LGPD).

Principais objetivos do backend:
- Expor endpoints REST para usuários, autenticação, pratos, registros de refeições, perfis nutricionais e consumo diário.
- Calcular TDEE a partir do perfil (idade, peso, altura, nível de atividade) e sugerir refeições dentro de uma faixa de adequação calórica.
- Realizar recomendações content-based por categorias de consumo e ajustar por feedback (like/dislike).
- Proteger o acesso com JWT.

## Tecnologias
- FastAPI, Uvicorn
- SQLAlchemy 2.x, Alembic (migrations)
- Pydantic e pydantic-settings
- pytest, pytest-cov, taskipy, ruff
- PyJWT (JWT) e pwdlib + argon2 (hash de senha)
- loguru (logs)

## Arquitetura (pastas principais)
- `fast_zero/app.py`: app FastAPI, CORS e inclusão de routers.
- `fast_zero/routes/`: `auth`, `users`, `recipes`, `records`, `recommendations`, `analytics`.
- `fast_zero/models/`: ORM (Users, Recipes, UserProfile, ConsumptionLog, RecommendationFeedback).
- `fast_zero/schemas/`: contratos Pydantic com exemplos OpenAPI.
- `fast_zero/security/`: JWT (`auth.py`) e hash de senha (`passwords.py`).
- `fast_zero/seeds/`: seed idempotente dos pratos (`recipes.py` + `recipes.json`).
- `fast_zero/services/`: TDEE/BMR e recommendation engine.
- `fast_zero/repositories/`: consultas (histórico diário, feedbacks, etc.).
- `migration/`: migrações Alembic.
- `tests/`: testes unitários e de integração.

## Endpoints
Documentação interativa em `/docs` e `/redoc` (botão **Authorize** usa `/auth/token`).
Rotas de coleção não têm barra final (`/users`, `/recipes`, `/records`).

| Rota | Auth | Descrição |
|---|---|---|
| `POST /auth/token` | não | Login. Form `username` (= **e-mail**) e `password`. Devolve `{access_token, token_type}`. 401 se e-mail/senha errados. |
| `POST /users` | não | Cadastro `{username, email, password ≥ 8}`. 409 se username/e-mail já existem. |
| `GET /users/me` | sim | Usuário logado. |
| `PUT /users/me` | sim | Altera `username`, `email` e/ou `password` (todos opcionais). |
| `DELETE /users/me` | sim | Remove o usuário e seus registros, perfil e feedback. |
| `GET /recipes` | sim | Lista `{recipes: [...]}`. |
| `GET /recipes/{id}` | sim | Um prato. 404 se não existe. |
| `POST /recipes` | sim | Cria prato. |
| `PUT /recipes/{id}` | sim | Substitui o prato. |
| `DELETE /recipes/{id}` | sim | Remove. 409 se já foi registrado por algum usuário. |
| `GET /records?date=AAAA-MM-DD` | sim | Registros de refeição do usuário no dia: `{records: [...]}`. |
| `POST /records` | sim | Cria `{data, tipo_refeicao, recipe_id, quantidade_g}`. O `kcal` é calculado: `kcal_do_prato × quantidade_g ÷ gramas_do_prato`. |
| `PUT /records/{id}` | sim | Edita (recalcula kcal). |
| `DELETE /records/{id}` | sim | Exclui. |

- `tipo_refeicao`: `cafe_da_manha`, `almoço` ou `jantar`.
- Cada usuário só enxerga/edita os próprios registros (registro alheio devolve 404).
- Qualquer usuário autenticado pode alterar o catálogo `/recipes` (não há papéis/admin).
- Os registros ficam em `consumption_logs`, a mesma tabela usada por analytics e recomendações.

Outros módulos (JWT obrigatório):
- Recomendações:
  - `GET /recomendacoes/recommend` → sugestões com adequação percentual.
  - `GET /recomendacoes/profile` / `PUT /recomendacoes/profile` → perfil nutricional.
  - `POST /recomendacoes/consumptions` → registrar consumo (legado; prefira `POST /records`).
  - `POST /recomendacoes/feedback` → like/dislike.
- Analytics — Meus Registros:
  - `GET /analytics/me/summary` → total de kcal, nº de refeições, total de alimentos.
  - `GET /analytics/me/calories-by-day` → série de kcal por dia no período.
  - `GET /analytics/me/distribution-by-meal` → kcal e percentual por tipo de refeição.
  - Parâmetros (query): `start_date`, `end_date`, `tz` (opcional; defaults a janela de 7 dias, UTC).

Quando faltar perfil, a API retorna: “Atualize suas informações pessoais para receber recomendações de refeição.”

## Como rodar localmente
### Pré-requisitos
- Python 3.12 (o `poetry.lock` não instala em 3.14: `pydantic-core` fixado sem wheel para 3.14)
- Poetry

### 1. Instalar
```bash
cd fast_zero
poetry env use 3.12        # caminho do python 3.12, se preciso
poetry install
```

### 2. Variáveis de ambiente
Copie o exemplo e ajuste. **O `.env` não é versionado.**
```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # cole em JWT_SECRET_KEY
```
| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL SQLAlchemy. Padrão do exemplo: `sqlite:///database.db` (outro banco basta trocar a URL). |
| `JWT_SECRET_KEY` | Segredo de assinatura do JWT. **Obrigatório**, sem valor padrão. |
| `JWT_ALGORITHM` | Padrão `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token. Padrão `60`. |
| `CORS_ORIGINS` | Lista JSON de origens liberadas. Padrão `["http://localhost:4200"]`. |

### 3. Migrações e seed
```bash
poetry run alembic upgrade head
poetry run task seed        # insere os 11 pratos de rangos-week-ui/json/db.json
```
O seed é idempotente: insere só os pratos cujo `id` ainda não existe e nunca sobrescreve edições. Os ids 1 a 11 são os mesmos usados pela tela de detalhes da marmita no frontend. Os dados vêm de `fast_zero/seeds/recipes.json` (cópia fiel de `AlimentoOptions`, só trocando `codigo` por `id`).

### 4. Executar
```bash
poetry run task run         # http://localhost:8000
```
No Windows, se o `fastapi dev` falhar com `UnicodeEncodeError`, defina `PYTHONUTF8=1` antes (PowerShell: `$env:PYTHONUTF8=1`).

O frontend em desenvolvimento acessa a API pelo proxy do Angular (`/api` → `http://localhost:8000`); o CORS cobre chamadas diretas a partir de `http://localhost:4200`.

## Testes e cobertura
```bash
poetry run task lint
poetry run task test        # roda o lint antes; exige cobertura >= 90%
# ou
poetry run pytest -s -x --cov=fast_zero --cov-report=term-missing --cov-fail-under=90 -vv
```
Os testes usam SQLite em memória isolado (fixtures em `tests/conftest.py`); não tocam no `database.db`.

Marcadores úteis:
- Rodar apenas testes rápidos (exclui perf): `pytest -q -m "not slow"`
- Incluir testes de performance: `pytest -q -m slow`

## Autenticação (JWT)
1. `POST /auth/token` com `username` (e-mail) e `password` (form `application/x-www-form-urlencoded`).
2. Envie o token nas demais chamadas:
```
Authorization: Bearer <token>
```
O token carrega `sub` = id do usuário e `exp`; sem token, token inválido/expirado ou usuário removido devolvem 401. Senhas são guardadas com hash argon2.

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
- Papéis (admin) para escrita no catálogo de pratos.
- Limite de tentativas de login e refresh token.

## Licença
Projeto acadêmico para fins de estudo. Respeite a LGPD.
