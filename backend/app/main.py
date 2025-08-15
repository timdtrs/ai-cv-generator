import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .services.openai_service import (
    generate_latex_via_openai,
    edit_latex_via_openai,
)
from .services.latex_service import compile_latex_to_pdf


class GenerateRequest(BaseModel):
    input_text: str
    template_override: Optional[str] = None


class GenerateResponse(BaseModel):
    latex: str


class TemplateUpdateRequest(BaseModel):
    template: str


class RenderRequest(BaseModel):
    latex: str

class EditRequest(BaseModel):
    latex: str
    instruction: str


 


def get_template_dir() -> Path:
    return Path(os.getenv("TEMPLATE_DIR", "/app/templates")).resolve()


def get_default_template_path() -> Path:
    tmpl_dir = get_template_dir()
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    return tmpl_dir / "cv_template.tex"


def read_template() -> str:
    path = get_default_template_path()
    if not path.exists():
        # Fallback to packaged default inside app if present
        packaged = Path(__file__).parent / "templates" / "cv_template.tex"
        if packaged.exists():
            return packaged.read_text(encoding="utf-8")
        raise FileNotFoundError("No LaTeX template found.")
    return path.read_text(encoding="utf-8")


def write_template(content: str) -> None:
    path = get_default_template_path()
    path.write_text(content, encoding="utf-8")


def strip_code_fences(text: str) -> str:
    # Remove ```latex ... ``` or ``` ... ``` fences if present
    code_block = re.search(r"```(?:latex)?\n([\s\S]*?)```", text, re.IGNORECASE)
    if code_block:
        return code_block.group(1).strip()
    return text.strip()


app = FastAPI(title="CV Generator API")

# CORS: allow local dev and nginx-served frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/template")
def get_template():
    try:
        return {"template": read_template()}
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
    template = req.template_override if req.template_override else read_template()
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
    # cleanup after response is sent
    background.add_task(Path(pdf_path).unlink, missing_ok=True)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename=filename)


@app.post("/api/generate-pdf")
def generate_and_render(req: GenerateRequest, background: BackgroundTasks):
    template = req.template_override if req.template_override else read_template()
    try:
        latex = generate_latex_via_openai(input_text=req.input_text, template=template)
        latex = strip_code_fences(latex)
        pdf_path = compile_latex_to_pdf(latex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation or compilation failed: {e}")
    background.add_task(Path(pdf_path).unlink, missing_ok=True)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename="cv.pdf")


@app.post("/api/edit", response_model=GenerateResponse)
def edit(req: EditRequest):
    if not req.latex.strip():
        raise HTTPException(status_code=400, detail="LaTeX must not be empty.")
    if not req.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction must not be empty.")
    try:
        updated = edit_latex_via_openai(current_latex=req.latex, instruction=req.instruction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI edit failed: {e}")
    updated = strip_code_fences(updated)
    return GenerateResponse(latex=updated)


 
