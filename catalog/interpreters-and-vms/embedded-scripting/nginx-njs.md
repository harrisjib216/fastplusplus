# njs (nginx JavaScript)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> nginx's built-in JavaScript engine (ES5.1 plus an ES6+ subset) for request scripting; about 1.5x Duktape on v8-v7, behind QuickJS.

| | |
|---|---|
| **Beats** | Duktape 2.99.99 (unreleased master, built by ahaoboy/duktape-build with Duktape's development Makefile, which uses -Os -fomit-frame-pointer -g) on ubuntu/macos-arm64; QuickJS 2026.06.04 is faster than njs in this suite |
| **Claimed result** | Score (higher is better), ubuntu / macos-arm64: njs 0.9.2 721 / 950 vs duktape 489 / 905 (windows: no njs build). About 1.5x Duktape on ubuntu and 1.05x on macOS (derived from page data); quickjs scores 1217 / 1761 so njs is behind QuickJS. |
| **Workload** | Score is the sum over the v8-v7 benchmark suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes), higher is better; each engine's shell runs the inlined dist/run.js once per daily CI run on GitHub Actions runners (ubuntu-latest, macos-latest arm64, windows-latest) and the result is published in the repo README (snapshot 10/5/2026, 4:04:34 AM). njs is invoked without an engine flag, so the built-in njs engine (not njs's QuickJS backend) is what is measured. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions runners (ubuntu, macos-arm64); CPU model not stated |
| **Compiler and flags** | njs built by ahaoboy/njs-build build.sh: git clone nginx/njs, ./configure --with-quickjs (Bellard QuickJS linked) with njs's default compiler options; Duktape built with -Os; compiler versions not stated |
| **Adoption** | 1.6k stars; dynamic module for NGINX Open Source (1.14+) and NGINX Plus |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/nginx/njs) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

In ahaoboy/js-engine-benchmark's v8-v7 run (snapshot 10/5/2026, GitHub-hosted runners, CPU not stated, one run per engine), the njs CLI 0.9.2 running its built-in engine scored 721 on Ubuntu and 950 on macOS arm64 versus Duktape 2.99.99 (-Os build of master) at 489 and 905, about 1.5x and 1.05x (derived from page data); QuickJS 2026-06-04 scored 1217 and 1761. njs was built from nginx/njs master by ahaoboy/njs-build with njs's default -O flags and linked against Bellard's libquickjs.a; there is no Windows result.

## Use it when

- You already run nginx and need request-time logic (auth checks, header or body rewriting, routing, subrequests, ngx.fetch) without a separate service.
- Short-lived per-request scripts: each request gets a clone of a precompiled VM and its memory is released in one shot at request end.
- Existing scripts written for the default njs engine that you are not ready to move to js_engine qjs.
- Choosing between small interpreters for nginx-style scripts on Linux: njs scored 721 vs Duktape 489 on Ubuntu in this suite.

## Skip it when

- General embedding outside nginx: QuickJS scores 1217 / 1761 vs njs 721 / 950 (Ubuntu / macOS arm64), is about 1 MB, and is documented for embedding; njs's C API is documented only through nginx and the CLI.
- New code: the built-in engine is deprecated since 1.0.0; the README recommends js_engine qjs and says QuickJS will eventually become the default.
- Modern JavaScript: the njs engine covers ES5.1 plus selected ES6+ features (logical assignment ||= and &&= arrived only in 0.9.6, March 2026), while its QuickJS engine supports ES2023.
- RegExp-heavy or allocation-heavy scripts: njs loses RegExp to the -Os Duktape build on both platforms (113 vs 129, 216 vs 244) and Splay on macOS (1472 vs 2594); on macOS arm64 it loses 4 of 8 tests and the total margin is only about 5%.
- Windows hosts: the shootout has no njs build, and ahaoboy/njs-build's Windows job is commented out.

## How it is fast

The built-in engine parses and generates bytecode for its own VM (src/njs_parser.c, njs_generator.c, njs_vmcode.c) and is built around cheap per-request VMs: nginx compiles the script once and njs_vm_clone gives each request a copy backed by a fresh fast memory pool (njs_mp_fast_create) that is freed in one step when the VM is destroyed; njs.h exposes no garbage-collector entry point. Regular expressions go to PCRE2 (or PCRE). Against the -Os Duktape build its lead comes from Richards, DeltaBlue and EarleyBoyer (1.7-3.0x on Ubuntu, derived from page data); it is a plain interpreter, so QuickJS's tighter bytecode interpreter stays ahead.

## Compared with alternatives

Pick njs only inside nginx, where it is the supported scripting module, and there prefer its QuickJS engine; outside nginx QuickJS is faster (1217 vs 721 on Ubuntu, 1761 vs 950 on macOS) and documented for embedding. Among small interpreters in the same shootout it sits with PrimJS (737) and LibJS (691) on Ubuntu, below Quanta (1068).

## Integration

| | |
|---|---|
| **Form** | nginx dynamic module (ngx_http_js_module, ngx_stream_js_module) or built into nginx; standalone njs CLI; libnjs.a static library |
| **Dependencies** | PCRE2 or PCRE, zlib, OpenSSL (WebCrypto), libxml2 and libxslt (xml module); optional libquickjs.a for the QuickJS engine; libedit for the interactive CLI |
| **Minimum toolchain** | C compiler, gcc or clang (auto/cc); default flags are -O -g -W -Wall -Wextra -Werror, so a newer compiler that adds warnings can break the default build |
| **Platforms** | Unix-like systems that nginx supports (the README points to nginx's tested-platform list); the shootout builds Linux x86-64 and macOS arm64; no Windows build |
| **Thread safety** | Not documented; a VM (njs_vm_t) is used from one thread, and nginx runs single-threaded worker processes that clone one VM per request |
| **Drop-in for the baseline** | no |

## Gotchas

- Stale build of a deprecated engine: the shootout's njs comes from ahaoboy/njs-build, which rebuilds only on a push or tag to that repo (no schedule), and reports 0.9.2 (released 23 Sep 2025); eight releases (0.9.3 to 1.0.1, 02 Sep 2026) have shipped since, including engine fixes such as an Array.prototype.sort use-after-free, a Buffer.concat type confusion and Buffer out-of-bounds reads.
- Engine measured: njs_shell.c defaults to the njs engine ('-n njs|QuickJS ... njs is default') and update.ts passes no flag or NJS_ENGINE, so the recommended QuickJS backend that njs-build links into the same binary (configure --with-quickjs against libquickjs.a) was not measured; the 1.9 MB size behind Score/MB 386 likely includes that QuickJS code.
- Harness: one run per engine per day on unnamed GitHub runner CPUs; v8-v7 base.js discards a 1 s warm-up and times at least 1 s per test, so Time(s) has a 20 s floor and the 62 s vs 70 s wall times compare only coarsely. Neither side is a tuned build: njs uses its default -O (not -O2) and Duktape is an -Os build of unreleased master.
- Memory model: njs.h has no GC API and NGINX describes njs as creating a VM per request and freeing its memory when the request completes (QuickJS blog, search snippet only), so expect allocation-heavy loops in long-running CLI or stream scripts to hold memory until the VM is destroyed. The same blog says QuickJS with js_context_reuse runs within 1% of the njs engine on request workloads, so the v8-v7 gap says little about nginx throughput.

## Known shortcomings

- The measured binary is a stale njs 0.9.2 running the built-in engine, deprecated since 1.0.0 (current 1.0.1) in favour of QuickJS; the Duktape baseline was built -Os, and on macOS njs lost 4 of 8 sub-benchmarks with longer wall time (50 s vs 46 s).
- Enricher: the measured binary is stale and deprecated (njs-build has no schedule and reports 0.9.2 of 2025-09-23, 8 releases behind), the CLI defaults to the built-in engine (njs_shell.c) so the QuickJS backend linked into the same binary was never measured, njs was built at default -O against Duktape at -Os, and the 1.9 MB size likely includes libquickjs.a; no GC API in njs.h. An NGINX blog snippet puts QuickJS with js_context_reuse within 1% of the njs engine on request workloads.

## Caveats and trade-offs

Engines are prebuilt through the suite owner's \*-build repos or release binaries; compiler versions and CPU models are not stated (GitHub Actions runners), and each engine runs once per day with no variance reported. The measured binary reports njs 0.9.2, while nginx/njs is at 1.0.1 (tags 1.0.0 2026-06-23, 1.0.1 2026-08-20), and the njs README says the built-in njs engine has been deprecated since 1.0.0 in favour of the QuickJS engine, so the result measures a stale build of a deprecated engine; njs's recommended QuickJS backend is QuickJS itself (already listed), which outscores njs here (1217/1761). The Duktape baseline is an -Os build of unreleased master (2.99.99). On macos-arm64 the margin is only about 5% by score, njs loses 4 of 8 sub-benchmarks (Crypto 1215 vs 1257, RayTrace 684 vs 1032, RegExp 216 vs 244, Splay 1472 vs 2594) and its wall time is longer (50 s vs 46 s); on ubuntu it loses RegExp (113 vs 129). No njs build on Windows. The v8-v7 suite is old and partly micro-benchmark. njs is mainly an nginx module; libnjs exists for embedding but is not a general-purpose embedding library. [retier] Measured binary is stale njs 0.9.2 (2025-09-23; njs-build has no schedule, 8 releases behind) running the deprecated built-in engine: the CLI defaults to it (njs_shell.c), so the QuickJS backend linked into the same binary was never measured. njs built at default -O against Duktape at -Os; the 1.9 MB size likely includes libquickjs.a; no GC API in njs.h. On macOS 4 of 8 sub-benchmarks lost with longer wall time (50 s vs 46 s). An NGINX blog snippet puts QuickJS with js_context_reuse within 1% of the njs engine on request workloads.

Subset of JavaScript (ES5.1 plus curated ES6+) in its built-in engine; the README says the built-in engine is deprecated in favour of an optional QuickJS backend, so the engine measured may be the one being phased out; primarily an nginx module with a standalone CLI.

## Maintenance

Actively maintained by NGINX (1.0.1 on 02 Sep 2026, master at 1.0.2) under BSD-2-Clause, but the measured built-in engine is deprecated in favour of QuickJS, so this entry is evidence about legacy njs scripts rather than a reason to adopt the engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party CI shootout (ahaoboy/js-engine-benchmark, 59 stars; v8-v7 suite code in v8-v7/, driver scripts/update.ts, results 10/5/2026) shows njs Score 721/950 vs Duktape 489/905 on ubuntu/macos-arm64; not A because the GitHub Actions runners' CPU models and compiler versions are not stated (njs is built by ahaoboy/njs-build build.sh with default configure options). B matches the ChakraCore and v8 verdicts on the same suite.
- **Verifier notes:** Numbers match the README tables (ubuntu njs 721 vs duktape 489, macos-arm64 950 vs 905, quickjs 1217/1761). Main shortcomings: stale 0.9.2 binary of the built-in engine that upstream deprecated in 1.0.0, a -Os Duktape baseline, and a mixed macOS result (slower wall time, 4 of 8 sub-benchmarks lost).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/scripts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://github.com/ahaoboy/njs-build>
  - <https://raw.githubusercontent.com/ahaoboy/njs-build/HEAD/build.sh>
  - <https://github.com/ahaoboy/duktape-build>
  - <https://raw.githubusercontent.com/ahaoboy/duktape-build/HEAD/build.sh>
  - <https://raw.githubusercontent.com/svaarala/duktape/HEAD/Makefile>
  - <https://github.com/nginx/njs>
  - <https://github.com/nginx/njs/commits/master>
  - <https://github.com/nginx/njs/tags>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/nginx/njs>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/README.md>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/external/njs_shell.c>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/src/njs.h>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/src/njs_vm.c>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/src/njs_vmcode.h>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/auto/cc>
  - <https://raw.githubusercontent.com/nginx/njs/HEAD/auto/pcre>
  - <https://github.com/nginx/njs/issues?q=is%3Aissue+performance>
  - <https://raw.githubusercontent.com/ahaoboy/njs-build/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ahaoboy/njs-build/HEAD/.github/workflows/build.yml>
  - <https://github.com/ahaoboy/njs-build/actions>
  - <https://github.com/ahaoboy/njs-build/releases>
  - <https://github.com/ahaoboy/njs-build/releases/tag/v0.1.1>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/run.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/base.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/action.yml>
  - https://nginx.org/en/docs/njs/engine.html (EGRESS_BLOCKED)
  - https://blog.nginx.org/blog/quickjs-engine-support-for-njs (WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nginx/njs`) · [data/wave12/enrich/raw/github_com_nginx_njs.json](../../../data/wave12/enrich/raw/github_com_nginx_njs.json) (enrichment confidence 0.7)

</details>
