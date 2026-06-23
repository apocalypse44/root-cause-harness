# Root Cause Harness

AI-powered root cause investigation engine that correlates deployments, logs, metrics, and git history to automatically diagnose production failures.

## Quick Start

```bash
# 1. Set your Groq API key
cp backend/.env.example backend/.env
# Edit backend/.env with your GROQ API key

# 2. Start everything
docker compose up --build

# 3. Seed demo data
docker compose exec backend python -m app.seed

# 4. Open
# http://localhost:3000
```

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **AI:** Groq API (OpenAI-compatible — swappable to Ollama/OpenAI)
- **Frontend:** Next.js, TypeScript, TailwindCSS, ShadCN UI, React Query
- **Infra:** Docker Compose

## How It Works

Create an incident → click "Investigate" → 5 AI agents run sequentially:

1. **Deployment Agent** — checks recent deployments and failures
2. **Logs Agent** — finds error patterns and stack traces
3. **Metrics Agent** — detects anomalies in CPU, memory, latency, error rates
4. **Git Agent** — identifies recent commits and changed files
5. **Correlation Agent** — calls LLM to correlate all findings into a root cause report

Output: root cause, confidence score, timeline, evidence, and recommendations.
