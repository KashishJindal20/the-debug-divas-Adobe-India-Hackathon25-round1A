# 📄 Adobe Challenge Round 1A - PDF Heading Extractor

## 🧠 Problem Statement
Extract structured heading information (Title, H1, H2, etc.) from PDF documents. The extracted headings should be saved in `.json` format with the same base filename as the original `.pdf`.

---

## 🚀 Approach

We use a rule-based method that combines PDF layout features with textual heuristics. The steps include:

- **Text & Layout Extraction**: Using `PyMuPDF` to extract text, font size, style, position.
- **Heading Classification**: Classify text blocks as Title, H1, H2, H3, etc. based on font size, boldness, and layout context.
- **Post-processing**: Filter noise, ensure hierarchy consistency, and write structured output.

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.11
- **Libraries**:
  - [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/) for PDF parsing
  - `spaCy`, `scikit-learn`, `numpy` (optional NLP helpers)
  - No internet/network access required during runtime

All required packages are listed in `requirements.txt`.

---

## 📁 Directory Structure

ROUND1A/
│
├── input/ # PDF input files (mounted by Docker)
│ ├── file01.pdf
│ └── ...
│
├── output/ # Output JSON files (mounted by Docker)
│ ├── file01.json
│ └── ...
│
├── src/ # Core logic
│ ├── extractor.py # Contains process_pdf() method
│
├── run.py # Entrypoint script
├── Dockerfile
├── requirements.txt
└── README.md



---

## 🐳 Docker Setup

### 🏗️ Build the Docker Image

```bash
docker build --platform linux/amd64 -t headingextractor:adobe1a .
```

▶️ Run the Container
On Windows PowerShell:
```bash
docker run --rm `
  -v ${PWD}\input:/app/input `
  -v ${PWD}\output:/app/output `
  --network none `
  headingextractor:adobe1a
```
On Unix/macOS/Linux (bash or WSL):
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  headingextractor:adobe1a
```
✅ What the Container Does
It reads all .pdf files from /app/input

Processes each PDF to extract heading structure

Writes a corresponding .json file to /app/output

For example: file01.pdf → file01.json

📦 Constraints Met
Constraint	Status ✅
CPU-only (amd64)	✅
Model size < 200MB	✅
No network access	✅
Offline, dependency-contained	✅
Processes all PDFs automatically	✅

🧪 Sample Output Format (file01.json)

[
  {
    "text": "Introduction",
    "level": "H1",
    "page": 1
  },
  {
    "text": "Overview of Problem",
    "level": "H2",
    "page": 1
  },
  ...
]
