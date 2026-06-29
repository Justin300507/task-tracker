# Architecture — Task Tracker

## ER Diagram

```
┌─────────────────────┐
│ Collaborations      │
├─────────────────────┤
│ id         Integer ││
│ project_id Integer ││
│ user_id    Integer ││
│ role       Enum("owne│
│ invited_at DateTime││
│ accepted_at DateTime││
└─────────────────────┘

┌─────────────────────┐
│ Project             │
├─────────────────────┤
│ id         Integer ││
│ name       String  ││
│ description Text    ││
│ owner_id   Integer ││
│ created_at DateTime││
│ updated_at DateTime││
└─────────────────────┘

┌─────────────────────┐
│ Tag                 │
├─────────────────────┤
│ id         Integer ││
│ name       String  ││
└─────────────────────┘

┌─────────────────────┐
│ TaskTag             │
├─────────────────────┤
│ task_id    Integer ││
│ tag_id     Integer ││
└─────────────────────┘

┌─────────────────────┐
│ Task                │
├─────────────────────┤
│ id         Integer ││
│ title      String  ││
│ description Text    ││
│ status     Enum("pend│
│ due_date   DateTime││
│ reminder_offset Integ│
│ project_id Integer ││
│ owner_id   Integer ││
│ ... (1 more)    │
└─────────────────────┘

┌─────────────────────┐
│ Users               │
├─────────────────────┤
│ id         Integer ││
│ email      String  ││
│ hashed_password Strin│
│ full_name  String  ││
│ created_at DateTime││
│ is_active  Boolean ││
└─────────────────────┘

```

## Backend Architecture

```
FastAPI Application
├── Routing Layer (app/routes/)     → HTTP request handling
├── Service Layer (app/services/)   → Business logic
├── Model Layer (app/models/)       → Database ORM (SQLAlchemy)
├── Schema Layer (app/schemas/)     → Validation (Pydantic v2)
└── Database (app/database.py)      → Session management (SQLite)
```

## Design Patterns

- **Repository pattern**: services own DB queries, routes own HTTP logic
- **Dependency injection**: `get_db` session injected via FastAPI `Depends()`
- **Schema separation**: ORM models never exposed directly; Pydantic schemas serialize responses
- **JWT auth**: Bearer tokens validated via `oauth2_scheme` dependency
