#!/usr/bin/env python3
"""
Parse quiz markdown files from 08_Documenti_Finali_Per_Esame and merge
them into the existing questions.json, deduplicating by question text.
"""

import json
import re
import random
import os

BASE = "/Users/giancarlocorso/Projects/EMBA/00.Lezioni/04.Organizzazione e Lavoro/08_Documenti_Finali_Per_Esame"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Map professor folders to chapter IDs
CHAPTER_MAP = {
    "01_Mura": 1,
    "02_Fiore": 2,
    "03_Zamarian": 3,
    "04_Comacchio": 4,
    # 05_Orzes: skip (no .md file)
    "06_Garofalo": 6,
    "07_Zilli": 7,
}

MD_FILES = {
    "01_Mura": "quiz-transizione-sostenibile-69.md",
    "02_Fiore": "quiz-digital-analytics-70.md",
    "03_Zamarian": "quiz-change-management-71.md",
    "04_Comacchio": "quiz-competenze-comportamento-organizzativo-77.md",
    "06_Garofalo": "quiz-diritto-lavoro-83.md",
    "07_Zilli": "quiz-relazioni-industriali.md",
}


def parse_md_file(filepath, chapter_id):
    """Parse a markdown quiz file into a list of question dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    questions = []
    # Split by ## headers (question blocks)
    blocks = re.split(r"\n## \d+\.\s*", content)

    for block in blocks[1:]:  # skip header before first ##
        lines = block.strip().split("\n")

        # Extract question text: first non-empty lines before options
        q_lines = []
        option_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("- **"):
                option_start = i
                break
            if stripped:
                q_lines.append(stripped)

        question_text = " ".join(q_lines)
        # Remove any leading title-like text before a question mark if there's a newline pattern
        # Some questions have a title line then the actual question
        if "\n" in block:
            # Check if first line is a title (no question mark) and second+ lines are the question
            first_line = lines[0].strip() if lines else ""
            rest_lines = []
            for i in range(1, option_start):
                if lines[i].strip():
                    rest_lines.append(lines[i].strip())
            if rest_lines and not first_line.endswith("?"):
                question_text = " ".join(rest_lines)
            elif not rest_lines and first_line:
                question_text = first_line

        # Parse options
        options = {}
        correct_letter = None
        option_lines = []

        for i in range(option_start, len(lines)):
            line = lines[i].strip()
            if line.startswith("- ") or line.startswith("- **"):
                option_lines.append(line)
            elif line.startswith("*") and not line.startswith("**"):
                # This is the explanation
                break
            elif option_lines and not line.startswith("#") and not line.startswith("---"):
                # Continuation of previous option
                option_lines[-1] += " " + line

        for opt_line in option_lines:
            # Check if this is the correct answer (bold)
            is_correct = "**" in opt_line and "✅" in opt_line

            # Extract letter and text
            # Patterns: "- A. text" or "- **A. text** ✅"
            match = re.match(r'-\s*\*{0,2}\s*([A-D])[\.\)]\s*(.*?)(?:\*{0,2}\s*✅?\s*)$', opt_line)
            if not match:
                # Try without strict end
                match = re.match(r'-\s*\*{0,2}\s*([A-D])[\.\)]\s*(.*)', opt_line)

            if match:
                letter = match.group(1)
                text = match.group(2).strip()
                # Clean up bold markers and checkmarks
                text = text.replace("**", "").replace("✅", "").strip()
                # Remove trailing period if present
                text = text.rstrip(".")
                options[letter] = text

                if is_correct:
                    correct_letter = letter

        # Extract explanation (italic text after options)
        explanation = ""
        in_explanation = False
        for i in range(option_start, len(lines)):
            line = lines[i].strip()
            if line.startswith("*") and not line.startswith("**") and line.endswith("*"):
                explanation = line.strip("*").strip()
                break
            elif line.startswith("*") and not line.startswith("**"):
                in_explanation = True
                explanation = line.lstrip("*").strip()
            elif in_explanation and line.endswith("*"):
                explanation += " " + line.rstrip("*").strip()
                break
            elif in_explanation and line and not line.startswith("---"):
                explanation += " " + line.strip()

        if len(options) == 4 and correct_letter and question_text:
            questions.append({
                "chapter": chapter_id,
                "question": question_text,
                "options": options,
                "correct": correct_letter,
                "explanation": explanation or "Nessuna spiegazione disponibile.",
            })

    return questions


def normalize_text(text):
    """Normalize text for comparison to detect duplicates."""
    t = text.lower().strip()
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t[:80]  # Compare first 80 chars


def main():
    # Load existing questions
    qfile = os.path.join(DATA_DIR, "questions.json")
    with open(qfile, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = data["questions"]
    max_id = max(q["id"] for q in existing)

    # Build set of existing question texts for dedup
    existing_texts = set()
    for q in existing:
        existing_texts.add(normalize_text(q["question"]))

    new_questions = []
    stats = {}

    for folder, md_file in MD_FILES.items():
        chapter_id = CHAPTER_MAP[folder]
        filepath = os.path.join(BASE, folder, md_file)

        if not os.path.exists(filepath):
            print(f"  ❌ File not found: {filepath}")
            continue

        parsed = parse_md_file(filepath, chapter_id)
        added = 0
        dupes = 0

        for q in parsed:
            norm = normalize_text(q["question"])
            if norm in existing_texts:
                dupes += 1
                continue

            max_id += 1
            q["id"] = max_id
            new_questions.append(q)
            existing_texts.add(norm)
            added += 1

        stats[folder] = {"parsed": len(parsed), "added": added, "dupes": dupes}
        print(f"  Cap. {chapter_id} ({folder}): {len(parsed)} parsed, {added} new, {dupes} duplicates")

    # Randomize correct answer positions for new questions
    random.seed(42)
    letters = ["A", "B", "C", "D"]
    for q in new_questions:
        items = list(q["options"].items())
        correct_text = q["options"][q["correct"]]
        random.shuffle(items)
        q["options"] = {letters[i]: text for i, (_, text) in enumerate(items)}
        for letter, text in q["options"].items():
            if text == correct_text:
                q["correct"] = letter
                break

    # Merge
    data["questions"].extend(new_questions)

    # Count distribution
    dist = {}
    for q in data["questions"]:
        dist[q["correct"]] = dist.get(q["correct"], 0) + 1

    print(f"\n  Total questions: {len(data['questions'])} (was {len(existing)}, +{len(new_questions)})")
    print(f"  Answer distribution: {dist}")

    # Per-chapter counts
    ch_counts = {}
    for q in data["questions"]:
        ch_counts[q["chapter"]] = ch_counts.get(q["chapter"], 0) + 1
    for ch_id in sorted(ch_counts):
        ch = next((c for c in data["chapters"] if c["id"] == ch_id), None)
        name = ch["title"] if ch else f"Cap. {ch_id}"
        print(f"  Cap. {ch_id}: {ch_counts[ch_id]} domande — {name}")

    # Save
    with open(qfile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n  ✅ Saved to {qfile}")


if __name__ == "__main__":
    main()
