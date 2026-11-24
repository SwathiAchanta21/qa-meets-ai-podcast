import os
import json
import re
from src.nlp.parser import extract_chapters_from_pdf
from src.nlp.planner import generate_chapter_script

def sanitize_filename(name: str) -> str:
    """Converts a chapter title like 'Chapter 1: Intro' into a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_').lower()

def run_pipeline():
    pdf_path = os.path.join("data", "input_pdfs", "ASTQB_AI_Testing.pdf")
    output_dir = os.path.join("data", "intermediate")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Parse the PDF into chapters
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find PDF at {pdf_path}")
        return
        
    chapters = extract_chapters_from_pdf(pdf_path)
    
    if not chapters:
        print("No chapters found. We may need to adjust the chapter regex in parser.py to match the ASTQB PDF format.")
        return

    # Step 2: Generate and save JSON scripts for each chapter
    for chapter_title, chapter_text in chapters.items():
        print(f"\n--- Processing {chapter_title} ---")
        
        # Safety check: skip tiny/empty table-of-contents matches
        if len(chapter_text) < 200:
            print(f"Skipping '{chapter_title}' (too short, likely a Table of Contents entry).")
            continue
            
        script_data = generate_chapter_script(chapter_title, chapter_text)
        
        safe_name = sanitize_filename(chapter_title)
        output_file = os.path.join(output_dir, f"{safe_name}_script.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=4, ensure_ascii=False)
            
        print(f"Saved script to: {output_file}")

if __name__ == "__main__":
    run_pipeline()