# Living Map — Project Context

## What This Is
A visual editor for managing Knowledge Components (KCs) in a DAG structure for mathematical education. Built as a prototype for the Living Map research project.

## Architecture

### Two-Map System
1. **Knowledge Map**: KCs connected by prerequisite edges, organized into schemas within frames
2. **Math Domains DAG**: Mathematical organizing categories (whole-numbers, integers, rationals...) forming their own DAG, linked to KCs via `kc_math_contexts`

### Tech Stack
- **Backend**: Python, FastAPI, SQLite, NetworkX, Pydantic — `living_map/app.py`, `living_map/dal.py`
- **Frontend**: React, TypeScript, Vite, Cytoscape.js — `frontend/src/`
- **Visualization**: Cytoscape.js with dagre layout (top-to-bottom DAG)

### Key Data Concepts
- **Frame**: A version of a knowledge map (e.g., counting-numbers-v1, coordinate-plane-v1)
- **Schema**: A grouping of KCs within a frame; supports nesting via `parent_schema_id`
- **KC**: A knowledge component — the atomic unit of learning
- **Prerequisite edge**: Directed edge between KCs (source must be learned before target)
- **Math domain**: A mathematical category (formerly "math concept" in the API — backend routes still use `math-concepts`)
- **Structural edge**: Directed edge between math domains in the Math Domains DAG

### Validation
Frames are validated for:
- **Convexity**: Each schema's atom set must be convex in the DAG
- **Laminarity**: Schema atom sets must be either disjoint or nested (not partially overlapping)
- **Connectedness**: The KC graph must be connected
- **Acyclicity**: No cycles in prerequisite edges

### Quotient Operation
Collapse schemas into single nodes. Sequential quotienting supported — collapsing a parent auto-includes child schemas. Convexity violations are caught and shown inline.

## Running

### Development (two servers)
```bash
# Backend on :8000
cd living-map && python3 -m living_map.app

# Frontend on :5173
cd frontend && npm run dev
```

### Production / Sharing
```bash
./deploy.sh                       # Build + run on port 8000
./deploy.sh --sandbox --tunnel    # Safe copy + public URL via cloudflared
./deploy.sh --rebuild             # Kill existing, rebuild, fresh sandbox + tunnel
./restore.sh                      # Reset DB to seed snapshot
```

## Current State (as of 2026-03-15)

### Data
- 137 KCs (68 CNM + 69 COP), 130 edges, 2 frames, 30 schemas
- 1 math domain: whole-numbers (coordinate-plane was deleted — needs rebuilding from scratch)
- CNM KCs have `kc_type` annotations (Skill/Fact); COP KCs do not yet
- Both frames validate as fully valid

### UI Features
- Knowledge Map view with Cytoscape DAG visualization
- Math Domains view with its own DAG editor (add/delete domains and edges)
- Side panel: click any node to view/edit details, add/remove math domain tags
- Color modes: language demand, schema, category (skill type), math domain
- Hover labels (not always-on, to avoid collision)
- "Show only active frame" toggle
- Sequential quotient panel with auto-child-inclusion
- Expandable validation detail panel with clickable violation links

### Recently Completed
- Skill type (kc_type) editing added to KC side panel with dropdown and ability to add new types
- COP KCs now have skill types assigned
- Edge deletion UI added to Knowledge Map and Math Domains views
- Add KC and Add Edge buttons added to Knowledge Map toolbar
- KC ID auto-generation: pick schema from dropdown, system generates next sequential ID
- Math domain data rebuilt for COP KCs

## Mac Mini Deployment (completed 2026-03-15)

### Setup
- Project lives at `~/Living Map/living-map` on Mac Mini (macOS, Intel)
- Python 3.11 via Homebrew, Node.js via Homebrew
- Venv at `.venv` — dependencies: fastapi, uvicorn, aiosqlite, networkx, openpyxl

### Database Strategy
- **`living_map.db`** — working copy (source of truth), edited during dev sessions
- **`living_map.live.db`** — what collaborators see via the tunnel (server reads this)
- **`living_map.seed.db`** — original snapshot for recovery
- Run `./publish.sh` on Mac Mini to copy working DB → live DB

### Server & Tunnel
- macOS Launch Agent: `~/Library/LaunchAgents/com.livingmap.server.plist`
- Runs `start-server.sh` which starts uvicorn (against `living_map.live.db`) + cloudflared quick tunnel
- Free trycloudflare.com URL — changes on reboot
- `./get-url.sh` — prints current tunnel URL
- `launchctl kickstart -k gui/$(id -u)/com.livingmap.server` — restart service
- cloudflared is at `/usr/local/bin/cloudflared`
- "Show only active frame" defaults to checked (changed in App.tsx)

### Upgrading to permanent URL (future)
- Register a domain, add to Cloudflare
- Create a named tunnel with `cloudflared tunnel create living-map`
- Route DNS to tunnel — gives a fixed URL that survives restarts

## Coding Conventions

### Python (Backend)
- **Sync SQLite, async FastAPI**: DAL methods are synchronous (using `sqlite3.Connection`); FastAPI routes call them via `run_in_executor`
- **Module singletons**: `_dal`, `_graphs`, `_staging_dal` initialized in FastAPI lifespan; accessed via getter functions that assert non-None
- **Timestamps**: Always UTC, formatted as `"%Y-%m-%dT%H:%M:%S.%fZ"` — use `_now()` helper in DAL classes
- **Models**: Every route has explicit Pydantic request/response models in `models.py` — never accept raw dicts from the API
- **SQL style**: Inline SQL strings in DAL methods, parameterized with `?` placeholders. No ORM. Use `INSERT OR IGNORE` for junction tables
- **Graph sync**: Every DAL write that affects nodes or edges must also update the corresponding NetworkX graph via `GraphStore` methods
- **Error pattern**: Raise `HTTPException` in routes; raise `CycleError` from graph operations (caught by routes)
- **JSON fields**: Complex data stored as JSON text in SQLite (language_demands, math_contexts, reviewer_comments) — serialize/deserialize in the DAL
- **Naming**: snake_case everywhere; files match module names; class names are PascalCase

### TypeScript (Frontend)
- **API client**: All backend calls go through typed functions in `api.ts` — never call `fetch` directly from components
- **State management**: useState/useContext only — no Redux or external state library
- **Props over context**: State lives in App.tsx, passed down via props. Use `useCallback` for stable callback references
- **Cytoscape**: Graph rendering isolated in `DAGView.tsx`; exposed to parent via `forwardRef` + `useImperativeHandle` (for `resetLayout`)
- **Node ID prefixes**: `schema-` for schema nodes, `domain-` for math domain nodes in Cytoscape — always strip prefixes before API calls
- **Styling**: Plain CSS in `index.css` — no Tailwind, no CSS modules, no styled-components
- **Color maps**: Defined as static constants at module level, not computed

### General
- **Don't rename API routes**: Backend uses "math-concepts" in URLs; UI says "Math Domains." Keep both as-is
- **Leaf-only schema nesting**: KCs only belong to leaf schemas; parent membership is inferred as the union of children
- **Test with**: `python -m pytest tests/` from project root

## Implementation Stories (Steps 5–7)

Use this template when starting work on a new feature. Write the story into `## Next Session Tasks` before coding.

```
### Story: [short title]
**Goal**: What the user can do when this is done
**Touches**: Which files need changes
**Depends on**: Any prerequisite stories or data
**Acceptance**:
- [ ] Concrete, testable criterion
- [ ] Another criterion
**Notes**: Any edge cases or design decisions to resolve
```

### Step 5 — Staging-Aware Visualization
**Goal**: Users can see proposed (staged) KCs and edges overlaid on the committed graph, visually distinguished
**Touches**: `DAGView.tsx`, `App.tsx`, `api.ts`, `app.py`
**Depends on**: Steps 1–4 (complete)
**Acceptance**:
- [ ] Staged KCs render with a distinct visual style (e.g., dashed border, muted color)
- [ ] Staged edges render differently from committed edges (e.g., dashed lines)
- [ ] Toggle to show/hide staged items
- [ ] Clicking a staged node opens it in the side panel with staging metadata visible
**Notes**: Need to decide whether staged items participate in quotient operations or are excluded

### Step 6 — Tier 2 Review
**Goal**: Multiple reviewers can approve/reject staged KCs with comments, reaching consensus before commit
**Touches**: `staging_dal.py`, `models.py`, `app.py`, new review UI component
**Depends on**: Step 5 (staged items visible on graph)
**Acceptance**:
- [ ] Each staged KC/edge/schema tracks per-reviewer approval status
- [ ] Reviewers can add comments (stored in reviewer_comments JSON)
- [ ] A staged item is "approved" only when all designated reviewers approve
- [ ] Dashboard shows review progress per session
**Notes**: Determine whether reviewers are named users or just approval counts

### Step 7 — Commit Pipeline
**Goal**: Approved staged items are flushed to the production tables, becoming permanent KCs/edges/schemas
**Touches**: `staging_dal.py`, `dal.py`, `app.py`, `graph_store.py`
**Depends on**: Step 6 (items are approved)
**Acceptance**:
- [ ] One-click commit for a fully-approved session
- [ ] Committed items appear in the main graph immediately
- [ ] Staging tables are cleaned up after commit
- [ ] Validation runs on the post-commit graph (convexity, laminarity, acyclicity)
- [ ] Rollback or undo is possible if validation fails
**Notes**: Decide whether commit is all-or-nothing per session or can be partial

## Next Session Tasks
(none currently — awaiting new priorities)

## Planned Features (discussed but not yet built)

### Bulk Edge Generation from Math Domains
- Tag KCs within a schema to math domains, then auto-propose prerequisite edges following the math domain DAG structure
- UX: select a schema, click "Apply domain structure," preview proposed edges highlighted on graph, confirm to create
- Review-only, not auto-create

### Knowledge Domains (future)
- Formalize the domain prefix (CNM, COP) as a first-class entity with its own DAG
- Similar to math domains but representing pedagogical/curricular progression
- Would enable cross-domain prerequisite suggestions
- Needs discussion with collaborators first — keep implicit in ID prefix for now

## File Guide
- `living_map/app.py` — FastAPI routes
- `living_map/dal.py` — Data access layer (SQLite)
- `living_map/models.py` — Pydantic models
- `living_map/seed_loader.py` — CNM seed data loader
- `living_map/seed_loader_cop.py` — Coordinate plane seed data loader
- `frontend/src/App.tsx` — Main React component, toolbar, quotient panel, validation
- `frontend/src/DAGView.tsx` — Cytoscape graph rendering
- `frontend/src/MathDomainsView.tsx` — Math Domains DAG editor
- `frontend/src/SidePanel.tsx` — Detail/edit panel for selected nodes
- `frontend/src/api.ts` — TypeScript API client
- `frontend/src/index.css` — All styles
- `deploy.sh` — Build + deploy script
- `restore.sh` — Reset DB to seed snapshot
- `start-server.sh` — Launch Agent startup script (server + tunnel)
- `get-url.sh` — Print current tunnel URL
- `publish.sh` — Copy working DB to live DB
- `com.livingmap.server.plist` — macOS Launch Agent config

## API Note
Backend routes still use "math-concepts" (e.g., `/api/math-concepts`, `/api/math-concept-edges`). The UI labels say "Math Domains." Don't rename the routes — just keep the UI terminology consistent.
