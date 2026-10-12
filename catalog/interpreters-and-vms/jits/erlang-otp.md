# BeamAsm (Erlang/OTP JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (asmjit-based JIT inside the Erlang/OTP runtime)` · `Apache-2.0` · 🟢 active

> BeamAsm: Erlang/OTP's load-time AsmJit template JIT, about 1.5x the BEAM interpreter's estone score on Erlang-heavy code.

| | |
|---|---|
| **Beats** | BEAM emulator (interpreter) without JIT, OTP 23 |
| **Claimed result** | PR description: estone score 'about 50% larger'; individual benchmarks 'from a 170% increase (pattern matching) to no change at all (huge messages)'; JSON benchmarks '30% to 130% increase (average at about 70%) in the number of iterations per second'; RabbitMQ handles 30% to 50% more messages per second. |
| **Workload** | Erlang/OTP workloads: the estone benchmark suite, JSON encode/decode benchmarks across Erlang and Elixir libraries, and RabbitMQ message throughput, JIT on versus off. |
| **Metric** | throughput |
| **Adoption** | 12.4k stars (erlang/otp) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/erlang/otp) · [benchmark](https://github.com/erlang/otp/pull/2745) |

## Verdict

The original BeamAsm PR (#2745, merged 2020-09-22 for OTP 24) compared the JIT with the BEAM interpreter on the same pre-OTP-24 master: estone score about 50% higher (pattern matching +170%, huge messages +0%), Poison/Jason JSON benchmarks +30% to +130% iterations per second (average about 70%), RabbitMQ +30-50% messages per second, with no hardware, compiler or run count stated. An independent third-party CI table (sntran/BEAM.com docs/BENCHMARKS.md, OTP 29 built with Cosmopolitan libc, unnamed shared CI runners, best of 3) shows interpreter-to-JIT fib(32) 70 to 30 ms and lists 249 to 116 ms on Linux x86-64, fib 139 to 12 ms on Linux aarch64, messages unchanged (111 to 117 ms) and startup slower (142 to 222 ms).

## Use it when

- Long-running Erlang or Elixir services whose time goes into Erlang code (pattern matching, function calls, list and binary processing, JSON encoding/decoding): the PR reports 30-130% more JSON iterations per second and 30-50% more RabbitMQ messages per second.
- AArch64 servers and Apple silicon, where the interpreter is comparatively slow: an independent CI table (BEAM.com) shows fib(32) 139 ms to 12 ms and lists 411 ms to 104 ms on Linux aarch64.
- Any OTP 24+ deployment on x86-64 or AArch64 that wants the free speedup; it is on by default and needs no code changes.
- Profiling production Erlang with Linux perf: +JPperf true exports JIT symbols and frame pointers so perf report and flame graphs show Erlang functions.

## Skip it when

- Short-lived escripts and command-line tools: every module is compiled at load time, so startup gets slower (BEAM.com measured +40 to +90 ms, +35% to +65%, on every platform) and the design doc warns tiny scripts can be slower than the interpreter.
- Workloads dominated by message passing, ETS, ports, NIFs or C BIFs (crypto, huge messages): the estone 'huge messages' micro showed no change and BEAM.com's messages, crypto and SQLite rows stayed within noise.
- CPU-bound numeric code where a tracing or optimising JIT is needed: BeamAsm has no profiling tier, inlining across instructions or register allocation beyond the Erlang compiler's, so expect 'no difference to up to four times as fast', not LuaJIT-style gains.
- 32-bit targets and architectures other than x86-64 and AArch64 (configure falls back to the interpreter), x86-64 macOS (JIT disabled by default since Sonoma because dual-mapped memory triggers system popups) and strict W^X environments without the needed mapping support.
- Code that relied on HiPE native compilation: the BeamAsm loader removed HiPE support, so HiPE-compiled code cannot run from OTP 24 on.

## How it is fast

It is a template (load-time) JIT: each BEAM instruction is emitted by a C++ function (instr_\*.cpp) as a few native instructions, which removes the interpreter's dispatch overhead and lets every instruction be specialised on its actual arguments and on type information the Erlang compiler records in the .beam file (always_small and similar checks in beam_jit_common.hpp skip tag tests). Hot process state lives in statically allocated callee-saved registers (scheduler registers, current process, remaining reductions, heap pointer on x86-64), and on x86-64 Erlang code can run on the native stack using call/ret. Code size is kept to about 10% above the interpreter's by jumping to shared global fragments (context switch, error handling, breakpoints) instead of inlining them; there is hardly any cross-instruction optimisation, no profiling tier and no recompilation.

## Compared with alternatives

BeamAsm, like the CPython copy-and-patch JIT and the PHP opcache JIT, is a JIT measured against its own runtime's interpreter; it reports larger general gains than CPython's 7-8% geomean but smaller numeric gains than PHP JIT's loop benchmarks, and for BEAM languages it is the only choice. If you are building your own template JIT in C++, use the AsmJit sibling directly and read BeamAsm's design doc as a worked example of shared fragments and fixed register assignment.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond the Erlang/OTP build; AsmJit is vendored in erts/emulator/asmjit |
| **Minimum toolchain** | C++17 compiler (configure disables the JIT, or errors with --enable-jit, if C++17 is missing) plus the usual gcc or clang C toolchain; OTP 24 or later |
| **Platforms** | x86-64 (Linux, Windows, FreeBSD, NetBSD, OpenBSD without native stack; macOS x86-64 only with explicit --enable-jit) and AArch64 (Linux when DC CVAU/IC IVAU/ISB are available, macOS, Windows); everything else runs the interpreter |
| **Thread safety** | Generated code is shared by all schedulers; code pages are mapped twice (executable and writable views) so breakpoints, tracing and NIF loading patch code without W+X pages, coordinated through thread progress |
| **Drop-in for the baseline** | yes |

## Gotchas

- Harness: the PR's headline 'estone about 50% larger' is a single weighted score from estone_SUITE.erl, where each micro contributes weight^2 x 31,000,000 / microseconds, so the total depends on the hand-picked weights (medium messages 14, port I/O 12, small messages 10) and on one pass of each micro; the PR names no CPU, OS, compiler, run count or variance, and the JSON (Poison and Jason bench suites) and RabbitMQ runs have no published scripts or settings.
- A user report (issue #5437, CentOS 7.5, 4 cores) measured a non-tail-recursive function 5.7x slower on OTP 24 with the JIT than on OTP 22 (548,853 vs 95,996 microseconds average) while the tail-recursive variant was 1.3x faster; it was closed as an enhancement with no diagnosis visible on the page, and the comparison mixes OTP versions, not just JIT versus interpreter.
- Loaded code is about 10% larger than under the interpreter, and module load time scales with emitted code size, so systems that hot-load many modules pay more at load time.
- W^X-hardened systems need special handling: NetBSD with PaX MPROTECT failed to build the JIT in OTP 25.2 (issue #6909, addressed by PR #6933 using mremap); OpenBSD cannot use the native stack because of its MAP_STACK checks.

## Known shortcomings

- PR #2745 numbers are against BEAM's own interpreter with no CPU, compiler or flags; BeamAsm.md itself says 'no difference to up to four times' and short scripts can be slower. Off-baseline (not PyPy, LuaJIT, V8 or HotSpot); Erlang/C runtime, not C++.
- Enricher: the PR #2745 'estone +50%' is one weighted score (weight squared times 31e6 over microseconds per micro-benchmark), single pass, no CPU, compiler or run count; issue #5437 reports non-tail recursion 5.7x slower on the OTP 24 JIT than the OTP 22 interpreter (548,853 vs 95,996 us) with versions differing. Independent sntran/BEAM.com docs/BENCHMARKS.md (OTP 29 under Cosmopolitan on CI runners) shows fib(32) 70 to 30 ms on Linux x86_64 and 139 to 12 ms on aarch64 with messaging unchanged and startup 35-65% slower; modified runtime and unnamed CPU, so not a B retier.

## Caveats and trade-offs

Numbers are from the description of the original BeamAsm merge PR (merged 2020-09-22, shipped in OTP 24); hardware, compiler and flags are not stated, and the exact runs are not reproducible from the page. The project's own BeamAsm design doc (erts/emulator/internal_doc/BeamAsm.md) says to expect 'anything from no difference to up to four times as fast' and that very short-lived small scripts can be slower than the interpreter. Baseline is the project's own interpreter (still buildable with --disable-jit or FLAVOR=emu), not one of PyPy, LuaJIT, V8, HotSpot. JIT only on x86-64 and AArch64 (asmjit). The entry is the JIT inside the much larger Erlang/OTP repository (code in erts/emulator/beam/jit/).

Load-time template JIT (no tracing or optimising tier), so gains are modest compared with LuaJIT-style tracing JITs; needs a C++17 compiler to build; communication-bound code gains little.

## Maintenance

Actively developed by the Ericsson OTP team inside erlang/otp (12.4k stars, last commit 2026-10-06, Apache-2.0) and on by default in every OTP 24+ build on supported targets; it is usable by anyone running Erlang or Elixir, but it is not a standalone library, so for reuse in another C++ project take AsmJit and the design ideas, not the code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #2745 (merged 2020-09-22 by garazdawi) states the estone, JSON and RabbitMQ gains of the JIT over the BEAM interpreter verbatim as in the record, but names no CPU, compiler or flags and links no run scripts, so these are first-party numbers without methodology.
- **Verifier notes:** Claim matches PR #2745 exactly; off-baseline for the jits category (own interpreter, not PyPy/LuaJIT/V8/HotSpot) and no methodology. Metadata checked on github.com: Apache-2.0, 12.4k stars, not archived, last commit 2026-10-06 on master.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/erlang/otp/pull/2745>
  - <https://github.com/erlang/otp>
  - <https://github.com/erlang/otp/commits>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/emulator/internal_doc/BeamAsm.md>
- **Sources the enricher read:**
  - <https://github.com/erlang/otp/pull/2745>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/emulator/internal_doc/BeamAsm.md>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/emulator/test/estone_SUITE.erl>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/HOWTO/INSTALL.md>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/configure.ac>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/emulator/beam/jit/beam_jit_common.hpp>
  - <https://raw.githubusercontent.com/erlang/otp/HEAD/erts/emulator/asmjit/asmjit.h>
  - <https://github.com/erlang/otp/issues?q=is%3Aissue%20jit%20slower>
  - <https://github.com/erlang/otp/issues/5437>
  - <https://github.com/erlang/otp/issues/6909>
  - <https://github.com/sntran/BEAM.com/pull/12>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/README.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/tests/bench/bench.erl>
  - https://www.erlang-solutions.com/blog/performance-testing-the-jit-compiler-for-the-beam-vm/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/erlang/otp`) · [data/wave12/enrich/raw/github_com_erlang_otp.json](../../../data/wave12/enrich/raw/github_com_erlang_otp.json) (enrichment confidence 0.75)

</details>
