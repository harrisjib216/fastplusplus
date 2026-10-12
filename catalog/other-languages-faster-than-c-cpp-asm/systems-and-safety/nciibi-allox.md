# allox (Rust general-purpose allocator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust thread-caching global allocator; author's harness shows 1.9-3.5x the best C allocator on mixed-size churn, parity elsewhere.

| | |
|---|---|
| **Beats** | glibc malloc (the 'system' column of the Linux table), mimalloc and snmalloc, each driven through a Rust GlobalAlloc wrapper; Rust-native talc and dlmalloc are also compared |
| **Claimed result** | Linux x86-64 (Ryzen 5 1600) direct-call table, ops/s: tight-small 1T 52.52 M/s vs glibc 44.77, mimalloc 48.00, snmalloc 41.54 (1.09x vs best); mixed-small 8T 196.03 M/s vs system 37.17, mimalloc 40.42, snmalloc 57.87 (3.39x vs best); large-only 1T 7.36 M/s vs system 340 K/s, mimalloc 2.52 M/s. The zeroed-large row (86.63x) is struck: a recycled block gets madvise(MADV_DONTNEED) with the memset skipped while the bench touches 1 byte, so the zeroing cost is never paid. |
| **Workload** | 22 direct-call workloads in benches/alloc.rs driven through GlobalAlloc (small, mixed and large size classes at 1 and 8 threads, zeroed allocation, producer/consumer remote free, thread churn, a pthread calibration row, json-ish, request and ECS realloc-growth shapes); ops/s, higher is better. Each allocated block is written at one byte only, so the large and huge rows measure allocator bookkeeping and memory retention rather than memory traffic. A separate process-global String/Vec/HashMap application benchmark (examples/app_workload.rs, scripts/app_bench.sh) runs at 1 and 4 threads. |
| **Metric** | throughput |
| **Hardware** | Linux x86-64 AMD Ryzen 5 1600, taskset -c 0-7, 3 GiB cgroup, BENCH_FRESH=1 BENCH_SAFE_LIVE=1, one fresh process per allocator/workload/repetition, median of 3 x 2 s runs. The Windows x86-64 table names no CPU. |
| **Compiler and flags** | cargo bench; the bench profile inherits [profile.release] opt-level = 3, lto = true, codegen-units = 1 from Cargo.toml; rustc version and RUSTFLAGS not stated (MSRV 1.79). Comparators: mimalloc crate 0.1 and snmalloc-rs 0.7 (build_cc feature) compiled by their build scripts with unlogged C/C++ flags; 'system' is the distro glibc malloc (version unstated); talc 5 and dlmalloc 0.2 are Rust. Every allocator, allox included, is called through a &'static dyn GlobalAlloc, so allox gets no inlining advantage from LTO. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: every fast path is lock-free per thread with sharded class locks touched only by batched slow paths, while single-heap allocators (talc, dlmalloc) serialize on one mutex; no mechanism is given for the glibc/mimalloc/snmalloc gaps on the mixed-size and large rows. |
| **Adoption** | 1 star, 0 forks; 1,355 commits, but the latest batch (2026-10-10/11) are docs-only commits that append hidden '&lt;!-- updated: ... --&gt;' comments to README.md; not published on crates.io (API: crate `allox` does not exist) despite the README's `allox = "0.1"` snippet. |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/Nciibi/allox) · [benchmark](https://raw.githubusercontent.com/Nciibi/allox/HEAD/README.md) |

## Verdict

In the author's own direct-call harness (benches/alloc.rs: every allocator called through a &'static dyn GlobalAlloc, fresh process per run, median of 3 x 2 s, Ryzen 5 1600 pinned to 8 logical CPUs, release LTO build; rustc, glibc and the comparators' C flags unstated, Cargo.lock pins mimalloc 0.1.52 and snmalloc-rs 0.7.5), allox beat the best of glibc, mimalloc and snmalloc by 1.9-3.5x on mixed-size and medium churn and by 1.25-6.3x on large rows that write one byte per block, and tied (1.02-1.12x, inside the stated noise) on fixed-size small rows. It lost zeroed-small 8T (0.67x) and the 4-thread String/Vec/HashMap application run (0.90-0.94x), and led that application run 1.06x at 1 thread.

## Use it when

- Rust binaries that want a faster global allocator but cannot rely on a C toolchain: cross-compilation, wasm32 (replacing dlmalloc, the wasm default) or i686, where the mimalloc, snmalloc and jemalloc crates need cc or CMake.
- Allocation-heavy code that churns mixed sizes from 16 B to 64 KiB on one or a few threads: 2.6-3.5x the best of glibc, mimalloc and snmalloc at 1 thread and 1.9-3.4x at 8 threads in the author's harness.
- Container growth by realloc doubling up to 1 MiB (growable extents): ecs 8T at 1.25x glibc, which uses zero-copy mremap.
- Windows programs contending on HeapAlloc: 3.7-4.96x the system allocator on the small-object rows of the older Windows table.

## Skip it when

- C or C++ programs: there is no malloc/free interposition and no operator new replacement, only prefixed allox_\* symbols in an rlib (Cargo.toml declares no staticlib or cdylib), and allox_malloc(0) returns null; use mimalloc, snmalloc or jemalloc there.
- Many-threaded services that calloc small objects or run String/Vec/HashMap work across threads: zeroed-small 8T at 0.67x snmalloc and the 4-thread application benchmark at 0.90x snmalloc and 0.94x mimalloc.
- Production use that needs maturity: single author, 1 star, explicitly not audited, API may change before 0.2, and not published on crates.io even though the README tells you to add allox = "0.1".
- Memory-tight processes: it retains freed pages and regions (up to 32 MiB hot per large-region shard across 8 shards, plus per-thread stashes and discarded virtual reserves); peak RSS in the harness was 93 MiB on mixed-small 8T, 118 MiB on mixed-all 8T and about 300 MiB on prodcons 8T.

## How it is fast

It follows the mimalloc design: about 12.5%-spaced size classes in 64 KiB single-class pages, per-thread free lists with no locks or atomics on the fast path, and per-class sharded global heaps reached only by batched refills (about 64 blocks per lock). Rust-specific choices add to that: GlobalAlloc frees take the size class from the Layout through a lookup table instead of loading a page header (the changelog puts that load at about 48% of free cycles on mixed-all), the fast paths are frameless leaf functions with slow paths tail-called, and growing realloc chains move once into a reserved slack region and then grow in place. Large blocks are kept in per-thread, hot and cold (madvise-discarded) region caches instead of being unmapped, which is where the large-row gains come from.

## Compared with alternatives

No sibling in this category is an allocator (they are sorts, file tools, compilers and codecs). Against mimalloc and snmalloc themselves, pick allox only for Rust targets where a C toolchain is a problem (cross-compiling, wasm32, i686) or for mixed-size churn on a few threads, and keep mimalloc or snmalloc for many-threaded production services and for any C/C++ code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (tikv-jemallocator is an optional bench-only feature; mimalloc, snmalloc-rs, talc and dlmalloc are dev-dependencies for the benchmarks) |
| **Minimum toolchain** | Rust 1.79 (MSRV, stable channel; checked in CI) |
| **Platforms** | Linux and other Unix, macOS, Windows, wasm32-unknown-unknown, i686; the arena-backed big tier and in-place growth are Unix+std only; no_std mode needs a supported memory backend and is meant for single-threaded targets |
| **Thread safety** | Thread-safe GlobalAlloc with lock-free per-thread caches and mutex-sharded global heaps; thread pools should call allox::flush_current_thread() to hand back cached blocks; no_std builds use one global cache behind a spin mutex |
| **Drop-in for the baseline** | partial — a one-line #[global_allocator] swap for Rust programs; not a malloc/free or operator new replacement for C/C++ (prefixed allox_\* C ABI only, rlib only, zero-size requests return null) |

## Gotchas

- zeroed-large 1T's 86.63x is a harness artifact: for a recycled 5-8 MiB block, alloc_large_ex calls sys::discard (madvise MADV_DONTNEED) and calloc then skips its memset, but benches/alloc.rs writes only the first byte of each block, so allox pays one madvise and one page fault while glibc, mimalloc and snmalloc memset 5-8 MiB. A caller that writes the whole buffer would pay roughly 1,300-2,000 page faults with kernel zero-fill instead, a cost the benchmark never triggers. The same one-byte touch applies to every large and huge row, so those rows measure bookkeeping and memory retention, not memory traffic; snmalloc's 1-22 K/s on them works out to a near-constant 6.5-9 GB/s of block bytes (derived from page data), which suggests it touches or zeroes whole blocks on every allocation, so the large-row ratios against snmalloc reflect that behaviour and its build settings.
- The direct-call harness exercises only the GlobalAlloc path, whose frees take the size class from the Layout (dealloc_with_layout) and skip the page-header load that the changelog says was about 48% of free cycles on mixed-all. C callers going through allox_free take dealloc_impl's header lookup instead, a path the published tables never measure, and glibc's free gets no size at all. Part of the mixed-size lead may come from this sized free, which C callers would not get (an inference, not measured).
- scripts/app_bench.sh runs under set -o pipefail but checks the build with `if ! cargo build ... | grep -q '^error'`: when the build fails, cargo's non-zero status becomes the pipeline status, `!` makes it look like success, and the script runs whatever older binary sits in target/app-&lt;feature&gt;/. The 'build failed' branch is effectively unreachable, so a stale binary can be benchmarked silently. The script also runs each backend once (APP_SECS defaults to 3), so the README's 'median of 3-5 x 2 s, interleaved' protocol for the application table was done by hand and not logged.
- The README says the numbers come from a shared dev box whose load average 'wanders between 2 and 12' with a \~10% run-to-run noise floor, and its size labels disagree with the code (big-tail is 262145-524289 B, big-upper-tail 524289-1048577 B, large-only 8T 32768-262144 B). Its own known-defects note says the batched telemetry counters lose their last window, so the counter-based zeroed-small analysis is unreliable.

## Known shortcomings

- Most 'wins' are 1.02-1.12x inside its own \~10% noise floor; the large-row gaps come from memory retention with each block touched at one byte (zeroed-large 86.63x skips the memset); loses zeroed-small 8T (0.67x) and the 4-thread app bench (0.90-0.94x); 1 star, not on crates.io, recent commits are README padding.
- Harness flaw: the zeroed-large 86.63x is an artefact. A recycled 5-8 MiB block gets madvise(MADV_DONTNEED) and the memset is skipped (alloc_large_ex known_zeroed), while the bench writes 1 byte, so the zeroing becomes about 1,300-2,000 page faults that are never triggered; the same 1-byte touch applies to all large rows, and snmalloc's 1-22 K/s works out to about 6.5-9 GB/s of block bytes, so it likely zeroes or touches whole blocks. scripts/app_bench.sh's build check is inverted under set -o pipefail, so a failed build counts as built and a stale binary is benchmarked silently. The direct-call harness measures only the Layout-routed sized free; the C ABI allox_free header path is unmeasured. rlib only, no malloc interposition, not on crates.io.

## Caveats and trade-offs

Very young single-author repo (1 star), not on crates.io; commit count is inflated by README-comment padding commits. Workloads are the author's own and rows carry a stated \~10% noise floor (median of 3 x 2 s), so the 1.02x-1.12x 'wins' are ties. Each block is touched at one byte: large/huge rows reward allox for keeping arena memory mapped while glibc (mmap threshold) and snmalloc return or decommit it (snmalloc reads 1 K/s on huge-only), and zeroed-large 1T's 86.63x comes from skipping the memset of 5-8 MiB blocks after a madvise discard while the benchmark never faults in more than one page. README size-range labels disagree with the code (big-tail labelled 64K-256K is 262145-524289 in code; big-upper-tail 256K-1M is 524289-1048577; large-only 8T 32K-1M is 32768-262144). mimalloc/snmalloc measured through Rust GlobalAlloc wrappers with unlogged build flags, glibc version unstated, no independent reproduction. The README documents its losses (zeroed-small 8T, 4-thread app workload) and a known telemetry-counter defect rather than hiding them. [retier] The zeroed-large 86.63x is an artefact: a recycled 5-8 MiB block gets madvise(MADV_DONTNEED) and the memset is skipped (alloc_large_ex known_zeroed) while the bench writes 1 byte, so the zeroing becomes page faults that are never triggered; the same 1-byte touch applies to all large rows, and snmalloc's 1-22 K/s implies it zeroes or touches whole blocks. scripts/app_bench.sh's build check is inverted under set -o pipefail, so a failed build counts as built and a stale binary is benchmarked silently. The direct-call harness measures only the Layout-routed sized free; the C ABI allox_free header path is unmeasured.

Rust crate with a GlobalAlloc type and allox::malloc/free functions; peak RSS is higher on several rows (93 MiB mixed-small 8T, 118 MiB mixed-all 8T, 300 MiB prodcons 8T). Loses to snmalloc and mimalloc on 8-thread zeroed small allocations.

## Maintenance

Active but very young: the README and changelog call it v0.1.0 (2026-09-26), yet crates.io has no allox crate, so it needs a git dependency. Its 1,355 commits end in auto-numbered 'v0.0.13xx' commits and 20 docs commits that only append hidden README comments. It is MIT OR Apache-2.0 with zero dependencies, CI runs Miri, fuzzing and Kani on a schedule, and the author says it is not audited.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables backed by public benchmark code (benches/alloc.rs, run via cargo bench with BENCH_FRESH=1 BENCH_SAFE_LIVE=1) and a named CPU (Ryzen 5 1600), but the rustc version, RUSTFLAGS, glibc version and the C/C++ flags used for the mimalloc/snmalloc comparators are not stated, so it falls short of A; no independent run exists.
- **Verifier notes:** Numbers match the README exactly; confirm at C. Shortcomings to record: wins mostly within the stated 10% noise floor except mixed-size, medium and large rows; large-row gaps reflect memory retention under a one-byte-touch benchmark (zeroed-large 86.63x skips memset with one page touched); losses at zeroed-small 8T (0.67x) and the 4-thread application benchmark (0.90x-0.94x); repo is 1 star, unpublished on crates.io, with padding commits. same_opt_level left null: comparators are built by cc/cmake build scripts under the bench profile (likely -O3) and glibc is the distro build, but no build log states the flags.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-107 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/README.md>
  - <https://github.com/Nciibi/allox>
  - <https://github.com/Nciibi/allox/commits>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/benches/alloc.rs>
  - <https://crates.io/api/v1/crates/allox>
- **Sources the enricher read:**
  - <https://github.com/Nciibi/allox>
  - <https://github.com/Nciibi/allox/commits>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/README.md>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/benches/alloc.rs>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/examples/app_workload.rs>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/scripts/app_bench.sh>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Nciibi/allox/HEAD/src/ffi.rs>
  - <https://crates.io/api/v1/crates/allox>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/nciibi/allox`) · [data/wave14/enrich/raw/github_com_nciibi_allox.json](../../../data/wave14/enrich/raw/github_com_nciibi_allox.json) (enrichment confidence 0.7)

</details>
