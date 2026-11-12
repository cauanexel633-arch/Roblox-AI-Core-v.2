# PARTH AI Server

Backend HTTP para o PARTH: IA (Roblox). Inclui geração estruturada de armas, mapas e eventos via OpenRouter, validação Pydantic, autenticação por `X-API-Key`, persistência opcional no Supabase e adaptador para Vercel Functions.

## Requisitos

- Python 3.11 ou superior
- Uma chave OpenRouter
- Uma chave de API própria do PARTH (`PARTH_API_KEY`)
- Supabase opcional para persistência

## Rodar localmente (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edite .env e preencha OPENROUTER_API_KEY e PARTH_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000/docs` para a documentação interativa e `http://127.0.0.1:8000/health` para verificar o serviço.

## Endpoints

| Método | Caminho | Autenticação | Descrição |
|---|---|---|---|
| GET | `/health` | Não | Saúde/configuração do serviço |
| GET | `/v1/models` | Sim | Modelo primário e fallbacks configurados |
| POST | `/v1/weapons/generate` | Sim | Gera uma definição de arma |
| GET | `/v1/weapons/{id}` | Sim | Consulta arma persistida no Supabase |
| POST | `/v1/maps/generate` | Sim | Gera especificação estruturada de mapa |
| POST | `/v1/events/generate` | Sim | Gera especificação estruturada de evento |

Todas as rotas protegidas exigem o header `X-API-Key: SUA_PARTH_API_KEY`.

### Exemplo: gerar arma

```powershell
$headers = @{ "X-API-Key" = "SUA_PARTH_API_KEY" }
$body = @{
  description = "Rifle futurista azul, rajada de três tiros, bom alcance e recarga lenta"
  player_id = "123456789"
  preferred_category = "rifle"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/v1/weapons/generate" -Headers $headers -ContentType "application/json" -Body $body
```

Categorias: `pistol`, `rifle`, `smg`, `shotgun`, `sniper`, `special`.
Raridades: `common`, `uncommon`, `rare`, `epic`, `legendary`, `mythic`.

### Exemplo: gerar mapa

```powershell
$body = @{ description = "Arena industrial compacta com cobertura e rotas laterais"; player_id = "123456789" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/v1/maps/generate" -Headers $headers -ContentType "application/json" -Body $body
```

### Exemplo: gerar evento

```powershell
$body = @{ description = "Chuva de meteoros com aviso antes do impacto"; mode = "crazy"; player_id = "123456789" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/v1/events/generate" -Headers $headers -ContentType "application/json" -Body $body
```

## OpenRouter

O serviço tenta primeiro `response_format: json_schema`. Se o provedor/modelo não aceitar esse formato, tenta `json_object` e valida a resposta localmente com Pydantic. O modelo padrão é `openrouter/free`; configure fallbacks em `OPENROUTER_FALLBACK_MODELS` separados por vírgula. A disponibilidade e suporte a saída estruturada variam por modelo/provedor.

## Supabase (opcional)

Crie as tabelas abaixo no SQL Editor do Supabase. O backend usa a API REST PostgREST e a Service Role Key somente no servidor. Nunca coloque essa chave no Roblox, no cliente ou no Git.

```sql
create table if not exists public.weapons (
  id uuid primary key, owner_user_id bigint not null default 0, name text not null,
  category text not null, rarity text not null, definition jsonb not null,
  asset_version text, created_at timestamptz not null default now()
);
create table if not exists public.weapon_requests (
  id text primary key, player_user_id bigint not null default 0,
  description text not null, status text not null, created_at timestamptz not null default now()
);
create table if not exists public.generated_maps (
  id uuid primary key, name text not null, definition jsonb not null, created_at timestamptz not null default now()
);
create table if not exists public.generated_events (
  id uuid primary key, name text not null, definition jsonb not null, created_at timestamptz not null default now()
);
```

Ative RLS nas tabelas se houver acesso de cliente, e não exponha a Service Role Key. Neste projeto, as operações são feitas pelo backend.

## Deploy na Vercel

1. Suba o conteúdo desta pasta para um repositório GitHub.
2. Na Vercel, importe o repositório.
3. Configure Root Directory como a pasta que contém `vercel.json`, `api/` e `app/` (na raiz se este projeto for o repositório).
4. Configure as variáveis de ambiente em Project Settings → Environment Variables: `ENVIRONMENT=production`, `PARTH_API_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_SITE_URL`, e as variáveis Supabase se for usar persistência.
5. Faça Deploy.
6. Teste `https://SEU-PROJETO.vercel.app/health` e depois `/docs`.

Não envie `.env` ao GitHub. Vercel recebe os valores em Environment Variables. Após alterar variáveis, faça um novo deploy para que sejam aplicadas.

## Roblox HttpService

- Ative `Allow HTTP Requests` nas configurações da experiência.
- Faça chamadas HTTP apenas em Scripts do servidor.
- Use `https://SEU-PROJETO.vercel.app/v1/weapons/generate`.
- Envie `X-API-Key` com o valor de `PARTH_API_KEY`.
- Nunca replique a chave em ReplicatedStorage ou LocalScripts.
- O cliente envia apenas a descrição e dados de solicitação; o servidor Roblox deve validar jogador, cooldown, tamanho da descrição e propriedade da arma.

Exemplo de body enviado pelo servidor Roblox:

```json
{
  "description": "Rifle de plasma azul com rajada",
  "player_id": "123456789",
  "request_id": "req-unique-001",
  "preferred_category": "rifle"
}
```

## Limitações importantes

- Este backend gera **definições JSON**, não executa scripts Luau nem cria/publica meshes 3D sozinho. O Roblox Weapon Builder deverá converter os identificadores de template/componentes em modelos aprovados no `ServerStorage`.
- A geração de mapas retorna uma especificação; o Map Builder no Roblox precisa montar estruturas da biblioteca aprovada.
- O Supabase é opcional em desenvolvimento; sem ele, as rotas de geração funcionam, mas não existe persistência durável nem consulta posterior de armas.
- Vercel Functions são stateless e orientadas a requisições HTTP. Não use memória do processo como fila persistente ou servidor de jogo contínuo. Para jobs longos, adicione posteriormente uma fila/workflow durável.
- A execução real de chamadas OpenRouter depende de chave válida, saldo/créditos ou disponibilidade de modelos gratuitos e limites do provedor.

## Segurança

- Use uma chave `PARTH_API_KEY` longa e aleatória.
- Rotacione imediatamente qualquer segredo que tenha sido publicado.
- Não registre chaves em logs.
- Não aceite scripts, URLs de assets ou IDs arbitrários retornados pela IA.
- Valide novamente a resposta no servidor Roblox antes de construir ou equipar uma arma.
