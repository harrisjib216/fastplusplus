# ZLB (Zig Language Benchmark) Mandelbrot SIMD row

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig @Vector(8, f64) Mandelbrot kernel 1.7x faster than 4-lane AVX intrinsics in C, because its block is twice as wide.

| | |
|---|---|
| **Beats** | C Mandelbrot with 4-lane SIMD intrinsics, gcc 16.1.1 and clang 22.1.8 at -O3 -march=native -ffp-contract=off (also zig cc) |
| **Claimed result** | Mandelbrot 4000x4000, max_iter 1000, hyperfine mean of 20 runs (results/mandel_\*.json): zig_simd_fast 1.922 s and zig_simd_safe 2.249 s vs c_simd_clang 3.261 s, c_simd_gcc 3.302 s, c_simd_zigcc 3.380 s and rust_simd 3.321 s, so the 8-lane Zig kernel is 1.70x to 1.76x faster than the 4-lane C kernels (ReleaseSafe 1.45x to 1.50x) (derived from page data); README ratios vs scalar gcc: 0.16x, 0.18x, 0.26x, 0.27x, 0.27x, 0.27x. Same-algorithm scalar rows are parity: zig_std_fast 12.374 s vs c_std_gcc 12.386 s (1.00x) and c_std_clang 12.631 s (1.02x). Other rows in the same suite (README ratios vs c_std_gcc): sieve zig_static_bitset_fast 0.63x vs c_std_gcc 1.00x but zig_std_fast 1.06x; btree zig_compact_fast 0.19x vs c_arena_gcc 0.21x; log_proc zig_std_fast 0.83x vs c_std_gcc 1.00x; atomics parity (0.97x to 1.00x). |
| **Workload** | Mandelbrot set calculation, hyperfine mean of 20 runs after 1 warmup, wall-time ratio against the scalar gcc build (1.00x). |
| **Metric** | throughput |
| **Hardware** | Linux 7.1.4-arch; CPU model not stated |
| **Compiler and flags** | Zig 0.16.0 zig build-exe -O ReleaseFast (and ReleaseSafe) with no -target, so the host CPU is targeted (README: all binaries built for native); the SIMD kernel sets @setFloatMode(.strict). C SIMD: gcc 16.1.1 and clang 22.1.8 at -O3 -march=native -ffp-contract=off, zig cc -O3 -ffp-contract=off -march=native. C scalar: gcc/clang -O3 only (no -march=native), zig cc -O3 -ffp-contract=off. Rust 1.97.1: rust_simd rustc -C opt-level=3 -C target-cpu=native (no LTO); rust_std -C opt-level=3 -C lto=yes (Makefile). Measured with hyperfine --warmup 1 --min-runs 20 --output=null (tools/runner.sh); outputs are not checked against an expected checksum during timing. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Why it wins** | Source: Zig's @Vector with 8-lane f64 fills the CPU's execution units better than the 4-lane intrinsics used in C and Rust, and gives LLVM clearer intent. |
| **Adoption** | 0 stars (1 commit) |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/tsukumoakito/zlb) · [benchmark](https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/README.md) |

## Verdict

Hyperfine means of 20 runs after 1 warmup (n=4000, max_iter 1000, Linux 7.1.4-arch, CPU not named): Zig 0.16.0 ReleaseFast 8-lane kernel 1.922 s (sd 0.098) vs the 4-lane AVX intrinsics C kernel at 3.302 s with gcc 16.1.1 and 3.261 s with clang 22.1.8 (both -O3 -march=native -ffp-contract=off), 3.380 s with zig cc and Rust 1.97.1 at 3.321 s, i.e. 1.70x to 1.76x (derived from page data); the scalar same-algorithm rows tie (Zig 12.374 s, gcc 12.386 s, clang 12.631 s), so the gain is block width, not language.

## Use it when

- As a compact, MIT-licensed template for a masked escape-time loop with Zig's portable @Vector type: the kernel uses no target intrinsics, unlike the C and Rust baselines that include immintrin.h or std::arch::x86_64 and need AVX.
- When choosing a block width for latency-bound SIMD loops: the suite shows an 8-lane f64 block (16 doubles of state) beating a 4-lane block by 1.7x on the same per-lane math, a lesson that applies equally to C with two __m256d chains or GCC vector extensions.
- When you need bit-identical results across compilers: strict float mode in Zig and -ffp-contract=off in C keep FMA contraction out of both sides, so checksums should match the scalar versions.
- As a starting point for Zig 0.16 benchmark harnesses: Makefile builds every variant, tools/runner.sh drives hyperfine and tools/aggregate.py writes the README tables and SVG plots.

## Skip it when

- As evidence that Zig beats C or C++: the C kernel is 4 lanes wide and the Zig kernel 8, the scalar same-algorithm rows tie, and an 8-lane C kernel has not been measured.
- Multi-core or GPU rendering: the kernel is single-threaded and writes no pixels.
- Older Zig toolchains: main takes std.process.Init and writes through std.Io, the API of the Zig 0.16.0 release the README pins; it is not written for earlier releases.
- Regions where neighbouring pixels escape at very different counts: every 8-pixel block runs until its slowest lane finishes, so wasted lanes grow with the block width (not measured in the repo).
- As a maintained dependency: one commit (2026-08-20), 0 stars, no issues or releases.

## How it is fast

Masked escape-time SIMD: each block iterates z = z^2 + c on 8 lanes, ANDs the active mask with |z|^2 &lt;= 4, adds the mask to the counters, and leaves the block when @reduce(.Or) of the mask is zero. The C and Rust SIMD rows run the identical per-lane algorithm on one 4-lane __m256d block with 64-bit counters, so the Zig version holds twice as many independent iteration chains per loop; on AVX2 hardware the 8-wide vector is split into two 256-bit chains that overlap the multiply-add latency (or one 512-bit chain on AVX-512, and the CPU is not named). The wider block even does extra work (each block runs until the slowest of 8 pixels escapes, not 4) and still wins, which points to latency-bound 4-lane C code rather than better Zig code generation; the same-algorithm scalar rows are at parity (12.374 s vs 12.386 s).

## Compared with alternatives

No sibling in this category covers Mandelbrot; like the LangArena Zig std.sort.pdq row it is a language-suite comparison rather than a library, so for production Zig code with measured wins over C libraries look at zroar (vs CRoaring) or zipir (vs zlib-ng), and use this only as a SIMD-loop example.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Zig standard library only); the harness needs hyperfine and matplotlib |
| **Minimum toolchain** | Zig 0.16.0 (README; uses std.process.Init and std.Io) |
| **Platforms** | Zig kernel is target-independent @Vector code built for the host CPU; measured only on Linux 7.1.4-arch, CPU not named; the C and Rust SIMD baselines are x86-64 AVX only |
| **Thread safety** | single-threaded program with no shared state |
| **Drop-in for the baseline** | no |

## Gotchas

- Unequal kernels behind the headline: zig_simd uses @Vector(8, f64) with u32 counters while c_simd and rust_simd use one 4-lane __m256d block with 64-bit counters; the README attributes the 1.7x to @Vector giving LLVM 'clearer intent', but the per-lane math is identical and the gap matches doubling the independent dependency chains.
- Correctness is never checked during timing: runner.sh runs hyperfine with --output=null, and make test-all only prints each binary's checksum at n=100 for eyeballing, with no expected value or comparison.
- runner.sh skips re-measuring any row whose binary sha256 matches the stored results/&lt;name&gt;.hash, so rows in results/ can come from different sessions; with a single commit there is no way to tell, and the hyperfine JSON carries no timestamps or CPU model (the README only says AVX2/AVX-512 generically).
- ReleaseSafe costs about 17% on the SIMD kernel (2.249 s vs 1.922 s, derived from page data) though the README calls the cost negligible for Mandel; it is negligible only for the scalar kernel (12.393 s vs 12.374 s). The README also says all binaries are built for native, but the scalar gcc/clang and rust_std builds have no -march=native or target-cpu flag.

## Known shortcomings

- Unequal kernels: the Zig kernel is 8-lane while the C and Rust kernels are 4-lane AVX2, so the 1.70-1.76x (1.922 vs 3.261-3.380 s) is a wider kernel, not the language; the same-work scalar rows are parity (12.374 vs 12.386 s); CPU model unstated; 0 stars, 1 commit.
- The Zig kernel is @Vector(8, f64) with u32 counters while the C and Rust kernels use one 4-lane __m256d block; per-lane math is identical, so the gap is block width, and the scalar rows tie (12.374 vs 12.386 s). runner.sh skips re-measuring any row whose binary sha256 matches the stored results/\*.hash, so rows can come from different sessions and one commit makes that unknowable; timed runs use --output=null and make test-all only prints checksums at n=100 with nothing comparing them. ReleaseSafe costs 17% on the SIMD kernel (2.249 vs 1.922 s) although the README calls it negligible, and the README's 'all builds native' does not hold for the scalar gcc, clang and rust_std builds. Hyperfine JSON numbers confirmed.

## Caveats and trade-offs

Not like-for-like and not a language win. The Zig SIMD kernel (src/mandel/zig_simd/main_simd.zig) iterates an 8-lane @Vector(8, f64) block with u32 counters, which on AVX2 hardware compiles to two interleaved 4-wide chains (or one AVX-512 op if the unnamed CPU has it), while the C and Rust SIMD kernels (c_simd/main_simd.c, rust_simd/main_simd.rs) run a single 4-lane __m256d chain with 64-bit counters; the 1.7x gap is the extra ILP or width of the wider block, which the same C written with 8 lanes (two __m256d chains, AVX-512 intrinsics or GCC vector extensions) would also get. On the same algorithm with the same structure the scalar rows are parity (zig_std_fast 12.374 s vs c_std_gcc 12.386 s) even though the Zig scalar build targets the native CPU and the C scalar builds do not use -march=native. The sieve and btree wins come from different data layouts (a bitset instead of a byte array, 32-bit indices instead of 64-bit pointers), and the log_proc win compares Zig's std.fmt.bufPrint and parseUnsigned against glibc sprintf, strstr and atoi, so they are library and layout effects. Single commit (2026-08-20), 0 stars, CPU model not stated, no correctness check in the timed runs. [retier] Enricher: runner.sh skips re-measuring any row whose binary sha256 matches the stored results/\*.hash, so rows can come from different sessions and one commit makes that unknowable; timed runs use --output=null and make test-all only prints checksums at n=100 with nothing comparing them. The scalar rows tie (12.374 vs 12.386 s). ReleaseSafe costs 17% on the SIMD kernel (2.249 vs 1.922 s) although the README calls it negligible, and 'all builds native' does not hold for the scalar gcc, clang and rust_std builds.

Informal suite of five small benchmarks (mandel, sieve, btree, log_proc, atomics) in Zig, C, Rust, Go, Python and Bash.

## Maintenance

Single commit ('init: establish project baseline', 2026-08-20), 0 stars, MIT with REUSE metadata; small enough to copy, but it is a showcase suite tied to Zig 0.16.0 rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** Public code (src/mandel/{c_simd/main_simd.c,zig_simd/main_simd.zig,rust_simd/main_simd.rs,c_std/main.c,zig_std/main.zig}, Makefile, tools/runner.sh, tools/aggregate.py) with compilers and flags stated and raw hyperfine JSON in results/, but no CPU model anywhere, and it is a single-author, 0-star, one-commit suite written to showcase Zig, so first-party C, not A. Tier stays C; the claim is downgraded because the like-for-like rows show no language win.
- **Verifier notes:** Numbers match the README and the raw hyperfine JSON (zig_simd_fast 1.922 s, c_simd_gcc 3.302 s, c_std_gcc 12.386 s). Shortcomings to record: unequal SIMD kernels (8-lane Zig vs 4-lane C/Rust), scalar like-for-like rows at parity, sieve/btree/log_proc wins come from data layout or library differences, CPU model not stated, single-commit 0-star suite, timed runs not checked for correct output; same_algorithm corrected to false, same_opt_level true for the SIMD rows (all three at native with strict FP), rust_simd has no LTO.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/README.md>
  - <https://github.com/tsukumoakito/zlb>
  - <https://github.com/tsukumoakito/zlb/commits/master>
  - <https://github.com/tsukumoakito/zlb/tree/master/tools>
  - <https://github.com/tsukumoakito/zlb/tree/master/results>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/tools/runner.sh>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/tools/aggregate.py>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/c_std/main.c>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/c_simd/main_simd.c>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/zig_std/main.zig>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/zig_simd/main_simd.zig>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/rust_simd/main_simd.rs>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/log-proc/c_std/main.c>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/log-proc/zig_std/main.zig>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_simd_fast.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_simd_safe.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_gcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_clang.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_zigcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_rust_simd.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_std_gcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_std_clang.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_std_fast.json>
- **Sources the enricher read:**
  - <https://github.com/tsukumoakito/zlb>
  - <https://github.com/tsukumoakito/zlb/commits/master>
  - <https://github.com/tsukumoakito/zlb/issues>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/README.md>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/.envrc>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/tools/runner.sh>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/tools/aggregate.py>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/c_std/main.c>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/c_simd/main_simd.c>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/zig_std/main.zig>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/zig_simd/main_simd.zig>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/rust_simd/main_simd.rs>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/src/mandel/rust_std/main.rs>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_simd_fast.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_simd_safe.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_gcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_clang.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_zigcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_rust_simd.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_std_gcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_std_clang.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_std_zigcc.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_std_fast.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_std_safe.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_rust_std.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_go_std.json>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_zig_simd_fast.hash>
  - <https://raw.githubusercontent.com/tsukumoakito/zlb/HEAD/results/mandel_c_simd_gcc.hash>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/tsukumoakito/zlb#mandel-simd`) · [data/wave14/enrich/raw/lang_zig_tsukumoakito_zlb_mandel_simd.json](../../../data/wave14/enrich/raw/lang_zig_tsukumoakito_zlb_mandel_simd.json) (enrichment confidence 0.85)

</details>
