# MoveMind AI — Next Phase Architecture Plan

> Version: 1.0
> Date: April 2026
> Status: Draft — high-level decisions only, detail docs to follow
> Audience: Engineering team — reference for deep-dive design sessions

---

## 1. Where We Are Today (Current State Summary)

### What is built and working

```
Frontend (React 19 + MUI v6 + RSBuild)
  └── Chat UI with SSE streaming, agent pipeline viz, source panel

Backend (FastAPI + LangGraph)
  └── Fixed graph: classify → rewrite → resolve_context → retrieve → rerank → generate → classify_issue
  └── Pinecone (single namespace: cms3-logs)
  └── FlashRank reranker (ms-marco-TinyBERT)
  └── Multi-model routing: fast (gpt-4o-mini) / smart (gpt-4o) / thinking (o3)
  └── MemorySaver (in-memory checkpointer — per thread, per process, lost on restart)
  └── LangSmith observability + eval pipeline
  └── SSE streaming via POST /api/v1/chat

Infrastructure
  └── Docker Compose: backend:8000 + frontend:3000
  └── No database (no PostgreSQL, no Redis, nothing persistent)
  └── No auth
  └── No file storage
```

### What is NOT built yet

| Gap | Impact |
|-----|--------|
| **No persistent chat history** | Conversations lost on server restart; no cross-session continuity |
| **No file/image upload** | Users can't attach logs, screenshots, or documents |
| **No database** | No user accounts, no project records, no conversation storage |
| **No auth** | Single-user system; no multi-tenancy |
| **No MCP integration** | No code context grounding |
| **No Jira integration** | Planned in SOW but not started |
| **MemorySaver is in-memory only** | Volatile — all session state lost on restart |

---

## 2. Next Phase Goal

**Make MoveMind production-usable for a small team** — persistent conversations, file uploads, and the foundation for MCP integration. Not yet multi-tenant SaaS, but a solid single-team deployment.

This is the bridge between "working demo" and "deployable product".

---

## 3. Architecture Decisions (High Level)

### 3.1 — Persistent Chat History

**Problem:** `MemorySaver()` stores state in a Python dict. Server restarts wipe everything. Users can't see past conversations or resume sessions.

**Decision: PostgreSQL + LangGraph PostgresSaver**

```
                    ┌─────────────┐
  User sends msg →  │  FastAPI     │
                    │  /api/v1/chat│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  LangGraph  │
                    │  Agent      │
                    │             │
                    │  checkpointer = PostgresSaver(conn)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │             │
                    │  tables:    │
                    │  - checkpoints (LangGraph managed)
                    │  - conversations (our metadata)
                    │  - messages (our query layer)
                    └─────────────┘
```

**Key decisions:**

- **LangGraph PostgresSaver** replaces `MemorySaver` — gives us durable checkpoints with zero graph code changes
- **Separate `conversations` + `messages` tables** alongside LangGraph's checkpoint tables — for our own query/display needs (conversation list, search, metadata)
- **PostgreSQL over MongoDB** — structured data, LangGraph has native Postgres support, future multi-tenant queries are relational
- **No Redis for now** — not enough traffic to justify a caching layer yet; add when latency demands it

**Schema sketch:**

```sql
-- Our application tables (not LangGraph managed)
conversations (
  id UUID PK,
  session_id TEXT UNIQUE,       -- maps to LangGraph thread_id
  title TEXT,                    -- auto-generated from first message
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  metadata JSONB                 -- project_id, user_id (future), tags
)

messages (
  id UUID PK,
  conversation_id UUID FK,
  role TEXT,                     -- 'human' | 'ai'
  content TEXT,
  sources JSONB,                 -- retrieved docs/sources
  agent_metadata JSONB,          -- issue_type, confidence, node timings
  attachments JSONB,             -- file refs (Phase: file upload)
  created_at TIMESTAMPTZ
)
```

**API changes:**

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/conversations` | List past conversations (paginated) |
| `GET /api/v1/conversations/{id}` | Get full conversation with messages |
| `DELETE /api/v1/conversations/{id}` | Delete a conversation |
| `PATCH /api/v1/conversations/{id}` | Update title/metadata |
| `POST /api/v1/chat` | Existing — now persists automatically |

**Frontend changes:**
- Sidebar with conversation history list
- Resume conversation by selecting from list
- New conversation button

---

### 3.2 — File & Image Upload

**Problem:** Users need to attach log files, screenshots, error traces, and documents for the agent to analyse.

**Decision: Local file storage (S3-compatible interface) + multimodal message support**

```
                    ┌─────────────┐
  User uploads →    │  FastAPI     │
  file/image        │  /api/v1/   │
                    │  upload      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐      ┌──────────────┐
                    │  File       │ ───→ │  Local Disk   │  (Phase 1)
                    │  Service    │      │  or MinIO     │
                    │             │      │  or S3        │  (Phase 2+)
                    └──────┬──────┘      └──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Processing │
                    │  Pipeline   │
                    │             │
                    │  - Images: pass to GPT-4o vision
                    │  - Log files: chunk + index
                    │  - PDF/docs: extract text
                    └─────────────┘
```

**Key decisions:**

- **Two-phase approach:**
  - **Phase A (immediate):** File upload API → local disk storage → file reference in message → agent receives file content as context
  - **Phase B (later):** MinIO/S3 for production, virus scanning, size limits, retention policies

- **Supported file types (Phase A):**
  - **Images** (png, jpg, webp) → GPT-4o vision via multimodal messages
  - **Log files** (json, txt, csv) → parsed + injected into agent context
  - **Documents** (pdf, md) → text extraction → agent context

- **Upload flow:**
  1. Frontend uploads file via `POST /api/v1/upload` (multipart/form-data)
  2. Backend saves to disk, returns `file_id` + `file_url`
  3. Frontend sends chat message with `attachments: [{ file_id, type }]`
  4. Agent receives file content: images as base64 in multimodal message, text files as injected context

- **Max file size:** 10MB per file (configurable)
- **Storage path:** `data/uploads/{conversation_id}/{file_id}.{ext}`

**API:**

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/upload` | Upload file, returns file_id + metadata |
| `GET /api/v1/files/{file_id}` | Retrieve/serve uploaded file |
| `DELETE /api/v1/files/{file_id}` | Delete uploaded file |

---

### 3.3 — MCP Server Integration

**Problem:** The agent answers based only on log data. Grounding answers in source code (which function emits this log? what changed recently?) dramatically improves debugging quality.

**Decision: MoveMind as MCP Client, connecting to user-provided MCP servers**

```
┌───────────────────────────────────────────────┐
│  MoveMind Backend                              │
│                                                │
│  Agent Loop                                    │
│   │                                            │
│   ├── search_logs()      → Pinecone            │
│   ├── get_code_context() → MCP Client ─────────┼──→ User's MCP Server (GitHub, etc.)
│   ├── get_recent_changes()→ MCP Client ────────┼──→ User's MCP Server
│   └── search_docs()      → MCP Client ─────────┼──→ Docs MCP Server (optional)
│                                                │
│  MCP Client Manager                            │
│   ├── Connection pool per configured server    │
│   ├── Health checks                            │
│   ├── Tool discovery (list_tools on connect)   │
│   └── Config: mcp_servers.yaml                 │
└───────────────────────────────────────────────┘
```

**Key decisions:**

- **MoveMind is an MCP client, NOT a server** — we consume tools from external MCP servers
- **Configuration-driven:** users register MCP server endpoints via config (later via UI)
- **Multiple MCP servers:** architecture supports N servers, each providing different tool sets
- **Tool mapping:** MCP tools are registered as LangGraph tools — agent can call them like any other tool
- **Phased rollout:**
  - **Phase A:** Single MCP server connection, manual config in `mcp_servers.yaml`
  - **Phase B:** Dynamic MCP server management via API, UI for adding/removing servers
  - **Phase C:** Tool approval flow (user confirms which MCP tools the agent can use)

**MCP config format:**

```yaml
# config/mcp_servers.yaml
servers:
  - name: "github-codebase"
    transport: "stdio"                    # or "sse" for remote
    command: "npx @modelcontextprotocol/server-github"
    args: ["--repo", "acme/cms3"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"     # from .env
    enabled: true

  - name: "filesystem-docs"
    transport: "stdio"
    command: "npx @modelcontextprotocol/server-filesystem"
    args: ["/path/to/docs"]
    enabled: true
```

**Agent integration:**

```
Agent system prompt includes:
  "You have access to code context tools via MCP. Use get_code_context
   when the user asks about WHY something happens in code, or when
   you need to correlate a log event with its source."

MCP tools are dynamically discovered and registered as LangGraph tools.
The agent doesn't know or care that they come from MCP.
```

---

### 3.4 — Infrastructure Changes

**Current docker-compose.yml adds PostgreSQL + optional MinIO:**

```
┌─────────────────────────────────────────────┐
│  Docker Compose                              │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Frontend │  │ Backend  │  │ PostgreSQL│  │
│  │ :3000    │  │ :8000    │  │ :5432     │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                                              │
│  (Phase B)                                   │
│  ┌──────────┐  ┌──────────┐                  │
│  │ MinIO    │  │ Redis    │                  │
│  │ :9000    │  │ :6379    │                  │
│  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────┘
```

**Key additions:**
- **PostgreSQL** — conversations, messages, LangGraph checkpoints, future user/project data
- **Alembic** — database migrations (Python, integrates with SQLAlchemy)
- **MinIO** (Phase B) — S3-compatible file storage for uploads
- **Redis** (Phase B) — session cache, rate limiting

---

## 4. Phased Action Plan

### Phase N1 — Database + Persistent Chat (2–3 weeks)

> Priority: **Highest** — everything else depends on this

| # | Task | Effort |
|---|------|--------|
| 1 | Add PostgreSQL to docker-compose.yml | 1 day |
| 2 | Set up SQLAlchemy + Alembic in backend | 1 day |
| 3 | Create `conversations` + `messages` tables + migrations | 1 day |
| 4 | Replace `MemorySaver()` with `PostgresSaver` in agent.py | 1 day |
| 5 | Implement conversation CRUD API endpoints | 2 days |
| 6 | Message persistence middleware (save human + AI messages) | 2 days |
| 7 | Frontend: conversation sidebar + history list | 3 days |
| 8 | Frontend: resume conversation flow | 2 days |
| 9 | Test: conversation persists across server restarts | 1 day |

**Milestone:** User can see past conversations, resume them, and nothing is lost on restart.

---

### Phase N2 — File & Image Upload (2 weeks)

> Priority: **High** — users need to attach evidence

| # | Task | Effort |
|---|------|--------|
| 1 | File upload API endpoint (multipart/form-data) | 1 day |
| 2 | File storage service (local disk, abstracted interface) | 1 day |
| 3 | File metadata tracking in PostgreSQL | 1 day |
| 4 | Image handling: base64 → GPT-4o vision multimodal message | 2 days |
| 5 | Log file handling: parse JSON/CSV/text → inject as context | 2 days |
| 6 | Frontend: drag-and-drop file upload in chat input | 2 days |
| 7 | Frontend: image/file preview in messages | 1 day |
| 8 | File size/type validation + error handling | 1 day |

**Milestone:** User can upload a screenshot or log file and the agent analyses it.

---

### Phase N3 — MCP Integration (2–3 weeks)

> Priority: **Medium-High** — differentiating feature

| # | Task | Effort |
|---|------|--------|
| 1 | MCP client library integration (Python MCP SDK) | 2 days |
| 2 | MCP server config loader (`mcp_servers.yaml`) | 1 day |
| 3 | Connection manager (connect, health check, reconnect) | 2 days |
| 4 | Dynamic tool discovery + registration as LangGraph tools | 2 days |
| 5 | Agent prompt update for code context tools | 1 day |
| 6 | Test with GitHub MCP server (code search, file read) | 2 days |
| 7 | Test with filesystem MCP server (local docs) | 1 day |
| 8 | Error handling: MCP server down, tool timeout, auth failure | 2 days |

**Milestone:** Agent can answer "which function emits this log line?" by querying connected MCP server.

---

### Phase N4 — Production Hardening (2 weeks)

> Priority: **Medium** — required before real users

| # | Task | Effort |
|---|------|--------|
| 1 | Basic auth (API key or JWT — single team) | 2 days |
| 2 | Rate limiting on chat + upload endpoints | 1 day |
| 3 | Health checks for all services (Postgres, Pinecone, MCP) | 1 day |
| 4 | Graceful error handling + user-facing error messages | 2 days |
| 5 | Structured logging (JSON) for backend | 1 day |
| 6 | Environment-based config (dev/staging/prod) | 1 day |
| 7 | CI pipeline updates for new dependencies | 1 day |
| 8 | README + deployment guide update | 1 day |

**Milestone:** System is deployable for a small team with basic security and reliability.

---

## 5. Technology Choices Summary

| Concern | Decision | Rationale |
|---------|----------|-----------|
| **Database** | PostgreSQL 16 | LangGraph native support, relational queries, battle-tested |
| **ORM** | SQLAlchemy 2.0 + Alembic | Python standard, async support |
| **Chat persistence** | PostgresSaver (LangGraph) + custom tables | Checkpoints via LangGraph, metadata via our schema |
| **File storage** | Local disk → MinIO/S3 | Start simple, swap later without code changes |
| **MCP client** | `mcp` Python SDK | Official SDK, handles stdio + SSE transport |
| **Auth (Phase N4)** | JWT (python-jose) | Stateless, standard, works with future OAuth |
| **Migration** | Alembic | Integrated with SQLAlchemy, version-controlled |

---

## 6. What This Does NOT Cover (Deferred)

These are in the SOW but not in this next-phase plan:

| Item | Deferred to |
|------|-------------|
| Multi-tenancy (orgs, projects) | SOW Phase 3 |
| Descriptor-driven generics | SOW Phase 1 |
| Tool-calling ReAct agent | SOW Phase 2 |
| Jira integration | SOW Phase 0 (separate track) |
| Connector layer (S3, CloudWatch) | SOW Phase 3+ |
| Profiler Agent | SOW Phase 2 |
| Pricing / billing | SOW Phase 3 |

---

## 7. Dependency Graph

```
Phase N1 (Database + Chat Persistence)
    │
    ├──→ Phase N2 (File Upload — needs DB for file metadata)
    │         │
    │         └──→ Phase N3 (MCP — independent but benefits from file handling patterns)
    │
    └──→ Phase N4 (Production Hardening — needs all features stable)
              │
              └──→ SOW Phase 0 (Jira + Technical Report) — can start in parallel
```

---

## 8. Open Questions for Deep-Dive Sessions

| # | Question | Needs decision before |
|---|----------|----------------------|
| 1 | PostgreSQL hosting: Docker-managed vs. managed service (Supabase/Neon/RDS)? | Phase N1 start |
| 2 | File upload size limits and retention policy? | Phase N2 start |
| 3 | Which MCP servers to support first? (GitHub, filesystem, custom?) | Phase N3 start |
| 4 | Should MCP tool access require explicit user approval per tool? | Phase N3 design |
| 5 | Auth model: API key (simple) vs. JWT (standard) vs. OAuth (future-proof)? | Phase N4 start |
| 6 | Should we migrate to ReAct agent (SOW Phase 2) before or after this next phase? | Architecture review |
| 7 | Frontend state management: keep ChatContext or introduce something more robust? | Phase N1 frontend work |

---

_Next step: Pick a phase, create a detailed design doc, and start building. Recommend starting with **Phase N1** — database + persistent chat is the foundation for everything else._
