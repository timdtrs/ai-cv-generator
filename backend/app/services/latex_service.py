import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def compile_latex_to_pdf(latex_source: str) -> str:
    """
    Writes LaTeX source to a temp directory and compiles it using tectonic.
    Returns the absolute path to the resulting PDF.
    Raises CalledProcessError on failure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_path = tmp_path / "main.tex"
        tex_path.write_text(latex_source, encoding="utf-8")

        # Choose a LaTeX engine.
        # If the source uses fontspec/polyglossia or explicit XeLaTeX-only commands, prefer xelatex.
        lower_src = latex_source.lower()
        needs_xe = bool(
            # fontspec (usepackage or requirepackage)
            re.search(r"\\\s*(usepackage|requirepackage)\s*\{\s*fontspec\s*\}", lower_src)
            # unicode-math strongly implies XeLaTeX/LuaLaTeX
            or re.search(r"\\\s*(usepackage|requirepackage)\s*\{\s*unicode\-math\s*\}", lower_src)
            # Common XeLaTeX commands
            or "\\setmainfont" in lower_src
            or "\\newfontfamily" in lower_src
            or "polyglossia" in lower_src
        )

        engine = None
        if needs_xe and shutil.which("xelatex"):
            engine = "xelatex"
        else:
            if shutil.which("tectonic"):
                engine = "tectonic"
            elif shutil.which("pdflatex"):
                engine = "pdflatex"
            elif shutil.which("xelatex"):
                engine = "xelatex"
            else:
                raise RuntimeError(
                    "No LaTeX engine found. Install 'tectonic' (recommended) or 'pdflatex/xelatex'."
                )

        if engine == "tectonic":
            # Tectonic produces main.pdf in the same directory.
            try:
                result = subprocess.run(
                    ["tectonic", str(tex_path)],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except FileNotFoundError:
                # Defensive: in case the binary disappears between which() and run()
                raise RuntimeError("'tectonic' not found on PATH. Please install it.")
            if result.returncode != 0:
                raise RuntimeError(
                    f"Tectonic failed (code {result.returncode}). stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
        else:
            # Fallback using (pdf|xe)latex; run twice to resolve refs.
            latex_cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
            for i in range(2):
                try:
                    result = subprocess.run(
                        latex_cmd,
                        cwd=tmp_path,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                except FileNotFoundError:
                    raise RuntimeError(f"'{engine}' not found on PATH. Please install a LaTeX engine.")
                if result.returncode != 0:
                    raise RuntimeError(
                        f"{engine} failed (code {result.returncode}). stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )

        pdf_path = tmp_path / "main.pdf"
        if not pdf_path.exists():
            raise RuntimeError("PDF not produced. Check LaTeX source.")

        # Move PDF to a stable temp file outside the ctx so FileResponse can stream it
        final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        final_tmp.close()
        Path(final_tmp.name).write_bytes(pdf_path.read_bytes())
        return str(Path(final_tmp.name).resolve())
