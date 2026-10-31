# src/

<sub>[fastpp](../README.md)</sub>

`fastpp`, the tool that turns the records under [`data/`](../data/README.md) into the published catalog and keeps
personal data out of the repository. C++20, standard library only. CI builds it and runs all three commands on
every push, and fails if the committed catalog differs from a fresh render.

```sh
cmake -B build && cmake --build build
build/fastpp seeds       # catalog/seeds-no-evidence.md from data/seeds/no_evidence/
build/fastpp render      # catalog/ and the generated blocks of README.md
build/fastpp check-pii   # fails on home-directory paths, personal emails or credentials in tracked files
```

`check-pii --commits` also checks the author and committer emails of every commit on HEAD; `check-pii --fix`
rewrites home-directory paths to `/path/to/fastpp`. Run it from anywhere inside the repository.

| File | Does |
|---|---|
| `main.cpp` | The command line. |
| `render.cpp` | Index, domain, category and entry pages, the rejected list, the JSONL and CSV exports and the README blocks. Entries are ranked by tier, then copyable before study-only, then maintenance status, then GitHub stars. |
| `seeds.cpp` | The page of seeds that never published a comparison against a baseline. |
| `check_pii.cpp` | The privacy check. Its three patterns are matched by hand rather than with `<regex>`, and each scan jumps straight to the characters a match can start with, so the whole tracked tree is read in about a second. |
| `catalog.cpp` | Loads [`data/catalog_meta.json`](../data/catalog_meta.json): domain order, titles and intros, category titles and aliases, and the README highlights. |
| `json.cpp` | A small JSON reader and writer. Objects keep their key order and numbers print in Python's `repr` format, so the exports stay byte-stable across renders. |
| `text.cpp` | UTF-8 helpers: lengths and slices in code points, Unicode whitespace, lowercasing, and SHA-1 for shortening long page names. |

The catalog was first rendered by a Python script. This tool replaced it after reproducing that script's output
byte for byte across every page and export.
