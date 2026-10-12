# XS (xs-lang)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> New scripting language with VM and register-allocating x86-64/arm64 JIT; about 2x CPython on recursive fib, far behind V8.

| | |
|---|---|
| **Beats** | CPython 3.13 and Node 20 (V8), measured in the same README table; the Node column is dominated by Node's own 57 ms process startup |
| **Claimed result** | README table (wall time including process startup, best of three): fib(30) XS --jit 31 ms vs Node 20 62 ms vs Python 3.13 71 ms (--vm 180 ms, --interp 950 ms); hello world startup XS 3 ms vs Node 57 ms vs Python 15 ms. Subtracting each runtime's hello-world startup, fib(30) compute is about 28 ms for XS --jit vs about 56 ms for CPython (about 2x faster) and about 5 ms for Node (XS about 5x slower than V8) (derived from page data). The committed cross-runtime run (benchmarks/results.json, 2026-05-03, best of 5) shows fib XS --jit 0.038 s vs python3 0.083 s vs node 0.117 s vs go 0.005 s, and mandelbrot XS --jit 0.577 s vs python3 0.338 s vs node 0.112 s, i.e. XS slower than both CPython and Node on mandelbrot. |
| **Workload** | README: two programs run cold from disk with wall time including process startup: hello world (startup) and recursive fib(30); XS shown in --interp, --vm and --jit modes; best of three runs. The repo's benchmarks/run.sh adds sort, mandelbrot, nbody, json, strings, hash and startup ports in XS, Python, JavaScript and Go. |
| **Metric** | throughput |
| **Hardware** | Linux x86-64, AMD Ryzen 7 (exact model not stated) |
| **Compiler and flags** | Not stated for the README table; Makefile default build is gcc -O2 -std=c11, make release is -O3 -flto -DNDEBUG; which build produced the table is not said |
| **Adoption** | 129 stars |
| **Last commit** | 2026-05-20 |
| **Links** | [repository](https://github.com/xs-lang0/xs) · [benchmark](https://github.com/xs-lang0/xs) |

## Verdict

On an unspecified 'AMD Ryzen 7' Linux x86-64 box (build flags and compiler not stated), best of three cold runs with wall time including process start-up, XS --jit ran fib(30) in 31 ms vs Node 20 at 62 ms and CPython 3.13 at 71 ms; subtracting each runtime's hello-world time leaves about 28 ms for XS vs about 56 ms for CPython (about 2x faster) and about 5 ms for Node (XS about 5x slower) (derived from page data). The repo's committed 2026-05-03 cross-runtime run agrees on fib (0.038 s vs CPython 0.083 s) but shows XS --jit slower than both CPython and Node on mandelbrot.

## Use it when

- You are writing XS anyway and have call-heavy integer code (recursion, counters): --jit cut fib(30) from 274 ms (VM) to 38 ms in the repo's own 2026-05-03 run.
- Short-lived scripts where start-up dominates: hello world is about 3-7 ms versus 15-28 ms for CPython and 53-110 ms for Node in the repo's runs.
- Experimenting with a small, readable register-allocating baseline JIT for a dynamic language (about 4,900 lines across the x86-64 path files in src/jit), on x86-64 or aarch64.

## Skip it when

- Float-heavy numeric code: the repo's own mandelbrot run has XS --jit at 0.577 s vs CPython 0.338 s and Node 0.112 s; floats are boxed XS_FLOAT values, only small integers get tagged fast paths.
- Anything where V8 is the alternative: STATUS.md's own table has fib(35) at 520 ms for XS --jit vs 210 ms for Node, and on README fib(30) XS is about 5x slower than Node once process start-up is subtracted (derived from page data).
- Multi-core compute: the VM holds a global lock in its dispatch loop, so pure-compute threads take turns (README).
- Production systems that need a stable, audited runtime: young project with 129 stars, the HTTPS client does not validate certificate chains (README), and STATUS.md admits silent JIT miscompiles on some corner cases.
- iOS, ESP32 or other targets without the JIT (README: mobile builds drop it; ESP32 is VM-only).

## How it is fast

With --jit, main.c calls jit_compile on the whole program at start-up: every function proto is lowered to a small linear IR (src/jit/ra_lower.c), split into basic blocks, given per-block liveness and linear-scan allocated onto three callee-saved registers, then emitted as x86-64 or arm64 machine code. The code has tagged small-integer (SMI) fast paths for arithmetic and compares, an XMM path for boxed XS_FLOAT operands, an inlined monomorphic inline cache for global loads, a fused compare-and-branch peephole and refcount-pair elimination. Recursive self-calls stay native through tier2_run_until and the per-proto jit_entry cache; unsupported opcodes (throw, yield, await, effects, imports) go through the vm_step_jit trampoline.

## Compared with alternatives

Pick XS only if you want the language itself; to speed up existing Python code, Numba, Cinder or CPython's own copy-and-patch JIT work on unchanged Python, and for JavaScript workloads V8 is already several times faster than XS on compute, with Perry and katsu the catalogued options that claim wins over Node.

## Integration

| | |
|---|---|
| **Form** | standalone statically linked binary (xs); src/xs_embed.h offers an embedding entry point (not reviewed) |
| **Dependencies** | none (BearSSL is vendored under src/tls/bearssl) |
| **Minimum toolchain** | C11 with gcc or clang and GNU make; default build -O2, make release -O3 -flto -DNDEBUG |
| **Platforms** | JIT on x86-64 and aarch64 (Linux, macOS, FreeBSD via mmap; Windows via VirtualAlloc); VM also on WASI, iOS, Android, ESP32 |
| **Thread safety** | OS threads via spawn, but the bytecode VM runs under a global lock released only around blocking calls (README) |
| **Drop-in for the baseline** | no |

## Gotchas

- --jit silently becomes --vm when the top-level script cannot be lowered: main.c falls back to the VM if jit_compile returns NULL for the main proto, and vm.c intentionally does not dispatch into compiled inner functions from VM frames, so one unsupported construct in the script body can disable the JIT without a message (the fallback notice needs XS_VERBOSE_JIT=1). The 2026-04-24 benchmarks/baseline.json shows exactly this pattern (fib --jit 0.155 s vs --vm 0.150 s). The 'threshold-driven' compile in jit.h (jit_maybe_compile, XS_JIT_THRESHOLD) is not on the --jit path.
- STATUS.md: 'JIT and VM disagree on a few --jit corner cases listed in the test suite as documented carryovers; pass --vm if you hit a silent miscompile.' tests/run.sh also counts a JIT that fell back to the VM as passing, since outputs then match trivially.
- Benchmark harness flaws: every timing includes process start-up (in benchmarks/results.json every Node row is 0.101-0.119 s against a 0.110 s start-up row, so the Node column measures start-up), and the README's reproduction pointer tests/bench_backends.sh runs no Node or Python and lists benchmarks/bench_fibonacci.xs, which does not exist (the file is bench_fib.xs), so that row times an error exit on all three backends and still reports 'ok' because the three empty stdouts match.
- The JIT code buffer is mapped read-write-execute (PROT_READ|PROT_WRITE|PROT_EXEC on Linux, PAGE_EXECUTE_READWRITE on Windows) with no W^X switching, 4 MiB by default (XS_JIT_CODE_SIZE_MB raises it to 1 GiB).

## Known shortcomings

- The Node win is a startup artifact: on fib(30) compute V8 takes about 5 ms against XS's 28 ms (derived), and the repo's own benchmarks/results.json (omitted from the README) has mandelbrot at XS 0.577 s vs CPython 0.338 s vs Node 0.112 s; the CPython 2x win is real. bench_backends.sh has no Node or Python, CPU model and build unstated. Separate language from Moddable's XS engine.
- Enricher: --jit compiles the whole program at startup and silently falls back to the VM when the top-level script cannot be lowered (visible only with XS_VERBOSE_JIT=1), which fits baseline.json where jit equals vm; STATUS.md admits silent JIT miscompiles. The README reproduction script tests/bench_backends.sh lists a missing benchmarks/bench_fibonacci.xs, so it times an error exit and still reports 'ok'; every Node row in results.json (0.101-0.119 s) is mostly Node's 0.110 s startup; JIT code pages are RWX; STATUS.md has fib(35) at XS --jit 520 ms vs Node 210 ms.

## Caveats and trade-offs

The README says 'treat as indicative, not authoritative'. Only one compute benchmark (call-bound recursive fib) is shown, and every timing includes process startup: Node 20's 57 ms startup is almost all of its 62 ms fib(30) time, so the apparent 2x win over Node is a startup artifact and on compute XS --jit is about 5x slower than V8 (derived from page data); the win over CPython (about 2x on fib compute) is real on this one kernel. The README omits the repo's own mandelbrot result (benchmarks/results.json: XS --jit 0.577 s vs CPython 0.338 s vs Node 0.112 s), where XS is slower than both baselines; the other rows in that file (sort, nbody, json, strings, hash) run 1-30 ms and are dominated by Python and Node startup. The reproduction pointer tests/bench_backends.sh only compares XS's own backends (median, fib(28), no Node or Python); the cross-runtime harness is benchmarks/run.sh. In the 2026-04-24 benchmarks/baseline.json the JIT was no faster than the VM (fib 0.155 s vs 0.150 s). CPU model ('AMD Ryzen 7') and compiler/build not stated. XS is its own language, not a drop-in for JavaScript or Python programs, and is unrelated to the Moddable XS JavaScript engine.

A new language shipped as one static binary with compiler, language server, formatter and package manager; compiles to native code, JavaScript or WebAssembly. The JIT compiles only the opcodes in its supported set and falls back to the VM for the rest, and is meant for profiled hotspots.

## Maintenance

Actively developed (v1.2.32, 489 commits, last commit 2026-05-20, Apache-2.0) and easy to build from source, but young and single-maintainer, with acknowledged JIT miscompiles and a JIT that only pays off on integer-heavy, call-heavy code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README table; a public cross-runtime harness exists (benchmarks/run.sh with bench_fib.xs/.py/.js/.go, results in benchmarks/results.json) but the CPU model ('AMD Ryzen 7'), compiler and which build (default gcc -O2 or make release -O3 -flto) are not stated, so C.
- **Verifier notes:** Separate project, not a duplicate: xs-lang0/xs is a new standalone language (own syntax, compiler, VM and JIT, Apache-2.0, 489 commits) with no relation to the Moddable XS JavaScript engine already listed under embedded-scripting. README numbers match the record, but the claim is overstated: the Node comparison is startup-dominated (V8 compute about 5 ms vs XS about 28 ms on fib(30), derived) and the repo's own results.json shows XS slower than CPython and Node on mandelbrot; only the fib win over CPython holds. Metadata checked: Apache-2.0, 129 stars, last commit 2026-05-20, not a fork.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/xs-lang0/xs>
  - <https://github.com/xs-lang0/xs/commits/main>
  - <https://github.com/xs-lang0/xs/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/README.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/tests/bench_backends.sh>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/results.json>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/baseline.json>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.xs>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.js>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.py>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/Makefile>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/xs-lang0/xs>
  - <https://github.com/xs-lang0/xs/tree/main/benchmarks>
  - <https://github.com/xs-lang0/xs/tree/main/src>
  - <https://github.com/xs-lang0/xs/tree/main/src/jit>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/README.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/STATUS.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/VERSION>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/Makefile>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/results.json>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/baseline.json>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.xs>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.py>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_fib.js>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_mandelbrot.xs>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_mandelbrot.py>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/benchmarks/bench_mandelbrot.js>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/tests/bench_backends.sh>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/tests/run.sh>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/jit.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/jit.h>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/ra_ir.h>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/ra_lower.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/ra_alloc.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/ra_live.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/jit/ra_codegen.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/vm/vm.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/xs-lang0/xs/HEAD/src/core/value.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/xs-lang0/xs`) · [data/wave12/enrich/raw/github_com_xs_lang0_xs.json](../../../data/wave12/enrich/raw/github_com_xs_lang0_xs.json) (enrichment confidence 0.75)

</details>
