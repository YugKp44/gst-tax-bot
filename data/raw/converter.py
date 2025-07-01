import os
import glob
import pdfplumber
import re
import json
from pathlib import Path

# 1. Define where your raw PDFs and faqs.json live
SCRIPT_DIR = Path(__file__).parent
PDF_GLOB   = SCRIPT_DIR / "*.pdf"
JSON_PATH  = SCRIPT_DIR / "faqs.json"

# 2. Improved Extraction: handles Q: ... A: ... format correctly
def extract_faqs_from_pdf(pdf_path: Path):
    faqs = []
    text = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text += txt + "\n"

    # Find all Q: ... A: ... blocks using regex
    qa_blocks = re.findall(
        r"Q:\s*(.+?)\s*A:\s*(.+?)(?=\s*Q:|\Z)",  # match up to next Q: or end of file
        text,
        flags=re.DOTALL
    )

    for question, answer in qa_blocks:
        faqs.append({
            "question": question.strip(),
            "answer": answer.strip(),
            "source": pdf_path.name
        })

    return faqs

# 3. Load existing JSON (if any)
if JSON_PATH.exists():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        existing = json.load(f)
else:
    existing = []

# 4. Build a map to dedupe by question
faq_map = {item["question"]: item for item in existing}

# 5. Process each PDF in the folder
pdf_files = sorted(glob.glob(str(PDF_GLOB)))
print(f"Found {len(pdf_files)} PDF(s) in {SCRIPT_DIR}")

for pdf_file in pdf_files:
    pdf_path = Path(pdf_file)
    print(f" → Processing {pdf_path.name}")
    new_faqs = extract_faqs_from_pdf(pdf_path)
    for faq in new_faqs:
        faq_map[faq["question"]] = faq  # overwrite or add new

# 6. Save final merged + deduplicated JSON
merged = list(faq_map.values())
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"✅ Total FAQs after merge: {len(merged)} saved to {JSON_PATH}")
