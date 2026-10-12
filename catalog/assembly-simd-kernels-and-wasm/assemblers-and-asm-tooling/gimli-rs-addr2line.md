# addr2line (gimli-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust DWARF symbolication library plus addr2line-style CLI; first-party chart shows it beating binutils, elfutils and llvm-addr2line.

| | |
|---|---|
| **Beats** | GNU binutils addr2line (also elfutils eu-addr2line and llvm-addr2line) |
| **Claimed result** | README: 'Current benchmarks show a performance improvement in all cases'. Mean wall times read from the bar heights of benchmark-time.svg (derived from page data: bar geometry measured against the chart's 0.5 s axis ticks): libxul.so (162MB, 500 queries) gimli 0.10 s vs binutils addr2line 1.15 s (about 11x), llvm-addr2line 0.48 s (about 4.7x), eu-addr2line 3.25 s (about 32x); clangd-18 (360MB, 500 queries) 0.18 s vs binutils 2.92 s (about 16x), llvm 0.39 s (about 2.1x), eu 2.17 s (about 12x); mold (314MB, 1000 queries) 0.14 s vs binutils 1.19 s (about 8.5x), llvm 0.36 s (about 2.6x), eu 0.82 s (about 5.9x); postgres (38MB, 10000 queries) 0.067 s vs binutils 0.176 s (about 2.6x), llvm 0.079 s (about 1.2x), eu 1.91 s (about 28x). All ratios are approximate chart readings. |
| **Workload** | Whole-command wall time (hyperfine mean) of 'addr2line -af -e &lt;file&gt;' resolving a fixed-seed random sample of addresses read from stdin, on four debug-info files: Firefox libxul.so.debug (162MB, 500 queries), clangd-18.debug (360MB, 500), mold.debug (314MB, 1000) and postgres.debug (38MB, 10000); each run includes process start-up and DWARF loading. |
| **Metric** | throughput |
| **Compiler and flags** | cargo build --release --features bin inside an opensuse/tumbleweed Docker image (scripts/docker/Dockerfile-opensuse installs rustup, binutils, elfutils, llvm and hyperfine unpinned) via scripts/benchmark-addr2line-docker.sh; baseline tools are the image's /usr/bin/addr2line, /usr/bin/llvm-addr2line and /usr/bin/eu-addr2line, versions not stated |
| **Adoption** | 429 stars; crates.io addr2line has about 541M downloads |
| **Last commit** | 2026-08-01 |
| **Links** | [repository](https://github.com/gimli-rs/addr2line) · [benchmark](https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/benchmark-time.svg) |

## Verdict

Hyperfine mean wall time of 'addr2line -af -e &lt;file&gt;' over fixed-seed random address samples on four openSUSE Tumbleweed debuginfo files, chart read approximately: libxul.so 0.10 s vs binutils 1.15 s (about 11x), llvm-addr2line 0.48 s, eu-addr2line 3.25 s; clangd-18 0.18 s vs 2.92 s (about 16x); mold 0.14 s vs 1.19 s; postgres 0.067 s vs 0.176 s (about 2.6x) and llvm 0.079 s (about 1.2x). Rust stable from rustup in Docker, baseline tool versions and CPU not stated, chart dated 2024-08-06.

## Use it when

- Long-lived processes that symbolize many addresses against the same binary (profilers, crash reporters, tracing tools): the parse cost is paid once per unit and amortised.
- Batch symbolization of hundreds to thousands of addresses from large C/C++/Rust debug files (hundreds of MB), where the chart shows 2.6-16x over binutils addr2line.
- Rust projects that need in-process symbolization without shelling out to binutils or llvm-symbolizer, including no_std + alloc targets (the Context API) and wasm (feature 'wasm').
- Split DWARF (DWO/DWP), Mach-O dSYM bundles next to the executable, and DWARF supplementary files (--sup) on any platform the object crate parses.

## Skip it when

- Memory-constrained hosts: the README says it 'optimizes for speed over memory by caching parsed information', the benchmark measures time only, and issue #212 (2021, an older version) measured 2.6 GB RSS on a 470 MB libxul.debug against 1.3 GB for binutils.
- One-off lookups of a handful of addresses: every CLI invocation reloads DWARF, and on the 38 MB postgres input it is only about 1.2x ahead of llvm-addr2line.
- Scripts that rely on GNU addr2line's full option set or debug-file discovery: the CLI has no -b target, no demangling-style selection, and the Loader does not follow .gnu_debuglink or .gnu_debugaltlink (a TODO in src/loader.rs), so you must point -e at the .debug file and pass --sup yourself.
- C or C++ codebases that want a C API: it is a Rust crate with no C bindings in this repo.
- Binaries without DWARF (stripped, or PDB-only Windows builds): it falls back to the symbol table for function names only.

## How it is fast

Lazy, cached parsing: a Context first builds a sorted table of unit address ranges (DW_AT_ranges, .debug_aranges, low/high pc) and binary-searches it per probe; a unit's line program, function DIEs and inlined-function tree are parsed only on first hit and memoised in OnceCell, so later lookups in the same unit are cheap. Loader memory-maps the file and borrows sections zero-copy (only compressed sections are decompressed into an arena). Abbreviation tables shared by many small units are cached (PR #318), which the maintainer reported roughly doubled speed on the PostgreSQL input, where gimli had been 2.12x slower than llvm-addr2line before the fix.

## Compared with alternatives

No symbolizer siblings are catalogued; the nearest entries (iced, Zydis, bddisasm, Intel XED) decode instruction bytes, not debug info. Pick addr2line when you need address-to-source-line and inline-frame resolution, typically alongside one of those disassemblers.

## Integration

| | |
|---|---|
| **Form** | crate (library) plus optional CLI binary via the 'bin' feature |
| **Dependencies** | gimli 0.34 (read); optional object 0.40, memmap2, typed-arena (loader feature), rustc-demangle, cpp_demangle, smallvec, fallible-iterator, clap (bin) |
| **Minimum toolchain** | Rust 1.88 (rust-version in Cargo.toml), edition 2018 |
| **Platforms** | any: no_std + alloc for Context; std and mmap for Loader; object files are parsed by the object crate (ELF, Mach-O with dSYM lookup, wasm behind the 'wasm' feature) |
| **Thread safety** | Context is Send (asserted by a unit test) but not Sync, because lazy caches use core::cell::OnceCell; use one Context per thread or guard it with a lock. |
| **Drop-in for the baseline** | partial: the CLI accepts the common GNU addr2line flags and stdin address streams, but lacks -b, demangle-style selection and debuglink discovery, and output equivalence with binutils is not tested by the benchmark |

## Gotchas

- Harness scope: the chart times whole CLI runs of '-af' only (no -i inlines, no -C demangling) and never compares outputs across tools; the address sample is drawn from gimli addr2line's own --all listing, and hyperfine --min-runs=1 means eu-addr2line and binutils are timed only once or twice per input (PR #315's sample output shows elfutils as a single run).
- The chart is a one-off from 2024-08-06 (PR #325, around 0.24.x, Matplotlib metadata) and has never been regenerated for 0.25-0.27; tool versions come from an unpinned openSUSE Tumbleweed image whose Dockerfile names clang18 and postgresql16 debuginfo packages, so the image may not build as written today. No CPU, no RSS.
- The speedups depend on fixes merged during the benchmarking work: PR #315's first sample had gimli at 391 ms vs llvm-addr2line 398 ms on clangd-18 (1.02x), and PR #318 notes gimli was 2.12x slower than llvm-addr2line on postgres before the abbreviation cache.
- Maintainer stance on panics: issue #363 (0.25.1, unwrap on None in function.rs:205) was closed 'not planned' without a reproducer; malformed DWARF is otherwise returned as gimli::Error.

## Known shortcomings

- First-party numbers exist only as a bar chart with no CPU model and unpinned tool versions (openSUSE Tumbleweed); the 2.6-16x over binutils addr2line and 1.2-4.7x over llvm-addr2line ratios are read from SVG bar heights (derived from page data).
- Enricher: the chart is a one-off from 2024-08-06 (PR #325, around 0.24.x) never regenerated for 0.25-0.27.1; it times -af only (no -i, no -C, no output comparison, no RSS) on a sample drawn from gimli's own --all listing with hyperfine --min-runs=1 (eu-addr2line and binutils run 1-2 times); the Dockerfile pins clang18/postgresql16 debuginfo on rolling Tumbleweed; the lead changed during benchmarking (PR #315 clangd 391 vs 398 ms; PR #318 says gimli was 2.12x slower than llvm on postgres before the abbreviation cache); issue #212 (2021) reports 2.6 GB RSS vs binutils 1.3 GB; the loader skips .gnu_debuglink/.gnu_debugaltlink; Context is Send, not Sync.

## Caveats and trade-offs

First-party chart only: no numbers in text, no CPU model, tool versions float with the Tumbleweed image (SVG metadata dates the chart 2024-08-06), hyperfine --min-runs=1 so slow tools may be timed once or twice. Ratios above are read from SVG bar geometry, not from published values. Each run is a whole CLI invocation, so start-up and lazy DWARF parsing dominate at small query counts; the README itself says the library 'aims to perform similarly' to the existing tools. The address sample is generated by gimli addr2line itself (--all) and output equivalence across tools is not checked. Benchmark script and plotting script are public, so the chart can be regenerated.

Trades memory for speed by caching parsed DWARF (lazy parsing where possible). Rust library plus a CLI that implements only part of GNU addr2line's options; not a C or C++ API. Needs debug info in DWARF.

## Maintenance

Actively maintained in the gimli-rs organisation (0.27.1, 2026-08-01; about 541M crates.io downloads, 77 reverse dependencies including backtrace and wasmtime) and dual Apache-2.0/MIT, so it is safe to depend on; the published speed chart is two years and three minor versions old.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (benchmark-time.svg, hyperfine means from scripts/benchmark-addr2line.sh, plotted by scripts/benchmark-plot.py) shows gimli addr2line faster than binutils addr2line, eu-addr2line and llvm-addr2line on four inputs; benchmark code is public but no CPU model, compiler or tool versions are stated (openSUSE Tumbleweed rolling image, unpinned), so C.
- **Verifier notes:** README claim and chart confirmed; I extracted approximate means from the SVG bars (gimli about 2.6-16x faster than binutils addr2line, 1.2-4.7x faster than llvm-addr2line) and added them as derived values. Tier C stays (first-party, no CPU or versions). Metadata confirmed on github.com: Apache-2.0 OR MIT, 429 stars, not a fork or archived, last commit 2026-08-01 (Release 0.27.1), active. Shortcomings: chart-only numbers, no hardware or tool versions, single-run minimum, CLI start-up included.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-42 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/gimli-rs/addr2line>
  - <https://github.com/gimli-rs/addr2line/commits>
  - <https://github.com/gimli-rs/addr2line/tree/master/scripts>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/README.md>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/benchmark-time.svg>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-addr2line.sh>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-addr2line-docker.sh>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-plot.py>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/docker/Dockerfile-opensuse>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/README.md>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/benchmark-time.svg>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-addr2line.sh>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-addr2line-docker.sh>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/benchmark-plot.py>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/scripts/docker/Dockerfile-opensuse>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/src/bin/addr2line.rs>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/src/loader.rs>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/src/unit.rs>
  - <https://raw.githubusercontent.com/gimli-rs/addr2line/HEAD/benches/bench.rs>
  - <https://github.com/gimli-rs/addr2line/commits/master/benchmark-time.svg>
  - <https://github.com/gimli-rs/addr2line/commits/main/benchmark-time.svg>
  - <https://github.com/gimli-rs/addr2line/pull/315>
  - <https://github.com/gimli-rs/addr2line/pull/318>
  - <https://github.com/gimli-rs/addr2line/pull/325>
  - <https://github.com/gimli-rs/addr2line/issues?q=is%3Aissue%20memory%20OR%20slow%20OR%20performance>
  - <https://github.com/gimli-rs/addr2line/issues/212>
  - <https://github.com/gimli-rs/addr2line/issues/363>
  - <https://crates.io/api/v1/crates/addr2line>
  - <https://crates.io/api/v1/crates/addr2line/reverse_dependencies?per_page=10>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gimli-rs/addr2line`) · [data/wave13/enrich/raw/github_com_gimli_rs_addr2line.json](../../../data/wave13/enrich/raw/github_com_gimli_rs_addr2line.json) (enrichment confidence 0.8)

</details>
