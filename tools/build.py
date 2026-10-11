#!/usr/bin/env python3
"""Build the LLM Compendium static site from markdown in content/."""
import html
import re
import shutil
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ARTICLES_OUT = ROOT / "articles"

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — LLM Compendium</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="site-header">
  <a class="site-title" href="../index.html">LLM Compendium</a>
</header>
<main class="article">
{body}
</main>
<footer class="site-footer">
  <p>Part of the <a href="../index.html">LLM Compendium</a>.</p>
</footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Compendium</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header home">
  <span class="site-title">LLM Compendium</span>
</header>
<main>
  <p class="tagline">Compendium on LLM topics focusing on inference.</p>
{sections}
</main>
<footer class="site-footer">
  <p>Built from <a href="https://github.com/xkazuka/llm-compendium">xkazuka/llm-compendium</a>.</p>
</footer>
</body>
</html>
"""


def slugify(stem: str) -> str:
    return slug if (slug := re.sub(r"[^a-z0-9]+", "-", stem.lower())).strip("-") else "article"


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def section_name(content_dir: Path, md_file: Path) -> str:
    rel = md_file.relative_to(content_dir)
    if len(rel.parts) == 1:
        return "Articles"
    return rel.parts[0].replace("_", " ").title()


def main() -> int:
    md_files = sorted(CONTENT.rglob("*.md"))
    if not md_files:
        print("No markdown files found in content/", file=sys.stderr)
        return 1

    if ARTICLES_OUT.exists():
        shutil.rmtree(ARTICLES_OUT)
    ARTICLES_OUT.mkdir()

    sections: dict[str, list[tuple[str, str]]] = {}
    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        title = extract_title(text, md_file.stem.replace("_", " ").title())
        body = markdown.markdown(text, extensions=["fenced_code", "tables"])
        slug = f"{md_file.parent.name}-{slugify(md_file.stem)}" if md_file.parent != CONTENT else slugify(md_file.stem)
        out = ARTICLES_OUT / f"{slug}.html"
        out.write_text(
            ARTICLE_TEMPLATE.format(title=html.escape(title), body=body),
            encoding="utf-8",
        )
        sections.setdefault(section_name(CONTENT, md_file), []).append((title, f"articles/{slug}.html"))
        print(f"built {out.relative_to(ROOT)}")

    section_html = []
    for name, entries in sorted(sections.items()):
        items = "\n".join(
            f'      <li><a href="{link}">{html.escape(title)}</a></li>'
            for title, link in entries
        )
        section_html.append(f'  <section class="toc-section">\n    <h2>{html.escape(name)}</h2>\n    <ul>\n{items}\n    </ul>\n  </section>')

    (ROOT / "index.html").write_text(
        INDEX_TEMPLATE.format(sections="\n".join(section_html)),
        encoding="utf-8",
    )
    print("built index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
