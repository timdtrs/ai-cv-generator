FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Base tools and TeX Live (pdflatex-only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget perl xz-utils build-essential \
    texlive-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-xetex texlive-fonts-extra tex-gyre latexmk \
    fonts-dejavu-core fonts-liberation fonts-noto-core fonts-roboto-unhinted fonts-lato fonts-inter fonts-linuxlibertine fontconfig \
    && rm -rf /var/lib/apt/lists/* && fc-cache -f -v || true

# Verify LaTeX engine availability (pdflatex)
RUN pdflatex --version

WORKDIR /app

# Use files relative to the backend build context
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

# Seed default template into a writable templates directory
RUN mkdir -p /app/templates \
    && cp /app/app/templates/cv_template.tex /app/templates/cv_template.tex || true

ENV TEMPLATE_DIR=/app/templates

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
