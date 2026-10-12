# llama2.zig (cgbur)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Single-file Zig port of karpathy/llama2.c; single-threaded fp32 inference about 1.1-1.2x faster than gcc -Ofast llama2.c on stories15M.

| | |
|---|---|
| **Beats** | karpathy/llama2.c built with 'make runfast -march=native' (gcc -Ofast), single-threaded; also plain 'make run -march=native' (-O3) |
| **Claimed result** | README, single-threaded, stories15M, 256 tokens, AMD Ryzen 9 5900X: argmax llama2.zig 660 tok/s vs llama2.c 'make runfast -march=native' (gcc -Ofast) 548 (1.20x) and vs 'make run -march=native' 122; top-p 0.9 at temperature 1.0: 579 vs 463 (1.25x). The pairs are cross-session: in the last same-run measurement (2023-08-09, commit 19988eb) llama2.zig was 606 vs 548 (about 1.11x, derived from page data); the 660 came eight days later after page-aligning the weights, and the 463 was re-measured on 2023-08-17 while the 579 dates from 2023-08-15 or earlier. |
| **Workload** | stories15M.bin inference, 256 tokens, single-threaded, argmax and top-p 0.9 sampling, on AMD Ryzen 9 5900X. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X 12-core |
| **Compiler and flags** | llama2.zig: Zig 0.11.0-dev.4315+f5239677e, zig build -Doptimize=ReleaseFast, native target, @setFloatMode(Optimized) in src/main.zig; llama2.c: gcc (version unstated) -Ofast -march=native ('make runfast' with -march=native added, Makefile quoted in the README), plus an -O3 -march=native row. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: SIMD matrix multiplication with Zig @Vector (about 115 to 430 tok/s from that change alone), comptime-generated fused matmul, vector-aligned allocation and SIMD versions of other core functions. |
| **Adoption** | 224 stars |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/cgbur/llama2.zig) · [benchmark](https://raw.githubusercontent.com/cgbur/llama2.zig/main/README.md) |

## Verdict

On one AMD Ryzen 9 5900X core with stories15M and 256 tokens, the README reports llama2.zig (Zig 0.11-dev, ReleaseFast, native) at 660 tok/s argmax and 579 tok/s top-p 0.9, against karpathy/llama2.c built with gcc -Ofast -march=native at 548 and 463 (1.20x and 1.25x, derived from page data) and against gcc -O3 -march=native at 122; the last time both argmax rows were measured together (2023-08-09) the figures were 606 vs 548, about 1.11x.

## Use it when

- You want a readable single-file reference transformer forward pass in Zig, or a Zig project needs llama2-architecture inference without C dependencies.
- Single-threaded fp32 inference of small llama2.c checkpoints (stories15M/42M/110M class) on one core, where the README shows 660 vs 548 tok/s against gcc -Ofast llama2.c on a Ryzen 9 5900X.
- As a worked example of explicit @Vector SIMD, comptime kernel fusion and accumulator splitting that you can port back to C with intrinsics.
- Teaching or experimentation where llama2.c's checkpoint and tokenizer files should be reused unchanged.

## Skip it when

- Anything multi-core: there is no threading (README Todo calls it 'not going well'), and llama2.c's own OpenMP build reached 1564 tok/s on the same CPU, 2.4x the single-threaded figure.
- Real LLM serving or large models: fp32 only, no quantisation (llama2.c has runq.c for int8), no batching or prompt prefill, and the whole checkpoint is read into RAM rather than mmapped, so a 7B fp32 model needs about 27 GB resident before the first token.
- Very small models (\~100K parameters): the README Todo says llama2.c is faster there, blaming expf and GCC's floating-point reordering.
- Toolchains other than Zig 0.16: build.zig.zon sets minimum_zig_version 0.16.0 and the std.Io API it uses changed across 0.11-0.16; issue #12 ('mem.page_size has been removed', April 2025) shows how often it breaks.
- When bitwise-reproducible numerics matter: the file runs in optimized float mode, so results differ from strict IEEE builds.

## How it is fast

Every matrix-vector product goes through one comptime-generated matmul_fused that uses Zig @Vector at the target's suggested width (8 f32 on AVX2) and shares each load of x across the fused q/k/v and w1/w3 rows; the current code also keeps 8 (single) or 4 (fused) independent vector accumulators per row to break the FMA dependency chain. RMSNorm, the attention value sum and the elementwise multiply are SIMD too, scratch buffers are vector-aligned, and the weights are read into a page-aligned buffer instead of llama2.c's mmap, where the weights start 28 bytes into the file and every row load is misaligned; that change alone took the README figure from 612 to 656 tok/s (commit 23c0711, 'Page align weights file for \~8% boost'). The whole file is compiled with @setFloatMode(.optimized), the Zig equivalent of the -Ofast fast-math that llama2.c needs to vectorise its reductions.

## Compared with alternatives

Pick it over llama2.mojo when you want a Zig (not Mojo) single-file port and single-threaded speed, since llama2.mojo's wins are measured against llama2.c's OpenMP build with threads; pick fastGPT (Fortran, GPT-2 via BLAS) for GPT-2 models, and neither of the three for production serving.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Zig standard library only); needs llama2.c-format checkpoint and tokenizer.bin |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version; CI pins 0.16.0); the README numbers were taken with Zig 0.11.0-dev.4315+f5239677e |
| **Platforms** | any Zig target in principle (vector width from std.simd.suggestVectorLength, fallback 4); default build targets the native CPU, so binaries are not portable to older CPUs without -Dtarget; only measured on x86-64 (Zen 3, AVX2) |
| **Thread safety** | not applicable: single-threaded CLI with global PRNG and verbose state |
| **Drop-in for the baseline** | partial: same checkpoint and tokenizer files and similar -t/-p/-n/-i/-s flags as llama2.c run.c, but it is a separate program, has no OpenMP build and adds -v and -z flags |

## Gotchas

- The README table is a cross-session composite: the llama2.c runfast row (548) was last re-run on 2023-08-09 (commit 19988eb), when llama2.zig measured 606 (about 1.11x, derived from page data); afterwards only the llama2.zig row was updated (612 on Aug 15, 656 on Aug 16 after page-aligning the weights, 660 on Aug 17), so the headline 660 vs 548 (1.20x) compares runs eight days apart. The top-p row likewise pairs a llama2.zig 579 from Aug 15 or earlier with a llama2.c 463 re-measured on Aug 17 after llama2.c merged its top-p speedup; the OpenMP 1564 and llama2.rs rows date from before Aug 7.
- Part of the margin is data layout rather than code generation: llama2.c mmaps the file and reads weights at a 28-byte offset, so its vector loads are misaligned, while llama2.zig copies them into a page-aligned buffer; aligning the weights alone moved llama2.zig from 612 to 656 tok/s.
- Tokens/s is computed after the first token as (pos-1)/elapsed, like llama2.c, and generation stops early at BOS; before commit 78c7b94 ('Fix mistake in benchmarking', 2023-08-07) the divisor was seq_len-1 even when the story ended early, which inflated the figures (662 to 577 and 341 to 295 after the fix). With top-p sampling and time-seeded RNGs on both sides, each run generates a different-length story, so single runs vary.
- The README help text says top-p defaults to 1.0, but the code (and its own --help) defaults to 0.9, so a bare run does nucleus sampling; prompt tokens are fed one at a time and counted in tok/s, and the README benchmark was not re-run after the 2026-08-02 hot-path rewrite (independent accumulators, register attention sums, Zig 0.16 port).

## Known shortcomings

- 1.20-1.25x over -Ofast llama2.c comes from hand-written SIMD plus a fused matmul, not Zig itself; one CPU (Ryzen 9 5900X), single 2023 runs, gcc version and commits not pinned, the hot path changed 2026-08-02 without a rerun.
- Cross-session composite: the llama2.c runfast row (548) was last re-run on 2023-08-09 (commit 19988eb), when llama2.zig measured 606 (about 1.11x); afterwards only the llama2.zig row was updated (612, 656 after page-aligning the weights, 660 on 2023-08-17), so the headline 660 vs 548 (1.20x) compares runs eight days apart, and the top-p row pairs a llama2.zig 579 from 2023-08-15 or earlier with a llama2.c 463 re-measured on 2023-08-17. The 2026-08-02 commits changed the hot path (independent matmul accumulators, attention sums in registers, vectorised RMSNorm, Zig 0.16 port) without re-running the benchmark; gcc version unstated, neither commit pinned.

## Caveats and trade-offs

First-party 2023 numbers on one CPU, single runs, gcc version unstated and neither the llama2.c nor the llama2.zig commit pinned (the figures predate the 2024 Zig 0.12/0.14 ports). The Aug 2, 2026 commits were not only CI: they changed the hot path (independent matmul accumulators, attention sums in registers, vectorised RMSNorm, Zig 0.16 port) without re-running the README benchmark, and the current matmul uses 8 or 4 independent vector accumulators, a different accumulator structure from llama2.c's loop; the measured 2023 code (9b225a2) used one vector accumulator per output row. Both sides of the -Ofast row are fast-math builds for the native ISA; the 5x gap to the -O3 row is not a fair comparison because without -ffast-math gcc cannot vectorise the dot-product reduction. The 20-25% win comes from explicit @Vector SIMD, comptime-fused q/k/v and w1/w3 matmuls sharing loads of x, and SIMD-aligned allocation, all doable in C with intrinsics. The README Todo says llama2.c is faster on \~100K-parameter models (expf cost; GCC much better than clang there), and llama2.c's OpenMP build is 2.4x faster than single-threaded llama2.zig. [retier] First-party 2023 numbers on one CPU, single runs, gcc version unstated and neither the llama2.c nor the llama2.zig commit pinned. The table is a cross-session composite: the llama2.c runfast row (548) was last re-run on 2023-08-09 (commit 19988eb), when llama2.zig measured 606 (about 1.11x); afterwards only the llama2.zig row was updated (612 on Aug 15, 656 on Aug 16, 660 on Aug 17), and the top-p row pairs a llama2.zig 579 from Aug 15 or earlier with a llama2.c 463 re-measured on Aug 17. The 2026-08-02 commits changed the hot path (independent matmul accumulators, attention sums in registers, vectorised RMSNorm, Zig 0.16 port) without re-running the benchmark, and the figures predate the 2024 Zig 0.12/0.14 ports. Multi-threaded llama2.c (make runomp) is not compared.

Single-threaded only, small models; Zig toolchain version moved from 0.11 dev to 0.16 (CI pinned in 2026) so the table predates current Zig.

## Maintenance

Active again since a 2026-08-02 port to Zig 0.16 with CI (zig build test, zig fmt), MIT-licensed and a single file that is easy to vendor, but the 2023 benchmark table was not re-run on the current code or with a current llama2.c.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded C to A: the README Performance section names both programs (llama2.zig src/main.zig, which prints its own tok/s, and llama2.c run.c), the exact run commands, the C build (gcc -Ofast -march=native via the quoted Makefile, plus an -O3 -march=native row), the Zig build (zig build -Doptimize=ReleaseFast, Zig 0.11.0-dev.4315+f5239677e) and the CPU (AMD Ryzen 9 5900X); only the gcc version is missing, which the pdqsort precedent accepts as A. Both programs start the timer after the first token and divide pos-1 tokens by elapsed time, so the tok/s figures are computed the same way.
- **Retiered** A to C: Enricher: the README's 660 vs 548 tok/s pairs a llama2.zig run of 2023-08-17 with a llama2.c run of 2023-08-09 (code changed in between); the only same-run measurement is 606 vs 548 (1.11x). Cross-session composite with neither commit pinned and gcc unstated: A to C (LC precedent).
- **Verifier notes:** Upgraded to A on the pdqsort precedent (gcc named without a version, flags, CPU and code public); cap at C instead if pinned commits are required, since the 2023 commits measured are not named and the hot path changed on 2026-08-02 without a rerun. Shortcomings: one CPU and single 2023 runs, win from hand SIMD and matmul fusion rather than the language, slower than llama2.c on tiny models per the README Todo, no multithreading (llama2.c OpenMP 2.4x faster).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-04 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/README.md>
  - <https://github.com/cgbur/llama2.zig>
  - <https://github.com/cgbur/llama2.zig/commits/main>
  - <https://github.com/cgbur/llama2.zig/tree/main/benchmarks>
  - <https://github.com/cgbur/llama2.zig/tree/main/src>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/build.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/src/main.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/9b225a2/src/main.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/9b225a2/README.md>
  - <https://raw.githubusercontent.com/karpathy/llama2.c/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/cgbur/llama2.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/src/main.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/build.zig>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/build.zig.zon>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/9b225a2/src/main.zig>
  - <https://github.com/cgbur/llama2.zig/commits/main/README.md>
  - <https://github.com/cgbur/llama2.zig/commit/78c7b94>
  - <https://github.com/cgbur/llama2.zig/commit/35f65de>
  - <https://github.com/cgbur/llama2.zig/commit/23c0711>
  - <https://github.com/cgbur/llama2.zig/issues?q=is%3Aissue>
  - <https://github.com/cgbur/llama2.zig/issues/1>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/78c7b94/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/19988eb/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/8b819e5/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/f52ed86/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/ea19ffa/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/993dce9/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/121c63e/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/6d408e4/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/23c0711/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/8e23277/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/e46473c/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/a78d395/README.md>
  - <https://raw.githubusercontent.com/cgbur/llama2.zig/35f65de/README.md>
  - <https://raw.githubusercontent.com/karpathy/llama2.c/master/run.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/cgbur/llama2.zig`) · [data/wave14/enrich/raw/github_com_cgbur_llama2_zig.json](../../../data/wave14/enrich/raw/github_com_cgbur_llama2_zig.json) (enrichment confidence 0.8)

</details>
