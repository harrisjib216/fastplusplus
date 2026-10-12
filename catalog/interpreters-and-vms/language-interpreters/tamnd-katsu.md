# katsu

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pre-alpha JavaScript runtime in Rust (bytecode interpreter today) that starts a hello world about 16x faster than Node and 3x faster than Bun.

| | |
|---|---|
| **Beats** | Node.js 26.8.1 (V8); Bun 1.4.0 and Deno 2.9.6 are also measured |
| **Claimed result** | Cold start (spec 15.5.1, katsu 0.0.5): katsu 1.55 ms vs Node 26.8.1 24.63 ms (page: 15.9x faster), Bun 1.4.0 4.97 ms (3.2x), Deno 2.9.6 12.49 ms; peak RSS 2.44 MiB vs 48.14 MiB for Node (19.7x) and 10.92 MiB for Bun (4.5x); binary 1.7 MiB vs 139.0 MiB for Node (80x). The lead holds in later katsu-bench runs (0.1.8: 1.68 ms vs Bun 5.67 ms, 3.37x ahead). Compute is a loss: katsu README fib(35) 875 ms vs Node 53.4 ms, Bun 34.3 ms and Deno 56.5 ms (16.4x slower than Node, 25.5x slower than Bun, 0.1.6 baseline); katsu-bench shows fib 19-25x behind Bun across 0.1.3-0.1.8. |
| **Workload** | Wall-clock cold start (spawn to exit) of a one-line console.log hello world, 25 runs per runtime, median and IQR (spec 15.5.1 says no warmup for startup; the katsu-bench README says 25 runs after 3 discarded), plus peak RSS from a separate /usr/bin/time -l pass and distribution size (executable plus non-system shared libraries). |
| **Metric** | startup |
| **Hardware** | Apple M4 (10 cores, 24 GB), macOS 15.8 (Darwin 15.8), a laptop with turbo and frequency scaling not pinned (numbers labelled 'indicative' by spec 15.5) |
| **Compiler and flags** | rustc 1.98.0 pinned in rust-toolchain.toml (also at tag v0.0.5); cargo --release with Cargo.toml [profile.release] opt-level=3, lto="fat", codegen-units=1, panic="abort", strip="symbols"; 0.0.5 measured from a local release build, 0.1.2 onwards from the published tarballs; Node 26.8.1, Bun 1.4.0 and Deno 2.9.6 are their official release binaries |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/tamnd/katsu) · [benchmark](https://raw.githubusercontent.com/tamnd/katsu/HEAD/spec/15-benchmarks.md) |

## Verdict

With katsu-bench on an Apple M4 laptop (macOS 15.8, turbo not pinned, 'indicative'), katsu 0.0.5 built with rustc 1.98.0 and fat LTO took a median 1.55 ms (IQR 0.09) to spawn, print one console.log line and exit, against official Bun 1.4.0 at 4.97 ms, Deno 2.9.6 at 12.49 ms and Node 26.8.1 at 24.63 ms (25 back-to-back runs each), with a 1.66 MiB distribution against Node's 139.05 MiB. Later release tarballs hold the lead (0.1.8: 1.68 ms vs Bun 5.67 ms), while the only compute workload katsu can run, fib, is about 23x slower than Bun.

## Use it when

- Studying how a Rust JavaScript engine is being designed: the spec/ directory (18 documents) and the per-release benchmark write-ups are unusually candid about costs, losses and noise.
- Tracking the cold-start and footprint floor of a minimal JS runtime: about 1.5-1.7 ms spawn-to-exit and 1.7 MiB on disk on an Apple M4, against Bun at about 5 ms and Node at about 25 ms.
- Reusing the companion harness tamnd/katsu-bench (MIT OR Apache-2.0) to measure cold start, idle RSS, distribution size and checksummed compute workloads across Node, Bun and Deno; it is more careful than most runtime shoot-outs (wait4 peak RSS, IQR-overlap 'too close to call' verdicts, load average recorded).

## Skip it when

- Any real program: no module system, event loop, filesystem, `process`, `Buffer` or npm compatibility; most of test262 fails (12.31% passes at 0.1.8).
- Compute: fib(35) is 16-25x slower than Node and Bun (875 ms vs 53.4 ms Node and 34.3 ms Bun at 0.1.6; 781.89 ms vs Bun 33.43 ms at 0.1.8), because there is no JIT yet.
- Anything that allocates in a loop: there is no garbage collector, so the heap (a bump allocator over a 4 GiB cage) fills and the process dies (issue #60); the katsu-bench `strings` workload dies this way.
- Code that depends on primitive property reads: `'abc'.length` returns undefined rather than 3 without throwing (issue #58, open), a silent wrong answer.
- Serverless or CLI cold-start wins on real code: the measured lead is on a one-line hello world and the author expects it to shrink as the runtime gains features (0.1.8 already paid about 0.1 ms for error constructors).

## How it is fast

The startup lead comes from doing almost nothing at startup: a 1.7 MiB Rust executable that loads no non-system shared libraries, a small realm built eagerly at launch (there is no Node bootstrap, no module resolution and no large JavaScript-implemented standard library to instantiate), an oxc-based parser and a register bytecode interpreter. The object model uses NaN-boxed values, shapes that carry the prototype and property flags, a monomorphic per-site inline cache for property reads, and a bump allocator over a 4 GiB compressed-pointer cage with no collector, which is why peak RSS stays near 2.5 MiB. The spec's realm snapshot, resolution cache, bytecode cache and copy-and-patch baseline JIT (Deegen-style, generated from the interpreter description) are planned, not built; crates/katsu-jit/src/lib.rs is a 61-line stub of enums and constants.

## Compared with alternatives

Pick katsu only to follow or study a from-scratch JS engine's startup and memory floor; for real speed over Node pick Perry (TypeScript AOT, beats Node on compute) or quickjs-jit (a working embeddable JS JIT), and note that XS shows the same 'Node startup dominates' effect on its tiny workloads.

## Integration

| | |
|---|---|
| **Form** | standalone CLI binary (GitHub release tarballs; not published on crates.io) |
| **Dependencies** | none at runtime beyond OS libraries (katsu-bench counts only the 1.66 MiB executable); building pulls oxc 0.147, tokio, regress, bumpalo and others from the workspace Cargo.toml |
| **Minimum toolchain** | Rust 1.98 stable (rust-toolchain.toml pins 1.98.0, edition 2024) |
| **Platforms** | release binaries for aarch64 and x86-64 macOS, aarch64 and x86-64 Linux (gnu), x86-64 Windows (msvc); all published numbers are from an Apple M4 |
| **Thread safety** | single-threaded interpreter; the katsu-vm crate docs say an isolate is Send but not Sync |
| **Drop-in for the baseline** | partial: `katsu run file.js` executes a one-file script that uses only the implemented subset; no Node modules, APIs or npm packages |

## Gotchas

- Filed under JITs but contains no JIT: the measured binary is a bytecode interpreter with a monomorphic inline cache, and crates/katsu-jit/src/lib.rs is a 61-line placeholder (a Tier enum, a tier-up constant and a DeoptReason enum).
- Harness detail: katsu-bench's startup axis (src/main.rs measure_axis) ignores --warmup and runs 25 back-to-back spawns per runtime, so 24 of 25 runs see a warm page cache; the 'cold start' median is effectively a warm process start for every runtime (fair across runtimes, but not a true cold start). The katsu-bench README's '25 runs after 3 discarded' applies to the compute workloads, not to startup.
- The hello-world peak RSS figures in spec 15.5.1 (katsu 2.44 MiB, Node 48.14, Bun 10.92) came from a separate manual `/usr/bin/time -l` pass that is not in the committed baseline file; results/baselines/2026-08-29-m4-macos.md has no hello-world RSS row, and its idle-memory axis cannot run katsu because katsu exits instead of idling.
- Silent wrong answers exist: `'abc'.length` is undefined (issue #58), and a `let` in a `for` head gets one binding per call rather than per iteration (README).

## Known shortcomings

- Raised C to A on the public katsu-bench harness (rustc 1.98.0 pinned, Cargo release profile flags, Apple M4), but the startup lead comes from doing less (no modules, event loop or GC; an interpreter, not a JIT yet) and fib is 16-25x slower than Node and Bun; laptop with turbo on, numbers the author labels indicative, 0 stars. Rust.
- Enricher: katsu contains no JIT (crates/katsu-jit/src/lib.rs is a 61-line stub), so the measured binary is a bytecode interpreter with inline caches; filed under language-interpreters. katsu-bench's startup axis (src/main.rs measure_axis) ignores warm-up and does 25 back-to-back spawns per runtime, a warm-page-cache start rather than a cold start (fair across runtimes); the README's '25 runs after 3 discarded' applies to compute only, and the hello-world RSS figures (2.44 vs 48.14 MiB) come from a separate manual /usr/bin/time pass. Open bugs #58 ('abc'.length undefined, silent wrong answer) and #60 (no GC, allocation loops die); not on crates.io.

## Caveats and trade-offs

The author states the lead exists 'because it does less, not because it is better'. The measured binary is an interpreter with an inline cache, not yet a JIT, and compute is 16-25x slower than Node and Bun. Numbers are the project's own, from a laptop with turbo on and are labelled 'indicative' in the spec. Included mainly as a startup and footprint claim against V8-based Node.

Pre-alpha JavaScript/TypeScript runtime in Rust that plans a three-tier engine with a copy-and-patch baseline JIT. No module system, event loop, filesystem or standard library beyond console.log at the time of measurement. 12.31% of test262 passing at v0.1.8.

## Maintenance

Active pre-alpha (0.1.8, last commit 2026-08-31, 0 stars, MIT OR Apache-2.0) with release binaries for five targets, but it is a research-stage interpreter with no GC, modules or event loop, so it is reference material rather than something to deploy; the author says the startup lead exists because it does less, not because it is better.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The harness is public (tamnd/katsu-bench src/ and workloads/, command 'katsu-bench run --runs 25', committed table results/baselines/2026-08-29-m4-macos.md). The compiler is pinned (rust-toolchain.toml channel 1.98.0, the same at tag v0.0.5), release flags are in katsu's Cargo.toml [profile.release] (opt-level 3, lto fat, codegen-units 1, panic abort), the CPU is named (Apple M4, macOS 15.8), and the rivals are named official releases (Node 26.8.1, Bun 1.4.0, Deno 2.9.6).
- **Verifier notes:** Numbers match spec/15-benchmarks.md and the katsu-bench baseline file exactly. Metadata checks out: MIT OR Apache-2.0, 0 stars, 67 commits, last commit 2026-08-31, so active. Shortcomings: by the author's own statement the startup and memory lead exists because katsu does less (no module system, event loop, process, Buffer or GC; it is an interpreter with an inline cache, not yet a JIT), compute is 16-25x slower than Node and Bun, and numbers come from a laptop with turbo on and are labelled indicative. A by the letter of the rubric (public harness, pinned compiler, flags and CPU); the orchestrator may prefer to note the feature gap prominently.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/spec/15-benchmarks.md>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/README.md>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/tamnd/katsu/v0.0.5/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/Cargo.toml>
  - <https://github.com/tamnd/katsu>
  - <https://github.com/tamnd/katsu/commits>
  - <https://github.com/tamnd/katsu-bench>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/results/baselines/2026-08-29-m4-macos.md>
- **Sources the enricher read:**
  - <https://github.com/tamnd/katsu>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/README.md>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/spec/15-benchmarks.md>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/spec/02-the-10x-goal.md>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/crates/katsu-jit/src/lib.rs>
  - <https://raw.githubusercontent.com/tamnd/katsu/HEAD/crates/katsu-vm/src/lib.rs>
  - <https://github.com/tamnd/katsu/tree/main/crates/katsu-jit/src>
  - <https://github.com/tamnd/katsu/issues>
  - <https://github.com/tamnd/katsu/releases>
  - <https://github.com/tamnd/katsu/releases/expanded_assets/v0.1.8>
  - <https://crates.io/api/v1/crates/katsu>
  - <https://crates.io/api/v1/crates/katsu-runtime>
  - <https://crates.io/api/v1/crates/katsu-vm>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/results/baselines/2026-08-29-m4-macos.md>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/Cargo.toml>
  - <https://github.com/tamnd/katsu-bench/tree/main/src>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/src/measure.rs>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/src/runtime.rs>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/src/report.rs>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/workloads/hello.js>
  - <https://raw.githubusercontent.com/tamnd/katsu-bench/HEAD/workloads/compute/fib.js>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/tamnd/katsu`) · [data/wave12/enrich/raw/github_com_tamnd_katsu.json](../../../data/wave12/enrich/raw/github_com_tamnd_katsu.json) (enrichment confidence 0.75)

</details>
