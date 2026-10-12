# librope

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Two-file C99 skip-list UTF-8 rope with O(log n) insert/delete at character offsets; beats flat strings on large documents.

| | |
|---|---|
| **Beats** | flat contiguous string (a hand-written Rust String insert/delete by Unicode character offset, labelled 'Raw string'); the README itself says 'straight C strings' but gives no numbers for that |
| **Claimed result** | README table of jumprope-rs, librope (C) vs Raw string: automerge-paper 16.28 ms vs 3908.13 ms; rustcode 3.93 ms vs 569.44 ms; sveltecomponent 1.59 ms vs 41.05 ms; seph-blog1 10.01 ms vs 1238.44 ms (about 240x, 145x, 26x and 124x faster, derived from page data). Same table: librope beats Ropey on all four (for example 16.28 ms vs 25.16 ms on automerge-paper) but is 2-3x slower than its Rust rewrite Jumprope (6.66 ms). librope's own README claims about 15 million edit operations per second and that inserts and deletes outperform straight C strings for any document longer than a few hundred bytes (no table for the C-string claim). |
| **Workload** | Replaying real-world text-editing traces (automerge-paper, rustcode, sveltecomponent, seph-blog1 from josephg/crdt-benchmarks) as insert/delete operations at character offsets, measured as total replay time in ms; librope is called from Rust through FFI ('librope (C)' column). |
| **Metric** | throughput |
| **Hardware** | A single core of a Ryzen 5800X (from the jumprope-rs README); OS and memory not stated. |
| **Compiler and flags** | Not fully stated. rope_benches README says to run `cargo run --release -- --bench` (criterion 0.3); the jumprope-rs workspace release profile sets lto = true and codegen-units = 1; rope.c is compiled by the Rust `cc` crate from rope_benches/build.rs with no explicit flags (so the optimization level comes from cargo's release profile, not stated in the README); librope's own Makefile uses -O2 -Wall -std=c99 but that build is not what the table measured. rustc and C compiler versions are not given. |
| **Adoption** | 301 stars |
| **Last commit** | 2021-10-13 |
| **Links** | [repository](https://github.com/josephg/librope) · [benchmark](https://github.com/josephg/jumprope-rs) |

## Verdict

In the author's jumprope-rs criterion harness on a single core of a Ryzen 5800X (Rust calling a vendored rope.c with ROPE_MAX_HEIGHT 20 through FFI, built by the cc crate at the cargo release opt level, compiler versions not stated), librope replayed four real editing traces in 1.59-16.28 ms against 41-3908 ms for a naive Rust String that rescans characters on every edit (about 26-240x, derived from page data), beat Ropey (16.28 vs 25.16 ms on automerge-paper) and lost 2-3x to Jumprope. There are no std::string, plain C buffer or SGI crope numbers: librope's own test/benchmark.c defines 'c string' and 'sgirope' rows but its loop runs only the first implementation.

## Use it when

- Editor buffers, OT/CRDT document replay or collaborative-editing servers in C or C++ where documents are kilobytes to megabytes and edits land at arbitrary character offsets
- Keystroke-level edit streams (inserts and deletes of a few characters), which is the measured workload
- Interop with JavaScript, Java, C# or Objective-C positions: build with -DROPE_WCHAR=1 and use rope_insert_at_wchar / rope_del_at_wchar instead of O(n) offset conversion
- Projects that want a dependency-free, MIT-licensed two-file C99 source drop with pluggable allocators

## Skip it when

- Small strings: the README claims a win only above a few hundred bytes (no measurement in the repo; open issue #10 asks whether the roughly 200-byte crossover still holds), and every rope allocates an oversized head block of about 8.8 KB on 64-bit targets
- Reading parts of the text: there is no substring, character-at, line/column or search API, only whole-string export or per-node iteration (substring request issue #6 open since 2018)
- New code that can use Rust: the author's maintained rewrite Jumprope (josephg/jumprope-rs, gap buffer in each skip-list node) is 2-3x faster on the same traces
- Concurrent access to one rope, or untrusted edit streams where a predictable skip-list shape matters: node heights come from the unseeded global random(), and Jumprope later added a 'ddos_protection' RNG feature for that reason
- Builds that need tested MSVC or Apple Silicon support: the code relies on POSIX ssize_t and random() (a _WIN32 shim maps random() to rand()), and the Makefile forces -arch x86_64 on macOS

## How it is fast

The text is split into nodes holding up to ROPE_NODE_STR_SIZE (136) bytes of UTF-8, linked as a skip list whose every link records how many characters it skips, so locating a character offset is an O(log n) descent like an order-statistic tree, with no rebalancing (node heights are random with a 25% promotion chance, ROPE_BIAS). An insert that fits is a memmove inside one small node; otherwise the node is split and new nodes are spliced in, so no edit moves more than a node's worth of bytes. With ROPE_WCHAR each link also carries a UTF-16 unit count, giving O(log n) UTF-16-to-character offset conversion at roughly 30-35% throughput cost.

## Compared with alternatives

None of the catalogued siblings (bstring, buffet, FastString, Str, zuu_string_view, to_static_string, jank persistent_string) offer O(log n) edits in the middle of a large document; pick librope for editor-style workloads on kilobyte-plus texts from C, and bstring or buffet for ordinary small-string handling in C, where librope's 8.8 KB-per-rope overhead and missing read API would hurt.

## Integration

| | |
|---|---|
| **Form** | source-drop (rope.c and rope.h; the Makefile can also build librope.a) |
| **Dependencies** | none beyond libc |
| **Minimum toolchain** | C99 (Makefile uses -std=c99); needs POSIX ssize_t and random(); the public structs nest a flexible-array-member struct inside another struct, which GCC and Clang accept as an extension (the header has extern "C" guards for C++ use) |
| **Platforms** | not documented beyond POSIX-style C; Windows only via a random() to rand() shim; Makefile hard-codes -arch x86_64 on Darwin |
| **Thread safety** | Not synchronized: rope.h says not to access the same rope from multiple threads; separate ropes still share libc random() state for node heights |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the cited table (jumprope-rs rope_benches, first-party): the 'Raw string' baseline finds each byte offset by scanning char_indices from the start and grows by pushing one '\0' per byte, so 26-240x mostly measures that O(n) scan; the realworld loop only asserts the final char_len, never the content (CRope::to_string is unimplemented), so librope's output on those traces is not checked; rope.c is built by the cc crate, which does not define NDEBUG, so its assert() calls stay live, and each insert allocates a CString (both slightly handicap librope); rope_del is declared '-&gt; u32' on the Rust side although it returns void in C.
- Memory: ROPE_SIZE is sizeof(rope) + sizeof(rope_node) \* ROPE_MAX_HEIGHT, which reserves a 144-byte node per level where a 16-byte link would do (about 8.8 KB per rope instead of about 1.1 KB at height 60; computed from the struct layout); nodes are never merged, since deletes shrink nodes in place and free them only when empty, and mid-node inserts split off the tail as its own node.
- No allocation-failure handling: rope_new2 and alloc_node dereference the allocator's result without a NULL check, so OOM crashes rather than returning an error.
- UTF-8 handling is lax and out-of-range positions are clamped: the validator only checks lead and continuation bit patterns (it accepts 5- and 6-byte forms, overlong encodings and surrogates), invalid input returns ROPE_INVALID_UTF8 without inserting, rope_insert/rope_del silently clamp positions past the end, and the header comment says each height is half as likely while the code uses a 25% promotion bias.

## Known shortcomings

- Tier C: the jumprope-rs README table (16.28 vs 3908.13 ms on automerge-paper, Ryzen 5800X) compares against the author's naive Rust String with an O(n) char_indices scan per edit, not std::string or a C buffer; the String row is commented out in rope_benches/src/main.rs with a stale &test_data argument and a hard-coded /home/seph path; the table dates from 2021-10 (commits 7842779, 6df4d19); the benchmarked rope.c is a modified vendored copy (ROPE_MAX_HEIGHT 20 vs 60); no libstdc++/libc++/MSVC run; superseded by the author's 2-3x faster Jumprope. Abandoned (last commit 2021-10-13); MIT.
- Enricher (jumprope-rs rope_benches): the realworld check compares only the final char_len and never the content (CRope::to_string unimplemented); the cc crate never defines NDEBUG so rope.c's assert()s stay live; a CString is built per insert; rope_del is declared as returning u32 vs C void (all handicap librope slightly); the raw-string baseline rescans char_indices from the start on every edit. Code: ROPE_SIZE uses sizeof(rope_node) per level (about 8.8 KB per rope vs about 1.1 KB); no node merging; no NULL checks on allocation; lax UTF-8 validator (5/6-byte, overlong, surrogates accepted); unseeded global random() heights; Makefile forces -arch x86_64 on macOS; no substring API (issue #6).

## Caveats and trade-offs

First-party: the table lives in the README of the author's own Rust rewrite (jumprope-rs), where librope is a comparison column, not the subject; the table was last updated in October 2021 (commits 7842779 and 6df4d19) and the full criterion report on home.seph.codes is blocked from this environment (EGRESS_BLOCKED), so it was not opened. The 'Raw string' baseline is the author's own Rust String wrapper (rope_benches/src/edittablestr.rs) that finds the byte offset by scanning char_indices from the start on every edit and grows the string one pushed '\0' at a time, so the 25x-240x gaps mostly measure an O(n) character-offset scan on a flat string, not a tuned memmove-based std::string or C char buffer. The String row is commented out in the current rope_benches/src/main.rs ('This takes a long time to run') and passes a variable (&test_data) that no longer exists, and the realworld group loads traces from a hard-coded /home/seph/src/diamond-types/benchmark_data path, so the table is not reproducible out of the box. The C column ('C-JumpRope' in the code) is a vendored copy of rope.c/rope.h inside rope_benches that differs from librope HEAD (ROPE_MAX_HEIGHT 20 instead of 60, skip_size renamed skip_chars, minor type casts); the algorithm is the same. librope is driven through FFI with a CString allocation per insert, which handicaps it slightly. No libstdc++, libc++ or MSVC STL comparison and no C++ std::string or SGI rope baseline appears anywhere (librope's own test/benchmark.c loops only over the first implementation, librope; the 'c string' and SGI crope rows exist but are skipped). The librope README's 15M ops/s figure links to the blocked home.seph.codes report. Last commit 2021-10-13; the author says the library works but he has moved to Rust and points users to Jumprope, which the same table shows is 2-3x faster.

Skip-list rope over UTF-8; O(log n) insert and delete at character offsets, two files (rope.c, rope.h) to drop into a project. Compiling with -DROPE_WCHAR=1 for UTF-16 offset support costs about 35% throughput per its README. Heavier than a plain string for small documents (its README only claims a win for documents longer than a few hundred bytes). The author recommends the Rust rewrite Jumprope for new work.

## Maintenance

Abandoned since 2021-10 (the author says it works but points users to Jumprope), yet MIT-licensed, two files and C99, so easy to vendor; the only numbers are first-party and their harness has flaws (String baseline row commented out and rescanning characters per edit, length-only result check, assert()s left enabled, traces loaded from a hard-coded /home/seph path), so read the 26-240x as rope versus a char-scanning flat string, not versus std::string.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The jumprope-rs README table (Ryzen 5800X, single core) shows librope (C) at 16.28/3.93/1.59/10.01 ms vs Raw string 3908.13/569.44/41.05/1238.44 ms, exactly as claimed; it is first-party (author's own rewrite repo), the harness rope_benches/src/main.rs is public but rustc and C compiler versions are never stated, the C flags are left to the cc crate defaults, and the Raw string row is commented out in the current code, so it falls short of A.
- **Verifier notes:** Numbers match the jumprope-rs README exactly; tier C stands (first-party, compiler versions unstated, baseline row disabled in current code). Shortcomings to record: baseline is a naive Rust String with an O(n) char-offset scan per edit (not std::string or a C buffer), table dates from 2021-10 and is not reproducible as checked in, benchmarked rope.c is a lightly modified vendored copy (ROPE_MAX_HEIGHT 20), and the library is superseded by the author's own 2-3x faster Jumprope. maintenance_status corrected to abandoned (last commit 2021-10-13, about 5 years old; the README says it works but the author moved on, not that it is complete).
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-65 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/josephg/librope>
  - <https://github.com/josephg/librope/commits>
  - <https://github.com/josephg/jumprope-rs>
  - <https://github.com/josephg/jumprope-rs/commits/master/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/build.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/edittablestr.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.c>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.h>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/Makefile>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/benchmark.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/rope.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/rope.h>
- **Sources the enricher read:**
  - <https://github.com/josephg/librope/issues?q=is%3Aissue>
  - <https://github.com/josephg/librope/issues/10>
  - <https://github.com/josephg/librope/issues/6>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/rope.h>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/rope.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/Makefile>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/benchmark.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/tests.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/tests.h>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/slowstring.c>
  - <https://raw.githubusercontent.com/josephg/librope/HEAD/test/slowstring.h>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/README.md>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/Cargo.toml>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/build.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/main.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/rope.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/src/edittablestr.rs>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.c>
  - <https://raw.githubusercontent.com/josephg/jumprope-rs/HEAD/rope_benches/rope.h>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/flags.rs>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/tool.rs>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/josephg/librope`) · [data/wave1/enrich/raw/github_com_josephg_librope.json](../../../data/wave1/enrich/raw/github_com_josephg_librope.json) (enrichment confidence 0.75)

</details>
