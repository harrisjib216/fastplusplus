# Spice

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `0BSD` · 🟢 active

> Zig fork/join library using heartbeat scheduling; sub-nanosecond fork/join overhead versus Rayon's \~15 ns per join.

| | |
|---|---|
| **Beats** | Rayon (cross-language comparison) |
| **Claimed result** | 100M-node tree sum (bench/README.md SVGs): Zig sequential baseline 3.63 ns/node, Spice 3.93 ns at 1 thread (sub-ns overhead), 0.36 ns at 16 threads (\~11x); Rust sequential baseline 7.48 ns/node, Rayon 22.99 ns at 1 thread (\~15 ns overhead), 1.64 ns at 16 threads (\~14x). Spice at 16 threads is \~4.6x faster than Rayon in absolute per-node time (derived from page data), but the languages' baselines differ 2x. 1000-node tree: Rayon becomes \~60x slower than its baseline at 32 threads on 16 vCPUs, while Spice stays flat because no work is distributed. |
| **Workload** | Binary tree summation fork-join (100M nodes) at up to 16 threads, and a 1000-node small tree, versus a Zig sequential baseline and Rayon on the same algorithm. |
| **Metric** | throughput |
| **Hardware** | Google Cloud c4-standard-16 (16 vCPUs, 60 GB), europe-west4, NixOS 24.05, Linux 6.6.41; CPU model not stated |
| **Compiler and flags** | Zig 0.14.0-dev.564+75cf7fca9, ReleaseFast; Rayon side rustc 1.77.2 / cargo 1.77.1 with Criterion |
| **Adoption** | 973 stars; Rust port chili |
| **Last commit** | 2026-03-22 |
| **Links** | [repository](https://github.com/judofyr/spice) · [benchmark](https://github.com/judofyr/spice) |

## Verdict

Author's single make bench run (August 2024, commit 0b697d6, Zig 0.14.0-dev ReleaseFast versus rustc 1.77.2 with Criterion) on a Google Cloud c4-standard-16 (16 vCPUs, CPU model not stated): summing a 100M-node balanced tree took 3.93 ns/node with Spice on 1 thread against a 3.63 ns Zig baseline, and 0.36 ns at 16 threads; Rayon took 22.99 ns on 1 thread against a 7.48 ns Rust baseline, and 1.64 ns at 16 threads. On a 1000-node tree Rayon became about 60x slower than its baseline at 32 threads while Spice stayed flat. Each library is compared with its own language's baseline, and those baselines differ by 2x.

## Use it when

- Recursive divide-and-conquer in Zig (tree walks, quicksort-style recursion) where each leaf does only nanoseconds of work and Rayon-style per-join overhead would dominate.
- Code that runs on inputs of unpredictable size: on a 1000-node tree Spice stays at sequential speed instead of slowing down, because nothing gets shared before the first heartbeat.
- Shared or busy machines where you want idle worker threads to sleep rather than spin.
- As a reference design for building a low-overhead heartbeat scheduler in C or C++; the whole runtime is one readable file under 0BSD.

## Skip it when

- Production or safety-critical code: the author calls it a research project with zero test coverage, heavy use of @panic for errors, and no plans for active development.
- Large coarse-grained workloads that need the best scaling: Rayon scaled 14x at 16 threads against Spice's 11x, because each worker shares at most one job per heartbeat.
- Data-parallel loops over arrays or slices: there is no parallel-for or iterator API, only fork/join on recursive functions.
- Mixes of slow and fast tasks: open issue #10 describes how a thread waiting on a stolen slow job is not woken for new work, so the pool can degenerate.
- C++ projects that need a native library: it is Zig-only with no C ABI layer, so use from C++ means writing and exporting your own wrapper.

## How it is fast

Heartbeat scheduling (Acar, Charguéraud, Rainey): instead of making every fork stealable, a heartbeat thread flips a per-worker atomic flag about every 100 us, and only then does the worker promote its oldest queued fork into a shared job. Between heartbeats a fork is a push onto a branch-free, sentinel-headed intrusive doubly-linked list on the stack with no atomics, and an unclaimed join is a pop plus a direct, inlinable static call, so the code compiles close to the sequential version. The heartbeat path is marked cold so it costs no registers, Task state is passed as function parameters so LLVM keeps it in registers, and coordination uses a single uncontended mutex with condition waits and no spinning.

## Compared with alternatives

Pick Spice over chili (its Rust port) only if you write Zig or want the original reference code; pick it over Fork Union or citor only for fine-grained recursive fork/join, since those are C++ libraries with parallel-for APIs and broader benchmarks. For C++ heartbeat scheduling the deepsea-inria/heartbeat prototype is the closest catalogued sibling.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the library (parg is a lazy dependency only for the example) |
| **Minimum toolchain** | Current HEAD targets Zig 0.16.0-dev (uses std.Io; last commit supports 0.16.0-dev.2915); the published benchmark used commit 0b697d6 on Zig 0.14.0-dev.564 |
| **Platforms** | any target Zig's std.Thread supports; benchmarked only on x86-64 Linux (and an M3 Pro anecdote) |
| **Thread safety** | Pool is shared across threads via one internal mutex; ThreadPool.call creates a one-off worker per caller. Task and Future values are per-thread and must not be shared. |
| **Drop-in for the baseline** | no |

## Gotchas

- Every fork must be followed by join or tryJoin, and a null result from join means you must run the work yourself; misuse is not checked and the README warns that 'weird things could happen'.
- A forked function's result is limited to 32 bytes (4 u64 words); larger return types are a compile error.
- Finding a ready job is an O(workers) scan under the global mutex (open issue #8), and the heartbeat thread visits workers round-robin, so each worker's effective heartbeat interval stays near 100 us however many workers there are.
- The code tracks Zig dev releases (std.Io API), so it breaks across Zig versions; pin a commit that matches your compiler.

## Known shortcomings

- Zig only, no C ABI. Zero tests, @panic error handling, author not developing it further. Open issue 10 (a thread waiting on a stolen slow job is not woken for new work, so the pool can degenerate) and issue 8 (O(workers) job scan under a global mutex); forked results are capped at 32 bytes. HEAD needs Zig 0.16-dev (std.Io) while the bench ran commit 0b697d6 on Zig 0.14-dev.

## Caveats and trade-offs

Cross-language comparison: the Zig sequential baseline (3.63 ns/node) is twice as fast as the Rust one (7.48 ns/node), so absolute Spice-vs-Rayon times mix scheduler and codegen differences; the author compares each against its own language's baseline. Rayon scales better (14x vs 11x at 16 threads); Spice's win is sub-nanosecond fork/join overhead and no slowdown on tiny inputs. Single workload (tree sum), single run of make bench, August 2024. Author calls it a research project with minimal tests. Zig, usable from C++ only via a C ABI wrapper.

Heartbeat scheduling (work shared every \~100 us), fork/join only, Zig API.

## Maintenance

Described by the author as a research project with no active feature work, but commits through 2026-03-22 keep it building on Zig 0.16-dev; 0BSD and about 500 lines, so easy to vendor or port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark with public code (bench/, make bench), zig 0.14.0-dev ReleaseFast and rustc 1.77.2/Criterion stated, but hardware is only a Google Cloud c4-standard-16 instance with no CPU model, so not A; no independent measurement.
- **Verifier notes:** Record mislabelled 7.48 ns as the sequential baseline; that is Rust's, Zig's is 3.63 ns. Claim corrected with the per-thread numbers read from the bench SVG text; tier stays C, verdict downgrade for the overstated/misattributed claim only. Metadata (0BSD, 973 stars, last commit 2026-03-22) checked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/judofyr/spice>
  - <https://github.com/judofyr/spice/commits>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/README.md>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/bench/spice-tree-sum-100M.svg>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/bench/rayon-tree-sum-100M.svg>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/README.md>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/build.zig>
  - <https://raw.githubusercontent.com/judofyr/spice/HEAD/build.zig.zon>
  - <https://github.com/judofyr/spice/issues?q=is%3Aissue>
  - <https://github.com/judofyr/spice/issues/10>
  - <https://github.com/judofyr/spice/issues/8>
  - <https://github.com/judofyr/spice/commits>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/judofyr/spice`) · [data/wave11/enrich/raw/github_com_judofyr_spice.json](../../../data/wave11/enrich/raw/github_com_judofyr_spice.json) (enrichment confidence 0.8)

</details>
