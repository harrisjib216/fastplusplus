#!/usr/bin/env python3
"""Book mining (docs/QUEUE.md section F, books): extract a C++ book's text, split it into page-tagged chunks
and render one mining prompt per chunk. The book file, its text, the chunks and the prompts all stay in a work
directory OUTSIDE the repository (books are copyrighted); only the agents' JSON seed arrays are committed, as
data/seeds/raw/book-<slug>__<NN>.json, and they flow on through seeds_merge.py and seed_backfill.py."""
import argparse, json, re, subprocess
from pathlib import Path

from mine import taxonomy, slug  # noqa: E402  (same directory)

ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "data" / "seeds"

PROMPT = """You are mining one chunk of a C++ book to produce SEED CANDIDATES for a
catalog of implementations that are faster than a default/incumbent tool. You
are NOT verifying anything; a later agent looks for proof. Extract every
library, project or benchmarked implementation the chunk names that might
plausibly qualify, with enough metadata that a later agent can find it.

Today's date: {today}
Book:         {title}
Chunk:        {chunk_path}  (part {n} of {total}; "[p. N]" lines mark PDF pages)
Skip list:    {known} (canonical lowercase repo URLs already catalogued or
              seeded; grep it before including an entry; the orchestrator
              dedups again downstream, so when unsure include)

=====================================================================
PROCESS
=====================================================================
1. Read the chunk in slices (sed -n ranges or grep), not all at once if it
   is long. Look for: named libraries and projects, "X is faster than Y"
   comparisons, benchmark tables or timings, the book's own companion code
   repository, and replacements for std:: containers, algorithms, allocators,
   strings, I/O, formatting, hashing, sorting, parsing, concurrency.
2. For each library or project, find its canonical home: the URL printed in
   the book if any; otherwise open at most one github.com page per project
   (WebFetch https://github.com/OWNER/REPO, or github.com/topics) to resolve
   it. No URL after that: still record it with repo_url null.
3. A technique the book benchmarks with numbers but no public code (for
   example a hand-rolled flat map timed against std::map) is kind
   "technique": record it with repo_url set to the book's companion
   repository when the code lives there, else null.
4. Map each entry to a wave and category from the taxonomy below and guess
   the baseline it would be compared against. These are guesses; mark
   confidence accordingly.

=====================================================================
HARD RULES
=====================================================================
- Copyright: paraphrase. Never copy code from the book, and quote at most
  25 words per entry. Never write book text anywhere but your scratch dir.
- Do not assign an evidence tier. A book's own numbers are first-party
  unless the book ran someone else's published benchmark.
- Never send the user's email, name or other personal identifiers to any
  outside service. Write nothing in the repository except the output file.
- Style: caveman ultra in all your own text and your final reply (fragments,
  no articles, no filler, no arrows, no invented abbreviations; names,
  numbers and errors exact); the JSON output stays normal prose.
- Write ONLY the JSON array (an empty array when the chunk names nothing) to:
    {output_path}
  then check it parses: python3 -c "import json,sys; json.load(open(sys.argv[1]))" {output_path}
- Final reply to the orchestrator: one line, entry count and names.

=====================================================================
CATALOG TAXONOMY (wave: categories)
=====================================================================
{taxonomy}

=====================================================================
OUTPUT SCHEMA
=====================================================================
[
  {{
    "name": "string",
    "kind": "library" | "technique",
    "repo_url": "string or null",
    "listed_description": "one-line paraphrase of what the book says it is",
    "listed_license": "license the book states, or null",
    "performance_claim_in_description": true | false,
    "claim_text": "the book's claim with its numbers, paraphrased or quoted (max 25 words), or null",
    "book_benchmark": "what the book measured (workload, baseline, compiler, flags, CPU) as far as stated, or null",
    "guessed_wave": "e.g. stdlib-replacements",
    "guessed_category": "e.g. hash-maps-sets",
    "guessed_baseline": "e.g. std::unordered_map, or null",
    "found_in": "book: {title}, p. N",
    "confidence": 0.0-1.0
  }}
]
"""


def extract(book, work):
    """Return the book's plain text with '[p. N]' page markers where the format has pages."""
    suffix = book.suffix.lower()
    if suffix == ".pdf":
        txt = work / "book.txt"
        subprocess.run(["pdftotext", "-layout", str(book), str(txt)], check=True)
        pages = txt.read_text(errors="replace").split("\f")
        return "\n".join(f"[p. {i}]\n{p}" for i, p in enumerate(pages, 1) if p.strip())
    if suffix in (".epub", ".docx", ".html", ".htm", ".odt"):
        return subprocess.run(["pandoc", "-t", "gfm-raw_html", "--wrap=none", str(book)],  # gfm keeps link URLs
                              check=True, capture_output=True, text=True).stdout
    return book.read_text(errors="replace")


def split(text, size):
    """Cut at paragraph or page boundaries into chunks of about `size` characters; a chunk that starts
    mid-page opens with that page's marker."""
    chunks, cur, n, page = [], [], 0, None
    for para in re.split(r"(?=\n\s*\n|\n\[p\. \d+\]\n)", text):
        if n + len(para) > size and cur:
            chunks.append("".join(cur)); cur, n = [], 0
            if page and not para.lstrip().startswith("[p. "):
                cur.append(f"[p. {page}]\n")
        cur.append(para); n += len(para)
        page = (re.findall(r"^\[p\. (\d+)\]$", para, re.M) or [page])[-1]
    if "".join(cur).strip():
        chunks.append("".join(cur))
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", type=Path, help="PDF, EPUB, DOCX, HTML or plain-text file")
    ap.add_argument("--title", required=True, help="title and edition, e.g. 'C++ High Performance, 2nd ed.'")
    ap.add_argument("--work", type=Path, required=True, help="work directory outside the repository")
    ap.add_argument("--today", required=True)
    ap.add_argument("--chunk", type=int, default=150_000, help="characters per chunk")
    args = ap.parse_args()
    work = args.work.resolve()
    if work.is_relative_to(ROOT):
        ap.error("--work must be outside the repository: book text is copyrighted and must not be committed")
    name = "book-" + slug(args.title)[:60]
    work = work / name
    work.mkdir(parents=True, exist_ok=True)
    (SEEDS / "raw").mkdir(parents=True, exist_ok=True)
    chunks = split(extract(args.book.resolve(), work), args.chunk)
    tax = taxonomy()
    for n, chunk in enumerate(chunks, 1):
        cp = work / f"chunk-{n:02d}.txt"
        cp.write_text(chunk)
        out = (SEEDS / "raw" / f"{name}__{n:02d}.json").resolve()
        pp = work / f"prompt-{n:02d}.txt"
        pp.write_text(PROMPT.format(today=args.today, title=args.title, chunk_path=cp, n=n, total=len(chunks),
                                    known=(ROOT / "data" / "known_list.txt").resolve(), taxonomy=tax,
                                    output_path=out))
        pages = re.findall(r"^\[p\. (\d+)\]$", chunk, re.M)
        span = f"pp. {pages[0]}-{pages[-1]}" if pages else "no page marks"
        print(f"{len(chunk):7d}  {span:16s}  -> {pp}")
    (work / "meta.json").write_text(json.dumps({"title": args.title, "source": str(args.book), "chunks": len(chunks)}))
    print(f"\n{name}: {len(chunks)} chunks; outputs data/seeds/raw/{name}__NN.json")


if __name__ == "__main__":
    main()
