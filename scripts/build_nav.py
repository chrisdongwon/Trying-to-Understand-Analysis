#!/usr/bin/env python3
import os, re, json

EXERCISES_DIR = "exercises"
THEOREMS_DIR = "theorems"
CHAPTERS_DIR = "chapters"
CHAPTER_RE = re.compile(r"^chapter-(\d+)$")
EX_FILE_RE = re.compile(r"^ex-(\d+)-(\d+)-(\d+)\.qmd$")
THM_FILE_RE = re.compile(r"^theorem-(\d+)-(\d+)-(\d+)\.qmd$")  # adjust if numbering differs

def get_title(path, fallback):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:30]:
            if line.strip() == "---":
                break
            m = re.match(r'^\s*title:\s*["\']?(.+?)["\']?\s*$', line)
            if m:
                return m.group(1)
    return fallback

def list_chapters(base_dir):
    chapters = []
    if not os.path.isdir(base_dir):
        return chapters
    for name in sorted(os.listdir(base_dir)):
        m = CHAPTER_RE.match(name)
        if m and os.path.isdir(os.path.join(base_dir, name)):
            chapters.append((int(m.group(1)), name))
    chapters.sort()
    return chapters

def main():
    nav = {}

    # ---- Exercises: full prev/next/index chain ----
    ex_chapters = list_chapters(EXERCISES_DIR)
    flat = []
    for _, chap_name in ex_chapters:
        listing_path = f"/{CHAPTERS_DIR}/{chap_name}.qmd"
        chap_dir = os.path.join(EXERCISES_DIR, chap_name)
        files = []
        for fname in os.listdir(chap_dir):
            m = EX_FILE_RE.match(fname)
            if m:
                sec, num = int(m.group(2)), int(m.group(3))
                files.append((sec, num, fname))
        files.sort()
        for sec, num, fname in files:
            full_path = os.path.join(chap_dir, fname)
            key = fname[:-4]
            fallback_title = f"Exercise {EX_FILE_RE.match(fname).group(1)}.{sec}.{num}"
            title = get_title(full_path, fallback_title)
            root_path = "/" + full_path.replace(os.sep, "/")
            flat.append({"key": key, "path": root_path, "title": title, "listing": listing_path})

    for i, entry in enumerate(flat):
        prev_entry = flat[i - 1] if i > 0 else None
        next_entry = flat[i + 1] if i < len(flat) - 1 else None
        nav[entry["key"]] = {
            "title": entry["title"],
            "prev": {"path": prev_entry["path"], "title": prev_entry["title"]} if prev_entry else None,
            "next": {"path": next_entry["path"], "title": next_entry["title"]} if next_entry else None,
            "index": entry["listing"],
        }

    # ---- Theorems: index-only, no prev/next ----
    thm_chapters = list_chapters(THEOREMS_DIR)
    thm_count = 0
    for _, chap_name in thm_chapters:
        listing_path = f"/{CHAPTERS_DIR}/{chap_name}.qmd"
        chap_dir = os.path.join(THEOREMS_DIR, chap_name)
        for fname in os.listdir(chap_dir):
            if not fname.endswith(".qmd"):
                continue
            m = THM_FILE_RE.match(fname)
            key = fname[:-4]
            fallback_title = key.replace("-", " ").title()
            full_path = os.path.join(chap_dir, fname)
            title = get_title(full_path, fallback_title)
            nav[key] = {
                "title": title,
                "prev": None,
                "next": None,
                "index": listing_path,
            }
            thm_count += 1

    with open("nav.json", "w", encoding="utf-8") as f:
        json.dump(nav, f, indent=2)

    print(f"nav.json written with {len(flat)} exercises and {thm_count} theorems across "
          f"{len(ex_chapters)} exercise chapters / {len(thm_chapters)} theorem chapters")

if __name__ == "__main__":
    main()
    