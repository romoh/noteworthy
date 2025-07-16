# noteworthy/notes_formattor.py

import markdown
from typing import Literal


def format_release_notes(notes: str, output_format: Literal["markdown", "html"] = "markdown") -> str:
    if output_format == "markdown":
        return notes
    elif output_format == "html":
        return markdown.markdown(notes, extensions=["extra", "sane_lists", "toc"])
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
