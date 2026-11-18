# Sistema Web de Vendas e Estoque para Distribuidora de Carvao

Aplicacao online com backend FastAPI, frontend React/Vite e suporte a PostgreSQL em producao. Em desenvolvimento, roda com SQLite automaticamente.

## Recursos entregues

- Login JWT com perfis `admin`, `gerente` e `vendedor`.
- CRUD de produtos, com tipos separados para saco fechado, embalagem vazia e outros.
- Entrada, saida, ajuste e devolucao de estoque com historico e auditoria.
- Cadastro de vendedores com usuario de acesso, WhatsApp, meta e comissao.
- Lancamento de vendas mobile-first com baixa automatica de estoque.
- Dashboard com estoque atual, total vendido, ranking, comissao e filtros.
- Exportacao de vendas em Excel e PDF.
- Configuracao de alertas com modo `mock`, Telegram Bot e estrutura para Meta, Z-API ou Twilio.
- O sistema cria somente o primeiro administrador quando o banco ainda nao possui usuarios.

## Primeiro administrador e dados de demonstracao

Defina uma senha forte antes da primeira inicializacao. O sistema recusa iniciar sem essa variavel quando nao ha usuarios cadastrados:

```env
ADMIN_INITIAL_PASSWORD=gere-uma-senha-unica-e-longa
ADMIN_INITIAL_EMAIL=admin@suaempresa.com
ADMIN_INITIAL_NAME=Administrador
```

Dados de demonstracao permanecem desligados por padrao. Para um ambiente local descartavel, habilite-os explicitamente e informe outra senha:

```env
SEED_DEMO=true
DEMO_USER_PASSWORD=senha-apenas-para-desenvolvimento
```

## Segredo JWT

`JWT_SECRET` e obrigatoria em todos os ambientes. Gere um valor aleatorio forte e armazene-o somente no gerenciador de variaveis do ambiente:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Depois, configure o resultado sem publica-lo no repositorio:

```env
JWT_SECRET=valor-gerado-fora-do-repositorio
```

## CORS e sessao entre Vercel e Railway

Como o frontend e a API estao em dominios diferentes, configure as duas variaveis no Railway. Em producao, `CORS_ORIGINS` deve conter **apenas** o dominio exato publicado na Vercel, sem barra final, sem `*` e sem lista de dominios.

```env
ENVIRONMENT=production
CORS_ORIGINS=https://seu-projeto.vercel.app
```

No desenvolvimento local, informe explicitamente a origem usada pelo Vite:

```env
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
```

## Rodar localmente

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`.

## Rodar com Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:8080`
- Backend/API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Variaveis de ambiente

Copie `.env.example` para `.env` no backend ou configure no provedor de hospedagem.

Para PostgreSQL, use:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/banco
```

## WhatsApp

O modo padrao `mock` registra as mensagens no console. Para provedor real, configure:

- `WHATSAPP_PROVIDER=meta`, `zapi` ou `twilio`
- `WHATSAPP_API_URL`
- `WHATSAPP_TOKEN`
- `MANAGER_WHATSAPP`

O endpoint atual envia `{ "to": "...", "message": "..." }` com bearer token. Caso o provedor escolhido tenha formato diferente, ajuste `backend/app/whatsapp.py`.

### Telegram

Crie um bot com o `@BotFather`, envie `/start` para o bot e obtenha o `chat.id` em `https://api.telegram.org/botSEU_TOKEN/getUpdates`. Na tela de alertas, selecione `Telegram Bot`, informe o token e o Chat ID do gestor ou grupo. O Telegram envia os alertas ao chat configurado; ele nao localiza vendedores pelo numero de telefone.

## Backup e deploy

Em producao, use PostgreSQL gerenciado com backup automatico no Railway, Render ou VPS. Exija HTTPS no proxy ou plataforma de deploy e nunca publique o `.env` real.
