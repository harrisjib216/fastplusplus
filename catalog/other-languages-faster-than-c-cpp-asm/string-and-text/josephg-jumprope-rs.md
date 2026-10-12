# jumprope (Rust rope)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `ISC (LICENSE.txt and README); Cargo.toml declares ISC OR Apache-2.0` · 🔴 abandoned

> Rust rope (skip list of gap-buffer leaves) that replays real editing traces about 2.4-2.7x faster than the author's C librope.

| | |
|---|---|
| **Beats** | librope (C skip-list rope by the same author) |
| **Claimed result** | README table, single core of a Ryzen 5800X: automerge-paper librope (C) 16.28 ms vs Jumprope 6.66 ms; rustcode 3.93 vs 1.66 ms; sveltecomponent 1.59 vs 0.59 ms; seph-blog1 10.01 vs 3.81 ms (about 2.4x to 2.7x, derived from page data). README also says jumprope is about 3x faster than ropey (a Rust rope) on real editing operations, and its JumpRopeBuf wrapper (merges runs of edits before applying them) is claimed about 10x faster again. |
| **Workload** | Replaying real text-editing traces (automerge-paper, rustcode, sveltecomponent, seph-blog1) from crdt-benchmarks against a rope: insert/delete at arbitrary positions. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5800X, single core |
| **Compiler and flags** | Not stated in the README. Workspace Cargo.toml release profile: lto = true, codegen-units = 1 (Rust side). rope_benches/build.rs compiles a vendored rope.c with cc::Build defaults (no explicit flags, no NDEBUG; cc follows Cargo's release opt-level), linked as a static library with no cross-language LTO, so every C call crosses an FFI boundary. Run with 'cargo run --release -- --bench' in rope_benches. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: jumprope is a skip list whose leaf nodes each contain a gap buffer, versus librope's plain skip list. |
| **Adoption** | 152 stars; 111,025 crates.io downloads |
| **Last commit** | 2023-05-20 |
| **Links** | [repository](https://github.com/josephg/jumprope-rs) · [benchmark](https://github.com/josephg/jumprope-rs) |

## Verdict

The author's criterion harness (rope_benches 'realworld') replays four crdt-benchmarks keystroke traces on one core of a Ryzen 5800X: jumprope 6.66 ms vs librope 16.28 ms on automerge-paper (2.4x), and 1.66 vs 3.93, 0.59 vs 1.59, 3.81 vs 10.01 ms on the other three (derived from page data), with compiler versions and C flags unstated and the table last updated in October 2021. The C side pays a per-insert CString allocation and UTF-8 validation that the Rust side does not, and the only correctness check is final length (the end contents of all four traces are ASCII, so that length check is at least valid).

## Use it when

- Replaying or applying keystroke-level edit streams to documents from tens of KB to MB (CRDT/OT engines, collaborative editors); the author's own diamond-types depends on it.
- Editors or servers that receive positions in unicode characters, or in UTF-16 units from JavaScript/Java/C# clients (enable wchar_conversion; costs about 15% per the README).
- Wasm builds where bundle size matters (README: 18 kB brotli vs 30 kB for ropey); build with default-features = false to drop the entropy-seeded StdRng.
- Typing-heavy workloads with runs of adjacent inserts or backspaces, via JumpRopeBuf, which merges them before touching the rope.

## Skip it when

- Small strings: the README says under about 100 bytes use String or SmartString; every JumpRope embeds a full head node (392-byte gap buffer plus a 21-entry next array) and an RNG, so even an empty rope is around 1 KB.
- Memory-constrained documents: issue #5 (open since 2023) reports over 90% memory overhead from node layout, and the maintainer says it can sit around 400% after many edits because split nodes are never merged back.
- When you need line/column indexing: ropey has it; the line_conversion feature flag in Cargo.toml only adds internal gap-buffer bookkeeping and exposes no line API.
- Long-term-supported dependencies: last release 1.1.2 (2023-05-15), last commit 2023-05-20, three open issues and two open PRs without maintainer activity.

## How it is fast

A skip list (random node heights, bias 65/256) whose nodes are fixed 392-byte gap buffers instead of librope's 136-byte plain arrays, so consecutive keystrokes at the same spot only move the gap inside one node instead of shifting bytes or walking the list. Each skip entry stores character counts, so locating a character offset is a top-down O(log n) walk; nodes are fixed-size structs with raw pointers and an inline head node. All operations take pre-validated &str, so there is no per-insert UTF-8 validation pass.

## Compared with alternatives

No other rope is catalogued in this category; the string-and-text siblings (regex, csv-zero, mail-parser and others) solve different problems. Against its C predecessor librope (wave 1), pick jumprope for any Rust or wasm project; librope only makes sense for C callers.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rand 0.8 (small_rng), str_indices 0.4 |
| **Minimum toolchain** | Rust edition 2021 (rustc 1.56+); no rust-version declared |
| **Platforms** | any (pure Rust, no SIMD); wasm build provided in jumprope-wasm |
| **Thread safety** | JumpRope is Send + Sync (mutation needs &mut); JumpRopeBuf uses a RefCell, so it is Send but not Sync and borrow() panics if already borrowed |
| **Drop-in for the baseline** | partial — same author and same skip-list idea as librope, but a Rust API (char offsets, &str, Range) rather than librope's C API; C code would need its own FFI shim |

## Gotchas

- Out-of-range positions are silently clamped: insert past the end appends, and remove past the end is ignored, so index bugs in the caller do not panic.
- Debug builds use 10-byte nodes (NODE_STR_SIZE is 10 under debug_assertions, 392 in release), so debug performance and memory behaviour are not representative, and JumpRope::new() uses a fixed seed (123) in debug or without ddos_protection, which makes the skip-list shape predictable to an adversary.
- wchar API: chars_to_wchars returned a wrong value in all cases before 1.1.2 (CHANGELOG); unreleased master adds is_ascii_only(), which actually tests for no surrogate pairs (issue #8).
- Benchmark harness flaws: the librope (C) column calls rope.c through FFI with a CString heap allocation and copy per insert inside the timed loop (182,315 of them per automerge-paper replay; not measured, but at an assumed 15-30 ns per small malloc/free pair that is roughly 2.7-5.5 ms of librope's 16.28 ms), and rope.c is built by cc defaults without NDEBUG. The README's 'about 10x faster again' JumpRopeBuf claim comes from benches/benches.rs, which runs collapse() on the trace outside the timer and feeds JumpRopeBuf the pre-merged ops (automerge-paper 259,778 patches become 10,712 ops; rustcode 40,173 become 13,561), so the merging work is not timed.

## Known shortcomings

- Table dates from October 2021 (before 1.0); the C side is called through FFI with a CString allocation per insert and live asserts (no NDEBUG); a different design (gap-buffer leaves). Licence ISC (Cargo.toml says ISC OR Apache-2.0).
- Harness flaws: the librope C column pays a CString malloc and copy for each insert inside the timed loop (182,315 allocations per automerge-paper replay, an unmeasured estimate of roughly 2.7-5.5 ms of librope's 16.28 ms) and rope.c is built without NDEBUG; the README's '10x faster again' for JumpRopeBuf comes from benches/benches.rs, which runs collapse() outside the timer and feeds pre-merged ops (automerge-paper's 259,778 patches reduced to 10,712 ops), so the merge work goes untimed. Memory overhead about 400% after many edits (issue #5); the line_conversion flag exposes no line API. The final-length check is valid (all 4 traces end in ASCII).

## Caveats and trade-offs

First-party numbers from the author, who also wrote the C baseline. The README table was last updated on 2021-10-05/06 (README commit history), before jumprope 1.0 (2022), so it does not reflect the current code. Benchmark code is public (rope_benches/src/main.rs, criterion 'realworld' group) but loads traces from a hard-coded /home/seph/src/diamond-types/benchmark_data path; compiler versions and C flags are unstated. Harness asymmetry: the C column ('C-JumpRope' in the code) is a vendored copy of librope's rope.c built by the cc crate without NDEBUG and driven through FFI with a CString allocation and copy per insert inside the timed loop, while Jumprope takes &str directly inside the same LTO-built Rust binary; this inflates the 2.4-2.7x gap by an unmeasured amount. The realworld check compares only the final char_len, not the content. Algorithms differ (gap-buffer leaves vs plain skip-list nodes), so the win is data-structure design rather than language. librope itself is already catalogued (wave 1, https://github.com/josephg/librope) from the same table; this record is its Rust successor, not a duplicate. The linked criterion report host (home.seph.codes) does not resolve (ENOTFOUND). No commits since 2023-05-20. [retier] The librope C column pays a CString malloc and copy for each insert inside the timed loop (182,315 allocations per automerge-paper replay, roughly 2.7-5.5 ms of librope's 16.28 ms, unmeasured estimate) and rope.c is built without NDEBUG. The README's '10x faster again' for JumpRopeBuf comes from benches/benches.rs, which runs collapse() outside the timer and feeds pre-merged ops (259,778 patches reduced to 10,712), so the merge work goes untimed. Memory overhead about 400% after many edits (issue #5).

Fewer features than ropey (no line/column conversion). Meant for large documents; the README recommends std String for strings under about 100 bytes.

## Maintenance

Unmaintained since May 2023 (1.1.2 on crates.io, about 111k downloads, used by diamond-types) but ISC OR Apache-2.0, about 3,300 lines of Rust in src/ (miri-clean since 1.0 per the CHANGELOG), and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table comes from the public criterion harness (rope_benches/src/main.rs, 'realworld' group) on a stated Ryzen 5800X, but no Rust or C compiler version or C flags are stated, the table was last updated in October 2021, and it is the author's own measurement against his own older C library; C, not A.
- **Verifier notes:** Numbers match the README table (16.28 vs 6.66 ms etc.); tier C stays. Same-author C baseline with a different design, called through FFI with a per-insert CString allocation and live asserts, so the 2.4-2.7x is design plus harness, not language. Not a duplicate: librope (wave 1) is the C library itself.
- **Fields the verifier corrected:** `license`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-13 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/josephg/jumprope-rs>
  - <https://github.com/josephg/jumprope-rs/commits>
  - <https://github.com/josephg/jumprope-rs/commits/master/README.md>
  - <https://github.com/josephg/jumprope-rs/tree/master/rope_benches>
  - <https://github.com/josephg/jumprope-rs/tree/master/rope_benches/src>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/build.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.h>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.c>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/rope.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/main.rs>
  - <https://crates.io/api/v1/crates/jumprope>
- **Sources the enricher read:**
  - <https://github.com/josephg/jumprope-rs>
  - <https://github.com/josephg/jumprope-rs/commits/master>
  - <https://github.com/josephg/jumprope-rs/issues?q=is%3Aissue>
  - <https://github.com/josephg/jumprope-rs/issues/4>
  - <https://github.com/josephg/jumprope-rs/issues/5>
  - <https://github.com/josephg/jumprope-rs/issues/8>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/jumprope.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/buffered.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/gapbuffer.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/fast_str_tools.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/src/iter.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/benches/benches.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/rope.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/build.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.c>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.h>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/crdt-testdata/src/lib.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/benchmark_data/automerge-paper.json.gz>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/benchmark_data/rustcode.json.gz>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/benchmark_data/sveltecomponent.json.gz>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/benchmark_data/seph-blog1.json.gz>
  - <https://crates.io/api/v1/crates/jumprope>
  - <https://crates.io/api/v1/crates/jumprope/reverse_dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/josephg/jumprope-rs`) · [data/wave14/enrich/raw/github_com_josephg_jumprope_rs.json](../../../data/wave14/enrich/raw/github_com_josephg_jumprope_rs.json) (enrichment confidence 0.8)

</details>
