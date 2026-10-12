# Cynic

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Pre-alpha strict-only JavaScript and WebAssembly engine in Zig whose interpreter beats QuickJS-NG on its author's micro-benchmarks.

| | |
|---|---|
| **Beats** | QuickJS-NG (qjs 0.15.1, prebuilt binary installed via jsvu per tools/bench-cross.sh, which names QuickJS-NG the headline non-JIT peer) |
| **Claimed result** | Micro (ms, Cynic vs qjs): arith_loop 77 vs 369, mod_loop 60 vs 388, array_literal_loop 308 vs 1361, construct_loop 312 vs 977, json_stringify 40 vs 146, class_instantiate 55 vs 173; faster on all 18 micro fixtures where qjs completed (qjs errors on tail_recursion), with near-ties on promise_chain (27 vs 28) and shallow_cons_miss (155 vs 158). Macro: crypto 387 vs 671, splay 479 vs 817, navier-stokes 270 vs 334, raytrace 216 vs 261, richards 579 vs 585 (tie), deltablue 430 vs 344 (slower). |
| **Workload** | Cross-engine snapshot bench-cross-results.md captured 2026-08-06: interpreter-tier micro fixtures and the vendored Octane compute-six macros, subprocess wall clock, median of N=12 after one warmup, pinned to CPU 1 with taskset, Cynic run with --no-jit (all other JIT engines run JIT-disabled). |
| **Metric** | throughput |
| **Hardware** | Linux 6.8.0-136-generic x86_64 (CPU model not stated), taskset CPU 1 |
| **Compiler and flags** | Cynic revision 6e125807 built by tools/bench-cross.sh with zig build -Doptimize=ReleaseFast (Zig version pinned in build.zig.zon), run with --no-jit (macros also --unhardened); qjs is the jsvu-installed QuickJS-NG binary, build flags not stated |
| **Adoption** | 26 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/chicoxyzzy/cynic) · [benchmark](https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench-cross-results.md) |

## Verdict

The author's internal cross-engine snapshot (tools/bench-cross.sh, revision 6e125807, Linux 6.8 x86_64, CPU model not stated, pinned to CPU 1, median of 12 subprocess wall-clock runs after one warmup) has Cynic --no-jit, built with zig build -Doptimize=ReleaseFast, ahead of QuickJS-NG 0.15.1 (jsvu's static musl/mimalloc release binary) on all 18 micro fixtures qjs completes (3.1-6.5x on the arithmetic and allocation loops, near ties on promise_chain and shallow_cons_miss) and on four of six Octane macros (1.2-1.7x), tied on richards and 1.25x slower on deltablue (derived from page data). The page labels itself an unpublished internal regression compass, so this is first-party evidence.

## Use it when

- You embed JavaScript in a Zig program, or want a hardened-by-default JS sandbox (frozen primordials, host-gated eval and Wasm compilation) and your scripts are strict-mode or ES modules.
- Interpreter-only throughput on tight int32 arithmetic, array-literal and constructor loops matters: in the author's interpreter-tier snapshot Cynic --no-jit is 3.1-6.5x faster than QuickJS-NG on arith_loop, mod_loop, array_literal_loop, construct_loop and class_instantiate.
- Compute-heavy scripts of the Octane kind where QuickJS-NG is your current engine and a few MB more RSS is acceptable (crypto 1.73x, splay 1.71x, navier-stokes 1.24x, raytrace 1.21x faster in the same snapshot, derived from page data).
- You need JS and WebAssembly in one small native engine on x86_64 Linux or Apple Silicon macOS.

## Skip it when

- Production use of any kind: the README calls it pre-alpha, the embedding API is still changing, test262 coverage is about 89% of the runtime-mode sweep, and closed issues include panics on large Numbers (#22, #23) and a CLI `eval` that ran code with syntax errors (#137).
- Legacy or web-compat code: sloppy-mode scripts, Annex B features, `with`, legacy octal literals and Annex B regex leniencies are rejected, so a lot of npm-era code will not run unmodified.
- Memory-constrained hosts: QuickJS-NG peaks at 1,792 KiB on nearly every micro fixture against 6,016-27,520 KiB for Cynic, and on deltablue 1,920 KiB vs 12,544 KiB.
- Workloads like deltablue (Cynic 430 ms vs qjs 344 ms) or richards (a tie), and anything where Hermes, V8 --jitless or JSC with JIT off is an option: all three beat Cynic on every Octane macro in the same snapshot.
- Windows, mobile, or a C/C++ host that needs a stable C API: Windows and mobile are unsupported and no C API is documented.

## How it is fast

The bytecode is register-file plus implicit accumulator (Ignition/Hermes style) with one-byte opcodes, narrow immediate forms, fused opcodes such as `make_array_n` and `LoopIncLt`, a post-finalization `Star r; Ldar r` forwarding pass, and a direct-threaded dispatch loop in the Lantern interpreter; the docs reject QuickJS's pure-stack design for its higher dispatch count. Values are NaN-boxed with the JSC encoding (unboxed doubles, 16-bit tags), and load, store, computed-property and method-call sites carry typed inline caches (the benchmarking doc credits the `lda_property` IC with a 66% drop on prop_access). Above Lantern sit two JIT tiers, Bistromath (T1) and Ohaimark (T2), on x86_64 and AArch64, but the cross-engine numbers that beat QuickJS-NG were taken with `--no-jit`.

## Compared with alternatives

Pick Cynic over QuickJS when you want a hardened, strict-only engine with a faster interpreter on arithmetic and allocation loops and can live with pre-alpha status and 3-7x the RSS; QuickJS remains the choice for small footprint, sloppy-mode compatibility and a stable C API. Hermes (faster than Cynic on every Octane macro here) or PrimJS and Escargot are better picks when you need a mature non-JIT engine today.

## Integration

| | |
|---|---|
| **Form** | Zig source build (`zig build`): CLI binary plus a Zig embedding API; no tagged releases |
| **Dependencies** | none declared in build.zig.zon; vendored test262, Wasm testsuite, Unicode, CLDR and IANA tzdata assets (Intl is a compile-time choice: -Dintl=off\|stub\|full) |
| **Minimum toolchain** | Zig development build 0.17.0-dev.1275+59a628c6d, pinned in build.zig.zon (anyzig can fetch it) |
| **Platforms** | Native CI on x86_64-linux-gnu and Apple Silicon macOS; cross-builds aarch64-linux-gnu, x86_64-linux-musl, aarch64-macos; wasm32-freestanding for the browser playground; JIT tiers only on x86_64 and AArch64 macOS/Linux; no Windows or mobile |
| **Thread safety** | not documented (state is owned by an explicit Engine struct, no globals) |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured posture is not the default posture: bench-cross.sh runs Cynic with --no-jit --unhardened --allow=eval, while the CLI default is hardened with both JIT tiers on; in the same snapshot the default JIT-on run is slower than --no-jit on several micros (arith_loop 99 vs 77 ms, construct_loop 337 vs 312, mod_loop 69 vs 60) and within 3% on every macro.
- Harness gap: bench-cross.sh sends every engine's stdout to /dev/null and checks only the exit code, so the checksums the micro fixtures print are never compared across engines (the Octane macros do self-check, e.g. crypto throws if decryption does not round-trip). Timing is spawn-to-exit wall clock with `date +%s%3N`, so start-up is inside every number, and arith_loop, array_literal_loop, construct_loop and json_stringify keep their accumulator in a top-level script `let`, so they also time each engine's global-binding access path.
- The baseline binary is pinned down after all: jsvu's QuickJS installer downloads quickjs-ng's release asset qjs-linux-x86_64, which quickjs-ng's release.yml builds on Alpine (musl) with GCC as a static CLI with static mimalloc in CMake's default Release mode; the CPU model of the benchmark host is still unstated.
- The snapshot is from revision 6e125807 (2026-08-06) and covers 19 micro fixtures; bench/micros now holds 39 (BigInt, relational and double-increment fixtures added later) with no newer cross-engine snapshot. The record's note that Cynic vendors QuickJS's libregexp comes from a bench-cross.sh comment that looks stale: vendor/ has no libregexp and ARCHITECTURE.md names Perlex as Cynic's own regex engine.

## Known shortcomings

- Enricher: tools/bench-cross.sh sends stdout to /dev/null and checks only the exit code, so micro checksums are never compared across engines; 4 micros keep the accumulator in a top-level let and so also time global-binding access; the benchmarked posture (--no-jit --unhardened --allow=eval) differs from the default, whose JIT-on run is slower than --no-jit on arith_loop (99 vs 77 ms); Zig's standardTargetOptions builds Cynic for the native CPU against a generic qjs (jsvu's quickjs-ng release binary: Alpine musl, static, mimalloc, CMake Release). The snapshot 6e125807 covers 19 micros while the repo now has 39; the record's 'vendors QuickJS libregexp' is stale (ARCHITECTURE.md names Perlex).

## Caveats and trade-offs

The results file calls itself an 'internal regression compass - not published', host-local and not comparable across hosts; CPU model missing, so tier C. Times are subprocess wall clock (spawn to exit), so process startup is included. The baseline is QuickJS-NG via jsvu, not Bellard's QuickJS; Cynic vendors QuickJS's libregexp. The comparison is interpreter tier only: on the same page Hermes, JavaScriptCore (JSC_useJIT=0) and V8 --jitless beat Cynic on every macro fixture, and in the full-speed table (JIT on) Cynic is about 4.5-12.6x slower than the fastest of V8, SpiderMonkey and JavaScriptCore on every macro fixture (derived from page data; that table has no qjs row), with Cynic's JIT-on macro times barely different from its --no-jit times. Cynic is strict-only (no sloppy mode or Annex B), so it runs a narrower language than qjs. qjs uses far less memory: peak RSS 1.8 MB versus 6-12.5 MB for Cynic on all fixtures except splay. Micro fixtures are chosen by the author and 13 of 19 Cynic micro cells carry more than 10% spread (promise_chain 51%, prop_write 65%). README makes no comparative claim; the engine is pre-alpha.

Strict-only ECMAScript engine (no sloppy mode, no Annex B, no web-compat built-ins) in Zig with built-in hardening and WebAssembly. Peak RSS is about 3-4x QuickJS in the same snapshot (about 6,000 KiB vs 1,792 KiB on arith_loop).

## Maintenance

Very active (2,558 commits, last commit 2026-10-05, 26 stars, no releases) and MIT-licensed, but pre-alpha with an evolving embedding API and a pinned Zig development compiler, so treat it as an engine to watch or experiment with, not one to ship.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** bench-cross-results.md is the project's own snapshot from public code (tools/bench-cross.sh with bench/micros and bench/macros fixtures, Cynic built with zig build -Doptimize=ReleaseFast) and states engine versions and the kernel, but no CPU model and no build flags for the jsvu-installed qjs binary, so it falls short of A; first-party, so C.
- **Verifier notes:** All claimed micro and macro numbers match the page exactly (18 of 18 completed micro fixtures faster than qjs, deltablue slower, richards a tie). Main shortcomings: baseline is QuickJS-NG via a jsvu binary, internal unpublished snapshot without CPU model, interpreter-tier only (Hermes, JSC and V8 jitless all faster on macros), and the JIT tier is 4.5-12.6x behind V8/SM/JSC.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench-cross-results.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/README.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/tools/bench-cross.sh>
  - <https://github.com/chicoxyzzy/cynic>
  - <https://github.com/chicoxyzzy/cynic/commits>
- **Sources the enricher read:**
  - <https://github.com/chicoxyzzy/cynic>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/README.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench-cross-results.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/tools/bench-cross.sh>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/docs/benchmarking.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/docs/jit.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/micros/arith_loop.js>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/micros/mod_loop.js>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/micros/array_literal_loop.js>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/micros/json_stringify.js>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/micros/construct_loop.js>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/macros/README.md>
  - <https://raw.githubusercontent.com/chicoxyzzy/cynic/HEAD/bench/macros/crypto.js>
  - <https://github.com/chicoxyzzy/cynic/tree/main/bench/micros>
  - <https://github.com/chicoxyzzy/cynic/tree/main/vendor>
  - <https://github.com/chicoxyzzy/cynic/issues?q=is%3Aissue>
  - <https://github.com/chicoxyzzy/cynic/issues/137>
  - <https://raw.githubusercontent.com/GoogleChromeLabs/jsvu/HEAD/engines/quickjs/extract.js>
  - <https://raw.githubusercontent.com/GoogleChromeLabs/jsvu/HEAD/engines/quickjs/get-latest-version.js>
  - <https://raw.githubusercontent.com/GoogleChromeLabs/jsvu/HEAD/engines/quickjs/predict-url.js>
  - <https://raw.githubusercontent.com/GoogleChromeLabs/jsvu/HEAD/shared/installer.js>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/chicoxyzzy/cynic`) · [data/wave12/enrich/raw/github_com_chicoxyzzy_cynic.json](../../../data/wave12/enrich/raw/github_com_chicoxyzzy_cynic.json) (enrichment confidence 0.75)

</details>
