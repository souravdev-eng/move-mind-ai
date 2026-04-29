# MoveMind AI — Next Phase Tracker

> Last updated: 2026-04-28
> Source: [next-phase-plan.md](../../../docs/architecture/next-phase-plan.md)

**Legend:** 🔴 Not Started · 🟡 In Progress · 🟢 Done · ⏸️ Blocked

---

## Overall Progress

| Phase                               | Status         | Progress |
| ----------------------------------- | -------------- | -------- |
| **N1 — Database + Persistent Chat** | � Done         | 9 / 9    |
| **N2 — File & Image Upload**        | 🔴 Not Started | 0 / 8    |
| **N3 — MCP Integration**            | 🔴 Not Started | 0 / 8    |
| **N4 — Production Hardening**       | 🔴 Not Started | 0 / 8    |

---

## Phase N1 — Database + Persistent Chat (2–3 weeks)

> Priority: **Highest** — everything else depends on this
> Milestone: User can see past conversations, resume them, and nothing is lost on restart.

| #   | Task                                                      | Effort | Status  | Notes                                                                                                           |
| --- | --------------------------------------------------------- | ------ | ------- | --------------------------------------------------------------------------------------------------------------- | --- |
| 1   | Add PostgreSQL + Redis to docker-compose.yml              | 1 day  | � Done  | Added Postgres 16 + Redis 7 with healthchecks, named volumes, env-var defaults                                  |
| 2   | Set up SQLAlchemy + Alembic in backend                    | 1 day  | 🟢 Done | SQLAlchemy 2.0 async + Alembic configured with DATABASE_ASYNC_URL                                               |
| 3   | Create `conversations` + `messages` tables + migrations   | 1 day  | 🟢 Done | Models in app/models/conversation.py; migration 001 created; runs on startup                                    |
| 4   | Replace `MemorySaver()` with `PostgresSaver` in agent.py  | 1 day  | 🟢 Done | AsyncPostgresSaver via psycopg pool; autocommit setup for DDL                                                   |
| 5   | Implement conversation CRUD API endpoints                 | 2 days | 🟢 Done | Async SQLAlchemy session; Pydantic schemas; full CRUD routes at /api/v1/conversations                           |
| 6   | Message persistence middleware (save human + AI messages) | 2 days | 🟢 Done | Service in app/services/message_persistence.py; saves on chat/stream with auto-create conversation              |
| 7   | Frontend: conversation sidebar + history list             | 3 days | 🟢 Done | ConversationSidebar component with list API; integrated into InvestigatePage layout                             |     |
| 8   | Frontend: resume conversation flow                        | 2 days | 🟢 Done | setSessionId in useChatStream; handleSelectConversation/handleNewConversation handlers (full history load TODO) |     |
| 9   | Test: conversation persists across server restarts        | 1 day  | � Done  | Manual verification: chat → sidebar → restart → verify persists                                                 |     |

---

## Phase N2 — File & Image Upload (2 weeks)

> Priority: **High** — users need to attach evidence
> Milestone: User can upload a screenshot or log file and the agent analyses it.
> Depends on: Phase N1 (needs DB for file metadata)

| #   | Task                                                       | Effort | Status         | Notes |
| --- | ---------------------------------------------------------- | ------ | -------------- | ----- |
| 1   | File upload API endpoint (multipart/form-data)             | 1 day  | 🔴 Not Started |       |
| 2   | File storage service (local disk, abstracted interface)    | 1 day  | 🔴 Not Started |       |
| 3   | File metadata tracking in PostgreSQL                       | 1 day  | 🔴 Not Started |       |
| 4   | Image handling: base64 → GPT-4o vision multimodal message  | 2 days | 🔴 Not Started |       |
| 5   | Log file handling: parse JSON/CSV/text → inject as context | 2 days | 🔴 Not Started |       |
| 6   | Frontend: drag-and-drop file upload in chat input          | 2 days | 🔴 Not Started |       |
| 7   | Frontend: image/file preview in messages                   | 1 day  | 🔴 Not Started |       |
| 8   | File size/type validation + error handling                 | 1 day  | 🔴 Not Started |       |

---

## Phase N3 — MCP Integration (2–3 weeks)

> Priority: **Medium-High** — differentiating feature
> Milestone: Agent can answer "which function emits this log line?" by querying connected MCP server.
> Depends on: Phase N1 (independent but benefits from file handling patterns)

| #   | Task                                                        | Effort | Status         | Notes |
| --- | ----------------------------------------------------------- | ------ | -------------- | ----- |
| 1   | MCP client library integration (Python MCP SDK)             | 2 days | 🔴 Not Started |       |
| 2   | MCP server config loader (`mcp_servers.yaml`)               | 1 day  | 🔴 Not Started |       |
| 3   | Connection manager (connect, health check, reconnect)       | 2 days | 🔴 Not Started |       |
| 4   | Dynamic tool discovery + registration as LangGraph tools    | 2 days | 🔴 Not Started |       |
| 5   | Agent prompt update for code context tools                  | 1 day  | 🔴 Not Started |       |
| 6   | Test with GitHub MCP server (code search, file read)        | 2 days | 🔴 Not Started |       |
| 7   | Test with filesystem MCP server (local docs)                | 1 day  | 🔴 Not Started |       |
| 8   | Error handling: MCP server down, tool timeout, auth failure | 2 days | 🔴 Not Started |       |

---

## Phase N4 — Production Hardening (2 weeks)

> Priority: **Medium** — required before real users
> Milestone: System is deployable for a small team with basic security and reliability.
> Depends on: All previous phases stable

| #   | Task                                                     | Effort | Status         | Notes |
| --- | -------------------------------------------------------- | ------ | -------------- | ----- |
| 1   | Basic auth (API key or JWT — single team)                | 2 days | 🔴 Not Started |       |
| 2   | Rate limiting on chat + upload endpoints                 | 1 day  | 🔴 Not Started |       |
| 3   | Health checks for all services (Postgres, Pinecone, MCP) | 1 day  | 🔴 Not Started |       |
| 4   | Graceful error handling + user-facing error messages     | 2 days | 🔴 Not Started |       |
| 5   | Structured logging (JSON) for backend                    | 1 day  | 🔴 Not Started |       |
| 6   | Environment-based config (dev/staging/prod)              | 1 day  | 🔴 Not Started |       |
| 7   | CI pipeline updates for new dependencies                 | 1 day  | 🔴 Not Started |       |
| 8   | README + deployment guide update                         | 1 day  | 🔴 Not Started |       |

---

## Open Questions

| #   | Question                                                | Status  | Decision |
| --- | ------------------------------------------------------- | ------- | -------- |
| 1   | PostgreSQL hosting: Docker-managed vs. managed service? | 🔴 Open | —        |
| 2   | File upload size limits and retention policy?           | 🔴 Open | —        |
| 3   | Which MCP servers to support first?                     | 🔴 Open | —        |
| 4   | Should MCP tool access require explicit user approval?  | 🔴 Open | —        |
| 5   | Auth model: API key vs. JWT vs. OAuth?                  | 🔴 Open | —        |
| 6   | Migrate to ReAct agent before or after next phase?      | 🔴 Open | —        |
| 7   | Frontend state management: keep ChatContext or upgrade? | 🔴 Open | —        |

---

## Dependency Graph

```
Phase N1 (Database + Chat Persistence)  🔴
    │
    ├──→ Phase N2 (File Upload)          🔴
    │         │
    │         └──→ Phase N3 (MCP)        🔴
    │
    └──→ Phase N4 (Hardening)            🔴
              │
              └──→ SOW Phase 0 (Jira)   🔴
```
