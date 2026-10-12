# scriptc (Vercel Labs TypeScript to native compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `Apache-2.0` · 🟢 active

> Ahead-of-time TypeScript-to-native compiler; executables start in about 2 ms against tens of milliseconds for Node and Bun, but run hot loops slower.

| | |
|---|---|
| **Beats** | Node.js 24.18.0 (V8) and Bun 1.3.12; slower than both on sustained throughput per the same reports |
| **Claimed result** | Snippet only: median CLI startup 1.78 ms for scriptc vs 21.29 ms for Bun 1.3.12 and 61.78 ms for Node 24.18.0 (about 12x and 35x, derived from the snippet); idle memory 1.9 MiB for a framework-free node:http server. Same coverage says Hono needs --dynamic and reaches 18.4k requests per second vs 70.5k for Bun. |
| **Workload** | CLI process startup (median) of a compiled scriptc 0.0.16 executable against the same program on Bun and Node, plus idle memory of a node:http server. |
| **Metric** | startup |
| **Adoption** | 6.0k stars, 170 forks; npm package scriptc |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/vercel-labs/scriptc) · [benchmark](https://www.infoq.com/news/2026/09/vercel-scriptc-node/) |

## Verdict

Snippets of launch news coverage (InfoQ and others, all blocked here) report median CLI startup for scriptc 0.0.16 executables of 1.78 ms, against 21.29 ms for Bun 1.3.12 and 61.78 ms for Node 24.18.0, and 1.9 MiB idle memory for a framework-free node:http server. Runner, hardware and program are not stated, and no repo benchmark reproduces the run. On sustained throughput scriptc loses: issue #357 (Ryzen 9 7900X, Linux, scriptc 0.1.3 LLVM release build, clang 22.1.8, Node 24.12.0) reached parity on xorshift32 only after a fix, and its byte loop stayed about 2.75x slower than Node.

## Use it when

- Short-lived CLIs, git hooks, editor helpers or build steps that run many times, where Node's 20-60 ms process start dominates wall time.
- Small node:http services or sidecars where idle RSS matters (launch coverage reports 1.9 MiB idle; an HN commenter measured 2.5 MiB vs 181 MiB for Node).
- Shipping a single-file binary to machines without Node: static builds need no runtime, and npm dependencies are embedded at build time with --dynamic.
- Embedding TypeScript logic in C/C++, iOS (arm64) or Android (API 26+) apps as a library-mode static archive, or in a browser or WASI host as a Wasm reactor.
- Strictly typed codebases where `scriptc coverage` reports 100% static, with little `any` and few npm dependencies.

## Skip it when

- Throughput-bound hot loops. V8's JIT still wins: issue #357 measured xorshift32 77.4x slower than Node 24.12.0 before the fix and at parity after it, but a byte loop stayed 2.75x slower (3.22 vs 1.17 ms/round, derived from page data). Issue #113 (scriptc 0.0.23) reported byte loops 2.1x to 6.5x slower than Node 22, and one HN commenter reported about 7.5x slower on byte arrays.
- Code dominated by npm packages or `any`. That code runs in the embedded quickjs-ng interpreter, and values copied across the boundary are validated at runtime. Snippets of launch coverage report Hono under --dynamic at 18.4k requests/s vs 70.5k for Bun.
- Programs that need N-API/.node addons, worker_threads Worker, Float16 or BigInt64 typed arrays, resizable or transferable ArrayBuffers, Date setters or locale formatting, object-to-primitive `==`, or other features listed as unsupported on the limitations page.
- Network servers on Windows or WASI. The Windows loop polls sockets with zero-timeout WSAPoll and a capped (\~1 ms) nanosleep instead of IOCP; the source comments say it is sized for dozens of sockets.
- Production code that needs exact Node semantics or a stable toolchain. The project is a self-described Vercel Labs experiment at 0.2.x, and 0.2.0 removed the C backend and the --emit=c output.

## How it is fast

The TypeScript checker's types and narrowing drive lowering to a typed IR: generics are specialized, unions become tagged values and closures get explicit captures. LLVM 22 then compiles that IR at -O2 and links it against a precompiled C runtime pack. Startup does no engine initialization, parsing, bytecode compilation or JIT warm-up, so process start costs little more than exec plus the C runtime's init. Memory is managed by reference counting with a cycle collector run at defined collection points, not a garbage-collected engine heap, which keeps idle RSS in the low MiB.

## Compared with alternatives

Pick scriptc over LLRT when your code is typed TypeScript and you want compiled native code and a single binary rather than a QuickJS interpreter with no JIT. Pick it over Porffor or katsu when you need a working Node API surface (http/https, tls, fs, child_process, fetch) as well as fast startup. For untyped JavaScript or compute-heavy work, stay on Node or Bun.

## Integration

| | |
|---|---|
| **Form** | compiler CLI (npm package `scriptc` with a native platform binary, or a standalone archive from GitHub Releases) that emits native executables, library-mode static archives, object/LLVM/IR files or WASI modules |
| **Dependencies** | a platform linker and SDK/sysroot for executables (Xcode Command Line Tools on macOS) and Zig for cross-linking to Linux, Windows and WASI. The compiler bundles the TypeScript 7 native checker and the LLVM 22 helper. The runtime vendors mbedTLS, curl, zlib, ryu and Unicode tables, plus quickjs-ng (linked only with --dynamic) |
| **Minimum toolchain** | Node.js 24+ and npm for installation (not needed to compile or run). GNU/Linux compiler and runtime packs need glibc 2.34+. The LLVM helper needs macOS 15+ (artifacts target macOS 14). iOS 15.0 and Android API 26 minimums for library mode. |
| **Platforms** | macOS arm64/x64, Linux x64/arm64 (glibc or musl), Windows x64; iOS arm64 and Android arm64 in library mode only; WASI Preview 1 (no sockets, child processes or signals) |
| **Thread safety** | Single-threaded script runtime with non-atomic reference counts and a fiber-based event loop (epoll on Linux, kqueue on macOS, WSAPoll on Windows). worker_threads Worker is unsupported; child_process.fork re-executes the binary. FFI callbacks from foreign threads are queued to the event loop. Library mode can make runtime state per-thread with abi.instance_per_thread. |
| **Drop-in for the baseline** | partial: the same TypeScript source and many Node 24 APIs compile, but only the typed subset runs natively. `any` code and npm code need --dynamic (quickjs-ng), addons are unsupported, and runtime behavior differs from Node in documented ways. |

## Gotchas

- Statically typed out-of-bounds reads from typed arrays abort the process, where Node returns undefined. Runtime traps cannot be caught; only thrown values and supported exceptions can.
- Strings are stored as UTF-8 but indexed with JavaScript's UTF-16 semantics. On non-ASCII strings, slice, charCodeAt, indexOf and similar calls must map UTF-16 positions to byte offsets. Issue #261 measured slice on a 20 MB string at 21 ms before the fix. The current runtime keeps checkpoints every 4 KiB for strings of 64 KiB or more, but only in four sparse cache entries per runtime, so indexing more than four large non-ASCII strings in turn can fall back to prefix scans.
- Semantics differ quietly from Node. Object.keys and JSON.stringify follow declaration order, not insertion order. `JSON.parse(s) as T` validates at runtime and throws. A record converted to a narrower shape is copied, so mutations through it do not reach the original. Uncaught exceptions print `Uncaught <value>` with no stack trace. Cycles through native handles, or across the static/quickjs-ng boundary, can leak.
- Harness and provenance flaw behind the headline: the 1.78 ms vs 21.29 ms (Bun 1.3.12) vs 61.78 ms (Node 24.18.0) startup figures exist only in news-article search snippets about scriptc 0.0.16 (current release 0.2.4), with no named runner, program or hardware. Their Node figure is 3.3x the 18.6 ms an HN commenter measured for Node 24, which points to a heavier program or slower machine, so treat the 12x and 35x ratios as order-of-magnitude only. No benchmark in the repo compares against Node or Bun; benchmarks/builds measures compile latency.

## Known shortcomings

- Startup-only win (1.78 ms vs Bun 21.29 ms vs Node 61.78 ms) run by an unknown party on 0.0.16 (now 0.2.4), snippet only (InfoQ blocked); throughput is slower than Node (#357 77.4x before a fix, about 1.02x after; #113 2.1-6.5x) and Hono --dynamic reaches 18.4k vs Bun 70.5k requests per second.
- Enricher: the 1.78/21.29/61.78 ms startup figures exist only in news snippets for scriptc 0.0.16 with no runner, program or hardware, and the 61.78 ms Node figure is 3.3x the 18.6 ms an HN commenter measured for Node 24, so the 12x/35x ratios are order-of-magnitude only; the repo has no Node or Bun benchmark (benchmarks/builds measures compile latency). Throughput losses: #357 byte loop still about 2.75x slower than Node 24.12.0 after the fix (3.22 vs 1.17 ms per round, derived from page data), #113 2.1-6.5x slower, #93 zstd 30-48x per element before a fix. Runtime: four sparse UTF-16 index entries per runtime so more than four large non-ASCII strings fall back to O(index) scans (#261); the Windows/WASI loop uses zero-timeout WSAPoll plus a capped nanosleep with no IOCP; typed-array out-of-bounds reads abort the process; non-atomic refcount plus cycle collector leaks across the quickjs-ng boundary.

## Caveats and trade-offs

Snippet only: the startup numbers come from WebSearch result snippets of news coverage (InfoQ and other outlets, all blocked here); the original run's author, hardware and measured program could not be identified (one search summary attributes it to Vercel Labs' launch, which would make it vendor evidence), and the figures were measured on scriptc 0.0.16 while the current release is 0.2.4. Neither the scriptc README, the docs/ site source, nor CHANGELOG.md contains a Node or Bun comparison; benchmarks/builds and scripts/bench-builds.mjs measure build latency, not Node or Bun. Throughput is the weak side: issue #357 (closed, opened 2026-09-20) measured xorshift32 at 88.878 ms/op vs Node 24.12.0 1.148 ms/op (77.4x slower) and a byte loop 56.4x slower, and its fix brought xorshift to 1.174 ms/op (about 1.02x Node); issue #113 (closed, opened 2026-08-10) measured scriptc 0.0.23 byte loops 2.1x to 6.5x slower than Node 22. A search snippet also quotes one Hacker News commenter measuring about 7.5x slower than Node 24 on byte arrays, while startup was 12x faster (1.5 ms vs 18.6 ms) and memory 72x lower (2.5 MiB vs 181 MiB). Hono needs --dynamic (embedded quickjs-ng) and then reaches 18.4k requests per second vs 70.5k for Bun. Third-party harnesses (proggeramlug/js-compiled and jlucaso1/js-compiled) benchmark scriptc against Node, Bun and Porffor on 22 programs, but results are only on GitHub Pages (blocked) and not committed. The startup advantage is structural for an AOT native executable versus a full JS runtime.

Compiles a typed subset of TypeScript/JavaScript and Node APIs to native code through LLVM, with no JS engine in static builds; --dynamic embeds quickjs-ng for npm dependencies and any-typed code and then loses the native speed. Runtime semantics differ from Node (see docs limitations page); experimental per the README.

## Maintenance

Very active: last commit 2026-10-06, 939 commits, release 0.2.4, Apache-2.0. It is labelled a Vercel Labs experiment, so it is usable for typed CLIs and small servers today, but flags and semantics still change between 0.x releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The startup figures (scriptc 0.0.16 median CLI startup 1.78 ms vs Bun 1.3.12 21.29 ms vs Node 24.18.0 61.78 ms; 1.9 MiB idle node:http server) appear only in WebSearch snippets of launch coverage (InfoQ, EGRESS_BLOCKED here); who ran them, on what hardware and with which program could not be read, and the repo has no Node or Bun comparison, so C (snippet-only precedent).
- **Verifier notes:** Snippets re-confirmed the 1.78/21.29/61.78 ms figures and the Hono 18.4k vs 70.5k numbers; InfoQ is EGRESS_BLOCKED, so benchmark_url points at the blocked article per the snippet-only precedent. Metadata checked: Apache-2.0, 6.0k stars, 170 forks, not a fork, last commit 2026-10-06. Shortcomings to record: startup-only win from snippet numbers of unknown provenance on an old version (0.0.16 vs current 0.2.4), sustained throughput slower than Node (issues #357, #113, HN 7.5x report), Hono via --dynamic 3.8x below Bun.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** throughput comparison on a current release; committed startup and throughput harness with hardware
- **Pages the verifier opened:**
  - <https://github.com/vercel-labs/scriptc>
  - <https://github.com/vercel-labs/scriptc/commits>
  - <https://github.com/vercel-labs/scriptc/tree/main/docs>
  - <https://github.com/vercel-labs/scriptc/issues/357>
  - <https://github.com/vercel-labs/scriptc/issues/113>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/README.md>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/package.json>
  - <https://github.com/jlucaso1/js-compiled>
  - <https://raw.githubusercontent.com/jlucaso1/js-compiled/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/vercel-labs/scriptc>
  - <https://github.com/vercel-labs/scriptc/commits>
  - <https://github.com/vercel-labs/scriptc/tree/main/docs>
  - <https://github.com/vercel-labs/scriptc/tree/main/docs/content/docs>
  - <https://github.com/vercel-labs/scriptc/tree/main/benchmarks/builds>
  - <https://github.com/vercel-labs/scriptc/tree/main/packages/runtime>
  - <https://github.com/vercel-labs/scriptc/tree/main/packages/runtime/src>
  - <https://github.com/vercel-labs/scriptc/tree/main/packages/runtime/vendor>
  - <https://github.com/vercel-labs/scriptc/issues?q=is%3Aissue>
  - <https://github.com/vercel-labs/scriptc/issues?q=is%3Aissue+performance>
  - <https://github.com/vercel-labs/scriptc/issues/357>
  - <https://github.com/vercel-labs/scriptc/issues/113>
  - <https://github.com/vercel-labs/scriptc/issues/261>
  - <https://github.com/vercel-labs/scriptc/issues/93>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/README.md>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/package.json>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/how-it-works.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/limitations.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/platforms.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/quickstart.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/dependencies.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/docs/content/docs/cli.mdx>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/packages/runtime/src/scr_runtime.h>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/packages/runtime/src/scr_string.c>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/packages/runtime/src/scr_loop_wsapoll.c>
  - <https://raw.githubusercontent.com/vercel-labs/scriptc/HEAD/packages/runtime/src/scr_async.c>
  - <https://github.com/jlucaso1/js-compiled>
  - <https://github.com/proggeramlug/js-compiled>
  - https://www.infoq.com/news/2026/09/vercel-scriptc-node/ (EGRESS_BLOCKED; WebSearch snippets only)
  - https://news.lavx.hu/article/vercel-labs-ships-scriptc-a-typescript-to-native-compiler-that-leaves-the-javascript-engine-behind (EGRESS_BLOCKED)
  - https://creuto.com/typescript-to-native-scriptc-startup (EGRESS_BLOCKED)
  - https://news.ycombinator.com/item?id=49063175 (WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vercel-labs/scriptc`) · [data/wave12/enrich/raw/github_com_vercel_labs_scriptc.json](../../../data/wave12/enrich/raw/github_com_vercel_labs_scriptc.json) (enrichment confidence 0.55)

</details>
