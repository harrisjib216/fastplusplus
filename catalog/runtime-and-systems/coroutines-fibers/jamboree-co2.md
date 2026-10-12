# CO2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Header-only C++14 macro emulation of N4286 stackless coroutines; resume costs about 6 ns versus 82 ns for Boost.Coroutine2.

| | |
|---|---|
| **Beats** | Boost.Coroutine2 |
| **Claimed result** | CO2 6 ns versus Boost.Coroutine2 (bench_coroutine2) 82 ns, native MSVC 5 ns (about 13.7x, derived from page data) |
| **Workload** | Generator-style yield/resume cost: CO2 stackless emulated coroutines versus Boost.Coroutine2 versus native MSVC coroutines in test/benchmark.cpp. |
| **Metric** | latency |
| **Hardware** | 4 x 3200 MHz CPU (model not stated) |
| **Compiler and flags** | VS2015 Update 3, boost 1.63.0, 64-bit release build (exact flags not stated) |
| **Adoption** | 343 stars |
| **Last commit** | 2024-01-17 |
| **Links** | [repository](https://github.com/jamboree/co2) · [benchmark](https://github.com/jamboree/co2) |

## Verdict

The README's Google Benchmark run of test/benchmark.cpp times one resume of a coroutine that suspends forever with an empty action: Boost.Coroutine2 pull_type 82 ns, CO2 6 ns, native MSVC co_await 5 ns, built with VS2015 Update 3, boost 1.63.0, 64-bit release, on an unnamed 4 x 3200 MHz CPU. That is about 13.7x versus Boost.Coroutine2 (derived from page data), but it compares a stackless switch with a stackful context switch.

## Use it when

- Maintaining an existing codebase on a pre-C++20 compiler (C++14 with Boost) that already uses CO2 for generators or async tasks.
- Generators and asynchronous continuations where every suspend point is in the coroutine body itself, not in nested calls.
- Tiny per-coroutine memory: frames hold only the declared locals plus a small awaiter buffer, versus a full stack per Boost.Coroutine2 coroutine.
- Bridging callback APIs (ASIO via the sister library act, PPL or TBB task_group) into await-style code on old toolchains.

## Skip it when

- New code: the README itself says all major compilers now support C++20 coroutines and recommends against CO2; use native co_await or the author's successor COZ (zero-allocation).
- You need to suspend from inside nested ordinary function calls (stackful semantics): only Boost.Coroutine2/Boost.Context or fiber libraries do that.
- Codebases that cannot tolerate heavy macro restrictions: locals crossing suspend points must be declared in CO2_BEG, no () initializers, auto needs CO2_AUTO, return/try/switch need macro replacements.
- Projects that need a maintained dependency: repository archived 2024-10-09.

## How it is fast

The macros turn the body into a resumable state machine: a heap frame (std::allocator by default, custom allocator via the new clause) holds the declared locals, and each suspend point is a `case __COUNTER__:` label in a switch on a stored `_co2_next` index (Duff's-device / protothread style). Resuming is one virtual run() call plus a jump through the switch, with no stack switch and no register save/restore, which is why it lands near native MSVC co_await (6 ns versus 5 ns) and far below Boost.Coroutine2's Boost.Context stack switch.

## Compared with alternatives

Pick CO2 over stackful switchers like libaco, libcopp, minicoro or Boost.Coroutine2 only when you want stackless, per-frame-allocated coroutines with TS-style await on a pre-C++20 compiler; if you are on C++20, Boost.Cobalt or plain co_await supersede it.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost (Boost.Config, Boost.Assert, Boost.Preprocessor in the core header; Boost.Thread/Optional for the adapted headers) |
| **Minimum toolchain** | C++14; benchmark run on VS2015 Update 3 with boost 1.63.0; GCC/Clang supported (statement-expression extension enables CO2_AWAIT as an expression) |
| **Platforms** | any (pure C++, no assembly) |
| **Thread safety** | not documented for coroutine objects; task scheduling across threads is shown with PPL/TBB examples, and co2::mutex/event are coroutine-level sync primitives |
| **Drop-in for the baseline** | no |

## Gotchas

- Awaits are statements, not expressions: CO2_AWAIT(something{temporaries}) lets temporaries die before resumption, unlike real co_await.
- Awaiters larger than (sizeof(pointer)+sizeof(int))\*2 bytes fall back to dynamic allocation; enlarge with CO2_TEMP_SIZE and define CO2_WARN_DYN_ALLOC to catch it.
- Exceptions thrown while initializing locals propagate directly to the caller and bypass set_exception, since initialization runs before initial_suspend.
- Benchmark compares stackless against stackful (open issue #4 says the comparison does not make sense without that context); the benchmark source names the test bench_coroutines2 while the README table prints bench_coroutine2. stack_allocator had a deallocate bug (issue #5, closed 2018).

## Known shortcomings

- Header-only C++14 plus Boost macro state machine (switch on __COUNTER__ labels, virtual run()): stackless against stackful Boost.Coroutine2, so the comparison is not like for like (open issue 4 says as much). README says it is obsolete and points to the successor COZ (31 stars, no numbers). README table says bench_coroutine2 but the code says bench_coroutines2; a stack_allocator deallocate bug (5) was closed in 2018.

## Caveats and trade-offs

Stackless emulated coroutines versus Boost.Coroutine2's stackful switch, so not like for like; CPU model not stated; VS2015-era numbers; repository archived 2024-10-09 (last commit 2024-01-17, 'Announce COZ', pointing to a successor project). License is BSL-1.0 per README; no LICENSE_1_0.txt found at repo root via raw fetch.

Stackless (macro-based) emulation, not stackful: no yielding from nested calls; needs Boost; superseded by the author's COZ; archived 2024-10-09.

## Maintenance

Archived 2024-10-09 and self-declared obsolete in favour of C++20 coroutines and COZ, but BSL-1.0 and header-only, so existing users can keep vendoring it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section shows a Google Benchmark sample run of test/benchmark.cpp (public): bench_coroutine2 82 ns, bench_co2 6 ns, bench_msvc 5 ns, VS2015 Update 3, boost 1.63.0, 64-bit release; CPU only 'Run on (4 X 3200 MHz CPU s)', no model and no explicit flags, so not A; first-party, so C.
- **Verifier notes:** Numbers match the README exactly; 13.7x ratio is correctly marked derived. Author's successor COZ may be worth a seed lead.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/jamboree/co2>
  - <https://raw.githubusercontent.com/jamboree/co2/HEAD/README.md>
  - <https://raw.githubusercontent.com/jamboree/co2/HEAD/test/benchmark.cpp>
  - <https://github.com/jamboree/co2/commits>
- **Sources the enricher read:**
  - <https://github.com/jamboree/co2>
  - <https://raw.githubusercontent.com/jamboree/co2/HEAD/README.md>
  - <https://raw.githubusercontent.com/jamboree/co2/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/jamboree/co2/HEAD/include/co2/coroutine.hpp>
  - <https://github.com/jamboree/co2/issues?q=is%3Aissue>
  - <https://github.com/jamboree/co2/issues/4>
  - <https://github.com/jamboree/co2/issues/5>
  - <https://github.com/jamboree/coz>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jamboree/co2`) · [data/wave11/enrich/raw/github_com_jamboree_co2.json](../../../data/wave11/enrich/raw/github_com_jamboree_co2.json) (enrichment confidence 0.8)

</details>
