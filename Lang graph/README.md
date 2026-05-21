# LangGraph Company Research API

A multi-agent pipeline that researches companies across **163 parameters** using
**Groq / Llama**, **GitHub / GPT-4o**, and **SambaNova** in parallel, exposed as
a FastAPI REST service alongside the existing LangGraph Studio interface.

---

## Architecture

```
POST /v1/agent/generate
        │
        ▼
WorkflowService.start_run()
        │
        ├─ background asyncio.Task ──▶ app/graph.py compiled_graph.astream()
        │                                   │
        │                           entry → [groq | github | sambanova] → consolidate → excel
        │
        ▼
GET /v1/agent/status/{run_id}   ← poll until status=completed
```

---

## Quick Start

### 1. Install dependencies

```powershell
cd "C:\Users\Lenovo\Downloads\Lang graph"
.\venv\Scripts\pip install -r requirements.txt
```

### 2. Configure environment

```powershell
copy .env.example .env
# Edit .env and add your API keys
```

### 3a. LangGraph Studio (unchanged)

```powershell
.\venv\Scripts\langgraph.exe dev
```

### 3b. FastAPI server

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

Swagger UI → **http://localhost:8000/docs**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/agent/generate` | Start a research run. Returns `{run_id, status: "queued"}` |
| `GET`  | `/v1/agent/status` | List all runs (newest first) |
| `GET`  | `/v1/agent/status/{run_id}` | Poll a specific run |
| `GET`  | `/health` | Liveness check |

### Example: start a run

```bash
curl -X POST http://localhost:8000/v1/agent/generate \
     -H "Content-Type: application/json" \
     -d '{"company_name": "Siemens"}'
```

Response:
```json
{
  "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "company_name": "Siemens",
  "status": "queued",
  "progress": 0,
  "message": "Queued — waiting for pipeline slot",
  "created_at": "2026-05-18T04:00:00Z",
  "updated_at": "2026-05-18T04:00:00Z",
  "output": null,
  "failed_parameters": null,
  "error": null
}
```

### Example: poll status

```bash
curl http://localhost:8000/v1/agent/status/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

---

## Running Tests

```powershell
.\venv\Scripts\pytest tests/test_api.py -v
```

---

## Output Files

When a run completes, two files are saved to `OUTPUT_DIR` (default: project root):

| File | Description |
|------|-------------|
| `{company}_golden_record.json` | Structured JSON with all 163 parameters |
| `{company}_golden_record.md`   | Markdown table matching the schema layout |

---

## Environment Variables

See [`.env.example`](.env.example) for the full list with descriptions.
