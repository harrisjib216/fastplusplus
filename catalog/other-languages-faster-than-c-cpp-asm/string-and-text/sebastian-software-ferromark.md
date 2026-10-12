# ferromark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust CommonMark/GFM Markdown-to-HTML engine, about 3x faster than md4c and 5-6x faster than cmark in its own harness.

| | |
|---|---|
| **Beats** | md4c (C); cmark (C) in a second report |
| **Claimed result** | Native Linux x86-64 report 2026-09-24 (AMD EPYC 7763): md4c reaches 0.31x (fresh) and 0.29x (reuse) of Ferromark v2 throughput on the 50 documents with matching output across five engines, so Ferromark is about 3.2x and 3.4x faster (derived from page data); on the 14 documents where all six engines agree md4c is 0.24x fresh and 0.20x reuse (about 4.2x and 5.0x, derived from page data). Held-out PGO evaluation (28 held-out documents, 24 of them compared with md4c): default builds 3.05x fresh and 3.22x reuse; with PGO applied to the Rust engines only (md4c not PGO-built) 3.84x and 4.02x. Second report, blacksmith Linux x86-64 (2026-10-01, all 57 documents including differing outputs, 'AMD EPYC'): vs md4c 2.95x fresh and 3.06x reuse (md4c marked with an asterisk for differing output), vs cmark 5.70x and 6.25x, vs cmark-gfm 6.15x and 6.67x (Comrak, a Rust sibling, 5.10x and 5.51x). |
| **Workload** | UTF-8 Markdown to complete HTML on a frozen 57-document corpus (37 to 113,609 bytes, CommonMark and shared GFM subset: tables, strikethrough, task lists), geometric mean of per-document time ratios, fresh and reuse lifecycles, parse plus render plus output destruction timed. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 64-Core Processor, 4 vCPUs (GitHub-hosted runner, Linux 6.17.0-1022-azure) for the native harness; the blacksmith manual-comparison report names only 'AMD EPYC, 15.4 GB RAM, Linux 6.6.141' (4 vCPU runner). |
| **Compiler and flags** | Native harness: all Rust crates built with one pinned nightly toolchain, -C target-cpu=generic (x86-64 baseline; Ferromark, memchr and Highway still pick SSSE3/AVX2 paths at run time), release optimization, fat LTO, codegen-units=1, panic=abort; md4c and C/C++ support compiled with clang -O3 (Ubuntu clang 18.1.3), no PGO and no cross-language LTO in the default build; all engines share mimalloc and md4c's allocations are redirected to it. Manual comparison (blacksmith report, prepare-native.py): cmark library built by CMake Release with -DCMAKE_C_FLAGS_RELEASE=-O3 (GNU 13.3.0 at /usr/bin/cc), its worker adapter compiled with clang -O3, system malloc; Rust worker built with cargo build --release --locked and RUSTFLAGS='-C target-cpu=generic'. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | README: arena allocation, reusable buffers, specialized byte scans, and SIMD reduce parser and renderer work; the harness also measures a reuse lifecycle (arena reset, borrowed output) separately from fresh calls. |
| **Adoption** | 9 stars; 963 commits; Node.js bindings |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/sebastian-software/ferromark) · [benchmark](https://github.com/sebastian-software/ferromark/blob/main/docs/reports/2026-09-24-native-linux-x86-64/README.md) |

## Verdict

On one GitHub-hosted AMD EPYC 7763 runner (4 vCPUs, 2026-09-24), Ferromark v2 rendered the 50 documents whose HTML agreed across five engines about 3.2x faster fresh and 3.4x faster with reuse than md4c built with clang 18 -O3 and sharing mimalloc (derived from page data: md4c 0.31x and 0.29x), and about 4.2x and 5.0x on the 14 documents where all six engines agreed. A later short balanced-profile run on an unnamed AMD EPYC blacksmith runner over all 57 documents, including differing outputs, gave 2.95x and 3.06x against md4c and 5.70x and 6.25x against cmark built with GCC 13.3 -O3.

## Use it when

- Rust or Node.js services and static-site generators rendering many Markdown documents per second, where a reused arena and output buffer can be kept per worker.
- CommonMark or GFM documents from tens of bytes to about 100 KB (the measured corpus spans 37 to 113,609 bytes) where md4c, cmark, cmark-gfm, pulldown-cmark or Comrak is the current bottleneck.
- Pipelines that also want JSX/MDX output, front matter, heading IDs, footnotes, callouts or a document tree to transform before rendering, from the same engine.
- x86-64 machines with SSSE3/AVX2 or aarch64 machines with NEON, where the vector byte scans are active.

## Skip it when

- C or C++ codebases that embed md4c or cmark directly: there is no documented C API, so you would add a Rust toolchain (1.95+) and your own FFI shim.
- Projects that need a stable API: v2 was re-based on an OX-Content snapshot in September 2026, v3 broke the Rust API on 2026-10-01, and crates.io shows eight releases between 2026-09-26 and 2026-10-11.
- When you need byte-identical output to md4c or cmark: only 14 of the 57 benchmark documents render the same across all six engines, and md4c's output differs on 7 of them.
- Untrusted input through the Rust API with default options: Rust defaults preserve raw HTML, so sanitize must be set explicitly (Node defaults escape it).
- Workloads that enable the product defaults (heading IDs, callouts, TOC, fence metadata, tag filtering): the benchmarks switch these off, and extra syntax adds parsing work, so the measured margin is an upper bound.

## How it is fast

The document tree lives in a bumpalo arena that can be reset between documents, and the renderer reserves twice the source length for its output up front and can lend the buffer out (render_borrowed) instead of allocating a String per call. Inline scanners stop on ASCII byte classes found with a nibble-table vector lookup (pshufb on SSSE3/AVX2 detected at run time, vqtbl1q_u8 on aarch64), and the line pre-pass uses an SSE2/NEON plus SWAR newline scan because memchr's per-call setup dominated on short lines. The v2 core is an import of the OX-Content parser (ubugeeei-prod/ox-content v3.2.3, 2026-09-13) that the project then rewrote; its own report measures v2 at about 2.1x its earlier v1 engine.

## Compared with alternatives

Pick it over rushdown or zigmark when you need GFM and JSX/MDX output and want the evidence with the widest baseline set (md4c, cmark, cmark-gfm, pulldown-cmark, Comrak and Bun's engine in one preserved harness); rushdown and zigmark are measured only against cmark/cmark-gfm. For non-Markdown text work (regex, CSV, word counting) the other siblings in this category apply instead.

## Integration

| | |
|---|---|
| **Form** | crate (Rust, edition 2024) plus a native Node.js package (npm ferromark) |
| **Dependencies** | bumpalo, compact_str, smallvec, memchr, rustc-hash, thiserror, serde_json; optional ferriki (syntax highlighting) and oxc_\* crates for the jsx feature |
| **Minimum toolchain** | Rust 1.95 (rust-version in Cargo.toml); Node.js 22.12+ for the bindings; the published benchmarks used nightly-2026-07-20 |
| **Platforms** | any Rust target; SSSE3/AVX2 vector scans on x86-64 detected at run time with a table-walk fallback, NEON scans on aarch64, SWAR elsewhere |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured engine is Ferromark v2 at commit 09e5e866da (2026-09-24) and the blacksmith run used source 9af95fc3; the current crate is 3.5.0 with a breaking Rust API, so the numbers describe an earlier revision.
- Harness asymmetry in the fresh lifecycle: the md4c adapter (worker.rs) starts each call with an empty Vec that grows through md4c's per-chunk output callback across FFI, while Ferromark's renderer reserves 2x the source length before rendering. The reuse lifecycle, where md4c also keeps a warm Vec, gives a similar ratio (0.29x vs 0.31x), so the effect is small but favours Ferromark.
- Toolchains differ: Rust engines use LLVM 22.1.8 with fat LTO, codegen-units=1 and panic=abort, md4c uses Ubuntu clang 18.1.3 -O3 with no LTO, and md4c's malloc calls are redirected to mimalloc by a benchmark-only header; PGO rows apply profiles to the Rust engines only.
- Earlier releases had super-linear paths on untrusted input (reference-link resolution #142, angle autolinks #244, footnote numbering #44) and a Node binding that aborted the process on any panic (#140); all are closed, but they were filed against the v1 code base before the OX-Content import, and no fuzzing or limit guarantee for v2 is documented in the README.

## Known shortcomings

- First-party run on a shared GitHub runner (EPYC 7763; md4c built with clang 18.1.3 -O3); the held-out set is 28 documents, 24 compared with md4c; the engines' HTML differs on 7-43 of 57 documents; md4c allocations go through mimalloc; different algorithms; PGO applied to the Rust engines only; cmark's -O3 line is absent from the blacksmith build log.
- Enricher: small fresh-lifecycle asymmetry in the harness (the md4c adapter starts each call with an empty Vec grown through a per-chunk FFI callback while ferromark reserves twice the source length; reuse ratios 0.29x vs 0.31x, so the effect is small); md4c built with clang 18 -O3 without LTO against Rust on LLVM 22 with fat LTO. The numbers measure v2 commit 09e5e866da while the crate is now 3.5.0 with a breaking v3 API; the v2 core was imported from ox-content v3.2.3.

## Caveats and trade-offs

First-party harness by the project author, with a very new, small project (9 stars) and many internal rewrites (963 commits, v1 and v2 controls). Engine outputs differ: only 14 of 57 documents agree across all six engines and 50 agree across the five with matching renderer options, so the 'all 57' ratios compare different outputs; the report says a throughput result does not establish conformance, and the manual-comparison table marks md4c with an asterisk for differing output. Rust is built for generic x86-64 while md4c is not PGO-built and not LTO'd; the shared-mimalloc control is not a stock system-malloc comparison, and in the manual comparison cmark runs with system malloc. Ferromark's own PGO build is shipped, md4c's is not, and PGO rows are only comparable with PGO rows. Timing is a short balanced profile (3 process rounds) in the second report, whose authors say it has less timing evidence than their standard profile. Runs on shared cloud runners. The README's '57-document comparison leads every measured library' claim page (ferromark.dev/guide/benchmarks) is blocked here; numbers come from the checked-in reports. Only the CPU model of the 2026-09-24 report is fully named.

Markdown to HTML/JSX with secure defaults, CommonMark and GFM plus opt-in Ferromark Flavored Markdown; the benchmark disables optional syntax and renderer extras (heading IDs, callouts) to measure engine throughput, which is not the secure product default. Extra syntax adds parsing work.

## Maintenance

Very active (963 commits, releases almost daily, last crates.io release 3.5.0 on 2026-10-11) but young and small (9 stars, about 5,700 crate downloads), MIT-licensed with preserved OX-Content attribution, and the API is still changing between major versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The 2026-09-24 native Linux report preserves its harness in docs/reports/2026-09-24-native-linux-x86-64/harness/ (prepare.py compiles md4c with clang -O3 -DNDEBUG -std=c99; build.json records Rust opt-level 3, fat LTO, codegen-units 1, -C target-cpu=generic), PROVENANCE.md names Ubuntu clang 18.1.3, and host.txt names the AMD EPYC 7763; md4c 0.31x/0.29x (50 agreeing documents) and 0.24x/0.20x (14 documents) appear in the table.
- **Verifier notes:** Numbers and build details check out against the report, PROVENANCE.md, build.json, host.txt and harness/prepare.py; the held-out comparison uses 28 held-out documents of which 24 enter the md4c ratio (the record said 24 documents of held-out half), and the PGO columns favour Ferromark because md4c is not PGO-built. Shortcomings to record: first-party harness on a shared GitHub runner, engines produce different HTML on 7 to 43 of 57 documents, md4c allocations redirected to mimalloc rather than its stock malloc, different parsing algorithms (same_algorithm false), and the blacksmith cmark build log does not show the -O3 line (GNU 13.3.0 confirmed, CMake Release defaults to -O3). README's 'leads every measured library' page (ferromark.dev) was not opened.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-114 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/sebastian-software/ferromark/blob/main/docs/reports/2026-09-24-native-linux-x86-64/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/PROVENANCE.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/build.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/host.txt>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/harness/prepare.py>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/README.md>
  - <https://github.com/sebastian-software/ferromark/tree/main/docs/reports>
  - <https://github.com/sebastian-software/ferromark/tree/main/docs/reports/2026-10-01-blacksmith-linux-x86-64>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-10-01-blacksmith-linux-x86-64/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-10-01-blacksmith-linux-x86-64/host.txt>
  - <https://github.com/sebastian-software/ferromark/tree/main/docs/reports/2026-10-01-blacksmith-linux-x86-64/native-cmark>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-10-01-blacksmith-linux-x86-64/native-cmark/build.log>
  - <https://github.com/sebastian-software/ferromark>
- **Sources the enricher read:**
  - <https://github.com/sebastian-software/ferromark>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/UPSTREAM.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/PROVENANCE.md>
  - <https://github.com/sebastian-software/ferromark/tree/main/docs/reports/2026-09-24-native-linux-x86-64/harness>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/harness/worker.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/harness/md4c_alloc.h>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/harness/native.h>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-09-24-native-linux-x86-64/harness/stack.c>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/docs/reports/2026-10-01-blacksmith-linux-x86-64/README.md>
  - <https://github.com/sebastian-software/ferromark/tree/main/src/parser>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/src/parser/byte_class.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/src/parser/line_scan.rs>
  - <https://github.com/sebastian-software/ferromark/tree/main/src/renderer>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/src/renderer/html.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/main/src/renderer/html/renderer.rs>
  - <https://github.com/sebastian-software/ferromark/issues?q=is%3Aissue>
  - <https://github.com/sebastian-software/ferromark/issues?q=is%3Aissue%20label%3Atype%3Abug>
  - <https://crates.io/api/v1/crates/ferromark>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sebastian-software/ferromark`) · [data/wave14/enrich/raw/github_com_sebastian_software_ferromark.json](../../../data/wave14/enrich/raw/github_com_sebastian_software_ferromark.json) (enrichment confidence 0.75)

</details>
