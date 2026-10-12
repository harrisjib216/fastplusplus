# metal-json

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust crate that parses JSON to a simdjson-format tape on Apple Silicon GPUs (Metal); beats C++ simdjson above \~4-5 MiB.

| | |
|---|---|
| **Beats** | simdjson |
| **Claimed result** | On twitter-shaped documents, 1.34x-2.71x faster than C++ simdjson from 8 MiB to 512 MiB (1.34x at 8 MiB, 1.81x at 16 MiB, 2.28x at 64 MiB, 2.06x/2.19x/2.71x at 100/256/512 MiB; 7.51 vs 2.77 GB/s at 512 MiB). On number-dense canada.json it is 1.42x faster at 2.1 MiB. It loses below the \~4.3 MiB twitter crossover: 0.96x at 4 MiB, 0.33x at 1 MiB, 0.12x (simdjson \~8x faster) at 0.6 MiB, and 0.44x on citm_catalog (1.6 MiB). |
| **Workload** | Parse-to-tape plus an identical stats walk (node count, unescaped string bytes, XOR of number payloads) inside the timed region, for both metal-json (Metal GPU kernels) and C++ simdjson's DOM tape API. The inputs are canonical twitter/citm_catalog/canada from simdjson-data plus deterministic twitter-template expansions from 1 MiB to 512 MiB. An untimed check asserts bit-identical stats before timing. |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max, 128 GiB unified memory, macOS 26.5.1 |
| **Compiler and flags** | simdjson v4.6.4 amalgamation built through the Rust cc crate with -O3 -std=c++17 -DNDEBUG and -mcpu=native on aarch64 (bench/build.rs). The C++ compiler and its version are not stated. metal-json: rustc 1.95.0 and Apple Metal toolchain 32023.883 (per bench-report.md). Criterion medians. |
| **Adoption** | 18 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/Brooooooklyn/metal-json) · [benchmark](https://github.com/Brooooooklyn/metal-json/blob/main/docs/parsing-json-on-an-apple-gpu.md) |

## Verdict

The author's bench report (2026-06-12) times parse-to-tape plus an identical stats walk for metal-json against vendored C++ simdjson v4.6.4 on one Apple M5 Max (128 GiB, macOS 26.5.1). simdjson ran its single-document DOM parser, built with -O3 -mcpu=native through the Rust cc crate (compiler version not stated), and both parsers were checked for bit-identical stats before timing. metal-json won 1.34x at 8 MiB rising to 2.71x at 512 MiB (7.51 vs 2.77 GB/s) on twitter-template expansions, and 1.42x on canada (2.1 MiB). It lost below about 4.3 MiB (0.12x at 0.6 MiB, 0.44x on citm_catalog), and non-twitter shapes were measured only at their small canonical sizes.

## Use it when

- Single JSON documents of roughly 8 MiB and up (dumps, exports, big API payloads) parsed on an Apple Silicon Mac. The author measured 1.34x over C++ simdjson at 8 MiB, rising to 2.06-2.71x at 100-512 MiB on twitter-shaped data.
- Number-dense documents such as coordinate/GeoJSON arrays: canada.json (2.1 MiB) already parsed 1.42x faster than simdjson, below the twitter crossover.
- Throughput-bound batch jobs that keep one `Parser` alive, so the Metal device, pipeline states and pooled buffers stay warm across parses.
- Rust code that needs a fully materialized tape of a huge file (random access, O(1) subtree skips) rather than streaming extraction. In the same report it was about 3.5x faster than Rust simd-json at 512 MiB (7.51 vs 2.16 GB/s) and 1.35x faster at 4 MiB.

## Skip it when

- Small documents or per-request latency paths. Every parse pays about 0.5-0.9 ms of fixed dispatch/sync overhead: simdjson was about 8x faster on twitter.json (0.6 MiB), about 3x faster at 1 MiB, and 2.3x faster on citm_catalog (1.6 MiB).
- Anything other than macOS on Apple Silicon: there is no Linux, Windows, x86 or discrete-GPU path. The only non-GPU backend is the slow `cpu-reference` oracle (0.23-0.36 GB/s). Inputs are also capped at 4 GiB - 65 bytes because tape and token indices are u32.
- Typed deserialization of mid-size payloads. On a \~4 MiB corpus, serde_json straight into structs was about 2.5x faster end-to-end than metal-json's serde path (\~972 vs \~384 MiB/s, both borrowed), because the GPU always builds the whole tape before any type-driven work.
- Workloads where CPU cores can run in parallel (many documents, NDJSON). The baseline was a single simdjson DOM parse on one core (per the vendored simdjson.h, its threading applies only to parse_many lookahead). Multi-core CPU parsing was not compared.
- Production dependencies that need a maintainer. The code was written over about two days in June 2026 and v0.1.0 has 83 crates.io downloads. Human commits stopped on 2026-06-15; only Renovate bumps have landed since. Hosted CI does not run the GPU kernels because GitHub's paravirtual Metal compiler crashes, so GPU tests run only on the author's hardware.

## How it is fast

Stage 1 ports simdjson's bitmap tricks to Metal: backslash-run escape detection and a prefix-XOR in-string mask. Each GPU thread handles one 64-byte word using `uint2` bitmaps, because 64-bit operations are emulated on Apple's 32-bit ALUs, and state crosses chunk boundaries through reduce-&gt;spine-&gt;apply scans rather than decoupled look-back. Brackets are matched without a stack: a stable LSD counting sort of the structural characters by nesting depth puts each open/close pair next to each other, which also yields separator context and child counts. Apple GPUs have no fp64, so numbers use an integer-only Eisel-Lemire port; rare hard roundings and strings over 16 KiB are sent to CPU fixup lists. Unified memory shares both the input (`MTLBuffer bytesNoCopy`) and the output tape with the CPU without copies, and a buffer pool makes steady-state parses free of large allocations.

## Compared with alternatives

Pick it over simdjson only for single documents above roughly 5-8 MiB on an Apple Silicon Mac, when you want a full simdjson-style tape from Rust; below that, simdjson is faster and portable. Rust simd-json likewise beat it at 0.6-1.6 MiB (except number-heavy canada) but trailed about 3.5x at 512 MiB. For huge single records on multi-core CPUs, Pison (reported 3.1-5.4x over simdjson with 4-8 threads) and the query-oriented JSONSki are the portable alternatives, but neither was benchmarked against metal-json.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | objc2, objc2-foundation, objc2-metal, block2, dispatch2, memmap2, thiserror; optional serde. The default build also needs the Xcode Metal toolchain (`xcrun metal`) unless the `runtime-shaders` feature is enabled. |
| **Minimum toolchain** | Rust 1.95 (edition 2024; the repo pins 1.96.0). The default ahead-of-time shader build needs the Xcode Metal toolchain; `--features runtime-shaders` compiles MSL at runtime instead. Minimum macOS version is not documented. |
| **Platforms** | macOS on Apple Silicon only (Metal GPU with unified memory); benchmarked only on an M5 Max |
| **Thread safety** | `Parser` is not Send/Sync (its GPU state is shared through `Rc`, and its docs call the Send/Sync story unfinished), so use one `Parser` per thread. `Document` is Send + Sync, and its buffers return to a Mutex-guarded pool on drop. Concurrent parsing from several parsers is neither documented nor benchmarked. |
| **Drop-in for the baseline** | no |

## Gotchas

- `Value::get` and `Value::at` scan the container's direct children linearly (nested containers are skipped in O(1)), so indexing a big array in a loop is quadratic; iterate with `elements()`/`entries()` instead. `len()` is O(1) except for containers with 16,777,215 or more children, where the saturated count forces a walk.
- Duplicate keys stay on the tape and resolve three different ways: `Value::get` returns the first, serde into a map keeps the last, and serde into a struct fails with a 'duplicate field' error. Integers beyond u64 are stored as f64 (simdjson parity), so i128/u128 targets reject them, unlike serde_json.
- The buffer pool grows to the high-water mark and never shrinks: after one huge parse, that memory stays held until the `Parser` and all its `Document`s are dropped. `parse` and `parse_file` copy the input once. Only `parse_aligned` (caller-held `AlignedInput`) and the `unsafe parse_file_mmap` are zero-copy, and the mmap path can SIGBUS if the file is truncated mid-parse.
- The tape mirrors simdjson's layout except for string-buffer offsets, which are allocated by raw (escaped) length and leave zero-filled gaps, so code that walks simdjson's dense string buffer will not work unchanged. For distributed binaries, prefer `--features runtime-shaders`: the default build panics in build.rs when `xcrun metal` is missing. GPU wall times jitter up to 4x from power-state ramping, so benchmark with warm-up and medians.

## Known shortcomings

- Apple Silicon GPU (Metal) only; the win is on twitter-shaped data (canada is 1.42x). The simdjson baseline was built by the Rust cc crate's default compiler (unnamed) at -O3 -mcpu=native. First commit 2026-06; 18 stars.
- One CPU core against the whole GPU: simdjson ran a single-document DOM parse, and multi-core CPU parsing was never compared. GPU kernels are never tested in CI (hosted CI disables the GPU), only on the author's M5 Max. Effectively dormant: human commits only 2026-06-11 to 06-15, since then dependency bots. Built in about two days with AI co-authoring. Parser is not thread-safe to share.

## Caveats and trade-offs

Single machine and single vendor (one Apple M5 Max; the library runs only on Apple Silicon Metal). All rows of 1 MiB and above are expansions of the twitter template. canada and citm_catalog were measured only at their 1.6-2.1 MiB canonical sizes, so the 100-512 MiB wins cover twitter-shaped data only. The crossover (\~4.3 MiB) depends on document shape and machine: canada already wins at 2.1 MiB, while citm_catalog still favors simdjson at 1.6 MiB. The timed work is a full DOM parse to tape plus a shallow stats walk on both sides. simdjson On-Demand was deliberately not compared. The C++ compiler version for the simdjson build is not stated. The project is young and small: first commit 2026-06-11, the benchmark report dated 2026-06-12, 54 commits, 18 stars. The README says 'MIT OR Apache-2.0', but the LICENSE file and Cargo.toml say MIT only.

GPU dispatch/sync overhead makes it far slower than simdjson on small documents; Apple Silicon/Metal + unified-memory specific, not portable to other GPUs or discrete-GPU systems; adds a GPU dependency and complexity a pure-CPU parser doesn't need.

## Maintenance

Published as crate 0.1.0 (MIT; the README's 'MIT OR Apache-2.0' contradicts LICENSE and Cargo.toml); since 2026-06-15 only Renovate dependency bumps have landed (latest 2026-09-21) and a v0.1.1 release PR sits unmerged, so treat it as a finished, heavily tested experiment rather than an actively developed library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The page and docs/bench-report.md compare metal-json directly with vendored C++ simdjson v4.6.4 (DOM tape API). The code is public (bench/benches/compare.rs, bench/src/lib.rs, bench/cpp/shim.cpp, bench/build.rs, driven by `cargo run -p xtask -- bench-report`), and the report gives the CPU (Apple M5 Max), rustc 1.95.0, the Metal toolchain version and the baseline flags (-O3, C++17, NDEBUG, -mcpu=native). But the C++ compiler that built the simdjson baseline is never named or versioned (only 'cc -O3', meaning the Rust cc crate's system default). By the same rule as simdxml (wave 4) and the Go toolchain retier, that is C, one fact short of A.
- **Verifier notes:** Every number in the record matches the page and bench-report.md exactly (0.12x at 0.6 MiB, 1.34x at 8 MiB, 2.06x-2.71x at 100-512 MiB, \~4.3 MiB crossover, M5 Max/128 GiB/macOS 26.5.1, simdjson v4.6.4 -O3 -mcpu=native). The record's caveats had two errors: 'stage-1/tape build only' is wrong, since both sides do a full DOM parse to tape plus a stats walk, and 'first commits this month' is wrong, since the first commit is 2026-06-11. The downgrade rests only on the unnamed C++ compiler for the baseline. If the orchestrator accepts the cc crate's system default (Apple clang, version unknown) as enough, this could stay A. Metadata checks out: MIT, 18 stars, not a fork, last commit 2026-09-21 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Brooooooklyn/metal-json>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/docs/parsing-json-on-an-apple-gpu.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/README.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/docs/bench-report.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/bench/build.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/rust-toolchain.toml>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/Cargo.toml>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/Brooooooklyn/metal-json>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/README.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/docs/parsing-json-on-an-apple-gpu.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/docs/bench-report.md>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/Cargo.toml>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/rust-toolchain.toml>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/LICENSE>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/build.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/lib.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/parser.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/document.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/value.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/pool.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/input.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/serde.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/src/metal/context.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/bench/build.rs>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/bench/cpp/shim.cpp>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/bench/cpp/vendor/VERSION>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/bench/cpp/vendor/simdjson.h>
  - <https://github.com/Brooooooklyn/metal-json/blob/main/.github/workflows/ci.yml>
  - <https://github.com/Brooooooklyn/metal-json/issues?q=is%3Aissue>
  - <https://github.com/Brooooooklyn/metal-json/pulls?q=is%3Apr>
  - <https://github.com/Brooooooklyn/metal-json/pull/7>
  - <https://github.com/Brooooooklyn/metal-json/commits/main>
  - <https://crates.io/api/v1/crates/metal-json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/brooooooklyn/metal-json`) · [data/wave4/enrich/raw/github_com_brooooooklyn_metal_json.json](../../../data/wave4/enrich/raw/github_com_brooooooklyn_metal_json.json) (enrichment confidence 0.85)

</details>
