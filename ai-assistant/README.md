# 🍽️ Michelin Concierge — AI-Powered Restaurant Intelligence

A production-grade multi-agent AI system that lets users discover, compare, and book Michelin-starred restaurants through a conversational interface. Built with the full modern agentic protocol stack: **MCP · AG-UI · A2A · Skybridge · Qdrant RAG · Pydantic · LangGraph**.

---

## What It Does

- **Semantic restaurant search** — "cozy 2-star Japanese in Paris under €150"
- **Multi-day food tour planning** — autonomous multi-step itinerary generation
- **Live streaming UI** — token-by-token responses with real-time widget rendering
- **Rich generative widgets** — restaurant cards, interactive maps, comparison tables rendered inside the chat
- **Human-in-the-loop** — agent pauses for user confirmation before booking
- **Multi-agent orchestration** — specialized agents collaborate via A2A protocol

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js + CopilotKit | Chat UI, AG-UI client, widget host |
| **Widget layer** | Skybridge (`skybridge/web`) | Type-safe React widgets from MCP structured content |
| **Agent ↔ UI** | AG-UI (SSE stream) | Real-time token streaming, tool events, generative UI, interrupts |
| **Agent ↔ Agent** | A2A protocol | Orchestrator delegates tasks to specialized sub-agents |
| **Agent ↔ Tools** | MCP via Skybridge server | Tool discovery, execution, typed structured content |
| **Agent runtime** | LangGraph (Python) | Multi-step agentic loop with planning + reflection |
| **Vector DB** | Qdrant | Semantic + filtered restaurant retrieval |
| **Data validation** | Pydantic v2 | Strict I/O contracts at every agent boundary |
| **LLM** | ChatGroq (Llama / Qwen) | Fast inference for reasoning and generation |
| **API layer** | FastAPI | AG-UI endpoint, A2A task server |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND  —  Next.js + Node.js                                         │
│                                                                         │
│  ┌──────────────────────────┐   ┌─────────────────────────────────┐    │
│  │  CopilotKit Chat (AG-UI) │   │  Skybridge Widget Layer         │    │
│  │  • streams tokens live   │   │  useToolInfo() typed hooks      │    │
│  │  • shows tool events     │   │  RestaurantCard, MapView,       │    │
│  │  • generative UI         │   │  ComparisonTable, Itinerary,    │    │
│  │  • INTERRUPT cards       │   │  BookingConfirm                 │    │
│  └──────────────────────────┘   └─────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ AG-UI (SSE)
┌──────────────────────────────▼──────────────────────────────────────────┐
│  ORCHESTRATION LAYER  —  LangGraph stateful graph (Python)              │
│                                                                         │
│  ┌──────────┐  simple  ┌────────────┐                                  │
│  │  Entry   │─────────►│ Supervisor │──► direct A2A to one agent       │
│  │  Node    │          └────────────┘                                  │
│  │          │  complex ┌────────────┐                                  │
│  │          │─────────►│  Planner   │ LLM → Pydantic TaskDAG           │
│  └──────────┘          └─────┬──────┘                                  │
│                              │                                         │
│                        ┌─────▼──────┐                                  │
│                        │ Dispatcher │ async fan-out per DAG             │
│                        └─────┬──────┘                                  │
│                              │ parallel A2A calls                      │
│                        ┌─────▼──────┐                                  │
│                        │ Reflector  │ constraints met? re-plan if not  │
│                        └─────┬──────┘ (INTERRUPT after 3 iterations)  │
│                              │                                         │
│                        ┌─────▼──────┐                                  │
│                        │Synthesizer │ merge all results → final answer │
│                        └────────────┘                                  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ A2A Task objects
          ┌────────────────────┼──────────────────────────┐
          │                    │                          │
┌─────────▼──┐  ┌──────────────▼──┐  ┌───────────────▼─┐  ┌────────────▼───┐
│  Search    │  │  Recommend      │  │  Reservation    │  │  Review        │
│  Agent     │  │  Agent          │  │  Agent          │  │  Agent         │
│  Qdrant    │  │  Pydantic       │  │  AG-UI          │  │  RAG over      │
│  hybrid    │  │  UserProfile    │  │  INTERRUPT      │  │  review corpus │
│  RAG       │  │  preference     │  │  booking flow   │  │                │
└────────────┘  └─────────────────┘  └─────────────────┘  └────────────────┘
                 All sub-agents exposed as MCP tools via Skybridge
                                      │
                     ┌────────────────▼──────────────────┐
                     │  Skybridge MCP Server (TypeScript) │
                     │  registerWidget() per tool         │
                     │  structuredContent → typed widget  │
                     └────────────────┬──────────────────┘
                                      │
                     ┌────────────────▼──────────────────┐
                     │  Qdrant Vector DB                  │
                     │  semantic search + payload filters │
                     │  Michelin dataset embedded         │
                     └───────────────────────────────────┘
```

---

## Project Structure

```
michelin-concierge/
│
├── .env.example
├── docker-compose.yml               # Qdrant + all backend services
├── README.md
│
├── data/
│   └── michelin_restaurants.csv     # Kaggle Michelin Guide dataset
│
├── backend/                         # Python — all agent logic
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── server.py                    # FastAPI root: AG-UI /run + health
│   ├── models.py                    # All Pydantic schemas (single source)
│   ├── rag.py                       # Qdrant client, embed, hybrid search
│   ├── ingest.py                    # One-time dataset → Qdrant ingestion
│   │
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── graph.py                 # LangGraph graph definition (all nodes wired)
│   │   ├── state.py                 # LangGraph AgentState TypedDict
│   │   ├── entry.py                 # Entry node: classify simple vs complex
│   │   ├── supervisor.py            # Supervisor node: route to one agent
│   │   ├── planner.py               # Planner node: LLM → TaskDAG
│   │   ├── dispatcher.py            # Dispatcher node: async A2A fan-out
│   │   ├── reflector.py             # Reflector node: constraint validation
│   │   └── synthesizer.py           # Synthesizer node: merge → final answer
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Base A2A FastAPI server class
│   │   ├── search_agent.py          # Port 8001 — Qdrant RAG search
│   │   ├── recommend_agent.py       # Port 8002 — preference ranking
│   │   ├── reservation_agent.py     # Port 8003 — booking + INTERRUPT
│   │   └── review_agent.py          # Port 8004 — review corpus RAG
│   │
│   └── a2a/
│       ├── __init__.py
│       ├── client.py                # A2A HTTP client (sends Task objects)
│       ├── models.py                # A2A Task, TaskResult, AgentCard schemas
│       └── discovery.py             # Reads /.well-known/agent.json from each agent
│
├── mcp-server/                      # TypeScript — Skybridge MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts               # Skybridge Vite plugin (HMR)
│   │
│   └── src/
│       ├── server.ts                # McpServer entry, registers all widgets
│       │
│       ├── tools/
│       │   ├── search.ts            # restaurant_search → RestaurantCard widget
│       │   ├── compare.ts           # compare_restaurants → ComparisonTable widget
│       │   ├── details.ts           # get_details → DetailPanel widget
│       │   └── itinerary.ts         # build_itinerary → ItineraryCard widget
│       │
│       └── lib/
│           ├── qdrant.ts            # Qdrant TypeScript client
│           └── types.ts             # Shared TypeScript types (mirrors Pydantic models)
│
└── frontend/                        # Next.js — Node.js
    ├── package.json
    ├── next.config.ts
    ├── tsconfig.json
    ├── .env.local
    │
    ├── app/
    │   ├── layout.tsx               # CopilotKitProvider + global setup
    │   ├── page.tsx                 # Main page: chat column + widget column
    │   └── api/
    │       └── copilotkit/
    │           └── route.ts         # CopilotKit Next.js API route (proxies to backend)
    │
    ├── components/
    │   ├── chat/
    │   │   ├── ChatPanel.tsx        # CopilotKit chat, AG-UI event display
    │   │   └── ThinkingIndicator.tsx
    │   │
    │   ├── widgets/
    │   │   ├── RestaurantCard.tsx   # useToolInfo() — search results grid
    │   │   ├── MapView.tsx          # useToolInfo() — map pins
    │   │   ├── ComparisonTable.tsx  # useToolInfo() — side-by-side compare
    │   │   ├── ItineraryCard.tsx    # useToolInfo() — day-by-day plan
    │   │   └── BookingConfirm.tsx   # AG-UI INTERRUPT confirmation card
    │   │
    │   └── layout/
    │       ├── Sidebar.tsx          # City/cuisine/stars filter panel
    │       └── Header.tsx
    │
    └── lib/
        ├── copilotkit.ts
        └── types.ts
```

---

## Agentic Protocols Used

### MCP (Model Context Protocol)
Connects agents to tools and data. Each sub-agent capability is registered on the Skybridge MCP server as a typed tool. The orchestrator calls tools via standard MCP without knowing the implementation — agents are fully decoupled from tool logic.

### AG-UI (Agent–User Interaction Protocol)
Connects the orchestrator agent to the frontend over SSE. Every step the agent takes — token generated, tool called, state updated, interrupt needed — is a typed AG-UI event. The frontend reacts to events without polling.

Key events used:
- `TEXT_MESSAGE_CHUNK` — streams response tokens live
- `TOOL_CALL_START` / `TOOL_CALL_END` — triggers widget loading/render
- `STATE_DELTA` — syncs city/filter state between agent and map
- `RUN_STARTED` / `RUN_FINISHED` — lifecycle
- `INTERRUPT` — pauses agent for booking confirmation

### A2A (Agent-to-Agent Protocol)
The orchestrator discovers and delegates to sub-agents via A2A Agent Cards. Each sub-agent publishes a `/.well-known/agent.json` descriptor. The orchestrator routes tasks without tight coupling to implementations — sub-agents are independently deployable and swappable.

### Agent Orchestration (LangGraph multi-node graph)
The orchestration layer sits between the user and the sub-agents. Five nodes handle different complexity levels:

- **Supervisor** — classifies and routes single-intent queries to one agent
- **Planner** — decomposes multi-step goals into a dependency DAG (`TaskDAG`)
- **Dispatcher** — executes the DAG, firing independent tasks in parallel via A2A
- **Reflector** — validates results against constraints; re-plans failed branches (max 3 iterations before AG-UI INTERRUPT)
- **Synthesizer** — merges all agent outputs into the final response

Simple queries ("find me a restaurant") hit the Supervisor and resolve in 2 LLM calls. Complex goals ("plan my food tour") run through the full Planner → Dispatcher → Reflector loop, streaming progress via AG-UI throughout.

### Agentic Loop
For complex goals the orchestrator runs multiple LangGraph cycles autonomously: **plan → delegate → collect results → reflect → re-plan if constraints fail → surface to user only when done or blocked**.

---

## AG-UI Events Per Query Type

| Scenario | Events emitted in order |
|---|---|
| Simple search | `RUN_STARTED` → `TEXT_MESSAGE_CHUNK` ×n → `TOOL_CALL_START` → `TOOL_CALL_END` → `TEXT_MESSAGE_CHUNK` ×n → `RUN_FINISHED` |
| Complex planning | Above × per sub-task + `STATE_DELTA` (progress %) × iterations |
| Booking | Above + `INTERRUPT` → wait → `INTERRUPT_RESOLVED` → `RUN_FINISHED` |
| Re-plan | Above + `TEXT_MESSAGE_CHUNK` ("Adjusting Day 2...") before re-dispatch |

---

## Protocol Layer Summary

| Protocol | Between | Transport |
|---|---|---|
| AG-UI | Agent ↔ User | SSE (HTTP stream) |
| A2A | Agent ↔ Agent | HTTP POST |
| MCP | Agent ↔ Tools/Data | stdio / HTTP |
| Skybridge | MCP ↔ React widgets | structuredContent |

---

## Data Source

[Michelin Guide Restaurants — Kaggle](https://www.kaggle.com/datasets/ngshiheng/michelin-guide-restaurants-2021)

Fields used: `name`, `cuisine`, `city`, `price`, `stars`, `description`, `latitude`, `longitude`

Ingestion: `backend/ingest.py` embeds descriptions and upserts into Qdrant with metadata as payload fields for hybrid semantic + filtered queries.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Qdrant](https://qdrant.tech/documentation/quick-start/) running locally or Qdrant Cloud
- Groq API key
- OpenAI API key (for embeddings)
- CopilotKit Cloud key (free tier available)

### 1. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys

# Ingest Michelin dataset into Qdrant (run once)
python ingest.py

# Start orchestrator
uvicorn server:app --reload --port 8000

# Start sub-agents (separate terminals or use docker-compose)
uvicorn agents.search_agent:app --port 8001
uvicorn agents.recommend_agent:app --port 8002
uvicorn agents.reservation_agent:app --port 8003
uvicorn agents.review_agent:app --port 8004
```

### 3. MCP Server (Skybridge)

```bash
cd mcp-server
npm install
npm run dev        # port 3001, HMR enabled
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev        # port 3000
```

Open [http://localhost:3000](http://localhost:3000)

### Or run everything with Docker Compose

```bash
docker-compose up
```

---

## Environment Variables

```bash
# backend/.env
GROQ_API_KEY=
OPENAI_API_KEY=                    # text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                    # only for Qdrant Cloud
QDRANT_COLLECTION=michelin
SEARCH_AGENT_URL=http://localhost:8001
RECOMMEND_AGENT_URL=http://localhost:8002
RESERVATION_AGENT_URL=http://localhost:8003
REVIEW_AGENT_URL=http://localhost:8004
MCP_SERVER_URL=http://localhost:3001

# frontend/.env.local
NEXT_PUBLIC_COPILOTKIT_PUBLIC_API_KEY=
NEXT_PUBLIC_AGENT_URL=http://localhost:8000
```

---

## Python Dependencies

```
fastapi uvicorn
langgraph langchain-groq langchain-core langchain-community
qdrant-client openai
pydantic>=2.0
ag-ui-sdk
httpx
python-dotenv pandas
```

## Node Dependencies

```
# mcp-server
skybridge @modelcontextprotocol/sdk zod typescript

# frontend
next react react-dom
@copilotkit/react-core @copilotkit/react-ui
skybridge
```

---

## Example Queries

```
# Supervisor → Search Agent → Qdrant RAG → RestaurantCard widget
"Find me a 2-star Japanese restaurant in Paris under €150"

# Supervisor → Recommend Agent → ComparisonTable widget
"Compare Kei and Taillevent for a business dinner"

# Planner → Dispatcher (parallel) → Reflector (cuisine check) → ItineraryCard widget
"Plan a 3-day Paris food tour: 2 starred lunches and 1 dinner per day,
no repeated cuisines, budget €400 total"

# Supervisor → Reservation Agent → AG-UI INTERRUPT → BookingConfirm
"Book a table at Guy Savoy for tonight, party of 2 at 8pm"

# Supervisor → Review Agent → review corpus RAG
"What do critics say about the tasting menu at Le Bernardin?"
```

---

## Key Design Decisions

**Why LangGraph over simple tool binding?**
Multi-step agentic goals require stateful cycles — plan, act, reflect, re-plan. LangGraph's graph model handles this natively; `bind_tools` only handles one-shot tool calls.

**Why Skybridge over raw MCP SDK?**
Raw MCP SDK has no React hooks, no HMR, and no `structuredContent` type inference. Skybridge adds `useToolInfo()` with full autocomplete, live reload, and a dual-surface sync model that keeps the LLM aware of widget state.

**Why A2A over direct function calls between agents?**
A2A agents are discoverable, independently deployable, and swappable. The orchestrator never imports sub-agent code — it talks to a URL. This mirrors real production microservice design.

**Why Pydantic at every boundary?**
LLMs hallucinate field names and types. Pydantic validation at every input/output catches bad model output before it silently corrupts downstream rendering or database writes.

**Why the Supervisor/Planner split?**
Not every query needs a full planning loop. Simple queries routed through the Supervisor resolve in 2 LLM calls instead of 5+, keeping latency low for the common case.

---

## License

MIT
