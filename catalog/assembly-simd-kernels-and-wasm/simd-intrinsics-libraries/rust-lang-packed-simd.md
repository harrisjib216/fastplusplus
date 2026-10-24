# packed_simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🔴 abandoned

> Archived, nightly-only Rust SIMD vector crate that preceded std::simd; with rayon it roughly matches ISPC on ISPC's examples.

| | |
|---|---|
| **Beats** | ISPC (ispc and ispc_tasks builds of the stock ISPC example programs) |
| **Claimed result** | README summary, packed_simd+rayon vs ISPC: aobench [-1.02x, +1.53x]; stencil [+1.06x, +1.72x]; mandelbrot [-1.74x, +1.2x]; options_pricing black_scholes +1.0x, binomial_put +1.4x ('+' is speed-up, '-' slowdown). Per-example readmes, parallel Rust vs ISPC with tasks: aobench tiled_par 98 ms vs ispc_tasks 150 ms on the 28-core Xeon E5-2690 v4, 102 vs 153 ms on the 40-core Xeon Gold 6148, 578 vs 567 ms on the dual-core i5. Stencil: vector_par 444 vs ispc_tasks 470 ms on the i5. On the E5-2690 v4, vector_par 167 ms vs serial ispc 287 ms and ispc_tasks 395 ms; the readme's '1.72x faster than ispc_tasks' equals 287/167 (the serial ispc row), while against ispc_tasks it is 2.37x (derived from page data). On the Gold 6148, 148 vs serial ispc 185 ms (1.25x). Mandelbrot, parallel simd vs ispc (ISPC with tasks): 21.0 vs 25.7 ms on the i5, 25.1 vs 14.4 ms on the E5-2690 v4 (1.74x slower), 29.9 vs 30.3 ms on the Gold 6148. Options_pricing, i5 only: Black-Scholes par_simd 246 vs ispc+tasks 248 ms; binomial put par_simd 279 vs ispc+tasks 404 ms. Single-thread packed_simd vs serial ISPC: aobench tiled 1328 vs 1158 ms (i5), 640 vs 576 ms (E5) and 770 vs 491 ms (Gold), so ISPC wins on all three; stencil vector 630 vs 558 ms (i5), 276 vs 287 ms (E5), 278 vs 185 ms (Gold); Black-Scholes simd 367 vs 360 ms, binomial put simd 651 vs 805 ms (i5). Single-thread SIMD vs the crate's own scalar loop on the i5: aobench vector 4.0x (1458 vs 5884 ms), stencil vector 4.5x (630 vs 2842 ms). Mandelbrot's 4.1x (21.0 vs 86.6 ms) is the parallel simd algorithm on two cores, not single-thread. |
| **Workload** | Ports of the ISPC example programs (aobench 800x600, stencil, mandelbrot 800x800, options_pricing Black-Scholes and binomial put) written with packed_simd vectors plus rayon, timed against the same programs compiled with ISPC, on three x86 machines. |
| **Metric** | throughput |
| **Hardware** | Dual-core AVX1 Core i5 @ 1.8 GHz (exact model not given); 28-core Xeon E5-2690 v4 @ 2.60 GHz; 40-core Xeon Gold 6148 @ 2.40 GHz |
| **Compiler and flags** | rustc nightly (the rust-toolchain file says only 'nightly', with no pinned date). examples/\*/benchmark.sh builds with RUSTFLAGS='-C target-cpu=native' cargo build --release --no-default-features and times each algorithm with hyperfine. The aobench script builds and times both a 256bit-feature and a 128-bit build, and the readme does not say which one the table shows. ISPC is built through the ispc crate, and examples/aobench/build.rs targets the SSE2, SSE4, AVX1, AVX2 and AVX512KNL ISAs. The rustc and ispc versions and the ISPC optimization flags are not stated. |
| **Adoption** | 649 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/rust-lang/packed_simd) · [benchmark](https://github.com/rust-lang/packed_simd) |

## Verdict

The crate's own ports of ISPC's aobench, stencil, mandelbrot and options examples, built with -C target-cpu=native and timed per process with hyperfine on a dual-core AVX i5, a Xeon E5-2690 v4 and a Xeon Gold 6148 (undated, about 2018, with rustc and ISPC versions not stated), range from 1.74x slower to 1.72x faster than ISPC. The wins come from rayon-parallel Rust against ISPC task builds that run on ispc-rs's simple task runtime, while serial ISPC was faster than serial packed_simd on aobench on all three machines.

## Use it when

- Maintaining an existing code base that already depends on packed_simd or packed_simd_2 and is pinned to a nightly from before March 2024.
- As reference code when porting ISPC-style SPMD kernels to explicit Rust vectors plus rayon; the examples keep scalar and vector versions of each kernel side by side.
- Reproducing the SIMD-plus-rayon versus ISPC comparison on x86: each example has a benchmark.sh that builds with -C target-cpu=native and times every variant with hyperfine.

## Skip it when

- Any new code: the repository was archived on 2026-09-16, and a maintainer said in April 2024 that the crate is effectively deprecated in favour of std::simd.
- Current nightly toolchains: 0.3.9 enables #![feature(platform_intrinsics)], which rustc removed (issue #360, first reported on 1.78.0-nightly 2024-03-02); the only workaround reported is pinning a 1.77-era nightly.
- Stable Rust: the crate has always required nightly.
- Expecting single-threaded wins over ISPC: serial ISPC beat serial packed_simd on aobench on all three machines (1158 vs 1328 ms, 576 vs 640 ms, 491 vs 770 ms) and on stencil on two of three.
- Vector transcendental math: per the performance guide's notes, it falls back to scalarised libm calls unless the optional sleef-sys feature (x86_64 only) is enabled.

## How it is fast

Vectors are #[repr(simd)] types whose operations lower through compiler SIMD intrinsics to LLVM vector IR, so instruction selection follows the RUSTFLAGS target features (for example SSE2 PCMPEQD by default, AVX2 VPCMPEQQ with +avx2). A verify/ crate disassembles the generated code to check it stays efficient. In the ISPC comparisons, the multi-threaded wins come from hand-vectorised kernels (8-wide f32 in the default 256-bit aobench build) run under rayon's work-stealing scheduler; single-threaded, serial ISPC was faster on aobench on every machine.

## Compared with alternatives

Only when you maintain code already built on it with a pinned pre-2024 nightly. Otherwise use Rust portable SIMD (std::simd), its direct successor with a similar vector API, or ISPC itself when you want the best single-threaded SPMD code generation, since serial ISPC beat serial packed_simd on aobench.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, num-traits (libm); optional core_arch and, on x86_64, sleef-sys |
| **Minimum toolchain** | Rust nightly only, edition 2018; 0.3.9 no longer builds on nightlies from about March 2024 (1.78), so pin a 1.77-era nightly |
| **Platforms** | README matrix: builds and passes tests on x86_64 Linux/macOS/Android, aarch64 Linux, arm/armv7/thumbv7neon Linux and powerpc64le; builds but fails tests on i586/i686, powerpc, powerpc64, s390x and sparc64; iOS targets do not build |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Two crate names: packed_simd_2 (0.3.4 to 0.3.8, 2020 to 2022, about 2.8 million downloads) was the interim release line; packed_simd 0.3.9 (2023-07-30) is the final release.
- Horizontal operations are much slower than vertical ones; the crate docs recommend accumulating in vectors and reducing once at the end. Use mask element widths equal to the data width, except for 512-bit vectors on AVX-512, where 1-bit masks are faster.
- The headline wins over ISPC are against ispc_tasks, whose launch/sync runs on ispc-rs's own Rust task system: it spawns num_cpus threads on first launch, and a syncing thread that finds no chunk left sleeps 50 ms (seen in ispc-rs 1.0.11 and current source; the 2018 version was not checked). That plausibly explains why stencil ispc_tasks is slower than serial ispc on both Xeons (395 vs 287 ms, 401 vs 185 ms).
- hyperfine times the whole process, so process start-up, thread-pool creation and, for aobench, writing the 800x600 PNG are inside the timed region; aobench's main.rs also prints an internal timer around the kernel alone, and the readmes do not say which number the tables show.

## Known shortcomings

- Claim overstated: serial ISPC beats serial packed_simd on aobench on all 3 machines; the Mandelbrot 4.1x is parallel, not single-thread; the stencil 1.72x is against serial ISPC (2.37x against ispc_tasks), and the ISPC tasks baseline looks crippled on the Xeons (stencil tasks 395 vs serial 287 ms, 401 vs 185 ms). The binomial put speedup column is inconsistent with its times. rustc and ispc versions unpinned; archived 2026-09-16.
- Enricher: the ispc_tasks baseline runs on ispc-rs's own task system (50 ms sleeps in the syncing thread), which makes it slower than serial ISPC on stencil, so the headline wins over ISPC are against a weak task runtime; hyperfine times process start and PNG output; 0.3.9 does not build on nightlies since 2024-03-02 (issue #360); archived 2026-09-16.

## Caveats and trade-offs

First-party numbers from the project's own examples. The README ranges mix wins and losses: aobench and mandelbrot each have a slowdown, and mandelbrot on the 28-core Xeon is 1.74x slower than ISPC. The headline wins come from rayon-parallel Rust variants against ISPC task builds. Single-threaded, packed_simd mostly matches or trails serial ISPC: aobench serial ISPC is faster on all three machines (up to 770 vs 491 ms on the Gold 6148), and stencil serial ISPC is faster on the i5 and the Gold 6148. So the wins measure rayon's thread scaling more than SIMD code generation. The ISPC task baseline looks crippled on the many-core Xeons: stencil ispc_tasks is slower than serial ispc (395 vs 287 ms on the E5-2690 v4, 401 vs 185 ms on the Gold 6148). The stencil readme labels its E5-2690 v4 ratio of 1.72x as 'vs ispc_tasks', but the ratio matches the serial ispc row. In the binomial put table the speedup column does not match the times (ispc 805 ms is listed as 7.4x and par_simd 279 ms as 4.3x against the 2057 ms scalar run), so use the time column. Mandelbrot 'simd' is a parallel algorithm and mandelbrot 'ispc' uses ISPC tasks; on the Xeons both reach only about 2x over scalar for 14-30 ms runs. Hyperfine times the whole process, so process start and thread-pool setup are inside the timed region. The results are undated (the examples date from about 2018), the rustc nightly and ISPC versions are not stated, and the i5 model is not given, so the runs are not fully reproducible. The baseline is ISPC, not std::arch or platform intrinsics, and no direct intrinsics comparison was found. The repository was archived (read-only) on 2026-09-16. The last code change was 2023-07-30 (0.3.9), the 2026-09-15 commit is the deprecation notice, and the crate is superseded by rust-lang/portable-simd (std::simd). The book's claim about this crate was not consulted. [retier] Enricher: the ispc_tasks baseline runs on ispc-rs's own Rust task system (it spawns num_cpus threads on first launch and the syncing thread sleeps 50 ms when no chunk is left; checked in ispc-rs 1.0.11 and HEAD, the 2018 version was not fetchable), a plausible cause of stencil ispc_tasks being slower than serial ispc on both Xeons (395 vs 287 ms, 401 vs 185 ms), so the headline wins over ISPC are against a weak task runtime. hyperfine timing includes process start, thread-pool creation and aobench's PNG write; aobench also prints an internal kernel-only timer and the readmes do not say which number the tables use. 0.3.9 no longer builds on current nightly (platform_intrinsics feature removed, issue #360); the only reported workaround is pinning a 1.77-era nightly. Interim crate name packed_simd_2 (0.3.4-0.3.8).

Nightly-only Rust. Archived by the owner on 2026-09-16 and superseded by rust-lang/portable-simd (std::simd), so new code should use that. Vector API very close to std::simd. Optional sleef-sys dependency for transcendental functions on x86_64. The README says SPMD is not the intended use and that combining it with rayon 'poorly emulates' ISPC's model; matching ISPC needs care (performance guide).

## Maintenance

Abandoned: archived on 2026-09-16, final release 0.3.9 on 2023-07-30, and no longer building on nightlies since March 2024, so treat it as MIT/Apache-2.0 reference code and migrate to std::simd.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers in the README and the per-example readmes. The benchmark code (examples/\*/benchmark.sh, hyperfine, RUSTFLAGS='-C target-cpu=native') is public, and two of the three CPU models are named, but the rustc nightly and ISPC versions are not stated, so the evidence falls short of A. The tier stays C; the claim and caveats were overstated and are corrected.
- **Verifier notes:** All quoted numbers appear in the example readmes. The verdict is downgrade because the claim and caveats overstated the result, not because the tier changed. The record said the serial ISPC rows are slower, but serial ISPC beats serial packed_simd on aobench on every machine. It also called the mandelbrot 4.1x single-thread, but that algorithm is parallel. Metadata checked on github.com: 649 stars, Apache-2.0 and MIT, archived 2026-09-16, last commit 2026-09-15; maintenance_status 'abandoned' is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-129 (wave 13 book seed pass, 2026-10-24); enrichment (wave 13 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/rust-lang/packed_simd>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/stencil/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/mandelbrot/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/options_pricing/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/benchmark.sh>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/stencil/benchmark.sh>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/build.rs>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/rust-toolchain>
  - <https://github.com/rust-lang/packed_simd/commits/master>
- **Sources the enricher read:**
  - <https://github.com/rust-lang/packed_simd>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/benchmark.sh>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/build.rs>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/Cargo.toml>
  - <https://github.com/rust-lang/packed_simd/tree/master/examples/aobench/src>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/src/ispc_.rs>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/src/main.rs>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/aobench/volta/ao.ispc>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/stencil/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/stencil/benchmark.sh>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/mandelbrot/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/mandelbrot/benchmark.sh>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/examples/options_pricing/readme.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/perf-guide/src/SUMMARY.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/perf-guide/src/float-math/svml.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/perf-guide/src/float-math/fp.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/perf-guide/src/target-feature/runtime.md>
  - <https://raw.githubusercontent.com/rust-lang/packed_simd/HEAD/perf-guide/src/target-feature/inlining.md>
  - <https://github.com/rust-lang/packed_simd/issues?q=is%3Aissue%20nightly%20compile>
  - <https://github.com/rust-lang/packed_simd/issues/360>
  - <https://crates.io/api/v1/crates/packed_simd>
  - <https://crates.io/api/v1/crates/packed_simd_2>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/HEAD/compile/src/lib.rs>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/HEAD/runtime/src/lib.rs>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/HEAD/runtime/src/exec.rs>
  - <https://raw.githubusercontent.com/Twinklebear/ispc-rs/1.0.11/runtime/src/exec.rs>
  - <https://github.com/Twinklebear/ispc-rs/tags>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rust-lang/packed_simd`) · [data/wave13/enrich/raw/github_com_rust_lang_packed_simd.json](../../../data/wave13/enrich/raw/github_com_rust_lang_packed_simd.json) (enrichment confidence 0.8)

</details>
