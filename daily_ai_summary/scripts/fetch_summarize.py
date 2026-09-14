#!/usr/bin/env python3
"""fetch_summarize.py
Fetch latest AI articles from the curated source list, select top 5 (by publish date), generate short summaries using Gemini, and write a markdown file for the day.

Requirements (install via pip):
  feedparser, requests, python-dotenv
  (Gemini SDK will be used via `google.generativeai`).
"""

import os
import datetime
import feedparser
import requests
from pathlib import Path

# Load environment variables (e.g., GEMINI_API_KEY) from .env if present
from dotenv import load_dotenv
load_dotenv()

# Gemini integration removed – using simple snippet as summary

def read_sources(file_path: Path):
    sources = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and "http" in line:
                # split by | and grab the last column (URL)
                parts = [p.strip() for p in line.split("|")]
                url = parts[-1]
                sources.append(url)
    return sources

def fetch_feed(url: str, max_items: int = 20):
    try:
        d = feedparser.parse(url)
        return d.entries[:max_items]
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

def select_top_articles(entries, limit=5):
    # Sort by published date (newest first)
    sorted_entries = sorted(
        entries,
        key=lambda e: e.get("published_parsed", None) or e.get("updated_parsed", None),
        reverse=True,
    )
    return sorted_entries[:limit]

def summarize_article(title: str, link: str, snippet: str):
    """Return a short two‑sentence summary using the article snippet."""
    # Use the first two sentences of the snippet if possible.
    sentences = [s.strip() for s in snippet.split('.') if s.strip()]
    if len(sentences) >= 2:
        short = ". ".join(sentences[:2]) + "."
    else:
        short = snippet.strip()
    return short

def main():
    project_root = Path(__file__).resolve().parents[2]  # daily_ai_summary
    src_file = project_root / "sources.md"
    sources = read_sources(src_file)
    all_entries = []
    for src in sources:
        entries = fetch_feed(src)
        all_entries.extend(entries)
    top_five = select_top_articles(all_entries, limit=5)

    summaries = []
for e in top_five:
    title = e.get("title", "(no title)")
    link = e.get("link", "#")
    snippet = e.get("summary", "")
    short = summarize_article(title, link, snippet)
    summaries.append({"title": title, "link": link, "summary": short})

    # Write markdown file
    today = datetime.date.today().isoformat()
    output_dir = project_root / "site" / "content"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{today}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# AI News Summary – {today}\n\n")
        f.write("| Title | Source | Summary |\n")
        f.write("|---|---|---|\n")
        for s in summaries:
            f.write(f"| [{s['title']}]({s['link']}) | {s['link']} | {s['summary']} |\n")
    print(f"Wrote summary to {out_path}")

if __name__ == "__main__":
    main()
