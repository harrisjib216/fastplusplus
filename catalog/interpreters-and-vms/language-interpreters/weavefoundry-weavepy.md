# WeavePy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Experimental Rust Python 3.14 interpreter with a Cranelift JIT; about 2x CPython 3.14.8 on its own fixtures.

| | |
|---|---|
| **Beats** | CPython 3.14.8 |
| **Claimed result** | README (i9-9980HK, CPython 3.14.8 from PATH): geomean 0.50x CPython time over 21 of 24 fixtures (report.rs drops deque_ops, datetime_ops and pickle_bench from the CPython geomean); all 24 rows give 0.53x and about 0.70-0.71x without the sumvm, jitloop and nested_loops micro-loops (derived from page data). The committed macOS-aarch64 baseline of 2026-09-07 showed 2.75x CPython's time. |
| **Workload** | 24 in-repo Python benchmark fixtures (deltablue, richards, nbody, fannkuch, fib, spectral_norm, json_bench, pickle_bench, pidigits, etc.) plus a startup fixture, run by the weavepy-bench gate; per-fixture median of the fixture's own timer, interleaved with CPython on the same machine. |
| **Metric** | throughput |
| **Hardware** | macOS x86-64 development host, Intel Core i9-9980HK |
| **Compiler and flags** | Release profile in Cargo.toml (opt-level 3, lto = fat, codegen-units 1); the parity doc says only 'release build', so whether tools/pgo_build.py (-Cprofile-generate/-Cprofile-use, trained on the benchmark fixtures at the harness work sizes plus regrtest and an import sweep) was used for the 0.50 run is not stated (PR #82's 0.592 run was PGO). Rust version not stated (rust-toolchain.toml pins 'stable'); CPython 3.14.8 source and build flags not stated. JIT on by default. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/weavefoundry/weavepy) · [benchmark](https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-CPYTHON-PARITY.md) |

## Verdict

The project's own bench gate on one Intel Core i9-9980HK macOS laptop ran a release build of WeavePy (PR #83 does not mention PGO) interleaved with CPython 3.14.8 from PATH. Per-fixture medians gave 0.50 of CPython's time as a geometric mean over 21 fixtures (0.53 over all 24 table rows), from 0.05 on sumvm to 3.03 on deltablue. The Rust version and CPython build flags are not stated.

## Use it when

- CPU-bound pure-Python loops over ints and floats (sumvm, nested_loops, jitloop ran in 0.05-0.08 of CPython 3.14.8's time; spectral_norm 0.20; fib 0.36).
- Experimenting with a faster CPython-compatible runtime on code that does not depend on CPython object identity or obscure C-API corners.
- Research into tiered JITs for Python: the repo keeps RFCs, per-pass performance reports and raw census data, and a Cranelift tier-2 design you can read.
- Workloads where per-process startup matters slightly: the parity run measured 19.4 ms vs CPython's 24.5 ms for the startup fixture (x86-64 host).

## Skip it when

- Class-heavy OO code like DeltaBlue: 3.03x CPython's time; class-attribute reads through an instance cost about 357 instructions vs CPython's 36, and isinstance about 1,635 vs 271.
- Memory-constrained or import-heavy processes: after importing logging or asyncio, peak RSS is 2-2.5x CPython's, and imports retire 1.3-1.8x CPython's instructions.
- Production use: single author, 3 stars, 0 open issues, no releases or crates.io package; performance moved from 2.75x slower than CPython (committed macOS-aarch64 baseline, early September) to 0.50x in four weeks of large PRs.
- Code relying on CPython object identity of numbers: the unboxed numeric model makes test_marshal's id()-based new-object checks unsatisfiable (documented divergence).
- Generator-heavy and dict-heavy code where it is at or behind parity (generators 1.10x, dict_ops 0.92-1.06x of CPython's time).

## How it is fast

Tiered execution: a bytecode interpreter with specialization and call-shape inline caches, a Cranelift-backed tier-2 JIT on by default (typed scalar, object, dict, string and slots lanes with guards and deopt back to exact interpreter frames, native-to-native calls, OSR at loop back edges), and since PR #83 a baseline 'frame compiler' for loops that tier 2 declines. Native Rust implementations replace pure-Python stdlib paths (deque, datetime, pickle, regex, map/filter), small ints and floats are unboxed, and tracebacks are built lazily. The biggest wins are integer and float loop kernels that compile entirely to native code.

## Compared with alternatives

Pick PyPy for a mature JIT that is far faster on loops and stable today. Codon, mypyc and Cython compile typed subsets for larger gains but are not drop-in. WeavePy is only worth a look if you need CPython 3.14 semantics and C-API wheels in a JIT runtime and accept experimental status; the CPython tail-calling interpreter is the conservative 3-5% option.

## Integration

| | |
|---|---|
| **Form** | built binary (Cargo workspace; the weavepy crate is embeddable but unpublished) |
| **Dependencies** | Rust toolchain; Cranelift 0.132 (JIT), rustls (ssl), rusqlite (sqlite3), vendored expat; tools/pgo_build.py needs the llvm-tools rustup component |
| **Minimum toolchain** | Rust 1.93 (workspace rust-version, set by Cranelift 0.132); rust-toolchain.toml tracks stable |
| **Platforms** | Linux, macOS x86-64 and ARM64, Windows (CI lanes on all three); benchmarks only on macOS |
| **Thread safety** | GIL by default with eval-breaker hand-off from JIT code; a free-threaded lane exists (PR #75) and PEP 684/734 sub-interpreters are supported |
| **Drop-in for the baseline** | partial: argv-compatible `python` replacement that the README says passes 546 of 550 CPython regrtest labels and 40 ecosystem rows (pandas, Django, FastAPI), but the parity report lists test_capi, test_genexps, test_tempfile and test_utf8_mode failing on the dev host, plus a documented id() divergence for numbers |

## Gotchas

- Harness flaw: the headline 0.50 geomean is not over 24 fixtures as the doc states. crates/weavepy-bench/src/report.rs drops the three census fixtures (deque_ops, datetime_ops, pickle_bench) from the CPython geomean, so 0.50 covers 21 fixtures. The 0.75 vs main uses all 24 (base_geomean has no filter). Over all 24 rows of the doc's table the CPython ratio is 0.53, derived from page data.
- The geomean leans on three JIT loop kernels (sumvm, jitloop, nested_loops at 0.05-0.08). Without them the other rows give about 0.70-0.71 of CPython's time (derived from page data).
- Fixtures discard bench(n)'s return value, and the gate never checks outputs. Per-iteration times (about 2 ns for sumvm's loop) are consistent with native loops, not dead-code elimination, but correctness rests on the separate test suites.
- Each sample is one bench(n) call in a fresh process (5 samples plus 1 discarded warm-up), so JIT compile time is inside the timed region. CPython is whatever `python3.14` is on PATH. An earlier pass on an Intel macOS host used CPython 3.14.5 built with PGO, LTO and the tail-call interpreter; the parity doc does not say how 3.14.8 was built.

## Known shortcomings

- Downgraded A to C: the geomean of 0.50x CPython 3.14.8 time is confirmed on the page, but whether the build was PGO or plain release, the rustc version and the CPython provenance are unstated, PGO trains on the bench fixtures, the README's earlier committed baselines said 2.85x slower than CPython, one laptop (i9-9980HK), 3 stars. Rust.
- Enricher: report.rs drops the census fixtures deque_ops, datetime_ops and pickle_bench from the CPython geomean, so the 0.50 covers 21 fixtures rather than 24 (all 24 rows give 0.53, derived; about 0.70-0.71 without sumvm, jitloop and nested_loops); the committed macOS-aarch64 baseline of 2026-09-07 showed 2.75x CPython's time, so the result is new and swings fast; fixture outputs are unchecked, PR #83 never mentions PGO, the parity doc says release build, and CPython is python3.14 from PATH with the build unstated. Unpublished on crates.io, MSRV 1.93.

## Caveats and trade-offs

Own harness and fixtures on one development laptop (macOS x86-64, i9-9980HK); the CPython 3.14.8 build and its flags are not stated, and neither are the Rust version or whether the measured binary was PGO. The PGO script trains on the very benchmark fixtures at the exact work sizes used for timing, so PGO numbers are fixture-tuned. Fixture timers discard the computed result, so the harness does not check outputs (correctness rests on separate test suites). The README's per-wave history still lists committed baselines of 2.85x CPython's time (slower) on a macOS-aarch64 host, and the September PERFORMANCE.md showed process startup slower than CPython on ARM64 (32.27 ms vs 22.08 ms), so the 0.50 geomean is new (PR #83, 2026-10-05), from a different host, and not reproduced elsewhere; the A/B gates on Linux, macOS ARM64 and Windows compare against main, not CPython. The geomean is dominated by JIT-friendly loop kernels (sumvm, jitloop, nested_loops at 0.05-0.08). Peak memory up to 2-2.5x CPython's. Very new project: 80 commits, single author, 3 stars. [retier] PGO or plain release unstated (PR #83 never mentions PGO; the parity doc says release build), rustc version and CPython build unstated, fixture outputs unchecked, one laptop, 3 stars, unpublished on crates.io (MSRV 1.93); the result swung from 2.75x slower to 0.5x within a month. Rust.

Python interpreter written in Rust aiming at drop-in CPython 3.14 compatibility, but compatibility is still partial (README tracks conformance against CPython's own test suite); the report says importing large stdlib modules still costs about 2x CPython and peak memory after those imports is about 2x. Needs a Rust toolchain; native JIT tiers.

## Maintenance

Very active (daily large PRs by one author, last commit 2026-10-05), dual MIT/Apache-2.0, unpublished 0.0.0 workspace. Its performance claims are four weeks old and swing fast between reports, so treat it as an experiment, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** docs/PERFORMANCE-CPYTHON-PARITY.md gives first-party per-fixture medians against CPython 3.14.8 from the project's own bench gate (crates/weavepy-bench, fixtures in crates/weavepy-bench/fixtures) on one Intel Core i9-9980HK laptop, but it does not state whether the WeavePy binary was the plain release or the PGO build, the Rust version (toolchain is unpinned 'stable'), or how CPython 3.14.8 was obtained or built (PR #83 description: not stated either). Partial methodology on own harness is C.
- **Verifier notes:** Numbers are on the page and match PR #83; downgraded A to C because the run's build mode (PGO or not), Rust version and CPython provenance are unstated, PGO training uses the benchmark fixtures themselves, and earlier committed baselines in the README showed WeavePy 2.85x slower than CPython. Metadata checked on github.com: Apache-2.0 and MIT license files (dual), 3 stars, 0 forks, not a fork or archived, last commit 2026-10-05 (active). 'Work-in-progress branch report' wording in the record is slightly off: the doc says 'This branch' but was merged into main via PR #83.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-CPYTHON-PARITY.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/README.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/tools/pgo_build.py>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/fixtures.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/fixtures/sumvm.py>
  - <https://github.com/weavefoundry/weavepy>
  - <https://github.com/weavefoundry/weavepy/commits>
  - <https://github.com/weavefoundry/weavepy/pull/82>
  - <https://github.com/weavefoundry/weavepy/pull/83>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/README.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-CPYTHON-PARITY.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-EXECUTION.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-JSON.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-RUNTIME-METADATA.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/docs/PERFORMANCE-DISPATCH-MEMORY.md>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/tools/pgo_build.py>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/fixtures.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/main.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/report.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/runner.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/src/stats.rs>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/fixtures/sumvm.py>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/fixtures/jitloop.py>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/fixtures/nested_loops.py>
  - <https://raw.githubusercontent.com/weavefoundry/weavepy/HEAD/crates/weavepy-bench/baselines/bench-macos-aarch64.json>
  - <https://github.com/weavefoundry/weavepy/tree/main/crates/weavepy-bench/src>
  - <https://github.com/weavefoundry/weavepy/tree/main/crates/weavepy-bench/baselines>
  - <https://github.com/weavefoundry/weavepy/commits/main>
  - <https://github.com/weavefoundry/weavepy/issues?q=is%3Aissue>
  - <https://github.com/weavefoundry/weavepy/pull/83>
  - <https://crates.io/api/v1/crates/weavepy>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/weavefoundry/weavepy`) · [data/wave12/enrich/raw/github_com_weavefoundry_weavepy.json](../../../data/wave12/enrich/raw/github_com_weavefoundry_weavepy.json) (enrichment confidence 0.65)

</details>
