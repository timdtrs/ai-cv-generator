import os
from typing import Optional

from openai import OpenAI


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def generate_latex_via_openai(input_text: str, template: Optional[str] = None) -> str:
    """
    Calls OpenAI to transform input_text into full LaTeX code for a CV.
    If a LaTeX template is provided, instructs the model to adapt and fill it.
    Returns raw LaTeX (no code fences).
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    system_msg = (
        "You are an expert LaTeX assistant that writes production-ready, compilable LaTeX. "
        "You only output raw LaTeX with no Markdown fences or commentary."
    )
    user_msg = (
        "Create a high-quality LaTeX CV from the following notes. "
        "Return complete LaTeX that compiles standalone with article/report or a typical CV class. "
        "Do not include Markdown code fences.\n\n"
        f"Notes:\n{input_text.strip()}\n"
    )

    if template:
        user_msg += (
            "\nUse the following LaTeX template as the base. Keep its structure, commands, and styling, "
            "and fill in content based on the notes. If fields are missing, omit them cleanly.\n\n"
            f"Template:\n{template}"
        )

    client = _client()
    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    return completion.choices[0].message.content or ""


def edit_latex_via_openai(current_latex: str, instruction: str) -> str:
    """
    Calls OpenAI to modify an existing LaTeX document according to a natural-language instruction.
    Returns full, compilable LaTeX without Markdown fences.
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    system_msg = (
        "You are an expert LaTeX assistant. You return complete, compilable LaTeX only, "
        "with no Markdown code fences or commentary. Preserve the document class, preamble, "
        "and overall structure unless the instruction explicitly requests otherwise."
    )
    user_msg = (
        "You are given an existing LaTeX document and an edit request. "
        "Apply the requested change to the LaTeX. Return the FULL updated LaTeX document.\n\n"
        f"Instruction:\n{instruction.strip()}\n\n"
        f"Current LaTeX:\n{current_latex}"
    )

    client = _client()
    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    return completion.choices[0].message.content or ""


 
