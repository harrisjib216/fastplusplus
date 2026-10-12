# rusty_alloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust rebuild of mimalloc's design; slightly fewer instructions than mimalloc, jemalloc and glibc malloc under callgrind.

| | |
|---|---|
| **Beats** | mimalloc v2.4.5 (also jemalloc, glibc malloc, dlmalloc on wasm32, esp-alloc on ESP32-S3) |
| **Claimed result** | Allocator-only instructions 0.52x / 0.81x / 0.83x of mimalloc on lua / perl / sqlite; whole program 0.96 / 0.99 / 1.00 vs mimalloc, 0.84 / 0.89 / 0.98 vs jemalloc, 0.81 / 0.81 / 0.99 vs glibc malloc; wasm32 churn 4.9-7.3x faster than dlmalloc (but a 2048 B tight loop runs 0.55-0.83x as fast); ESP32-S3 1.44-3.94x faster than esp-alloc 0.11 |
| **Workload** | Callgrind instruction counts (allocator-only and whole-program) on lua, perl and sqlite under LD_PRELOAD on x86-64 Linux; plus wasm32 churn and ESP32-S3 throughput. |
| **Metric** | other |
| **Hardware** | x86-64 Linux (CPU model not stated); XIAO ESP32-S3 at 240 MHz |
| **Adoption** | 3 stars; README claims 54,914 installs |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_alloc) · [benchmark](https://github.com/Remade-With-Rust/rusty_alloc/blob/main/README.md) |

## Verdict

Under callgrind with LD_PRELOAD on x86-64 Linux (CPU model and compiler flags not stated), short lua, perl and sqlite one-liner workloads ran 0.96 / 0.99 / 1.00 of mimalloc v2.4.5's whole-program instructions (0.84-0.98 of jemalloc, 0.81-0.99 of glibc malloc), with the allocator's own instructions at 0.52 / 0.81 / 0.83 of mimalloc's. Wall-clock numbers exist only for wasm32 in node (churn 4.9-7.3x vs dlmalloc, 2 KB loop 0.55-0.83x) and a Seeed XIAO ESP32-S3 at 240 MHz (1.44-3.94x vs esp-alloc 0.11).

## Use it when

- Pure-Rust projects that want a mimalloc-class allocator without a C toolchain in the build (no cc/cmake dependency).
- Shipping one allocator across Linux, macOS, Windows, wasm32 and an ESP32-class MCU from a single dependency.
- wasm modules with churny allocation (many live blocks of 8-512 B), where the README measures 4.9-7.3x over dlmalloc for +2,435 bytes gzipped.
- ESP32-S3 firmware with RAM to spare where small-object allocation throughput matters (1.44-3.94x faster than esp-alloc 0.11 per alloc/free pair).
- When you want double frees to abort rather than silently corrupt (mimalloc release builds accept them), with an opt-in encrypted free-list 'secure' mode.

## Skip it when

- If you need wall-clock evidence: every x86 claim is a callgrind instruction count; the workspace manifest says wall-clock measurement still needs a quiet machine, and whole-program gains over mimalloc are 0-4%.
- Memory-constrained MCUs: needs a 64 KiB RAM floor vs 8 KiB for esp-alloc, held 21 size classes at once vs 24, returned 357 NULLs in 50,000 hostile churn allocations vs 0, and refuses 64 KiB-aligned requests; the README itself says esp-alloc wins memory footprint by 8.5x.
- wasm code dominated by large (2 KB) tight alloc/free loops, where it runs 0.55-0.83x as fast as dlmalloc.
- Long-running processes that must give memory back by default: freed memory stays committed (purge_delay -1); one consumer saw 461 MB retained where the Windows heap dropped to 4 MB.
- Risk-averse production use: the repository dates from 2026, has 3 stars, an open blockmap race issue (#8), and a closed issue (#37) titled 'Whatever you are trying to achieve here, please stop!'; adoption figures in the README are first-party and inconsistent.

## How it is fast

mimalloc's free-list sharding: 32 MiB segments sliced into 64 KiB spans, per-page local free lists, and a four-state lock-free cross-thread free protocol (loom-verified). The authors tuned the hot paths instruction by instruction: free is 21 instructions vs mimalloc's 25 (pointer-to-page resolve through a per-slice owner table in the segment header), all divisions were replaced by shifts and a reciprocal table, and the Rust GlobalAlloc methods are #[inline] so rustc's __rust_alloc shims carry the fast path.

## Compared with alternatives

Pick it over Talc or rlsf when you want one mimalloc-style allocator spanning servers, wasm and an ESP32 rather than a wasm/embedded-only TLSF or arena design; on servers the C and C++ siblings (v8malloc, FastAlloc, Spaces) and upstream mimalloc itself have more mileage and wall-clock data.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none required beyond libc on Unix and windows-sys on Windows; optional portable-atomic for targets without native atomics |
| **Minimum toolchain** | Rust 1.88 (rust-version), edition 2024; repo pins 1.97.1 for development |
| **Platforms** | x86-64 and aarch64 on Linux, macOS and Windows; wasm32-unknown-unknown; no_std ESP32-S3 (Xtensa); RISC-V bare-metal targets listed but the toolchain file says the crate does not yet build for them |
| **Thread safety** | Thread-safe by default (per-thread heaps, lock-free cross-thread free, abandonment and adoption); bare-metal builds must set --cfg ra_single_threaded |
| **Drop-in for the baseline** | partial — LD_PRELOAD interposer and mi_\* C ABI for C/C++ programs, #[global_allocator] for Rust; not a link-time replacement for libmimalloc's full option/stat surface |

## Gotchas

- Bare-metal builds need three settings: --cfg ra_single_threaded, --cfg ra_small_profile, and a Region&lt;N&gt; handed over once; without ra_small_profile it builds and links but every allocation returns null (SEGMENT_SIZE stays 32 MiB).
- Size the embedded region with good_region_size()/region_for(), not a round number or a plain static [u8; N], or segments are stranded or the region is refused (FERR_MISALIGNED).
- The lua callgrind numbers move about 0.26% run to run (hash seed not pinnable); only perl and sqlite counts are bit-repeatable, and the allocator-only ratio is attributed by object, so the glibc arm has no allocator-only figure.
- alloc::stats() counters only exist in debug builds; the opt-in blockmap feature has an open race report under abandon/adopt at low core counts (issue #8).

## Known shortcomings

- Pure-Rust reimplementation of mimalloc; not callable from C++ without the Rust toolchain. Loses on wasm at 2048 B and returns NULL in 357 benchmark cases.
- The x86 claim is callgrind instruction counts only, no wall time; whole-program gain over mimalloc is 0-4%. README install count is inconsistent (54,914 vs 27,892). Open issue 8 (blockmap race); closed issue 37 reads 'Whatever you are trying to achieve here, please stop!'.

## Caveats and trade-offs

First-party only, and the repo is very new (commits since 2026-09-12, 3 stars). Instruction counts, not wall time; the whole-program lead over mimalloc is under 5% and sqlite is 1.00. CPU model and compiler flags for the x86 runs not stated; the lua count is not repeatable. It loses on a 2048 B tight loop in wasm (0.55-0.83x of dlmalloc). On ESP32-S3 it needs a 64 KiB RAM floor vs 8 KiB, returned 357 NULLs in 50,000 churn allocations vs 0, and refuses 64 KiB-aligned requests. The '54,914 active installs' figure is unverified marketing. It is a pure-Rust reimplementation of mimalloc (C mimalloc ships as a dev-only oracle). Bench scripts not run.

Rebuild of the mimalloc architecture in safe-leaning Rust; freed memory stays committed by default like mimalloc; ESP32 build needs a 64 KiB RAM floor and returned 357 NULLs in a 50,000-allocation hostile churn test; refuses 64 KiB-aligned requests.

## Maintenance

Very active (multiple releases since September 2026, now 2.2.x, semver-checked API) and MIT-licensed, but young, single-organisation and marketed heavily; bench scripts (bench/icount-arms.sh, oracle/build.sh) make the instruction counts reproducible on your own machine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party callgrind instruction counts against mimalloc v2.4.5, jemalloc and glibc, with bench scripts in the repo (bench/icount-arms.sh, bench/opscan.sh), plus wasm and ESP32-S3 timings. The x86 CPU model and the compiler and flags for the Linux runs are not stated, so it cannot be A.
- **Verifier notes:** The README tables match the record; I added the glibc whole-program row, widened the ESP32 range to the table's 1.44-3.94x, and added the wasm loss. It reimplements mimalloc in Rust, so the orchestrator may want to judge whether it folds as a mimalloc port (duplicate) or stands as its own entry. Metadata from github.com: MIT, 3 stars, not a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party numbers
- **Pages the verifier opened:**
  - <https://github.com/Remade-With-Rust/rusty_alloc>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/README.md>
  - <https://github.com/Remade-With-Rust/rusty_alloc/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/crates/rusty_alloc/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/crates/rusty_alloc_api/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/bench/icount-arms.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/oracle/build.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_alloc/HEAD/rust-toolchain.toml>
  - <https://github.com/Remade-With-Rust/rusty_alloc/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/remade-with-rust/rusty_alloc`) · [data/wave11/enrich/raw/github_com_remade_with_rust_rusty_alloc.json](../../../data/wave11/enrich/raw/github_com_remade_with_rust_rusty_alloc.json) (enrichment confidence 0.7)

</details>
