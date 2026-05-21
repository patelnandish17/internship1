# Placement Compass - Full-Stack Campus Analytics & Agentic Orchestration

A centralized monorepo application containing:
1. **Front-end**: A Vite + React + TypeScript + Tailwind CSS dashboard providing campus placement metrics, company research, and analytics.
2. **Back-end & Agentic Orchestration**: A FastAPI REST service integrated with a multi-agent LangGraph workflow that gathers, evaluates, and compiles company data using LLM providers (Google, Groq, OpenAI, SambaNova).

---

## Project Structure

```
├── .dockerignore
├── .gitignore
├── Dockerfile                  # Multi-stage Dockerfile for React Frontend (served via Nginx)
├── nginx.conf                  # Nginx configuration to support SPA routing
├── docker-compose.yml          # Container orchestration (Frontend + Backend)
├── Jenkinsfile                 # Jenkins Pipeline definition
├── package.json                # Frontend dependencies
├── src/                        # React Frontend Source Code
├── Lang graph/                 # FastAPI and Multi-Agent Orchestration folder
│   ├── app/                    # FastAPI App codebase
│   │   ├── main.py             # FastAPI entrypoint
│   │   └── graph.py            # LangGraph pipeline definition
│   ├── tests/                  # Backend smoke tests
│   ├── requirements.txt        # Python backend dependencies
│   ├── Dockerfile              # Backend Python image configuration
│   └── .dockerignore           # Backend docker ignores
```

---

## Local Setup

### Prerequisite: Environment Variables
Create a `.env` file at the project root with the following variables:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_groq_api_key
SAMBANOVA_API_KEY=your_sambanova_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Option 1: Run with Docker Compose (Recommended)
1. Ensure Docker is running.
2. Start all services using:
   ```bash
   docker compose up --build -d
   ```
3. Access the applications:
   - **Frontend**: http://localhost:3000
   - **FastAPI Backend (Swagger API Docs)**: http://localhost:8000/docs
   - **FastAPI Health Check**: http://localhost:8000/health

### Option 2: Run Separately
- **Frontend**:
  ```bash
  npm install
  npm run dev
  ```
- **Backend**:
  ```bash
  cd "Lang graph"
  python -m venv venv
  .\venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  ```

---

## Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a 4-stage pipeline:
1. **Initialize Environment**: Injects the `.env` secret file from Jenkins global credentials into the workspace.
2. **Front-end Pipeline**: Runs dependency installs (`npm ci`), runs front-end tests (`npm run test`), compiles the Vite build (`npm run build`), and packages the frontend Docker container.
3. **Back-end Pipeline**: Builds the virtual environment, executes backend smoke tests (`pytest`), and builds the backend Docker container.
4. **Agentic Orchestration Pipeline**: Launches the services (`docker compose up -d`) and performs health-check validations.
