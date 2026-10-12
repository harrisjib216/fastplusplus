# bzip2z (Zig bzip2 with SA-IS block sorting)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Clean-room Zig bzip2 with SA-IS block sorting; compresses 1.7-1.8x faster than bzip2 1.0.8 on a synthetic periodic input, decompresses slower.

| | |
|---|---|
| **Beats** | system bzip2 1.0.8 (C); pbzip2 1.1.13 reported as a third column |
| **Claimed result** | README, mixed pattern, 3 iterations, 1 MB: single thread compress 18.64 vs 10.43 MB/s (1.79x), decompress 67.14 vs 69.38 MB/s (0.97x); threads=auto (16) compress 27.18 vs 10.33 MB/s (2.63x), decompress 0.99x. Across the README's 1-128 MB rows, single-thread compression is 1.72-1.79x faster but decompression is 0.76-0.82x of system bzip2 at 8 MB and above; with 16 threads compression reaches 15.10x at 128 MB (162.74 vs 10.77 MB/s) against single-threaded bzip2, against 115.61 MB/s for pbzip2 (1.41x over pbzip2, derived from page data), and pbzip2 decompresses up to 9.58x faster than bzip2 while bzip2z does not parallelise default single-stream decompression. |
| **Workload** | Compression and decompression throughput of a 1.0 MB mixed-pattern buffer with the bundled bench-bzip2 tool, 3 iterations, single thread and 16 resolved threads. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max, Darwin 25.3.0 arm64, threads=auto resolved to 16, run 2026-01-15 |
| **Compiler and flags** | bzip2z: Zig 0.15.2, -Doptimize=ReleaseFast; system bzip2 1.0.8 and pbzip2 1.1.13 from a Nix dev shell (build flags not stated; bzip2 1.0.8's own Makefile defaults to -O2). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: SA-IS linear-time suffix array construction for the Burrows-Wheeler transform in place of bzip2's original block-sorting logic, plus optional concurrent block compression. |
| **Adoption** | 1 star (70 commits) |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/pmarreck/bzip2z) · [benchmark](https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/README.md) |

## Verdict

First-party runs on an Apple M4 Max (Zig 0.15.2 ReleaseFast against nixpkgs bzip2 1.0.8 and pbzip2 1.1.13, 2026-01-15) on a synthetic 1-128 MB mostly periodic input: single-thread compression 1.72-1.79x faster than bzip2 (18.64 vs 10.43 MB/s at 1 MB), decompression 0.97x at 1 MB and 0.76-0.82x at 8 MB and above; with 16 threads compression reaches 162.74 MB/s at 128 MB, 15.10x single-threaded bzip2 and 1.41x pbzip2 (derived from page data). The baselines were timed as subprocesses with file I/O.

## Use it when

- Zig projects that want a bzip2 encoder and decoder without linking libbz2, under the MIT licence.
- Compressing large, repetitive or machine-generated data (logs, periodic binary records) where bzip2's block sort hits its slow fallback path.
- Multi-core hosts that must emit a single standard bzip2 stream but want parallel block compression (threads &gt; 1).
- Decoders that need to say where corruption is: decompressStream reports stream, block, phase, bit offset and stored versus computed CRC.

## Skip it when

- Decompression-heavy workloads: the README's own rows show it at 0.76-0.82x of system bzip2 from 8 MB up, and pbzip2 multi-stream decode is far faster.
- When byte-identical output to reference bzip2 matters (reproducible archives, checksum-pinned artefacts): sizes differ by under 0.2% and the encoder is not the reference one.
- Memory-tight encoders: the SA-IS on a doubled block allocates on the order of 15-20 MB of scratch per 900 kB block in flight (derived from the allocations in bwtEncode and buildSuffixArraySAIS), times the worker count; the README's 'Peak memory' column is a formula, not a measurement.
- If you need a drop-in libbz2 C API (BZ2_bzCompress and friends): its C ABI is its own bzip2z_\* interface.
- Projects pinned to an older Zig: the current source uses the Zig 0.16 std.Io API and the flake pins Zig 0.16.0, although build.zig.zon still says minimum 0.15.2.

## How it is fast

The Burrows-Wheeler step builds a suffix array with SA-IS (induced sorting, linear time, after Yuta Mori's sais via sile/sais) over the block concatenated with itself, then keeps positions below n to get the rotation order. This replaces bzip2's mainSort/fallbackSort, which degrades on highly repetitive blocks, so the gain is largest on periodic data. Compression can also run blocks on a worker pool with a bounded queue and reassemble them in order into one stream; decompression of a normal single-stream file stays sequential.

## Compared with alternatives

Pick bzip2z over libbzip2-rs when you work in Zig or C and want faster single-stream compression on repetitive data or parallel block compression; pick libbzip2-rs when you need a libbz2-compatible API, byte-identical output or faster decompression.

## Integration

| | |
|---|---|
| **Form** | Zig module plus static lib (bzip2z, bzip2z_ffi) with C header; CLI binaries |
| **Dependencies** | none for the library; the CLI build pulls pmarreck/progrez (progress bar); the dev shell and benchmark use system bzip2 and pbzip2 from nixpkgs |
| **Minimum toolchain** | Zig 0.16.0 for the current source (flake.nix pins 0.16.0; build.zig.zon declares 0.15.2, which the std.Io code no longer matches) |
| **Platforms** | CI builds macOS aarch64, Linux x86_64 and aarch64, Windows x86_64 and aarch64; benchmarks only on Apple M4 Max |
| **Thread safety** | Not documented for shared state; each call takes its own allocator and spawns its own worker threads when threads &gt; 1 |
| **Drop-in for the baseline** | partial — the CLI accepts bzip2 flags and the format is interoperable, but the library API is not libbz2's and outputs are not byte-identical |

## Gotchas

- Harness flaw in bench/bench_bzip2.zig: bzip2z is timed as in-process library calls on an in-memory buffer, while system bzip2 and pbzip2 are timed as subprocesses including spawn, reading the temp input file and writing the output file, which flatters bzip2z most at small sizes (its 0.97x decompress parity at 1 MB likely hides a real deficit). The pbzip2 decompress command omits the -p thread flag, so pbzip2 decompresses with all cores even in the 'threads = 1' rows, which is why those rows show 2.55-9.56x; and because the benchmark never sets multi_stream, bzip2z's own parallel decode path is never measured.
- The 'mixed' benchmark input is 75% periodic (a-z cycle, XYXY, byte ramp) plus 25% random, the kind of block that pushes bzip2 1.0.8 into its slow fallback sort and favours linear-time SA-IS; the bench supports text, binary, repetitive and random patterns but the README reports only mixed, so the 1.7-1.8x compression gain on ordinary text is unmeasured. Each figure is the mean of 3 iterations with no warm-up, against bzip2 of unknown build flags.
- The 'Peak memory (Zig)' column is computed as input + compressed + decompressed + 2 MB, not measured, and is reported identically for 1 and 16 threads.
- The numbers date from 2026-01-15 on Zig 0.15.2; the benchmark source has since been ported to Zig 0.16 and the decoder changed (bit-reader refill 2026-10-11, structural checks and a randomized-block derandomize offset fix 2026-10-10), so the table predates the current code; the decoder fixes concern robustness on crafted or legacy input, not the measured round trips.

## Known shortcomings

- Zig timed in-process while bzip2 is timed as a subprocess; the 'mixed' input is 75% periodic (bzip2's worst case); the win is algorithmic (SA-IS); decompression 0.76-0.82x at 8-128 MB; the 16-thread compress figure (up to 15.10x) is against single-thread bzip2 and only 1.41x vs pbzip2; numbers predate the current code.
- Harness flaws in bench/bench_bzip2.zig: the pbzip2 decompress call omits -p, so the 'threads = 1' pbzip2 rows decode on all cores (2.55-9.56x); the 'peak memory' column is a formula (input plus compressed plus decompressed plus 2 MB), identical for 1 and 16 threads, while the real SA-IS scratch is about 15-20 MB per 900 kB block (derived from code); multi_stream is never set, so its parallel decode is never measured; in-process library calls are timed against subprocesses on a synthetic 75%-periodic input. Numbers predate the Zig 0.16 port and the October decoder changes (76 commits, last 2026-10-12).

## Caveats and trade-offs

Harness asymmetry: bench/bench_bzip2.zig times bzip2z as in-memory library calls but times system bzip2 and pbzip2 as subprocesses (process spawn, reading the temp input file and writing the .bz2 or output file), which favours bzip2z; even so its decompression is parity at 1 MB and 18-24% slower at 8-128 MB. The 'mixed' input is synthetic and 75% periodic (a-z cycle, XYXY, byte ramp, then random), a pattern that is bzip2's block-sort worst case and favours linear-time SA-IS. Three iterations of one pattern. Outputs are valid bzip2 but not byte-identical (sizes differ by under 0.2%); only bzip2z's round trip is checked. The threads rows add parallel block compression that stock bzip2 lacks; pbzip2 is the fair parallel comparison (bzip2z 1.41x at 128 MB compress, much slower to decompress). Numbers were recorded 2026-01-15 on Zig 0.15.2, while the current bench source uses the Zig 0.16 std.Io API and the code has changed since (70 commits, last 2026-10-10), so the table predates the current code. bzip2 likely built at -O2 against ReleaseFast. First-party, 1 star. [retier] bench/bench_bzip2.zig's pbzip2 decompress call omits -p, so the 'threads = 1' pbzip2 rows decode on all cores (2.55-9.56x); the 'peak memory' column is a formula (input plus compressed plus decompressed plus 2 MB), identical for 1 and 16 threads, while the real SA-IS scratch is about 15-20 MB per 900 kB block; multi_stream is never set, so its parallel decode is never measured. Numbers predate the Zig 0.16 port and the October decoder changes.

Library with C FFI plus a bzip2-compatible CLI; optional multi-stream (pbzip2-style) mode; clean-room rewrite so conformance is the main risk.

## Maintenance

Actively developed (76 commits, last 2026-10-12, heavy differential and fuzz testing against reference bzip2), MIT-licensed and copyable, 1 star, no releases; the published benchmark predates the current code and measures only one synthetic pattern with an asymmetric harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from the repo's own bench/bench_bzip2.zig with Zig 0.15.2 ReleaseFast and an Apple M4 Max stated, but the system bzip2 1.0.8 build flags are not stated and the harness is asymmetric (in-process Zig calls against a spawned bzip2 subprocess with file I/O), so not A.
- **Verifier notes:** README numbers match the record's 1 MB rows; the larger rows show decompression 18-24% slower than C bzip2 and the 16-thread compression gain measured against single-threaded bzip2. Keep at C; shortcomings: subprocess against in-process timing, synthetic periodic input that is bzip2's worst case, algorithmic (SA-IS) rather than language win, slower decompression, numbers predate the current code, unknown bzip2 build flags.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/README.md>
  - <https://github.com/pmarreck/bzip2z>
  - <https://github.com/pmarreck/bzip2z/tree/yolo/bench>
  - <https://github.com/pmarreck/bzip2z/commits/yolo>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/yolo/bench/bench_bzip2.zig>
- **Sources the enricher read:**
  - <https://github.com/pmarreck/bzip2z>
  - <https://github.com/pmarreck/bzip2z/commits/yolo>
  - <https://github.com/pmarreck/bzip2z/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/README.md>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/build.zig>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/test>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/CODE_MINIMAP.md>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/NEXT_STEPS.md>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/ZIG_0.15_TO_0.16_MIGRATION.md>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/bench/bench_bzip2.zig>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/src/bzip2.zig>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/src/core.zig>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/src/concurrency.zig>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/c/include/bzip2z.h>
  - <https://raw.githubusercontent.com/pmarreck/bzip2z/HEAD/docs/mktp-research/bzip2.md>
  - <https://crates.io/api/v1/crates/banzai>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/pmarreck/bzip2z`) · [data/wave14/enrich/raw/github_com_pmarreck_bzip2z.json](../../../data/wave14/enrich/raw/github_com_pmarreck_bzip2z.json) (enrichment confidence 0.65)

</details>
