# libbzip2-rs (libbz2-rs-sys, Rust port of libbzip2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `bzip2-1.0.6` · 🟢 active

> Memory-safe Rust port of libbzip2 exposing the same C API; about 11% fewer compression cycles than C libbzip2 on x86-64.

| | |
|---|---|
| **Beats** | libbzip2 (C, original bzip2 library) |
| **Claimed result** | Latest run in trifectatechfoundation/libbzip2-rs-bench (commit ac73367, 2026-10-06), mean of 20 repetitions per command. Linux x86-64, AMD Ryzen 9 9900X, CPU cycles of Rust vs C: compression of silesia-small.tar at levels 1-9 -10.1% to -12.3% (level 1 -12.28%, level 9 -10.12%), sample3.ref level 1 -5.49%, decompression of six bzip2 test files -3.4% to -7.4%. macOS arm64, Apple M2, user time: compression -3.3% to -4.2%, sample3.ref -5.6%, but decompression is slower in Rust on five of six files (+0.1% to +9.5%), a pattern stable across the 2025-08 to 2026-10 runs (derived from page data). The blog figures in the original record (-14.87% sample3.ref level 1, -14.30% and -9.66% silesia-small levels 1 and 9, 'significant speedups across the board' for decompression) come only from a blocked blog post and do not match any run in the public data (best runs: -12.95% small, -12.51% level 1). |
| **Workload** | CPU cycles for compression at levels 1-9 on silesia-small.tar and a small sample file, and decompression of bzip2 test files, comparing the C and Rust builds in one harness (bzip2_benchmarks.json). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9900X 12-core (self-hosted runner amd-bench, Linux x86-64; cycles, instructions, task-clock) and Apple M2 (runner mini-bench, macOS arm64; user time). |
| **Compiler and flags** | Workflow .github/workflows/bench.yml: Rust side cargo build --release -p test-libbz2-rs-sys --examples with RUSTFLAGS=-Cllvm-args=-enable-dfa-jump-thread (release profile defaults, opt-level 3, no LTO), rustc stable from rustup (version printed only in CI logs). C side: libbzip2 1.0.8 sources from bzip2-sys 0.1.13+1.0.8 (feature static) compiled by its build.rs through the cc crate with CC=clang at the release opt-level (-O3), -D_FILE_OFFSET_BITS=64 -DBZ_NO_STDIO; the extra LLVM DFA jump-threading pass is given to rustc only. Both libraries are linked into the same harness binaries and measured by trifectatechfoundation/benchmarker-action (perf counters, 20 repetitions). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 79 stars; libbz2-rs-sys has 42.7M crates.io downloads and is the default backend of the bzip2 crate since 0.6 |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/trifectatechfoundation/libbzip2-rs) · [benchmark](https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs-bench/main/metrics-linux-x86.json) |

## Verdict

In the project's own CI data (libbzip2-rs-bench, latest run at commit ac73367 on 2026-10-06, 20 repetitions per command), one harness binary calling libbz2-rs-sys versus libbzip2 1.0.8 (bzip2-sys, built with clang at -O3) used 10.1-12.3% fewer CPU cycles compressing the 15.7 MB silesia-small.tar at levels 1-9 and 3.4-7.4% fewer decompressing six bzip2 files on an AMD Ryzen 9 9900X. On an Apple M2 compression was 3.3-4.2% faster in user time but decompression was 0.1-9.5% slower on five of six files.

## Use it when

- Rust projects using the bzip2 crate: libbz2-rs-sys is already its default backend since 0.6.0, and it needs no C compiler when cross-compiling.
- Compression-heavy bzip2 work on x86-64: about 10-12% fewer CPU cycles at every level 1-9 on a 15.7 MB tar in the project's CI on a Ryzen 9 9900X.
- Replacing system libbz2 to get a memory-safe decoder for untrusted .bz2 input when speed parity, not a large speedup, is the goal.
- Reproducible archives that must match libbzip2 output byte for byte (tests assert identical output at level 9).
- Embedded or no_std targets: the cdylib builds without std using the c-allocator feature or caller-supplied bzalloc/bzfree.

## Skip it when

- Decompression-heavy work on Apple Silicon: on the Apple M2 runner the Rust decoder is slower than C on five of six files (+0.1% to +9.5% user time in the 2026-10-06 run), consistently since 2025.
- When you need a large bzip2 speedup: the gains are 3-12%; a parallel bzip2 or a different codec moves throughput far more, and the Zig bzip2z sibling claims 1.79x single-threaded compression.
- Builds pinned to libbz2-rs-sys 0.2.3 or 0.2.4: a blocksort logic error aborts compression with internal error 1002 on some inputs of about 600 KB or more (issue #137, fixed in 0.2.5 on 2026-05-16; the bad versions are not yanked on crates.io).
- Need for features beyond libbzip2 1.0.x (multithreading, bzip3): none are implemented; issue #139 asking for bzip3 is open.
- Projects that require an OSI-listed licence: it ships under the bzip2-1.0.6 licence (permissive, BSD-style, no patent grant).

## How it is fast

Same algorithm as libbzip2 (Burrows-Wheeler block sort with mainSort/fallbackSort and the workFactor budget, MTF/RLE, multi-table Huffman); the code began as a c2rust translation and was then rewritten into safe Rust (compress.rs, decompress.rs and blocksort.rs carry #![forbid(unsafe_code)]; unsafe is confined to the C-API layer in bzlib.rs). Visible implementation changes: the bit writer (LiveWriter) copies bs_buff, bs_live and num_z into locals and writes them back on Drop instead of updating EState fields through a pointer on every bsW call, and the decoder is a c2rust-style `'state_machine: loop { match current_block }` that the benchmark builds with LLVM's -enable-dfa-jump-thread pass. No SIMD or target-specific code. The Rust build executes 5-8% more instructions than C when compressing silesia-small.tar yet takes fewer cycles (derived from page data), so the gain is higher IPC, not less work; the project's own explanation is only that zlib-rs experience was applied (blog post not reachable, search snippet only).

## Compared with alternatives

Pick libbzip2-rs over bzip2z (Zig, SA-IS block sort, 1.79x faster single-threaded compression but 0.97x decompression and a new codebase) when you need the libbzip2 C API, byte-identical output and a widely deployed memory-safe drop-in (42.8M crates.io downloads); pick bzip2z when raw compression speed matters more than compatibility.

## Integration

| | |
|---|---|
| **Form** | crate (libbz2-rs-sys) or shared/static lib (libbz2-rs-sys-cdylib: libbz2_rs.so / libbz2_rs.a) |
| **Dependencies** | libc (optional; needed for the stdio and c-allocator features); none for a no_std build with a caller-supplied allocator |
| **Minimum toolchain** | Rust 1.82 (workspace MSRV) |
| **Platforms** | portable Rust with no SIMD or target-specific code; benchmarked on x86-64 Linux and aarch64 macOS |
| **Thread safety** | not documented; state lives per bz_stream as in libbzip2 and the Rust sources hold no mutable globals apart from an ASSERT_CODE atomic in no_std builds, so separate streams on separate threads should be safe |
| **Drop-in for the baseline** | partial: same BZ2_\* C API (capi version 1.0.9) and byte-identical output, but the cdylib is named libbz2_rs rather than libbz2, so C programs must relink or the library must be renamed/symlinked; BZ2_bzlibVersion reports 1.1.0-libbz2-rs-sys-0.2.5 |

## Gotchas

- Harness flag asymmetry: the CI builds the Rust side with RUSTFLAGS=-Cllvm-args=-enable-dfa-jump-thread while the C side (bzip2-sys build.rs via the cc crate, CC=clang, -O3) gets no such flag; the decoder is exactly the switch-in-a-loop state machine this pass targets, so part of the 3-7% x86 decompression gain may come from the pass rather than the port. Toolchains are unpinned (rustup stable, runner clang), and run-to-run drift exceeds within-run noise: within-run CV is 0.2-1.3%, but the version-bump-only commit c6b9b3d measured the x86 level-1 compression delta at -10.17% against -8.11% for its parent 7fe0c34, the level-1 delta ranged from -8.9% to -12.3% across 2026 runs, and the sample3.ref compression delta went -10.8%, -0.2%, -1.1%, +1.1%, -5.5% over the last five runs (2026-04-07 to 2026-10-06: a blocksort fix, a version bump and two clippy-fix commits).
- Three of the six decompression rows are tiny inputs (sample3.bz2 is 235 bytes, sample1.bz2 32 KB, sample2.bz2 74 KB; 0.5-4 ms per process), so whole-process cycles there are dominated by startup and stream initialisation; only zip64support.tar.bz2 and re2-exhaustive.txt.bz2 are large (about 2.2e9 and 1.8e9 cycles), showing -4.3% and -4.1% on x86 but +4.8% and +1.0% on the M2. On the M2, level-1 compression was 1.7-5.9% slower than C in every 2025 run and only turned 3-4% faster from the 2026-04-06 run onward.
- Internal asserts mirror libbzip2: with the std feature an internal error prints the report and calls std::process::exit(3), killing the host process; 0.2.3 and 0.2.4 hit this (error 1002) because a commit replaced the highest-set-bit loop for the quadrant shift in mainSort with count_ones().
- Rust executes more instructions than C (+5-8% compressing silesia-small.tar, +21-24% decompressing the three small files on x86; derived from page data), so the cycle win depends on the microarchitecture, which matches the weaker M2 results.

## Known shortcomings

- Public bench data in libbzip2-rs-bench (Ryzen 9 9900X, Apple M2): x86 compression 10-12% fewer cycles and decompression 3-7%, but on the M2 decompression is up to 9.5% slower; -enable-dfa-jump-thread is given to the Rust build only; the blog snippet numbers match no published run; the bzip2-1.0.6 licence is not OSI-approved, so usability is reference (wave 9 precedent).
- Flag asymmetry: -enable-dfa-jump-thread is given to the Rust build only, and the toolchains are unpinned. Run-to-run noise: the version-bump-only commit c6b9b3d shows level 1 at -10.17% against -8.11% for its parent; three of the six decompression files are tiny (sample3.bz2 is 235 bytes); on the large files x86 is -4.3%/-4.1% while M2 is +4.8%/+1.0%. Bug: 0.2.3 and 0.2.4 abort with internal error 1002 on some inputs of about 600 KB or more (issue #137, fixed in 0.2.5, old versions not yanked). Rust runs 5-8% more instructions when compressing; M2 compression is only faster than C from the 2026-04 runs on.

## Caveats and trade-offs

Gains are modest and platform-dependent: about 10-12% fewer cycles for compression and 3-7% for decompression on the Ryzen 9 9900X, but only 3-4% faster compression and up to 9.5% slower decompression on Apple M2. Flag asymmetry: the Rust build gets the LLVM -enable-dfa-jump-thread pass (useful for bzip2's switch-based decoder state machine) while the clang-built C does not, so part of the decompression gain may be the extra pass rather than the port. Whole-process measurement includes reading the input file, equally for both sides. Compiler versions are not in the public data. The port began as a c2rust translation of libbzip2, so the algorithm is the same and the gain comes from implementation changes. The blog numbers quoted earlier were snippet only and do not match the public data. License is the bzip2 and libbzip2 License v1.0.6 (SPDX bzip2-1.0.6), a permissive BSD-style licence that the SPDX list does not mark OSI-approved; usability set to reference for consistency with the wave 9 gitlab.com/bzip2/bzip2 record; no patent grant. [retier] Flag asymmetry: -enable-dfa-jump-thread is given to the Rust build only, and the toolchains are unpinned. The version-bump-only commit c6b9b3d shows level 1 at -10.17% against -8.11% for its parent; three of the six decompression files are tiny (sample3.bz2 is 235 bytes); on the large files x86 is -4.3%/-4.1% while M2 is +4.8%/+1.0%. 0.2.3 and 0.2.4 abort with internal error 1002 on some inputs of about 600 KB or more (issue #137, fixed in 0.2.5, old versions not yanked). Rust runs 5-8% more instructions when compressing.

Drop-in libbzip2 C API (cdylib) and Rust crate; memory-safe translation; project page says no further feature development is planned.

## Maintenance

Actively maintained (last commit 2026-10-06, v0.2.5 released 2026-05-16 with the error-1002 fix) and the default backend of the bzip2 crate; the bzip2-1.0.6 licence is permissive but not OSI-listed, and the benchmark has a Rust-only -enable-dfa-jump-thread flag, unpinned toolchains and tiny decompression inputs, so treat the decompression gain as unproven and the x86 compression gain of about 11% as the solid result.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C: the project's public benchmark data (trifectatechfoundation/libbzip2-rs-bench metrics-linux-x86.json and metrics-macos-arm64.json) records C-vs-Rust results per commit with the CPU model (AMD Ryzen 9 9900X; Apple M2), produced by public code (bzip2_benchmarks.json, test-libbz2-rs-sys/examples/compress.rs and decompress.rs, .github/workflows/bench.yml) with stated compilers and flags (CC=clang, cargo --release, RUSTFLAGS=-Cllvm-args=-enable-dfa-jump-thread; C built by bzip2-sys's build.rs via the cc crate at the release opt-level). Compiler versions appear only in CI logs, which I could not open.
- **Retiered** A to C: Enricher: the bench gives -enable-dfa-jump-thread to the Rust build only, with unpinned toolchains, and the run-to-run noise (a version-bump-only commit moves level 1 by 2 points) is of the order of the 10-12% margin; asymmetric-flags precedent: A to C.
- **Verifier notes:** Real, widely used port (79 stars; libbz2-rs-sys 42.7M crates.io downloads, default backend of the bzip2 crate since 0.6; last commit 2026-10-06). The public bench repo upgrades the evidence to A for the x86 compression win; record shortcomings: Apple M2 decompression slower than C, Rust-only -enable-dfa-jump-thread flag, compiler versions unstated, blog snippet numbers unverifiable, bzip2-1.0.6 licence not OSI-approved (usability reference).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/bzip2_benchmarks.json>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/examples/compress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/examples/decompress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/LICENSE>
  - <https://github.com/trifectatechfoundation/libbzip2-rs>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commits/main>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/tree/main/.github/workflows>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/tree/main/test-libbz2-rs-sys>
  - <https://github.com/trifectatechfoundation/libbzip2-rs-bench>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs-bench/main/metrics-linux-x86.json>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs-bench/main/metrics-macos-arm64.json>
  - <https://static.crates.io/crates/bzip2-sys/bzip2-sys-0.1.13+1.0.8.crate>
  - <https://crates.io/api/v1/crates/libbz2-rs-sys>
- **Sources the enricher read:**
  - <https://github.com/trifectatechfoundation/libbzip2-rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/bzip2_benchmarks.json>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/src/lib.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/src/compress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/src/decompress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/src/blocksort.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys/src/bzlib.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/src/lib.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/examples/compress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/test-libbz2-rs-sys/examples/decompress.rs>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys-cdylib/README.md>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/libbz2-rs-sys-cdylib/Cargo.toml>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/.gitmodules>
  - https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs/HEAD/silesia-small.tar (HEAD request, size only)
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs-bench/main/metrics-linux-x86.json>
  - <https://raw.githubusercontent.com/trifectatechfoundation/libbzip2-rs-bench/main/metrics-macos-arm64.json>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/issues?q=is%3Aissue>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/issues/137>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commits/main>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commits/main/.github/workflows/bench.yml>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commit/1948e55>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commit/7fe0c34>
  - <https://github.com/trifectatechfoundation/libbzip2-rs/commit/c6b9b3d>
  - <https://crates.io/api/v1/crates/libbz2-rs-sys>
  - <https://crates.io/api/v1/crates/bzip2>
  - https://trifectatech.org/blog/bzip2-crate-switches-from-c-to-rust/ (DNS failure; WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/trifectatechfoundation/libbzip2-rs`) · [data/wave14/enrich/raw/github_com_trifectatechfoundation_libbzip2_rs.json](../../../data/wave14/enrich/raw/github_com_trifectatechfoundation_libbzip2_rs.json) (enrichment confidence 0.8)

</details>
