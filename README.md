# CV Generator (Vue.js + FastAPI + Docker)

A small full‑stack project that turns free‑form text into compilable LaTeX for a résumé/CV using OpenAI/ChatGPT, then renders a PDF from it. The LaTeX template is configurable and stored server‑side.

![Landing Page](docs/screenshots/landing-page.png)


## Architecture
- Frontend: Vue 3 (Vite) + Nginx (serves the build and proxies `/api` to the backend)
- Backend: FastAPI (Python) with endpoints for generation (OpenAI) and rendering (Tectonic)
- PDF build: [Tectonic](https://tectonic-typesetting.github.io/) LaTeX engine in the backend container
- Orchestration: Docker Compose

## Prerequisites
- Docker and Docker Compose
- OpenAI API key
- If you run the backend locally without Docker: install a LaTeX engine
  (recommended: Tectonic). Examples:
  - macOS: `brew install tectonic`
  - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install tectonic`
  - Alternative (fallback): `pdflatex`/`xelatex` from a TeX distribution

## Getting Started
1. Create a `.env` in the project root (see `.env.example` below) or set environment variables.
2. Build & start:
   - `docker compose up --build`
3. Open the frontend: `http://localhost:8080`

## Screenshots

  ![User Input](docs/screenshots/form.png)

  <br>

  ![PDF Preview](docs/screenshots/pdf-vorschau.png)

## Authentication (Auth0)
- Landing page (`/`) is public, the tool (`/tool`) is protected via Auth0.
- All backend API routes under `/api/*` additionally require JWT (Auth0 access token); `GET /api/health` remains public.
- Create an SPA app in Auth0 and configure:
  - Allowed Callback URLs: `http://localhost:8080/callback`
  - Allowed Logout URLs: `http://localhost:8080`
  - Allowed Web Origins: `http://localhost:8080`
- Set the following variables in `.env` (injected at frontend build time):
  - `VITE_AUTH0_DOMAIN` – e.g. `your-tenant.eu.auth0.com`
  - `VITE_AUTH0_CLIENT_ID` – SPA app client ID
  - Optional: `VITE_AUTH0_AUDIENCE` – if you use an API audience

Backend additionally expects (already wired via Compose):
- `AUTH0_DOMAIN` and `AUTH0_AUDIENCE` (derived from the VITE variables)

The frontend automatically sends the access token as `Authorization: Bearer ...` header.

Note: Values are injected into the frontend at build time (Vite). Docker Compose passes them as build args to the frontend.

## Environment Variables
- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_MODEL` (optional): e.g. `gpt-4o-mini` (default), `gpt-4o`, `gpt-3.5-turbo`

Example `.env`:
```
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4o-mini

# Auth0
VITE_AUTH0_DOMAIN=your-tenant.eu.auth0.com
VITE_AUTH0_CLIENT_ID=yourClientId
VITE_AUTH0_AUDIENCE=
```

## API Endpoints (Backend)
- `GET /api/health` – health check
- `GET /api/template` – read current LaTeX template
- `PUT /api/template` – save template; body: `{ "template": "..." }`
- `POST /api/generate` – generate LaTeX; body: `{ "input_text": "...", "template_override"?: "..." }`; response: `{ latex: "..." }`
- `POST /api/render` – render PDF from LaTeX; body: `{ "latex": "..." }`; response: `application/pdf`
- `POST /api/generate-pdf` – generate and render in one step; body: `{ "input_text": "..." }`; response: `application/pdf`

## LaTeX Compilation Notes
- The backend container installs Tectonic automatically. When running the backend locally, the code tries `tectonic` first and falls back to `pdflatex` or `xelatex` if unavailable.
- When using external LaTeX packages, Tectonic may fetch them at runtime (requires internet access). For reproducible builds, prefer templates that work well with Tectonic’s defaults.
- Templates persist in the `cv_templates` volume under `/app/templates/cv_template.tex`.

## Development
- Frontend code lives in `frontend/`, backend in `backend/`.
- Local testing without Docker is possible (uvicorn, Vite), but Compose wiring is the default.

## Templates
- Select templates in the tool under step 1. Preview images live in `frontend/src/assets/templates/`.
- Configure available templates in the frontend at `frontend/src/templates.js` (id, name, preview image).
- The backend loads templates by `id` from `TEMPLATE_DIR` (default: `/app/templates`).
  - Filename pattern: `<id>.tex` (e.g. `cv_template.tex`, `modern.tex`, `minimal.tex`).
  - Packaged defaults: If present, files under `backend/app/templates/` are also considered.
- If a selected template does not exist in the backend, a 404 is returned.

## Security
- Provide the API key only via environment variable. It is not leaked to the frontend. Generation happens server‑side.

## Troubleshooting
- Generation fails: Check `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`.
- LaTeX compilation error "No such file or directory: 'tectonic'": Install Tectonic (see prerequisites) or ensure a LaTeX engine (`pdflatex`/`xelatex`) is on `PATH`.
- LaTeX errors: Inspect the generated LaTeX in the UI and adjust the template if needed.
- Package downloads blocked: Tectonic requires internet access in the container to fetch missing packages.
