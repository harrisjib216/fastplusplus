# elfmalloc (allocators-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🔴 abandoned

> Rust research malloc (elfmalloc) with a C API, faster than glibc ptmalloc2 and often 2017 jemalloc on multithreaded benchmarks.

| | |
|---|---|
| **Beats** | glibc ptmalloc2 (glibc 2.19) and jemalloc (dev build, August 2017); also llalloc and rpmalloc |
| **Claimed result** | Qualitative from plots normalised to ptmalloc2 (no ratios in text): highest throughput on threadtest small objects except at 32 threads where it is a bit behind jemalloc; top on threadtest medium objects at 32 threads; on shbench out-performs all competitors in throughput and memory at higher core counts but lags llalloc at low thread counts; highest throughput on producer-consumer at the cost of more memory. ptmalloc2 is described as consistently the slowest. |
| **Workload** | threadtest and shbench (small &lt;=64 B and medium few-KB objects) from the scalloc artifact, plus rpmalloc-benchmark in producer-consumer mode, at 1, 2, 4, 8, 16, 24 and 32 threads via LD_PRELOAD. |
| **Metric** | throughput |
| **Hardware** | Dual Xeon E5-2620v4, 16 cores / 32 threads, under WSL |
| **Adoption** | 318 stars |
| **Last commit** | 2020-04-04 |
| **Links** | [repository](https://github.com/ezrosent/allocators-rs) · [benchmark](https://github.com/ezrosent/allocators-rs/blob/master/info/elfmalloc-performance.md) |

## Verdict

The authors LD_PRELOADed elfmalloc into scalloc-artifact threadtest and shbench (objects of 64 B or less, and objects of a few KB) and into an adapted rpmalloc-benchmark producer-consumer run at 1-32 threads on dual Xeon E5-2620v4 under WSL, comparing against glibc 2.19 ptmalloc2, an August 2017 jemalloc dev build, llalloc and rpmalloc. The plots are normalised to ptmalloc2 and show elfmalloc leading most configurations, with jemalloc ahead at 32 threads on small-object threadtest and llalloc ahead on shbench at low thread counts. No compiler flags or numeric ratios are given, and the page is marked work in progress.

## Use it when

- Research or comparison runs on 64-bit Linux where you want a scalloc-style allocator with a different global-structure design to test against.
- Multithreaded C or C++ programs dominated by small-object churn or producer-consumer frees, where the authors' plots show it ahead of ptmalloc2 and usually ahead of 2017 jemalloc.
- Rust projects that need a type-specific object allocator (slab-alloc, object-alloc traits) and can build with an old nightly toolchain.
- Throughput matters more than resident memory and the process is long-running with stable allocation patterns.

## Skip it when

- Production use: the README calls elfmalloc 'early alpha' with 'certainly undiscovered bugs', and the project has been unmaintained since 2020.
- Memory-constrained services: dirty pages are never returned to the OS (the design doc says there is no madvise reclamation), and threadtest and producer-consumer show clearly higher memory use than the competitors.
- macOS, Windows or 32-bit targets: Mac 'will currently encounter bugs or crashes', 32-bit support is untested, and Windows CI was never fixed (issue #133).
- Anyone needing a modern drop-in: mimalloc, snmalloc and current jemalloc/tcmalloc were never compared, so the 2017 lead may not hold.

## How it is fast

Size-class slabs ('Slags') with a bit-set of free objects; the claimed bit and the free count share one word so remote frees are a single fetch-or plus fetch-add with no retry loop. A per-thread, per-size-class fixed-size stack (MagazineCache front end, after Bonwick's magazines) serves most allocations and frees without atomics and batches remote frees by composing masks before the fetch-or. Global pools are bagpipes (weakly ordered concurrent bags) instead of locked lists, and free() finds an object's path by rounding the pointer down to a 2 MiB-aligned header, following scalloc's virtual-span idea.

## Compared with alternatives

Mesh targets memory compaction and IsoAlloc targets hardening; pick elfmalloc only to study or benchmark a lock-free, scalloc-like Rust design that can be preloaded into C programs. For production C++ allocator replacement, a maintained sibling such as Mesh, or mimalloc outside this list, is the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate (elfmalloc) plus a cdylib shared lib (elfc) for LD_PRELOAD |
| **Dependencies** | Sibling path crates (alloc-fmt, alloc-tls, bagpipe, bsalloc, malloc-bind, mmap-alloc) plus lazy_static, libc, log 0.3, num_cpus, smallvec 0.4, sysconf |
| **Minimum toolchain** | Rust nightly from about 2018 (uses feature gates allocator_api, const_fn, const_size_of, thread_local_state, core_intrinsics); exact pinned nightly not documented |
| **Platforms** | 64-bit Linux (relatively complete); macOS crashes; 32-bit untested; Windows not working in CI |
| **Thread safety** | Thread-safe; designed for multithreaded allocation with cross-thread (remote) frees |
| **Drop-in for the baseline** | partial: replaces glibc malloc via LD_PRELOAD of the elfc .so, but has to be built with an old nightly Rust and is alpha quality |

## Gotchas

- lib.rs relies on nightly feature gates that have since been removed or renamed (const_size_of, the old Alloc trait), so a current nightly is unlikely to build it without patches.
- When the crate is linked into a Rust program without the use_default_allocator feature, bsalloc becomes the global heap and the README warns that other allocations get slower.
- The c-api feature, which elfc enables, speeds up the C API at the cost of worse memory use for the Rust Alloc API.
- It reserves a very large (many-terabyte) virtual region up front in 2 MiB pages, which can trip overcommit limits, ulimit -v or sanitizers.

## Known shortcomings

- README says early alpha; crashes on Mac, 32-bit untested. Dirty pages are never returned to the OS (no madvise). Needs a 2018-era nightly Rust: feature gates it uses (const_size_of, old Alloc trait) have since been removed.

## Caveats and trade-offs

First-party results run on WSL, compiler flags not stated, results are plot-only (no numeric ratios); harness is a locally modified scalloc-artifact not checked into the repo; old baselines (glibc 2.19 ptmalloc2, 2017 jemalloc dev); higher memory use than competitors on threadtest and producer-consumer; page is marked work in progress; unmaintained since 2020; mimalloc not compared.

Rust implementation, usable from C/C++ only through its C API or LD_PRELOAD; frequently uses more memory than competitors; compared against jemalloc dev version from August 2017.

## Maintenance

Abandoned since 2020 (alpha, 2018-era nightly Rust); Apache-2.0/MIT, so it is free to copy, but it is research code to read and benchmark rather than to ship.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party LD_PRELOAD runs of scalloc-artifact benchmarks (threadtest, shbench, rpmalloc-benchmark producer-consumer) against ptmalloc2 (glibc 2.19), a 2017 jemalloc dev build, llalloc and rpmalloc on dual Xeon E5-2620v4 under WSL; results only as plots normalised to ptmalloc2, no compiler or flags, and the modified harness is not in the repo, so not A.
- **Verifier notes:** Metadata confirmed from github.com pages: 318 stars, Apache-2.0/MIT dual license files present, last commit 2020-04-04. gh CLI blocked in this environment, so archived/fork flags checked only by page view (none shown).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/ezrosent/allocators-rs/blob/master/info/elfmalloc-performance.md>
  - <https://github.com/ezrosent/allocators-rs>
  - <https://github.com/ezrosent/allocators-rs/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/info/elfmalloc-performance.md>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/info/elfmalloc.md>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/elfmalloc/README.md>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/elfmalloc/Cargo.toml>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/elfmalloc/src/lib.rs>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/elfc/README.md>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/elfc/Cargo.toml>
  - <https://raw.githubusercontent.com/ezrosent/allocators-rs/HEAD/.travis.yml>
  - <https://github.com/ezrosent/allocators-rs/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ezrosent/allocators-rs`) · [data/wave11/enrich/raw/github_com_ezrosent_allocators_rs.json](../../../data/wave11/enrich/raw/github_com_ezrosent_allocators_rs.json) (enrichment confidence 0.7)

</details>
