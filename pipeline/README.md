# pipeline/

<sub>[fastpp](../README.md)</sub>

The scripts and prompt templates that built the catalog. They only render prompts, merge agent output and render
pages; the searching, verifying and writing is done by Claude Code agents that read the rendered prompts. Python
3.9 or later, standard library only.

## Prompts and rules

| File | What it is |
|---|---|
| [`spec.md`](spec.md) | The rulebook: orchestrator notes, the search-agent prompt (Part 2), the category × baseline tables for every wave (Parts 3 and 4), the enrichment prompt (Part 5) and the planned code audit (Part 6). |
| [`verifier_prompt.txt`](verifier_prompt.txt) | The verifier-agent prompt template. |
| [`cloud_harness.md`](cloud_harness.md) | Overrides for agents running in a cloud session (tools, network limits, output paths, final-reply style). |

## Scripts, in pipeline order

| Script | Does |
|---|---|
| `render.py data/waveN --batch bK` | Renders the search prompts for one source batch of a wave into `data/waveN/prompts/`. |
| `seed.py data/waveN --batch seed` | Renders seed-record prompts for named projects (leads, known-list entries). |
| `mine.py`, `seeds_merge.py`, `seed_backfill.py` | Seed-list mining: split a curated list into sections, merge the mined seeds, and group them into backfill seed passes per wave. |
| `merge.py data/waveN` | Merges and deduplicates a wave's raw search output into `merged.json` and regenerates `data/known_list.txt`. |
| `verify.py render data/waveN --assignments <ids>` | Renders verifier prompts (three records per batch) for the named assignments' new records. |
| `verify.py apply data/waveN` | Folds verdicts, retier files and decision overrides into `verified.json` and `rejected.json`. |
| `enrich.py data/waveN` | Renders an enrichment prompt for every verified entry that has no enrichment record yet. |
| `add_decisions.py` | Appends shortcomings, measurements, duplicates, rejects and override fields to `data/decisions.json` (JSON lines on stdin). |
| `seeds_no_evidence.py` | Compiles the seeds with no published comparison into `catalog/seeds-no-evidence.md`. |
| `render_lists.py` | Renders `catalog/` (index, domain, category and entry pages, rejected list, JSONL and CSV exports) and the generated blocks of the top-level `README.md`. Display titles and the README highlights are in `catalog_meta.py`. |
| `check_pii.py [--fix]` | Fails on home-directory paths, personal email addresses or credentials in tracked files; `--fix` rewrites the paths. |

## The wave loop

1. Write `data/waveN/assignments.json` (categories × source batches) from the spec's Part 4 and render the
   search prompts with `render.py`.
2. Launch one search agent per prompt: "Read <prompt file> and carry out that task exactly; it names your output
   file." When it reports, run `merge.py`, then `verify.py render` for that search's assignments.
3. Launch one verifier agent per batch. When it reports, record shortcomings with `add_decisions.py`, then run
   `verify.py apply` and `enrich.py`.
4. Launch enrichment agents (two prompts each) for the newly verified entries and record their shortcomings;
   findings that change a record go in a retier file.
5. Seed the leads the enrichers wrote down (`seed.py`), and send the seed records through merge, verify and enrich.
6. Close: a final `verify.py apply`, check every verified entry has an enrichment record, then
   `render_lists.py`, `check_pii.py`, commit and push.

The full operating notes (concurrency, rate limits, recovery after killed agents, id drift, the rules for
recording decisions) are in [CLAUDE.md](../CLAUDE.md#the-wave-loop).
