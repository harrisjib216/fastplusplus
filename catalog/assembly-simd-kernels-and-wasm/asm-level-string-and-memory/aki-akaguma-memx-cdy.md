# memx-cdy (C ABI of the Rust memx crate: memchr, memmem, memcmp, memcpy, memset)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust (C ABI shared and static library, LD_PRELOAD capable)` · `MIT OR Apache-2.0` · 🟢 active

> C-ABI (LD_PRELOAD-able) build of the Rust memx crate; memmem 2.7-5.9x faster than glibc/musl, other mem\* mixed.

| | |
|---|---|
| **Beats** | glibc and musl libc memchr, memmem, memcmp, memcpy and memset (called from Rust through FFI as libc_\* rows), alongside Rust std and the memchr crate |
| **Claimed result** | memx-cdy README: 'Faster os libc and musl libc'. Derived from page data (memx docs tables, Intel i5-4570, rustc 1.69.0, Criterion time per pass, libc divided by memx): memmem gnu:en 2.173 vs 0.798 us (2.7x), gnu:ja 3.828 vs 1.230 us (3.1x), musl:en 3.948 vs 0.794 us (5.0x), musl:ja 7.010 vs 1.197 us (5.9x); memchr gnu 1.09x and 1.07x (4.849 vs 4.451, 5.764 vs 5.402 us), musl 2.0x and 1.9x (8.757 vs 4.426, 10.205 vs 5.322 us); memcmp musl:en 1.14x and musl:ja 3.8x (8.653 vs 2.293 us) but slower on glibc (gnu:en 1.584 vs 2.828 us, 0.56x; gnu:ja 1.582 vs 2.022 us, 0.78x); memset gnu:ja 1.14x and musl:ja 1.50x but slower on the short en case (gnu:en 2.003 vs 3.388 us, 0.59x; musl:en 2.139 vs 3.515 us, 0.61x). memcpy: memx is 3.1x faster than musl on en (20.289 vs 6.527 us) and 1.55x on ja, but 0.50x of glibc on en (3.483 vs 7.016 us) and 0.96x on ja; memx-cdy does not deliver the musl memcpy win, because its memcpy export is compiled out on musl targets and by the default 'no_memcpy' feature. |
| **Workload** | Criterion time per pass (200 samples, 100 ms warm-up, 1 s measurement; cache lines flushed before each function's run) over a fixed set of text lines, each pass making many calls, not time per single call: memmem searches the 48-byte needle 'just before we went into the very simple problem' in 21 alternating English lines (en, 10 matches) or a 39-byte Japanese needle in 21 Japanese lines (ja); memchr scans for 'r' (768 matches on en); memcpy copies a 15-byte (en) or 144-byte (ja) source into successive slices of the lines. Built for x86_64-unknown-linux-gnu and x86_64-unknown-linux-musl from memx xbench/benches/\*.rs; the libc_\* rows call the C library through Rust FFI. |
| **Metric** | latency |
| **Hardware** | Intel i5-4570 @ 3.2 GHz for the quoted figures (AVX2 build); Intel Q6600 @ 2.4 GHz and an armv7 1.5 GHz device are also tabulated |
| **Compiler and flags** | rustc 1.69.0 (84c898d65 2023-04-16); cargo bench profile opt-level = 3, codegen-units = 1, lto = true (memx Cargo.toml); glibc and musl versions not stated |
| **Adoption** | 4 stars (memx-cdy), 26 stars (memx), memx has about 472k crates.io downloads |
| **Last commit** | 2026-06-03 |
| **Links** | [repository](https://github.com/aki-akaguma/memx-cdy) · [benchmark](https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memmem.md) |

## Verdict

On an Intel i5-4570 with rustc 1.69.0 (opt-level 3, LTO, one codegen unit), Criterion time per pass over 21 text lines (about 16 KB English or 32 KB Japanese) shows memx's memmem at 0.80 us versus glibc's 2.17 us (2.7x) and musl's 3.95 us (5.0x) on English, and 3.1x and 5.9x on Japanese; memchr is 1.07-1.09x faster than glibc and about 2x faster than musl, while memcmp, bcmp, memset and memcpy are slower than glibc on the short English case. These are memx crate numbers with glibc and musl called through Rust FFI; libc versions are not stated.

## Use it when

- x86-64 Linux C or C++ programs whose hot path is memmem over text (log scanning, grep-like filters, protocol parsing of ASCII) where you can test LD_PRELOAD or relink
- musl-linked x86-64 binaries (e.g. Alpine containers): the tables show memchr about 2.0x, memcmp up to 3.8x and memmem 5.0-5.9x faster than musl's simple C routines
- Quick experiments to see whether mem\* routines matter for an existing binary without recompiling it
- Rust code wanting the same routines: use the memx crate directly (it is what was benchmarked) rather than the C exports

## Skip it when

- Blanket LD_PRELOAD on glibc systems: in the same tables memx's memcmp is 0.56x of glibc (en), bcmp about 0.8x and memset 0.59x on the short case, and memchr is within 10%; only memmem is a clear win, and there is no switch to export memmem alone
- memmem over untrusted or repetitive input: the naive candidate-and-verify search is O(haystack x needle) in the worst case, whereas glibc and musl use linear-time two-way search; the frequency weights are tuned for English text and source code, not binary data
- Non-x86 targets: SIMD paths exist only for x86 and x86-64 (aarch64 only gained a prefetch helper); other architectures run the generic SWAR fallback
- Statically linked musl builds that need memcpy (duplicate memcpy symbol, noted in src/lib.rs), or code that needs memmove, strlen, strchr and other string.h functions, which are not provided
- Environments without a Rust toolchain: there are no prebuilt binaries beyond what cargo deb produces locally

## How it is fast

memx picks SSE2 or AVX2 kernels at run time (cpufeatures, cached in a static AtomicPtr after the first call), with unrolled 16/32-byte compare loops, alignment prologues and software prefetch; non-x86 targets use generic SWAR code. memmem is a 'stochastic naive' search (the author's naive_opt idea): it looks up the first and last needle bytes in a hard-coded English/source-code frequency table, runs a SIMD memchr for the rarer one and does a full SIMD compare at each candidate. On text with a rare boundary byte this is mostly one vectorised memchr pass, avoiding the per-call setup of glibc's and musl's two-way/hashed memmem.

## Compared with alternatives

Pick it over AOCL-LibMem when you want a portable x86-64 memmem/memchr injection on any vendor's CPU and especially on musl (AOCL-LibMem targets glibc on AMD Zen and publishes no numbers), and over sliceslice when the caller is C or C++ and cannot build a reusable searcher object; for memcpy or memset wins on glibc pick something else, since memx loses there.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Rust toolchain to build; crates libc 0.2 and memx 0.2 (memx pulls cpufeatures 0.2 on x86, x86-64 and aarch64). Also usable as a staticlib or as a Rust crate (call memx_cdy::memx_init() to force linking). |
| **Minimum toolchain** | Rust 1.65 (rust-version in both Cargo.toml files) |
| **Platforms** | x86 and x86-64 for the SSE2/AVX2 paths (run-time dispatch); other targets use generic code; the LD_PRELOAD workflow is Linux/ELF-specific (CI builds on Ubuntu, macOS and Windows) |
| **Thread safety** | Stateless functions; the dispatch pointer is a static AtomicPtr set on first call with a benign race, so concurrent calls are safe; not otherwise documented |
| **Drop-in for the baseline** | partial — same C signatures and symbol names, so LD_PRELOAD replaces libc's memchr, memrchr, memcmp, bcmp, memmem and memset as a set; memcpy is not exported in the default build, and calls inside glibc itself or compiler-inlined constant-size mem\* calls are not affected |

## Gotchas

- Benchmark scope: the memx docs tables (rustc 1.69.0, i5-4570, 2023) time memx's Rust functions, not memx-cdy's C exports or the LD_PRELOAD path, and predate memx 0.2.1 (2026-05-23), which rewrote every core and x86 loop; the en memmem needle 'just before we went into the very simple problem' starts with 'j', which has weight 0 (rarest) in memx's _ASCII_STOCHAS table and occurs only twice in the 16 KB of test lines, so that row measures little more than one AVX2 memchr pass, the best case for this algorithm.
- Unsound boundary: the exports are safe extern "C" fns that call slice::from_raw_parts on caller pointers, so memchr(NULL, c, 0) or memcmp(NULL, NULL, 0), which C programs pass and glibc tolerates (and C23 defines for n = 0), is undefined behaviour in Rust, and Rust code can trigger it without unsafe; issue #2 ('Unsound usages of unsafe implementation about c_void', 2026-06-08) is open with no reply.
- Self-interposition risk: the crate exports libc names without #![no_builtins], and 0.1.13 (2023-10-09) had to fix a stack overflow on a 3-byte memcmp by bypassing memx for n &lt; 4, consistent with the exported memcmp ending up calling itself; any path that the compiler lowers back to memset/memcmp/bcmp inside the preloaded library can recurse the same way.
- memcmp and bcmp return only -1, 0 or 1 (valid C, but different from glibc's byte difference), and memx's memcpy, which is 3.1x faster than musl in the tables, can never be reached on musl through memx-cdy because the export is compiled out there.

## Known shortcomings

- The memcpy export is compiled out on musl and by default (no_memcpy feature), so the musl memcpy 3.1x row is not delivered; times are per pass over 21 lines, not per call; the bench times the memx Rust crate, not the C ABI; the clear glibc win is memmem only (2.7-3.1x) and memcmp/memset are slower than glibc in the short case.
- Enricher: the en memmem row is favourable (the needle starts with 'j', weight 0 in memx's _ASCII_STOCHAS table, occurring twice in 16 KB, so the row is roughly one AVX2 memchr pass); memmem is naive candidate-and-verify with O(n\*m) worst case vs glibc/musl two-way; the tables (rustc 1.69) predate the memx 0.2.1 rewrite of 2026-05-23; exports are safe extern "C" functions using from_raw_parts (NULL with n=0 is UB), issue #2 on unsound unsafe is open without reply, no #![no_builtins], 0.1.13 fixed a memcmp self-recursion stack overflow; LD_PRELOAD on glibc loses on memcmp, bcmp and memset. Lead: aki-akaguma/naive_opt.

## Caveats and trade-offs

First-party benchmarks on a 2013-era desktop CPU with rustc 1.69 (2023); memx is now 0.2.2 (2026) and the tables were not regenerated with a date, so they may not reflect current code. glibc and musl versions are not stated. The benchmark times the memx Rust functions directly, not memx-cdy's C ABI exports or the LD_PRELOAD path; the wrappers add slice construction and memcmp switches to a byte loop for n &lt; 4. memx-cdy's memcpy is exported only on non-musl targets and only when the default 'no_memcpy' feature is disabled (src/lib.rs notes a duplicate-symbol link error on musl), so the memcpy musl rows do not apply to it, and on glibc memx's memcpy is slower on short copies. Timings are per pass over 21 text lines with many short calls each, so per-call overhead (FFI and PLT for libc_\*) weighs heavily; musl's memchr, memmem and memcpy are simple C, so the musl gaps largely reflect musl's weakness. memx's own harness calls memchr::memmem::find per call (building a searcher each time), which is why the memchr crate's memmem row is about 4x slower than glibc; treat the memmem comparison with care. One Criterion table per function, no confidence intervals reported. Benchmark code and docs live in the memx repository, not memx-cdy.

Rust implementation with SSE2/AVX2 paths selected at run time (cpufeatures) plus a basic fallback; usable from C or C++ by linking libmemx_cdy.a/.so or LD_PRELOAD, but it needs a Rust toolchain to build and the Rust side must call memx_init(). Substantially slower than glibc for memcmp, memcpy and memset on the same CPU, so only the search functions (memmem, memchr on musl) are wins.

## Maintenance

The wrapper changes rarely (0.2.0 on 2025-09-24, last commit 2026-06-03 a changelog reformat; 4 stars, about 41k crates.io downloads) while memx itself is active (0.2.2 on 2026-05-27, about 472k downloads); MIT OR Apache-2.0, so it is easy to adopt, but the published benchmark tables have not been regenerated since memx's 2026 rewrite.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** The memx docs tables (docs/README.memmem.md and siblings) compare memx against libc_\* rows for glibc and musl, the harness is public (memx xbench/benches/bench-memmem.rs, bench-memcpy.rs, create_data.rs, driven by makefile.build), the compiler is stated (rustc 1.69.0), the bench profile flags are in memx Cargo.toml (opt-level 3, codegen-units 1, lto) and the CPU is named (i5-4570), so tier A stands; the downgrade is for the overstated claim, not the tier.
- **Verifier notes:** Tier A kept; downgraded for overstatement: the memcpy musl 3.1x figure cannot be obtained through memx-cdy (memcpy export compiled out on musl and by the default no_memcpy feature), timings are per pass not per call, and memset/memcmp are slower than glibc on the short case. Real wins are memmem (2.7-5.9x over glibc and musl) and memchr/memcmp over musl; versus glibc only memmem is clearly faster. memx itself was already folded into this entry as a duplicate.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-48 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memmem.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memchr.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memcmp.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memcpy.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memset.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/README.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/makefile.build>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/bench-memmem.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/bench-memcpy.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/create_data.rs>
  - <https://github.com/aki-akaguma/memx-cdy>
  - <https://github.com/aki-akaguma/memx-cdy/commits>
  - <https://github.com/aki-akaguma/memx>
  - <https://github.com/aki-akaguma/memx/tree/main/xbench>
  - <https://github.com/aki-akaguma/memx/tree/main/xbench/benches>
  - <https://crates.io/api/v1/crates/memx>
  - <https://crates.io/api/v1/crates/memx-cdy>
- **Sources the enricher read:**
  - <https://github.com/aki-akaguma/memx-cdy>
  - <https://github.com/aki-akaguma/memx-cdy/commits>
  - <https://github.com/aki-akaguma/memx-cdy/issues?q=is%3Aissue>
  - <https://github.com/aki-akaguma/memx-cdy/issues/2>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/README.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/cbindgen.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/aki-akaguma/memx-cdy/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/README.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/arch/x86/x86_mem.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/arch/x86/mod.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/arch/x86/x86_cmp.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/arch/x86/x86_set.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/arch/x86/x86_cpy.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/mem/mod.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/mem/mem_cmp.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/src/utils/mod.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memmem.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memchr.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memcmp.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memcpy.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memset.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/README.memeq.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/docs/review.1.md>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/bench-memmem.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/bench-memcmp.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/bench-memset.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/benches/create_data.rs>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/xbench/Cargo.toml>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/makefile.build>
  - <https://raw.githubusercontent.com/aki-akaguma/memx/HEAD/Makefile>
  - <https://github.com/aki-akaguma/memx/tree/main/src/arch/x86>
  - <https://github.com/aki-akaguma/memx/tree/main/docs>
  - <https://crates.io/api/v1/crates/memx-cdy>
  - <https://crates.io/api/v1/crates/memx>
  - <https://crates.io/api/v1/crates/memx/reverse_dependencies>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/aki-akaguma/memx-cdy`) · [data/wave13/enrich/raw/github_com_aki_akaguma_memx_cdy.json](../../../data/wave13/enrich/raw/github_com_aki_akaguma_memx_cdy.json) (enrichment confidence 0.7)

</details>
