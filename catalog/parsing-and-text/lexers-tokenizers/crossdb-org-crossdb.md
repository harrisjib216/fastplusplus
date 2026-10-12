# CrossDB (hand-written SQL lexer/parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MPL-2.0` · 🟡 stale

> Hand-written SQL scanner/parser inside CrossDB's embedded RDBMS, claimed 10x faster than Flex/Bison-generated code.

| | |
|---|---|
| **Beats** | Flex/Bison |
| **Claimed result** | "a hand-written SQL parser that is over 10 times faster than Flex/Bison parser tools"; elsewhere: "approximately 10 times faster than Flex/Bison tools" and about one-third the code size of Flex/Bison-generated output |
| **Workload** | SQL statement tokenizing and parsing inside an embedded/client-server relational database, using a hand-written scanner and hand-written recursive-descent parser instead of Flex/Bison-generated code |
| **Metric** | throughput |
| **Adoption** | 268 stars |
| **Last commit** | 2025-06-20 |
| **Links** | [repository](https://github.com/crossdb-org/crossdb) · [benchmark](https://github.com/crossdb-org/docs/blob/main/docs/faq.md) |

## Verdict

CrossDB's docs FAQ claims its hand-written scanner+parser is 'over 10 times faster than Flex/Bison parser tools' and about one-third the code size, stated as a single unsourced bullet in docs/faq.md with no linked benchmark script, hardware, or compiler/flags, and it bundles scanning and parsing together rather than isolating lexer-only throughput.

## Use it when

- Embedding a small in-memory/on-disk OLTP relational engine in C/C++/Go/Python/Rust and wanting its internal SQL parsing fast without adding Flex/Bison to the build
- High-frequency, short OLTP-style SQL statements parsed repeatedly rather than parsed once and cached
- Needing portability across Linux/macOS/Windows/FreeBSD and x86/ARM/PowerPC/MIPS without a Flex/Bison toolchain dependency
- Wanting a reentrant, thread-safe SQL front end with no shared global parser state across connections
- Accepting CrossDB's own MySQL-flavored SQL dialect rather than needing a general-purpose or standard SQL grammar

## Skip it when

- You need a standalone, reusable SQL lexer/parser library: CrossDB's scanner and parser are internal to the engine and not exposed as an independent API
- You need the 10x claim substantiated: no benchmark script, workload, hardware, or scanner-only vs parser-only breakdown is published
- You need a mature, standard SQL dialect: the project itself says it is 'still in its early stages and currently lacks stability'
- You need active upstream development: last commit 2025-06-20, 268 stars, 21 forks, and only 3 open issues suggest limited real-world usage exercising parser edge cases
- Your dataset won't fit in available memory or lives on network-mounted disks, which the project's own FAQ lists as limitations of the engine the parser serves

## How it is fast

A hand-written recursive-descent parser calls a hand-written scanner directly, skipping the generated DFA table-walk that Flex output uses; the scanner classifies characters with a 256-entry static lookup table (s_tok_type) and switches on token type inline. Because xdb_token.c is textually #included into xdb_parser.c, the compiler can inline across the scanner/parser boundary in a way two separately compiled Flex/Bison translation units cannot. The \~10x and \~1/3-code-size figures come from a single unsourced FAQ bullet with no published benchmark script, hardware, or compiler flags.

## Compared with alternatives

All the catalogued siblings (logos, LRSTAR, simd-lexing, lexer-exp, Gigatoken, Accelerated-Zig-Parser, StreamTok, Ragel) are extractable, general-purpose lexers/tokenizers you drop into your own project; CrossDB's parser is only worth it if you're embedding the CrossDB RDBMS itself and want its SQL front end's speed as a side effect, not as a standalone lexer replacement.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (single C source tree; optional Go/Python bindings and JNI wrapper ship separately in the repo) |
| **Minimum toolchain** | not documented precisely; uses _GNU_SOURCE, stdint.h/stdbool.h; built with GCC via Makefile/CMake, MinGW64 for Windows |
| **Platforms** | Linux/macOS/FreeBSD/Windows; x86 32/64-bit, ARM, PowerPC, MIPS per README |
| **Thread safety** | FAQ states the scanner/parser is 'fully reentrant and thread-safe'; not independently verified beyond reading the source |
| **Drop-in for the baseline** | partial — it replaces Flex/Bison output inside CrossDB itself, but only as part of the whole engine; it cannot be swapped into another project's own grammar |

## Gotchas

- Scanner and parser aren't separable: xdb_token.c is #included directly into xdb_parser.c, so the tokenizer can't be linked or used on its own
- Parsing is tied to CrossDB's own metadata structs (xdb_stmt_t, xdb_tblm_t, xdb_tblm lookups) — output is not a generic, reusable AST
- Functions use XDB_STATIC internal linkage and file-scope static tables, confirming this is compiled as one amalgamated unit rather than a modular library
- One closed GitHub issue documents a parser bug on inequality expressions (Aug 2024), fixed before the 2025-06-20 last commit but indicative of a young grammar

## Known shortcomings

- Compared against Flex/Bison, which is not in this category's baseline list, and the \~10x figure is an unsourced FAQ number with no benchmark behind it.

## Caveats and trade-offs

The 10x figure is an unsourced FAQ bullet point with no linked benchmark script, methodology, workload description, or breakdown between scanner-only and parser-only speedup, so it cannot be confirmed to isolate lexer/tokenizer performance specifically (it bundles scanning + parsing).

Hand-written scanner+parser is harder to change than a Flex/Bison grammar if the SQL dialect needs to evolve, but the project reports it is smaller, fully reentrant/thread-safe, and gives better error messages than the generated alternative.

## Maintenance

Stale by this catalog's threshold (last commit 2025-06-20) with only 268 stars/21 forks, and the project's own README/CONTRIBUTING call it early-stage and not yet stable; MPL-2.0 and copyable as source, but not a drop-in component outside the full CrossDB engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The FAQ states 'over 10 times faster than Flex/Bison parser tools' and 'approximately 10 times faster than Flex/Bison tools' with no methodology. The repo's bench/ directory only covers SQLite/STL map/Boost multi-index, with no parser-vs-Flex/Bison benchmark, so this is a first-party number without methodology: Tier C.
- **Verifier notes:** Quotes, MPL-2.0, 268 stars, last commit 2025-06-20 (stale) all verified. A hand-written parser exists in src/parser/xdb_parser\*.c. baseline_in_list set to false because Flex/Bison is not in this category's baseline list ('re2c, hand-written baselines the benchmark names').
- **Fields the verifier corrected:** `baseline_in_list`
- **Pages the verifier opened:**
  - <https://github.com/crossdb-org/docs/blob/main/docs/faq.md>
  - <https://github.com/crossdb-org/docs>
  - <https://github.com/crossdb-org/crossdb>
- **Sources the enricher read:**
  - <https://github.com/crossdb-org/crossdb>
  - <https://github.com/crossdb-org/crossdb/blob/main/README.md>
  - <https://github.com/crossdb-org/docs/blob/main/docs/faq.md>
  - <https://github.com/crossdb-org/crossdb/blob/main/src/parser/xdb_token.c>
  - <https://github.com/crossdb-org/crossdb/blob/main/src/parser/xdb_parser.c>
  - <https://github.com/crossdb-org/crossdb/blob/main/include/crossdb.h>
  - https://github.com/crossdb-org/crossdb/git/trees/HEAD (full file tree)
  - https://api.github.com/repos/crossdb-org/crossdb (stars/pushed_at/license metadata)
  - https://github.com/crossdb-org/crossdb/issues (search: parser)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/crossdb-org/crossdb`) · [data/wave3/enrich/raw/github_com_crossdb_org_crossdb.json](../../../data/wave3/enrich/raw/github_com_crossdb_org_crossdb.json) (enrichment confidence 0.35)

</details>
