import os
import logging
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import httpx
import jwt
from jwt import PyJWKClient

from .services.openai_service import (
    generate_latex_via_openai,
    edit_latex_via_openai,
    generate_latex_from_linkedin_html,
)
from .services.latex_service import compile_latex_to_pdf


# --------------------------- Models ---------------------------


class GenerateRequest(BaseModel):
    input_text: str
    template_override: Optional[str] = None
    template_id: Optional[str] = None


class GenerateResponse(BaseModel):
    latex: str


class TemplateUpdateRequest(BaseModel):
    template: str


class RenderRequest(BaseModel):
    latex: str


class EditRequest(BaseModel):
    latex: str
    instruction: str


class LinkedInImportRequest(BaseModel):
    url: str
    template_override: Optional[str] = None
    template_id: Optional[str] = None


# --------------------------- Template helpers ---------------------------


def get_template_dir() -> Path:
    return Path(os.getenv("TEMPLATE_DIR", "/app/templates")).resolve()


def get_default_template_path() -> Path:
    tmpl_dir = get_template_dir()
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    return tmpl_dir / "cv_template.tex"


def read_template() -> str:
    path = get_default_template_path()
    if not path.exists():
        # Fallback zu paketierter Default-Datei
        packaged = Path(__file__).parent / "templates" / "cv_template.tex"
        if packaged.exists():
            return packaged.read_text(encoding="utf-8")
        raise FileNotFoundError("No LaTeX template found.")
    return path.read_text(encoding="utf-8")


def write_template(content: str) -> None:
    path = get_default_template_path()
    path.write_text(content, encoding="utf-8")


def strip_code_fences(text: str) -> str:
    # Entferne ```latex ... ``` oder ``` ... ```-Blöcke
    code_block = re.search(r"```(?:latex)?\n([\s\S]*?)```", text, re.IGNORECASE)
    if code_block:
        return code_block.group(1).strip()
    return text.strip()


def read_template_by_id(template_id: str) -> str:
    """Read a template by its id (= filename stem)."""
    tmpl_dir = get_template_dir()
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", template_id or "").strip()
    if not safe_id:
        raise FileNotFoundError("Invalid template id")
    candidate = tmpl_dir / f"{safe_id}.tex"
    if candidate.exists():
        return candidate.read_text(encoding="utf-8")
    packaged = Path(__file__).parent / "templates" / f"{safe_id}.tex"
    if packaged.exists():
        return packaged.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Template not found: {safe_id}")


def list_templates() -> list[dict]:
    """List available templates from TEMPLATE_DIR and packaged defaults."""
    tmpl_dir = get_template_dir()
    items = []
    seen = set()
    if tmpl_dir.exists():
        for p in sorted(tmpl_dir.glob("*.tex")):
            items.append({
                "id": p.stem,
                "name": p.stem.replace("_", " ").title(),
                "source": "custom",
            })
            seen.add(p.stem)
    packaged_dir = Path(__file__).parent / "templates"
    if packaged_dir.exists():
        for p in sorted(packaged_dir.glob("*.tex")):
            if p.stem in seen:
                continue
            items.append({
                "id": p.stem,
                "name": p.stem.replace("_", " ").title(),
                "source": "builtin",
            })
    if not items:
        # Ensure at least default is shown by id
        items.append({"id": "cv_template", "name": "Cv Template", "source": "implicit"})
    return items


# --------------------------- App & Logging ---------------------------

app = FastAPI(title="CV Generator API")
logger = logging.getLogger(__name__)


# --------------------------- Error mapping ---------------------------


def _map_status(code: int) -> int:
    from http import HTTPStatus

    try:
        _ = HTTPStatus(code)
        return code if code in (401, 403, 404) else (code if code < 400 else 502)
    except Exception:
        return 403 if code == 999 else 502


@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    mapped = _map_status(getattr(exc, "status_code", 500) or 500)
    if mapped != getattr(exc, "status_code", None):
        logger.info(
            "Mapped HTTPException status %s -> %s for %s",
            exc.status_code,
            mapped,
            request.url.path,
        )
    detail = getattr(exc, "detail", "Error")
    return JSONResponse(status_code=mapped, content={"detail": detail})


# --------------------------- CORS ---------------------------
# (Passe Origins/Methoden/Headers nach Bedarf an)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------- Auth0 (vereinfachte Prüfung) ---------------------------

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")  # z.B. your-tenant.eu.auth0.com
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")  # z.B. https://api.example.com
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/" if AUTH0_DOMAIN else None

_JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json" if AUTH0_DOMAIN else None
_JWKS = PyJWKClient(_JWKS_URL) if _JWKS_URL else None


def _unauth(detail: str = "Unauthorized", code: int = 401):
    return JSONResponse(status_code=code, content={"detail": detail})


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Schütze alle /api/* außer /api/health
    path = request.url.path
    if not (path.startswith("/api/") and path != "/api/health"):
        return await call_next(request)

    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE or not AUTH0_ISSUER or not _JWKS:
        return _unauth("Auth not configured", 500)

    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return _unauth("Missing bearer token")

    token = auth.split(" ", 1)[1].strip()
    try:
        signing_key = _JWKS.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
            options={"leeway": 10},  # kleine Clock-Skew-Toleranz
        )
        request.state.user = claims
    except jwt.ExpiredSignatureError:
        return _unauth("Token expired")
    except jwt.InvalidAudienceError:
        return _unauth("Invalid audience")
    except jwt.InvalidIssuerError:
        return _unauth("Invalid issuer")
    except Exception:
        return _unauth("Token validation failed")

    return await call_next(request)


# Optional: Scopes-Helfer, falls du Berechtigungen pro Route prüfen möchtest
# from fastapi import HTTPException as _HTTPExc
# def require_scopes(request: Request, *required: str):
#     got = set((request.state.user.get("scope") or "").split())
#     need = set(required)
#     if not need.issubset(got):
#         raise _HTTPExc(status_code=403, detail="Insufficient scope")


# --------------------------- Routes ---------------------------


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/templates")
def get_templates():
    return {"templates": list_templates()}


@app.get("/api/template")
def get_template(id: Optional[str] = None):
    try:
        content = read_template() if not id else read_template_by_id(id)
        return {"template": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/api/template")
def update_template(req: TemplateUpdateRequest):
    if not req.template.strip():
        raise HTTPException(status_code=400, detail="Template must not be empty.")
    write_template(req.template)
    return {"status": "updated"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    if req.template_override:
        template = req.template_override
    elif req.template_id:
        try:
            template = read_template_by_id(req.template_id)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        template = read_template()
    try:
        latex = generate_latex_via_openai(input_text=req.input_text, template=template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI generation failed: {e}")
    latex = strip_code_fences(latex)
    return GenerateResponse(latex=latex)


@app.post("/api/render")
def render_pdf(req: RenderRequest, background: BackgroundTasks):
    latex = strip_code_fences(req.latex)
    try:
        pdf_path = compile_latex_to_pdf(latex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LaTeX compilation failed: {e}")
    filename = "cv.pdf"
    background.add_task(Path(pdf_path).unlink, missing_ok=True)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename=filename)


@app.post("/api/generate-pdf")
def generate_and_render(req: GenerateRequest, background: BackgroundTasks):
    if req.template_override:
        template = req.template_override
    elif req.template_id:
        try:
            template = read_template_by_id(req.template_id)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        template = read_template()
    try:
        latex = generate_latex_via_openai(input_text=req.input_text, template=template)
        latex = strip_code_fences(latex)
        pdf_path = compile_latex_to_pdf(latex)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Generation or compilation failed: {e}"
        )
    background.add_task(Path(pdf_path).unlink, missing_ok=True)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename="cv.pdf")


@app.post("/api/edit", response_model=GenerateResponse)
def edit(req: EditRequest):
    if not req.latex.strip():
        raise HTTPException(status_code=400, detail="LaTeX must not be empty.")
    if not req.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction must not be empty.")
    try:
        updated = edit_latex_via_openai(
            current_latex=req.latex, instruction=req.instruction
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI edit failed: {e}")
    updated = strip_code_fences(updated)
    return GenerateResponse(latex=updated)


@app.post("/api/import/linkedin", response_model=GenerateResponse)
def import_linkedin(req: LinkedInImportRequest):
    from http import HTTPStatus

    if not req.url or not req.url.lower().startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Ungültige URL.")
    if "linkedin.com" not in req.url.lower():
        raise HTTPException(status_code=400, detail="Bitte gib eine LinkedIn-URL an.")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        with httpx.Client(
            follow_redirects=True, timeout=20.0, headers=headers
        ) as client:
            resp = client.get(req.url)
    except httpx.HTTPError as e:
        logger.warning("LinkedIn fetch failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Konnte Profil nicht laden: {e}")

    if resp.status_code >= 400:
        original = resp.status_code
        try:
            valid_status = HTTPStatus(original).value
        except Exception:
            valid_status = None

        if valid_status is None:
            mapped = 403 if original == 999 else 502
        else:
            mapped = original if original in (401, 403, 404) else 502

        logger.info(
            "LinkedIn upstream error: status=%s mapped=%s url=%s ctype=%s",
            original,
            mapped,
            req.url,
            resp.headers.get("content-type", ""),
        )
        raise HTTPException(
            status_code=mapped,
            detail="Profil nicht abrufbar (Login erforderlich oder nicht öffentlich).",
        )

    ctype = resp.headers.get("content-type", "").lower()
    if "text/html" not in ctype:
        raise HTTPException(
            status_code=400, detail="Unerwarteter Inhaltstyp. Erwartet HTML."
        )

    html = resp.text
    if len(html) > 150_000:
        html = html[:150_000]

    if req.template_override:
        template = req.template_override
    elif req.template_id:
        try:
            template = read_template_by_id(req.template_id)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        template = read_template()
    try:
        latex = generate_latex_from_linkedin_html(profile_html=html, template=template)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"OpenAI-Generierung fehlgeschlagen: {e}"
        )

    latex = strip_code_fences(latex)
    if not latex.strip():
        raise HTTPException(status_code=500, detail="Kein LaTeX erzeugt.")
    return GenerateResponse(latex=latex)
