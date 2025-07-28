import os
import json
from src.extractor import extract_headings

input_dir = "./input"
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(input_dir, filename)
        result = extract_headings(pdf_path)
        json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)
