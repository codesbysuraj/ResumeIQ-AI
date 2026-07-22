"""
Security utilities for input sanitization and basic protection.

Provides safe filename handling and user text sanitization to prevent
path traversal attacks and injection of control characters.
"""
import re
import unicodedata
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded filename to prevent path traversal and invalid characters.

    Steps:
        1. Normalize Unicode (e.g., accented characters → ASCII equivalents).
        2. Extract only the basename (strips directory components).
        3. Replace unsafe characters with underscores.
        4. Collapse repeated underscores/dots.
        5. Strip leading/trailing special characters.
        6. Fallback to "unnamed_file" if the result is empty.

    Args:
        filename: The original filename from the uploaded file.

    Returns:
        A safe filename string suitable for filesystem storage.

    Examples:
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("my  résumé (final).pdf")
        'my_resume_final_.pdf'
    """
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Extract only the basename to prevent path traversal
    filename = Path(filename).name

    # Replace any character that isn't alphanumeric, hyphen, underscore, or dot
    filename = re.sub(r"[^\w\-.]", "_", filename)

    # Collapse multiple consecutive underscores or dots
    filename = re.sub(r"_{2,}", "_", filename)
    filename = re.sub(r"\.{2,}", ".", filename)

    # Strip leading/trailing special characters
    filename = filename.strip("_.")

    if not filename:
        filename = "unnamed_file"

    return filename


def sanitize_text_input(text: str) -> str:
    """
    Sanitize user-provided text input (e.g., job descriptions, notes).

    Removes control characters while preserving readable formatting
    such as newlines and standard whitespace.

    Args:
        text: Raw user text input.

    Returns:
        Cleaned text with control characters removed and whitespace normalized.
    """
    # Remove null bytes and control characters (keep newlines \\n and tabs \\t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize horizontal whitespace (collapse multiple spaces, preserve newlines)
    text = re.sub(r"[^\S\n]+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
