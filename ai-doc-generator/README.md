# AI Documentation Generator

AI Documentation Generator is an MVP that creates a draft `README.md` from a public GitHub repository URL. It clones the repository into a temporary directory, extracts project metadata, ranks file summaries locally with TF-IDF, and generates Markdown with Groq's OpenAI-compatible chat completions API. See the [root README](../README.md) for the full overview.

## Features

- Public GitHub repository URL validation
- Temporary repository cloning with cleanup
- Ignore rules for `.git`, `node_modules`, `dist`, `build`, `__pycache__`, `.next`, large files, and common generated folders
- Extraction of directory tree, dependencies, existing README content, Dockerfile presence, `.env.example` variables, and API routes
- File summaries, local TF-IDF retrieval, and grounded README generation
- FastAPI backend with Pydantic models, structured logging, global exception handling, and pytest tests
- Next.js 15 frontend with loading state, Markdown preview, copy, download, and error handling
- Dockerfiles and Docker Compose for local deployment

## Tech Stack

- Backend: Python 3.12, FastAPI, GitPython, python-dotenv, `openai` SDK (pointed at Groq)
- Retrieval: local TF-IDF cosine similarity (no embedding API)
- LLM: Groq chat completions (`llama-3.3-70b-versatile` by default)
- Frontend: Next.js 15, TypeScript, Tailwind CSS, React Markdown
- Testing: pytest

## Project Structure

```text
ai-doc-generator/
├── backend/
│   ├── api/
│   ├── services/
│   ├── parsers/
│   ├── models/
│   ├── prompts/
│   ├── utils/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/
├── docker-compose.yml
└── README.md
```

## Configuration

Create backend and frontend environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Set `GROQ_API_KEY` in `backend/.env`. API keys are never hardcoded. Set `TRUSTED_PROXY_COUNT` to the number of reverse proxies in front of the API (`1` on Render, `0` if exposed directly) so rate limiting uses the real client address.

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs at `http://localhost:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

## Windows Helper Scripts

From the project root:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

Or with Docker:

```powershell
.\scripts\start-docker.ps1
```

## Docker Setup

```bash
docker compose up --build
```

## 🚀 Public Deployment

To deploy as a **fully working web app** (not localhost):

**👉 Follow the complete guide in [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)**

This includes step-by-step instructions for:
- Pushing to GitHub
- Deploying backend on Render (~10 min)
- Deploying frontend on Vercel (~5 min)
- Configuring environment variables
- Testing your live app

Your app will be publicly accessible at a URL like: `https://your-app.vercel.app`

## API

### `GET /health`

Returns backend health.

### `POST /api/generate`

Generates README Markdown.

```json
{
  "repository_url": "https://github.com/owner/repository"
}
```

Response:

```json
{
  "markdown": "# Project Name\n..."
}
```

## Tests

```bash
cd backend
pytest
```

## Notes

- The backend deletes cloned repositories after each request by using `TemporaryDirectory`.
- Git must be installed in the runtime environment for GitPython cloning.
- Files larger than 1 MB and common binary/generated paths are skipped.
