import fitz  # PyMuPDF
import re
from collections import Counter

def is_noise(text):
    """Filter noise lines like short strings, addresses, or URLs."""
    text = text.strip()
    return (
        len(text) <= 2 or
        re.match(r'^\d+\.?$', text) or
        "@" in text or
        text.lower().startswith("www") or
        "http" in text.lower() or
        re.match(r"^\d{4,5}", text)  # Zip code or numeric ID
    )

def normalize_font_size(size, tolerance=0.5):
    """Round font size to reduce duplicates caused by float rounding."""
    return round(size / tolerance) * tolerance

def is_likely_form(text_blocks):
    """Detect forms by heuristics: many fields, all on one page."""
    if all(b["page"] == 1 for b in text_blocks) and len(text_blocks) > 25:
        return True
    return False

def extract_headings(pdf_path, debug=False):
    doc = fitz.open(pdf_path)

    # Step 1: Detect title from first page (largest font)
    first_page = doc[0]
    spans = []
    for block in first_page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["text"].strip():
                        spans.append({
                            "text": span["text"].strip(),
                            "size": normalize_font_size(span["size"]),
                            "font": span["font"],
                            "y": span["bbox"][1]
                        })

    spans.sort(key=lambda x: (-x["size"], x["y"]))
    title = ""
    if spans:
        largest_size = spans[0]["size"]
        title_lines = [s["text"] for s in spans if abs(s["size"] - largest_size) < 0.5 and not is_noise(s["text"])]
        title = " ".join(title_lines).strip()

    # Step 2: Extract all text blocks with font sizes
    font_sizes = set()
    text_blocks = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_spans = line.get("spans", [])
                if not line_spans:
                    continue
                text = " ".join(span["text"].strip() for span in line_spans).strip()
                if not text or is_noise(text):
                    continue
                size = normalize_font_size(line_spans[0]["size"])
                font_sizes.add(size)
                text_blocks.append({
                    "text": text,
                    "size": size,
                    "page": page_number + 1  # 1-based
                })

    # Step 3: Heuristically skip outlines for form-style documents
    if is_likely_form(text_blocks):
        return {
            "title": title,
            "outline": []
        }

    # Step 4: Heading level mapping
    sorted_sizes = sorted(font_sizes, reverse=True)
    size_level = {}
    if len(sorted_sizes) > 0:
        size_level[sorted_sizes[0]] = "H1"
    if len(sorted_sizes) > 1:
        size_level[sorted_sizes[1]] = "H2"
    if len(sorted_sizes) > 2:
        size_level[sorted_sizes[2]] = "H3"
    if len(sorted_sizes) > 3:
        size_level[sorted_sizes[3]] = "H4"

    outline = []
    seen = set()
    text_counter = Counter([b['text'] for b in text_blocks])

    for block in text_blocks:
        text = block["text"]
        size = block["size"]
        page = block["page"]

        if text == title or text in seen:
            continue
        seen.add(text)

        # Skip repeated footer/header lines
        if text_counter[text] > 5:
            continue

        # Skip very short or known form field labels
        if len(text.split()) <= 2 and not text.endswith(('.', ':')):
            continue
        if re.match(r"^(Name|Date|Age|Sex|Rs\.?|S\.No\.?|Signature)$", text, re.IGNORECASE):
            continue

        # Step 5: Assign level
        level = size_level.get(size)

        # Step 6: Fallback using heading patterns
        if not level:
            if re.match(r"^\d+\.\d+\.\d+", text):  # 1.1.1
                level = "H4"
            elif re.match(r"^\d+\.\d+", text):     # 1.1
                level = "H3"
            elif re.match(r"^\d+\.", text):        # 1.
                level = "H2"
            elif text.upper().startswith("APPENDIX"):
                level = "H2"

        if level:
            outline.append({
                "level": level,
                "text": text,
                "page": page
            })
        elif debug:
            print(f"[Unmatched] Page {page}: {text} (size={size})")

    return {
        "title": title,
        "outline": outline
    }
