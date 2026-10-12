# libcr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟡 stale

> Stackless, macro-based C++17 coroutines and protothreads with 1:N and M:N schedulers; 3 ns switches versus 2.5 us kernel thread handoffs.

| | |
|---|---|
| **Beats** | kernel (OS thread) task switches |
| **Claimed result** | thread-unsafe coroutine switch 335 MHz (3 ns) vs kernel task switch about 400 kHz (2.5 us); README states around 837.5 times faster than kernel task switches; thread-safe 80 MHz (12 ns) single thread, 166 MHz (6 ns) across 12 threads |
| **Workload** | Coroutine and protothread task switches on an Intel Core i7-8700 3.20GHz: thread-unsafe, thread-safe single thread, thread-safe across 12 CPU threads |
| **Metric** | latency |
| **Hardware** | Intel Core i7-8700 @ 3.20GHz |
| **Compiler and flags** | release mode (per README); compiler and flags not stated |
| **Adoption** | 5 stars |
| **Last commit** | 2025-04-09 |
| **Links** | [repository](https://github.com/sm2coin/libcr) · [benchmark](https://github.com/sm2coin/libcr) |

## Verdict

The README reports, on an Intel Core i7-8700 in release mode, 335 MHz (3 ns) per thread-unsafe coroutine switch, 80 MHz (12 ns) thread-safe in one thread and 166 MHz (6 ns) thread-safe across 12 threads, against about 400 kHz (2.5 us) for kernel thread synchronisation handoffs (about 837.5x). The coroutine numbers come from the companion repo sm2coin/libcr-test (yield loops over N coroutines, -O3 -mtune=native in release, compiler version not stated), but that tool contains no kernel-thread benchmark, so the 2.5 us baseline has no published code; no comparison with Boost.Context, libco or other coroutine libraries is given.

## Use it when

- Very many small cooperative tasks (state machines, protocol handlers) on memory-limited Linux boards where a 64 KiB+ stack per fiber is unaffordable.
- Single-threaded event loops where switch cost dominates and the GCC/Clang computed-goto requirement is acceptable.
- M:N designs that need coroutines to migrate between worker threads, using the cr::mt or HybridScheduler variants.
- AGPL-compatible projects (or internal research code) that want a compact, allocation-free scheduler to study or vendor.

## Skip it when

- Closed-source or permissively licensed products: AGPL-3.0 copyleft also covers network use.
- MSVC builds: specific.hpp hits '#error "Compiler not supported!"' without __GNUC__.
- Code that needs to yield from deep inside ordinary (non-coroutine) call chains or call third-party blocking code: it is stackless, so every suspendable frame must itself be a libcr coroutine.
- New C++20 code: native stackless coroutines give similar memory benefits without the macro syntax and the restriction on locals across suspension points.
- Teams that need a maintained dependency: 81 commits, 5 stars, a 2020-2025 gap in commits, and the README warns that breaking changes are still made.

## How it is fast

Each coroutine stores only a resume address: suspension points save a label address with GCC's labels-as-values (&&label) and resume with a computed goto (goto \*ip), so a switch is an indirect jump with no stack swap or register save. Nothing is allocated dynamically and no stack is reserved, so a coroutine is 56 bytes on 64-bit (8 bytes for a bare protothread) and nested coroutines can be embedded in, or unioned inside, the parent's state. The thread-unsafe sync scheduler avoids atomics entirely, which is why it is about 4x faster than the mt variant in a single thread.

## Compared with alternatives

Pick libcr over stackful libraries such as libaco, libco-style libcopp or libdill when per-task memory matters more than the convenience of yielding from arbitrary calls; minicoro or libaco are simpler to adopt and license-friendlier when stacks are affordable, and CO2 is the closer stackless alternative with a published comparison against Boost.Coroutine2.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | sm2coin timer submodule (depend/timer), pulled by CMake running git submodule init/update; pthread for the mt parts |
| **Minimum toolchain** | C++17, GCC or Clang (labels-as-values extension); CMake 2.6+ |
| **Platforms** | any GCC-supported target (no OS-specific code per README); MSVC unsupported |
| **Thread safety** | Two families: cr::sync types are thread-unsafe (fastest); cr::mt types are thread-safe and let coroutines move between threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Native local variables do not survive CR_YIELD/CR_AWAIT/CR_CALL; anything live across a suspension must be declared in CR_STATE.
- Exceptions are a custom error/no-error flag (CR_THROW), not C++ exceptions; CR_FINALLY must not contain return, throw, yield or await.
- The library's CMakeLists hard-codes -Werror and -g, and release mode (-DLIBCR_RELEASE=ON) adds -O2 -mtune=native; the 2025-04-09 commit fixed a build break on a newer compiler, so expect warnings-as-errors breakage on new toolchains.
- CMake runs git submodule commands at configure time and copies headers into the source tree's include/ directory.

## Known shortcomings

- The coroutine numbers come from sm2coin/libcr-test (-O3 -mtune=native in release, compiler version not stated); libcr-test has no kernel-thread benchmark, so the 2.5 us baseline has no published code. GCC and Clang only (specific.hpp has an #error without __GNUC__). AGPL-3.0.

## Caveats and trade-offs

Baseline is kernel thread switching, not Boost.Context, Boost.Coroutine or libco, so it is not a comparison against the listed incumbents; compiler and flags not stated; first-party README numbers; very small project.

Stackless protothread-style coroutines for small devices (56 bytes per coroutine on 64-bit); AGPL-3.0 license is a strong copyleft constraint.

## Maintenance

Stale (two small commits in April 2025 after a gap since December 2020), AGPL-3.0 and small enough to vendor, but GCC/Clang only and still described by its author as evolving with breaking changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README states 335 MHz (3 ns) thread-unsafe switch vs about 400 kHz (2.5 us) kernel task switch on an i7-8700, 'release mode'; first-party, no benchmark code path, compiler or flags named, so C.
- **Verifier notes:** Last commit 2025-04-09 is about 18 months before today, so stale rather than active. Baseline is OS thread switching, a weak incumbent; kept since it is a recognizable baseline.
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/sm2coin/libcr>
  - <https://github.com/sm2coin/libcr/commits>
- **Sources the enricher read:**
  - <https://github.com/sm2coin/libcr>
  - <https://github.com/sm2coin/libcr/commits>
  - <https://github.com/sm2coin/libcr/tree/master/src>
  - <https://raw.githubusercontent.com/sm2coin/libcr/HEAD/README.md>
  - <https://raw.githubusercontent.com/sm2coin/libcr/HEAD/docs/intro.md>
  - <https://raw.githubusercontent.com/sm2coin/libcr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sm2coin/libcr/HEAD/src/specific.hpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr/HEAD/src/Coroutine.hpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/README.md>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/CMakeLists.txt>
  - <https://github.com/sm2coin/libcr-test/tree/master/src>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/src/test.cpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/src/Benchmark.hpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/src/bench/Scheduler.hpp>
  - <https://raw.githubusercontent.com/sm2coin/libcr-test/HEAD/src/bench/MtScheduler.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/sm2coin/libcr`) · [data/wave11/enrich/raw/github_com_sm2coin_libcr.json](../../../data/wave11/enrich/raw/github_com_sm2coin_libcr.json) (enrichment confidence 0.65)

</details>
