# BizuHub

Plataforma SaaS de recomendação de filmes, séries e livros com IA conversacional (backend FastAPI + LangChain, frontend Next.js).

## Segurança

- **Credenciais**: Todas as chaves e segredos vêm de variáveis de ambiente (`.env`). Nunca commitar `.env`.
- **Senhas**: Hash com bcrypt (passlib). Proteção contra timing attack no login.
- **JWT**: Acesso com token; expiração configurável. Token no frontend em `sessionStorage` (não `localStorage`).
- **CORS**: Origens permitidas definidas em `CORS_ORIGINS` (lista separada por vírgula).
- **Validação**: Entrada validada com Pydantic (backend) e limites de tamanho (ex.: chat 2000 caracteres).
- **Sanitização**: Texto do chat escapado para evitar XSS/injection.
- **Rate limiting**: Limite por IP em rotas de auth e chat (configurável).
- **Webhook Telegram**: Validação de secret (header) quando configurado.

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- Conta em [TMDb](https://www.themoviedb.org/settings/api), [Google Books](https://console.cloud.google.com/) (opcional), [Groq](https://console.groq.com/) (para chat com IA).

## Docker Compose

Sobe PostgreSQL, backend e frontend:

```bash
cp .env.example .env
# Edite .env e defina SECRET_KEY (mínimo 32 caracteres)
docker compose up -d
```

- **Frontend**: http://localhost:3000  
- **API (docs)**: http://localhost:8080/docs  
- **PostgreSQL**: serviço `db`, usuário/senha/db: `bizuhub` (altere em produção)

Os dados do PostgreSQL ficam no volume `postgres_data`. Rebuild: `docker compose up -d --build`.

## Configuração (local sem Docker)

1. Copie o arquivo de exemplo e defina pelo menos a `SECRET_KEY`:

   ```bash
   cp .env.example .env
   # Edite .env e defina SECRET_KEY (mínimo 32 caracteres).
   # Ex.: openssl rand -hex 32
   ```

2. Backend (na raiz do projeto):

   ```bash
   cd backend
   pip install -r requirements.txt
   # .env na raiz do projeto
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Frontend:

   ```bash
   cd frontend
   cp .env.local.example .env.local
   # Ajuste NEXT_PUBLIC_API_URL se necessário (padrão http://localhost:8000)
   npm install
   npm run dev
   ```

4. Acesse o frontend em `http://localhost:3000` e a API em `http://localhost:8000/docs`.

## Estrutura

- `backend/app`: FastAPI, rotas em `api/endpoints` e `api/bot_handlers`, modelos SQLAlchemy, serviços (recomendação, LLM).
- `frontend/app`: Next.js (App Router), páginas e serviço de API.
- `cursor.yaml`: Especificação do projeto (stack, segurança, endpoints).

## Endpoints principais

| Método | Caminho           | Descrição              |
|--------|-------------------|------------------------|
| POST   | /auth/signup      | Criar usuário          |
| POST   | /auth/login       | Obter JWT              |
| GET    | /recommendations  | Recomendações (auth)   |
| POST   | /interactions     | Registrar interação    |
| GET    | /history          | Histórico do usuário   |
| POST   | /chat             | Chat com IA            |
| POST   | /bot/webhook      | Webhook Telegram       |

## Licença

Uso interno / MVP.
