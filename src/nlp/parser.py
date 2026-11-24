import re
from PyPDF2 import PdfReader

def extract_chapters_from_pdf(pdf_path: str) -> dict[str, str]:
    """Extracts full chapter bodies in exact numerical order (Chapter 1..N)."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # Match exact uppercase 'Chapter <digit>' (ignores lowercase inline 'chapter 3' references)
    pattern = re.compile(r'\b(Chapter\s+\d+)\b')
    matches = list(pattern.finditer(full_text))

    chapters = {}
    for i, match in enumerate(matches):
        chapter_title = re.sub(r'\s+', ' ', match.group(1)).strip()
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[start_idx:end_idx].strip()

        # Keep only the longest block per chapter (skips short Table of Contents entries)
        if len(body) > 500:
            if chapter_title not in chapters or len(body) > len(chapters[chapter_title]):
                chapters[chapter_title] = body

    # Sort chapters numerically: Chapter 1, Chapter 2, ..., Chapter 6
    sorted_chapters = dict(
        sorted(chapters.items(), key=lambda item: int(re.search(r'\d+', item[0]).group()))
    )
    print(f"Successfully extracted {len(sorted_chapters)} clean chapters: {list(sorted_chapters.keys())}")
    return sorted_chapters