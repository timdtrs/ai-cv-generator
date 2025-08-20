import os
import re
from typing import Optional

from openai import OpenAI


SYSTEM_PROMPT = """
Developer: Beginne mit einer kurzen, konzeptuellen Checkliste (3–7 Punkte), die die wichtigsten Schritte zur Erstellung des LaTeX-Lebenslaufs aufführt. Erzeuge aus strukturierten Benutzereingaben und einer bereitgestellten LaTeX-Vorlage einen inhaltlich vollständigen, professionell formulierten und keyword-optimierten Lebenslauf als LaTeX-Quelltext. Setze relevante CV-spezifische Schlüsselbegriffe ein, passe Formulierungen an Branche und ggf. Zielposition an und variiere stilistisch im Rahmen professioneller Standards. Berücksichtige kreative, professionelle und positionsadäquate Textgestaltung, orientiere dich strikt an der Placeholder-Struktur der LaTeX-Vorlage und ignoriere Userdaten ohne zugehörigen Platzhalter.

### Vorgehensweise
- **Input:** Du erhältst strukturierte Benutzerdaten (wie Name, Kontakt, Berufserfahrung, Skills, Ausbildung, etc.) und eine LaTeX-Vorlage (als Klartext oder mit Platzhaltern). Die Eingabeschemata können variieren; gib nur aus, was in der Vorlage referenziert und im Userinput vorhanden ist.
- **Analyse (Reasoning):** Unmittelbar vor der LaTeX-Ausgabe analysierst du Userdaten, identifizierst Kernkompetenzen und branchenspezifisch relevante Stationen und optimierst gezielt auf aussagekräftige Schlüsselbegriffe (ggf. in mehreren Sprachen, falls im Userinput erkennbar). Entscheide situationsabhängig über Formulierungsebenen, z.B. technische Tiefe oder Führungserfahrung.
- Ergänze die Daten nur an Stellen, die in der LaTeX-Vorlage eindeutig vorgesehen sind, und wandle diese in hochwertige, professionelle Bullet Points bzw. präzise Kurztexte um. Nicht referenzierte Informationen werden weggelassen.
- Vermeide jegliche Fülltexte oder Platzhalter in nicht belegten Bereichen, gebe keine Fehler- oder Hinweistexte aus, wenn Abschnitte fehlen oder nicht vollständig sind.

### Ausgabeformat
- **Output:** Zuerst folgt IMMER die Checkliste und dann das Reasoning (Kurzanalyse und Strategie), direkt danach ausschließlich reiner LaTeX-Quellcode, exakt gemäß der bereitgestellten Vorlage.
- Die finale LaTeX-Ausgabe enthält ausschließlich LaTeX-Code, ohne zusätzliche Kommentare, Codeblöcke, Erklärtexte, Markdown-Formatierung oder andere Metainformationen.
- Textlänge und Detailgrad orientieren sich an Umfang der Userdaten und der Vorlagenstruktur. Die Gesamtlänge des Lebenslaufs entspricht branchenüblichen Standards (1–2 Seiten, sofern durch Daten und Vorlage möglich).

### Zusätzliche Hinweise
- Passe den Schwierigkeitsgrad und die Kreativität der Formulierungen an individuelle Angaben und Zielbranchen an.
- Bei internationalen oder mehrsprachigen Vorlagen/Userdaten werden Schlüsselbegriffe und Formulierungen entsprechend gewählt.
- Bei fehlenden oder nicht belegten Abschnitten in Daten/Vorlage werden diese einfach ausgelassen, ohne Ersatztexte oder Fehlermeldungen.
- Übertreibe nicht bei der Beschreibung von Erfahrungen und Fähigkeiten, erfinde nichts dazu.
- Liste bei den Fähigkeiten nur die wichtigsten Fähigkeiten auf, die mehrfach im Lebenslauf vorkommen.
- Benutze die Sprache, die in den Benutzerdaten verwendet wird.
- Passe Formatierungen an, falls notwendig.

### Ablauf
1. Fertige eine kurze Checkliste der wichtigsten Schritte an.
2. Analyse/Aufbereitung der Userdaten und Zuordnung zu den Vorlagenplatzhaltern (Reasoning).
3. Generiere danach ausschließlich den vollständigen, angepassten LaTeX-Quelltext basierend auf Vorlage und Userdaten.

"""


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
    # Verwende den zentral definierten System-Prompt für die CV-Generierung
    system_msg = SYSTEM_PROMPT
    user_msg = (
        "Erzeuge aus den folgenden Notizen einen professionellen Lebenslauf. "
        "Gib nach Checkliste und kurzer Analyse ausschließlich vollständigen LaTeX-Quelltext aus.\n\n"
        f"Notizen:\n{input_text.strip()}\n"
    )

    if template:
        user_msg += (
            "\nNutze die folgende LaTeX-Vorlage als Grundlage. Erhalte Struktur, Kommandos und Stil, "
            "fülle Inhalte basierend auf den Notizen und lasse nicht belegte Bereiche sauber weg.\n\n"
            f"Vorlage:\n{template}"
        )

    client = _client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    raw = completion.choices[0].message.content or ""
    return _extract_latex(raw)


def edit_latex_via_openai(current_latex: str, instruction: str) -> str:
    """
    Calls OpenAI to modify an existing LaTeX document according to a natural-language instruction.
    Returns full, compilable LaTeX without Markdown fences.
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # Beim Editieren weiterhin strikt nur LaTeX zurückgeben, ohne zusätzliche Vorrede
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
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    return completion.choices[0].message.content or ""


def generate_latex_from_linkedin_html(
    profile_html: str, template: Optional[str] = None
) -> str:
    """
    Transform raw (public) LinkedIn profile HTML into a full LaTeX CV using OpenAI.
    Returns raw LaTeX (no code fences).
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # Nutze den zentralen System-Prompt; die Extraktion aus HTML wird im User-Kontext beschrieben
    system_msg = SYSTEM_PROMPT
    user_msg = (
        "Du erhältst den HTML-Inhalt eines LinkedIn-Profils (evtl. unvollständig oder verrauscht).\n"
        "Extrahiere Name, Headline/Zusammenfassung, Erfahrung (Firmen, Rollen, Daten, Bulletpoints), Ausbildung, Skills, Projekte und Zertifikate.\n"
        "Erzeuge danach gemäß Vorlage einen vollständigen, kompilierbaren LaTeX-Lebenslauf.\n\n"
        "HTML:\n" + profile_html
    )

    if template:
        user_msg += (
            "\n\nNutze die folgende LaTeX-Vorlage als Grundlage. Erhalte Struktur und Stil; fülle sie mit den extrahierten Daten.\n\n"
            f"Vorlage:\n{template}"
        )

    client = _client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    raw = completion.choices[0].message.content or ""
    return _extract_latex(raw)


def _extract_latex(text: str) -> str:
    """Extract likely LaTeX from a response that may include preamble text.

    Strategy:
    - Remove Markdown code fences if present
    - Prefer capturing from \documentclass onward
    - Fallback to from \begin{document} onward
    - Otherwise, return original trimmed text
    """
    if not text:
        return ""
    # Strip code fences if the model added them despite instructions
    fence = re.search(r"```(?:latex)?\n([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()

    # Try to capture from \documentclass to end
    m = re.search(r"(\\documentclass[\s\S]*)", text)
    if m:
        return m.group(1).strip()

    # Fallback: from begin{document}
    m = re.search(r"(\\begin\{document\}[\s\S]*)", text)
    if m:
        return m.group(1).strip()

    # As last resort, return trimmed text
    return text.strip()
