# Talc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust no_std and WebAssembly heap allocator; about 2x DLmalloc's throughput on wasm at under a third of its code size.

| | |
|---|---|
| **Beats** | DLmalloc (Rust wasm default), RLSF, Galloc, FRuSA, system allocator |
| **Claimed result** | No numbers in text; BENCHMARKS_WASM.md concludes 'DLmalloc and RLSF's GlobalTlsf are worse in both size and performance to Talc' and 'If all you care about is performance, use Talc' (plots only). |
| **Workload** | Random alloc/dealloc/realloc actions (single and multi-threaded), heap efficiency and microbench via benches/src; wasm size and speed. |
| **Metric** | throughput |
| **Adoption** | 562 stars |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/SFBdragon/talc) · [benchmark](https://github.com/SFBdragon/talc/blob/master/BENCHMARKS.md) |

## Verdict

First-party plots only: on WebAssembly random actions Talc (Dynamic) does about 28 alloc+dealloc actions per microsecond vs about 12 for DLmalloc and about 19.5 for RLSF, and about 12 vs 6.3 with realloc (about 2x, read off the plot), with module size about 1.6 KB vs 5.5 KB for DLmalloc. On Linux x86_64 single-threaded random actions Talc scores 1.0 relative vs RLSF 0.87-0.93 and DLmalloc 0.55-0.75, but in the multithreaded run Galloc and RLSF score above Talc at most sizes; no compiler version, flags, CPU or wasm runtime are stated.

## Use it when

- Single-threaded wasm32 modules (no atomics) currently using the default DLmalloc, where both allocation throughput and .wasm size matter
- no_std embedded firmware or OS kernels that need a general malloc/realloc over one or more fixed memory regions, including adding or resizing heaps at runtime
- Per-subsystem arenas in Rust via TalcCell plus allocator-api2 collections, where a lock-free !Sync allocator is enough
- Workloads dominated by small-to-medium allocations (tens of bytes to tens of KB) with pointer-sized alignment, which is the distribution the benchmarks and design target

## Skip it when

- Hosted, allocation-heavy multithreaded programs: the author says jemalloc, mimalloc or the system allocator are better there, and TalcLock serializes all threads on one lock
- Large over-aligned allocations (size much smaller than alignment): issue #44 measured 1-byte allocations at 4096-byte alignment about 1,650x slower than dlmalloc (1.22 s vs 739 us)
- wasm heaps that can grow past 2 GiB: open issue #56 (2026-09-24, v5.1.1) reports fit checks that compare wrapped 32-bit addresses and can hand out overlapping memory
- When minimum module size is the only goal: the author recommends lol_alloc (and RLSF SmallGlobalTlsf is comparably small)
- Memory-tight wasm: the default wasm configuration is tuned for speed and the author estimates 10-15% higher runtime memory than alternatives

## How it is fast

It is a dlmalloc-style segregated free-list allocator with boundary tags and configurable size binning, which the author describes as close to TLSF (Two-Level Segregated Fit). Allocation is O(n) worst case but near-constant in practice; deallocation and in-place grow/shrink are O(1). v5 added a WasmBinning configuration tuned for wasm and cut code size, and in-place realloc can be turned off by feature to trade speed for module bytes.

## Compared with alternatives

Pick Talc over rlsf when you want the fastest wasm/no_std allocator in the author's plots (Talc leads RLSF by about 10% single-threaded and about 1.5x on wasm alloc+dealloc) and can spend roughly 500 more bytes than rlsf's small config; neither belongs on a hosted multithreaded server, where mimalloc-class allocators or v8malloc-style designs from the catalog fit better.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | allocator-api2 0.4, lock_api 0.4 (no default features); spinning_top or another RawMutex for TalcLock |
| **Minimum toolchain** | Rust 1.64 (stable by default since v5; nightly feature for core::alloc::Allocator) |
| **Platforms** | any no_std target; WebAssembly sources for wasm32; benchmarks run on Linux x86_64 |
| **Thread safety** | TalcCell is !Sync (single-threaded); TalcLock is thread-safe through a lock_api mutex, with no per-thread caching |
| **Drop-in for the baseline** | partial — on wasm it replaces DLmalloc with a two-line #[global_allocator] static; on no_std you must supply a heap Source and, for threads, a lock type |

## Gotchas

- Open issue #56: on wasm with heap addresses near 4 GiB, full_search_bin and try_grow_in_place compare wrapped addresses and can return overlapping allocations; the reported workaround is capping linear memory at 2 GiB
- Default wasm source changed in v5.1.0 to WasmGrowAndExtend; WasmGrowAndClaim (issue #51) can use 2-10x more linear memory on repeatedly grown vectors but saves about 97 bytes of code
- v5.0.4 fixed a chunk-tagging bug for huge chunks and an infinite-recursion bug in WasmGrowAndClaim, and raised per-allocation metadata from a u8 to a usize for allocations over 24 bytes
- Earlier soundness bugs (Span From&lt;&[T]&gt; UB #33, unaligned Tag read #27, free-list corruption #53, non-Send sources #54) are closed; the crate is tested with MIRI and fuzzing but has a history of unsafe-code bugs

## Known shortcomings

- Open issue 56 (v5.1.1, 2026-09-24): overlapping allocations once the wasm heap passes 2 GiB (full_search_bin and try_grow_in_place compare wrapped addresses); not behind the measured numbers. Issue 44: a 1 B allocation at 4096 alignment is about 1,650x slower than dlmalloc. In the multithreaded plot Galloc and RLSF score above Talc. Wasm plot reads: about 28 vs 12 actions/us against DLmalloc (about 2x with realloc), module 1.6 KB vs 5.5 KB. Rust, not C++.

## Caveats and trade-offs

Results are plots only, no compiler, flags or CPU stated. Author says jemalloc/mimalloc/system allocator are not compared and recommends them on hosted systems; notes the benchmark size/alignment distributions may be 'mildly fitted' to Talc and that Talc v4 was mediocre and RLSF 'walks all over' it (motivating v5). The win claimed is over DLmalloc, Rust's default wasm allocator. FRuSA is excluded from the heap-efficiency plot; the earlier claim that the author states Talc is slower than FRuSA under concurrency is not on the current pages.

no_std and WebAssembly allocator. Linked-list dlmalloc-style design; author says jemalloc and mimalloc are better on hosted systems and Talc scales worse under contention.

## Maintenance

Actively maintained (v5.1.1, last commit 2026-09-09, 562 stars) and MIT-licensed, but an unaddressed overlapping-allocation bug (#56) above 2 GiB is open as of 2026-09-24.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md and BENCHMARKS_WASM.md show first-party plots (random-actions, heap efficiency, microbench, wasm-perf) with public bench code in benches/src and wasm-perf/, but no compiler, flags or CPU are stated and no numbers appear in text; C.
- **Verifier notes:** Real wasm/no_std allocator; recognizable incumbent is DLmalloc (Rust wasm default). MIT (LICENSE.md), 562 stars, last commit 2026-09-09, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party plots
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/README.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/BENCHMARKS_WASM.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/talc/README.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/LICENSE.md>
  - <https://github.com/SFBdragon/talc/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/README.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/BENCHMARKS_WASM.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/talc/README.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/talc/README_WASM.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/talc/Cargo.toml>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/talc/CHANGELOG.md>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/plots/random-actions.png>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/plots/random-actions-multi.png>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/plots/wasm-perf.png>
  - <https://raw.githubusercontent.com/SFBdragon/talc/HEAD/plots/wasm-size.png>
  - <https://github.com/SFBdragon/talc/issues?q=is%3Aissue>
  - <https://github.com/SFBdragon/talc/issues/56>
  - <https://github.com/SFBdragon/talc/issues/44>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/sfbdragon/talc`) · [data/wave11/enrich/raw/github_com_sfbdragon_talc.json](../../../data/wave11/enrich/raw/github_com_sfbdragon_talc.json) (enrichment confidence 0.7)

</details>
