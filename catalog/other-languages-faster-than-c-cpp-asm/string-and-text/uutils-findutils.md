# uutils findutils (find, xargs, locate, updatedb)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust reimplementation of GNU find, xargs, locate and updatedb aiming at drop-in compatibility; never timed against GNU find.

| | |
|---|---|
| **Beats** | GNU findutils find (C) |
| **Claimed result** | None: no speed number or 'faster than GNU find' claim appears in the README, DEVELOPMENT.md, docs/src, the benches or the workflows I opened. |
| **Workload** | No timing comparison against GNU find was found. The repo has Criterion/CodSpeed end-to-end benchmarks (benches/find_bench.rs, xargs_bench.rs, locate_bench.rs, updatedb_bench.rs) that run only the uutils code through find_main with output sent to a sink, and a CodSpeed workflow (.github/workflows/codspeed.yml) that tracks regressions in simulation mode; the README compares only GNU and BFS test-suite pass rates over time. |
| **Metric** | throughput |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 649 stars, 109 forks; official uutils organisation project; latest crates.io release findutils 0.10.0 (20,982 downloads), repository Cargo.toml already at 0.11.0 (unreleased); no GitHub releases |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/uutils/findutils) |

## Verdict

No speed measurement against GNU find exists: the README compares only GNU and bfs test-suite pass rates, the benches time uutils find alone with output discarded, and searches of the issue tracker and the web found no uutils-versus-GNU timing.

## Use it when

- You want a memory-safe find/xargs/locate/updatedb that follows GNU syntax, for example alongside uutils coreutils on a Rust-based userland.
- Windows, macOS, Linux or wasm32-wasip1 targets where GNU findutils is unavailable or awkward to ship; CI builds all four.
- Embedding find semantics in a Rust program through find_main and the Dependencies trait, with output sent to your own writer.
- Scripts that rely on find expression syntax (-prune, -printf, -regex, -size) and are covered by the passing part of the GNU test suite.

## Skip it when

- As a speed upgrade over GNU find: no comparison exists, traversal is single-threaded, and the project's benchmarks measure only its own code.
- When exact GNU compatibility matters: the GNU test suite shows 425 of 495 tests passing and 69 failing, and the bfs suite 274 of 317 passing and 37 failing (findutils-tracking, 2026-10-10).
- Large-tree searches where a parallel walker helps; hunt, fd or ignore-based walkers are the measured options.
- Pure-Rust or minimal-dependency builds: it pulls in clap, chrono, nix, uucore, walkdir, regex and onig, the last binding the C Oniguruma library.

## How it is fast

It does not claim to be faster and no speed technique is documented. Traversal is a single-threaded depth-first walk through the walkdir crate, -regex matching uses the Rust regex crate with onig (Oniguruma bindings) also in the dependency list, and release builds use fat LTO, codegen-units=1 and panic=abort. Parallel traversal (#112, open since 2021) and a metadata and user/group-name cache (#430, open since 2024) are the only performance ideas on the tracker.

## Compared with alternatives

Pick it over hunt or walkdir/ignore-based walkers only when GNU find syntax and behaviour matter more than speed; hunt (12.31x on a first-match search) and walkdir in dkorunic/bench_walk (about 1.3x over system find) are the catalogued entries with measured wins over GNU find, and this project has none.

## Integration

| | |
|---|---|
| **Form** | crate with binaries (find, xargs, locate, updatedb) and a library API |
| **Dependencies** | argmax, chrono, clap, faccess, nix, onig (Oniguruma C library bindings), regex, uucore, walkdir, itertools, thiserror; rustix on WASI |
| **Minimum toolchain** | Rust 1.88 (rust-version in Cargo.toml, edition 2021) |
| **Platforms** | Linux, macOS and Windows tested in CI; wasm32-wasip1 build checked in CI |
| **Thread safety** | not documented (command-line tools; the library entry point takes a Dependencies object holding a RefCell writer) |
| **Drop-in for the baseline** | partial — same command names and GNU syntax, but 69 GNU test-suite failures and 37 bfs test-suite failures remain as of 2026-10-10 |

## Gotchas

- The repo's Criterion benches (benches/find_bench.rs and siblings) build a synthetic tree and call find_main with output sent to io::sink, and CodSpeed runs them in simulation mode; they track regressions in uutils itself and contain no GNU find baseline, so they cannot support a faster-than-GNU claim.
- The repository Cargo.toml is at 0.11.0 while crates.io's latest release is 0.10.0 (2026-08-03), so cargo install findutils gives an older build than main.
- Every file entry goes through a single-threaded walkdir walk; issue #430 (open) says file metadata is fetched repeatedly and uid/gid-to-name lookups are not cached, which costs most on -user, -group and -printf heavy expressions.

## Known shortcomings

- No speed comparison with GNU find anywhere; the benches cover only uutils code. crates.io's newest release is 0.10.0 while Cargo.toml says 0.11.0.
- Enricher: still no GNU find timing anywhere (CodSpeed benches time uutils alone in simulation mode with output to io::sink); traversal is single-threaded walkdir with parallel traversal (#112) and a metadata cache (#430) still open; compatibility as of 2026-10-10 is 425 of 495 GNU tests and 274 of 317 bfs tests.

## Caveats and trade-offs

The lead said uutils publishes benchmark comparisons against GNU find; I found none in the repo (README, DEVELOPMENT.md, docs/src, benches, workflows, issue and PR searches for performance and hyperfine). A third-party search result suggests minifind (a different Rust find clone) and bfs publish such comparisons, not uutils. Tier D is kept only so the project is on record with this explanation; 649 stars and uutils' reach are the only notability. The CodSpeed benches could become a source if a GNU baseline is ever added.

Goal is drop-in GNU compatibility, not speed; tracked via the GNU and BFS test suites at github.com/uutils/findutils-tracking. Issues #112 (leverage parallel capabilities) and #430 (create cache to optimize) show performance ideas exist; their current status was not checked.

## Maintenance

Actively maintained official uutils project (MIT, commits through 2026-10-12, crates.io 0.10.0 with about 21,000 downloads) that is a compatibility replacement rather than a performance pick; it stays at tier D on record only because it was proposed as faster than GNU find.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No timing against GNU find exists: the README compares only GNU and BFS test-suite pass rates, DEVELOPMENT.md has no performance claim, and benches/find_bench.rs runs only find_main with output sent to io::sink; a WebSearch found no published uutils-vs-GNU speed comparison.
- **Verifier notes:** Kept at D under the keep-and-document rule: not claimed faster and no baseline comparison anywhere (shortcoming: drop-in compatibility project, speed versus GNU find never measured). License MIT confirmed (LICENSE, Copyright Google Inc.); last commit 2026-10-12 confirmed, active.
- **Fields the verifier corrected:** `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-115 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/uutils/findutils>
  - <https://github.com/uutils/findutils/commits>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/README.md>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/DEVELOPMENT.md>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/benches/find_bench.rs>
  - <https://crates.io/api/v1/crates/findutils>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/README.md>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/DEVELOPMENT.md>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/benches/find_bench.rs>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/uutils/findutils/HEAD/.github/workflows/codspeed.yml>
  - <https://github.com/uutils/findutils/issues?q=is%3Aissue%20performance%20OR%20slow%20OR%20faster%20OR%20speed>
  - <https://github.com/uutils/findutils/issues/112>
  - <https://github.com/uutils/findutils/issues/430>
  - <https://github.com/uutils/findutils/commits>
  - <https://github.com/uutils/findutils-tracking>
  - <https://raw.githubusercontent.com/uutils/findutils-tracking/HEAD/gnu-result.json>
  - <https://raw.githubusercontent.com/uutils/findutils-tracking/HEAD/bfs-result.json>
  - <https://crates.io/api/v1/crates/findutils>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/uutils/findutils`) · [data/wave14/enrich/raw/github_com_uutils_findutils.json](../../../data/wave14/enrich/raw/github_com_uutils_findutils.json) (enrichment confidence 0.8)

</details>
