# sefer-alloc (SeferAlloc, Rust allocator with large-segment cache)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust global allocator whose committed large-segment cache makes same-size 4-64 MiB alloc/free 12-33x cheaper than mimalloc.

| | |
|---|---|
| **Beats** | mimalloc (C, via the Rust mimalloc 0.1 crate as GlobalAlloc) and the Windows System allocator |
| **Claimed result** | README large alloc/free table (lower is better, measured 2026-07-06): 4 MiB \~58.6 ns vs mimalloc \~716 ns (\~12.2x) vs System \~17.7 us (\~302x); 16 MiB \~61.9 ns vs \~1.13 us (\~13.5x); 64 MiB \~60.8 ns vs \~2.58 us (\~33x). README 'Why bother' summarises this as \~12-35x faster than mimalloc. realloc_grow_geometric (64 B to 4 MiB) \~238 us vs mimalloc \~431 us (\~1.8x; re-measured 2026-08-04 after the earlier '9.67 us / 39.6x' figure was withdrawn as physically impossible); realloc_grow_neighbour_pressure \~400 ns vs \~1.34 ms (\~3,350x). The 'Up to \~18x faster than mimalloc on cached large alloc/free' wording is from the GitHub About text, not the README. README also states 0.3.0 loses to mimalloc on the cold path at small sizes (16-64 B, \~1.9-2.7x slower; 2026-07-23 run 16 B 2.37x, 256 B 2.71x slower) and on single-thread larson/mstress at T=1 (1.28-1.36x behind). |
| **Workload** | criterion micro-benchmarks calling SeferAlloc directly through GlobalAlloc: alloc(N)+free round trips of 4, 16 and 64 MiB served by a large-segment cache, realloc growth chains, small-size churn and cold-path tables. |
| **Metric** | latency |
| **Hardware** | One Windows 10 dev machine, CPU model not stated; README gives host noise as +-15-20 percent and up to +-60 percent run-to-run drift of absolute ns/op (ratios declared the normative signal). |
| **Compiler and flags** | cargo bench --features production; Cargo.toml [profile.bench] lto = "thin", codegen-units = 1 (Cargo default opt-level 3 for bench); mimalloc's C core is built by the mimalloc 0.1 crate's build script (Cargo.toml comment: 'at full optimization'); criterion sample_size(10), 1-2 s warm-up, 2-3 s measurement; rustc version not stated (MSRV 1.93). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: the OPT-E large-segment cache keeps pages committed so a same-size re-allocation returns without an OS round trip, while mimalloc and System go back to the OS. |
| **Adoption** | 1 star, 0 forks; 2,976 commits; crates.io 1,351 downloads, latest published version 0.2.1 (2026-06-30) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/PHPCraftdream/sefer-alloc) · [benchmark](https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/README.md) |

## Verdict

Author-run criterion micro-benchmarks (sample_size 10, one Windows 10 dev machine with unstated CPU and rustc, absolute numbers drifting up to +-60 percent between runs) call SeferAlloc, the mimalloc 0.1 crate and System directly through GlobalAlloc: same-size alloc+free of 4/16/64 MiB took \~59-62 ns vs mimalloc \~0.72-2.58 us, and realloc 64 B to 4 MiB took \~238 us vs \~431 us (the earlier 9.7 us figure was withdrawn). The 2026-10-10 committed-span guard fix (07a3652) is in try_promote_to_large, which per the R15-3 changelog compiles only with the opt-in medium-classes feature, so it does not touch these `production` measurements.

## Use it when

- Rust programs that repeatedly allocate and free large buffers of the same size (4-64 MiB, size within 2x of a cached span) on the same thread, such as per-frame or per-batch scratch buffers, where the allocation call itself shows up in profiles.
- Workloads that grow single large Vec-like buffers by realloc within 4 MiB (realloc_grow_neighbour_pressure: \~400 ns vs mimalloc \~1.34 ms on the author's Windows host).
- Builds that must avoid any C/C++ dependency (cross-compilation or audit-perimeter reasons) but still want a per-thread-heap allocator on x86_64 or aarch64 Linux/Windows.
- Medium small-object churn of 256 B to 1 KiB with immediate reuse, where the author measured 1.57x (256 B) and 8.59x (1 KiB) over mimalloc on one noisy host.

## Skip it when

- Long-running services on the published crate: 0.2.1 (the only non-yanked crates.io release) has an open, unanswered report of 1,081 retained 4 MiB arenas (4.22 GiB committed) for one or two live 278-435 KB buffers, ending in an OOM abort after about six minutes on Windows.
- Programs with many live allocations over \~253 KiB: each takes its own 4 MiB segment (up to \~16x commit amplification at 256 KiB) and there is a hard wall of 4,095 simultaneously live Large objects, after which alloc returns null and a GlobalAlloc consumer aborts.
- Memory-capped containers or many-thread servers with default settings: the large cache keeps up to 256 MiB committed per thread heap, and idle time reclaims nothing (0 KiB in all 36 arms of the author's sweep) unless you call trim_current_thread() or start the maintenance worker.
- Small-object-heavy or single-threaded allocation-bound code: cold 16 B and 256 B allocations are 2.4-2.7x slower than mimalloc and single-thread larson/mstress is 1.28-1.36x behind; mixed-size large allocations miss the cache.
- Processes that fork without exec while multithreaded (no pthread_atfork handling), 32-bit targets (rejected at compile time), or anyone needing a released, externally reviewed allocator (README calls HEAD a dirty snapshot pending acceptance; 1 star, one author).

## How it is fast

Per-thread heaps with a lock-free magazine (tcache) fast path on 4 MiB segments, as in mimalloc-style designs. The headline large-block win is the OPT-E large-segment cache: freed large segments (8 slots per heap) stay reserved and committed, so a later request of similar size (needed &lt;= cached &lt;= 2x needed) is a slot scan plus header rewrite with no VirtualAlloc/mmap. Realloc of large blocks grows in place (OPT-G) because every allocation over \~253 KiB already owns a whole committed 4 MiB segment, so growth up to that span is a header update instead of copy-and-free.

## Compared with alternatives

Against allox, the only other Rust general-purpose allocator catalogued here (its wins are small-object throughput over glibc, mimalloc and snmalloc), pick sefer-alloc only when same-size large-buffer churn or in-place large realloc dominates and you can cap its retention; for small-object or mixed workloads allox's claims or plain mimalloc fit better.

## Integration

| | |
|---|---|
| **Form** | crate (sefer-alloc; HEAD is 0.3.0, crates.io latest 0.2.1) |
| **Dependencies** | No C/C++ libraries; at HEAD the allocator features pull the author's companion crates (aligned-vmem, once-ptr-cell, size-classes, sefer-region, numa-shim for numa-aware) as path+version dependencies; mimalloc 0.1 is a dev-dependency only, used as the benchmark baseline |
| **Minimum toolchain** | Rust 1.93 at HEAD (raised from 1.88 because older std aborts with TLS-destructor registration on Windows/Apple); crates.io 0.2.1 declares 1.88 |
| **Platforms** | 64-bit only for allocator features: x86_64 linux-gnu and windows-msvc, aarch64 linux-gnu and apple-darwin in CI; other 64-bit targets untested; 32-bit rejected at compile time |
| **Thread safety** | GlobalAlloc implementation with one heap per active thread and lock-free own-thread fast path; cross-thread free via the alloc-xthread feature (in `production`); fork() of a multithreaded process followed by allocation before exec is unsupported; Windows ExitProcess with allocator locks held degrades to leaking through System. |
| **Drop-in for the baseline** | partial — drop-in as a Rust #[global_allocator] (three lines), but the README documents no C malloc replacement path, and the `production` feature plus memory-policy settings are needed to avoid pinned segments and unbounded per-heap retention |

## Gotchas

- Open issue #1 (2026-08-22, no maintainer reply, not mentioned in README or CHANGELOG): a wezterm fork using sefer-alloc 0.2.1 `production` on x86_64-pc-windows-msvc kept 1,081 regions of exactly 4 MiB (4.22 GiB, each reserving 8 MiB) for at most one or two live per-frame buffers of 278-435 KB, about 10x amplification, until an OOM abort; this is the large-allocation path the headline benchmark flatters with same-size reuse.
- Harness: benches/large_realloc.rs allocates and immediately frees the same size without touching the memory, so page faults and commit cost are not measured. Derived from page data: mimalloc's \~716 ns at 4 MiB is already \~25x below System's \~17.7 us, so mimalloc is not making an OS round trip either; the 12-33x gap is about 0.65-2.5 us of bookkeeping per cycle, while the project's own CHANGELOG puts a 2 MiB copy at \~50-100 us on this host, so the saving is around 1 percent or less of the cost of writing the block once. The last published cache-miss figure for SeferAlloc at 4 MiB was \~237-254 us (13x slower than System), before later commit-path changes; no current miss-path number is published.
- Every allocation above SMALL_MAX (\~253 KiB) without the opt-in medium-classes feature owns a dedicated 4 MiB segment and a SegmentTable slot (cap 4,095 live); the realloc and neighbour-pressure wins come from that pre-committed span, a memory cost the benches do not charge.
- README discloses a Miri-reported Stacked/Tree Borrows violation (P1-box: free-list links inside freed small blocks freed through a by-value Box), no pthread_atfork handlers, and that the default large cache retains up to 256 MiB per heap with no reclamation while idle.

## Known shortcomings

- Win from a committed-segment cache, not the language; CPU and rustc unstated on a single noisy Windows 10 host (absolute numbers drift up to 60% between runs); an earlier realloc figure (9.67 us, 39.6x) was withdrawn as impossible; commit 07a3652 (2026-10-10) restored a realloc committed-span guard; '\~18x' appears only in the GitHub About text; crates.io latest 0.2.1.
- Open issue #1 (2026-08-22, unanswered, absent from the CHANGELOG): the published 0.2.1 'production' build on Windows kept 1,081 x 4 MiB arenas (4.22 GiB) for 1-2 live 278-435 KB buffers and OOM-aborted after about 6 minutes. Bench flaw: alloc plus free never touches memory; mimalloc's 716 ns is already about 25x below System, so the gap is about 0.65-2.5 us of bookkeeping, and with a 2 MiB copy at 50-100 us (CHANGELOG) the saving is around 1% or less per use. Every allocation over 253 KiB owns a committed 4 MiB segment with a hard cap of 4,095 live Large objects; the realloc wins ride on that span. try_promote_to_large compiles only with medium-classes, so the 07a3652 guard does not touch the production realloc rows.

## Caveats and trade-offs

Headline large alloc/free ratios hold only for same-size reuse inside the decay window with a size factor of 2x or less (OPT-E cache keeps 8 committed slots); README says not to extrapolate to mixed-size or cold first-touch workloads. The win is a caching policy (pages kept committed, no OS round trip; the bench never touches the memory) rather than language or codegen; mimalloc and System return large blocks to the OS. Single Windows 10 host with unstated CPU and rustc version, quick criterion profile (sample_size 10), +-60 percent absolute drift between runs; the 16/64 MiB mimalloc/System absolute cells are carried from an earlier pre-X-arc run. The realloc_grow_geometric row was earlier published as 9.67 us / 39.6x and withdrawn on 2026-08-05 as physically impossible; the current 1.8x is the corrected figure. Commit 07a3652 (2026-10-10, 'fix(perf): restore realloc committed-span guard') restored a try_promote_to_large committed-span rejection whose empty form crashes with 0xc0000005; when the guard was emptied relative to the 2026-08-04 realloc measurement was not established. The '\~18x' figure appears only in the GitHub About text (README tables give 12.2x-33x). The measured 0.3.0 tree is not on crates.io (latest 0.2.1), although the README install line asks for version 0.3. Sole author, 1 star, heavily agent-driven repo (2,976 commits, CLAUDE.md). [retier] Open issue #1 (2026-08-22, unanswered): the published 0.2.1 'production' build on Windows kept 1,081 x 4 MiB arenas (4.22 GiB) for 1-2 live 278-435 KB buffers and OOM-aborted after about 6 minutes. The bench's alloc plus free never touches memory; mimalloc's 716 ns is already about 25x below System, so the gap is about 0.65-2.5 us of bookkeeping, around 1% or less of a 2 MiB copy. Every allocation over 253 KiB owns a committed 4 MiB segment with a hard cap of 4,095 live Large objects.

Pure Rust, no libnuma/mimalloc/jemalloc dependency; handle store plus global allocator. README discloses a Miri-reported undefined-behaviour case (P1-box: free-list links inside freed small blocks) and a MAX_SEGMENTS pinning limit for long-running processes with many small-segment cycles.

## Maintenance

Very active single-author, heavily agent-driven project (3,048 commits, last commit 2026-10-11) under MIT OR Apache-2.0, but the crates.io release (0.2.1, June 2026) carries an open memory-retention OOM report and HEAD describes itself as a snapshot without a release GO, so treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party criterion numbers from public bench code (benches/large_realloc.rs drives SeferAlloc, mimalloc 0.1 and System through GlobalAlloc directly), but the CPU model and rustc version are never stated (only 'Windows 10 dev machine'), so not A; no independent measurement, so C.
- **Verifier notes:** All README table numbers match the record; baseline mimalloc (C) is measured in the same harness. Not a language-level claim: the large alloc/free and realloc wins come from SeferAlloc's committed-segment cache and in-place Large growth versus mimalloc's OS round trip and copy-and-free, so same_algorithm false stands and same_opt_level was left null (mimalloc C side built by its crate build script, Rust side thin LTO). Shortcomings to record: unstated CPU/rustc, single noisy Windows host, narrow same-size-reuse precondition, one withdrawn overstated realloc figure, crates.io lags HEAD (0.2.1).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-109 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/README.md>
  - <https://github.com/PHPCraftdream/sefer-alloc>
  - <https://github.com/PHPCraftdream/sefer-alloc/commits/main>
  - <https://github.com/PHPCraftdream/sefer-alloc/commit/07a3652b74ea535977cb7c5c487a66b416c4205c>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/docs/ALLOC_BENCH.md>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/benches/large_realloc.rs>
  - <https://crates.io/api/v1/crates/sefer-alloc>
- **Sources the enricher read:**
  - <https://github.com/PHPCraftdream/sefer-alloc>
  - <https://github.com/PHPCraftdream/sefer-alloc/issues>
  - <https://github.com/PHPCraftdream/sefer-alloc/issues/1>
  - <https://github.com/PHPCraftdream/sefer-alloc/commit/07a3652b74ea535977cb7c5c487a66b416c4205c>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/docs/ALLOC_BENCH.md>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/benches/large_realloc.rs>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PHPCraftdream/sefer-alloc/HEAD/CLAUDE.md>
  - <https://crates.io/api/v1/crates/sefer-alloc>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/phpcraftdream/sefer-alloc`) · [data/wave14/enrich/raw/github_com_phpcraftdream_sefer_alloc.json](../../../data/wave14/enrich/raw/github_com_phpcraftdream_sefer_alloc.json) (enrichment confidence 0.6)

</details>
