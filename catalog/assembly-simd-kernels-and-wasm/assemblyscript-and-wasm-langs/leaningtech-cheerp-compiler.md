# Cheerp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (LLVM/Clang based compiler)` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> LLVM/Clang-based C++ to WebAssembly and JavaScript compiler; vendor claims slightly smaller output than Emscripten at roughly equal speed.

| | |
|---|---|
| **Beats** | Emscripten (C/C++ to WebAssembly) |
| **Claimed result** | Cheerp 2.6rc1 release notes (search snippet): Cheerp output runs roughly 5% faster than Emscripten; Cheerp 3.0 post (snippet): about 7% smaller output and execution speed comparable to Emscripten |
| **Workload** | Vendor release-post comparison on Emscripten's own benchmark suite (Box2D, Bullet, zlib, LZMA) compiled with Cheerp 2.6rc1 and Emscripten 2.0.9, run on SpiderMonkey and V8, one MacBook Pro (Linux x86_64, TurboBoost disabled), averaged over three runs (snippet only; the post could not be opened) |
| **Metric** | throughput |
| **Hardware** | MacBook Pro, Linux x86_64, TurboBoost disabled (CPU model not stated; snippet only) |
| **Adoption** | 363 stars (cheerp-compiler); 1.2k stars (cheerp-meta) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/leaningtech/cheerp-compiler) · [benchmark](https://new.leaningtech.com/cheerp-2-6rc1-released/) |

## Verdict

Only first-party numbers exist: Leaning Technologies benchmarked Cheerp 2.6rc1 against Emscripten 2.0.9 on Emscripten's suite (Box2D, Bullet, zlib, LZMA) on one MacBook Pro running Linux with TurboBoost off, mean of three runs, and reported about 5% faster and 3% smaller output (search snippets only); the Cheerp 3.0 post against Emscripten 3.1.31 reports 7% smaller output and execution comparable on V8, SpiderMonkey and JavaScriptCore, with no CPU model or flags.

## Use it when

- C++ libraries that must live inside a JavaScript/TypeScript web app and call DOM or JS APIs directly, where Emscripten's embind/EM_JS glue is the pain point.
- Projects that want part of the code as plain JavaScript ([[cheerp::genericjs]], garbage-collected objects) and the hot part in linear-memory WebAssembly, from one C++ source.
- Download-size-sensitive web builds, where the vendor reports about 7% smaller output than Emscripten 3.1.31 on Emscripten's own test suite.
- Teams that want a single-step toolchain (no separate wasm-opt pass) under Apache-2.0 WITH LLVM-exception, the same licence as upstream LLVM.

## Skip it when

- When run-time speed is the reason to switch: the newest vendor data (Cheerp 3.0 vs Emscripten 3.1.31) claims execution 'comparable' to Emscripten, and no independent measurement shows Cheerp faster.
- Multithreaded code (pthreads, WebAssembly atomics): missing in the last tagged release, cheerp-3.0; thread and atomics work exists only on the master branch (libthreads.bc, a sharedmem feature flag, CheerpOS threads), with no tag after March 2023.
- Large ports that rely on Emscripten's ecosystem: virtual filesystem, SDL/GL ports, emscripten ports and wide community support; Cheerp issue #76 (2018) showed several Emscripten benchmark programs failing or not building under Cheerp, though that predates 2.0.
- Type-unsafe C (custom pool allocators, qsort/bsearch/memcmp on untyped memory) in the JavaScript (genericjs) target, which maps C++ objects to JS objects and rejects such code; the wasm target does not have this restriction.

## How it is fast

Cheerp keeps LLVM bitcode as the object and library format and internalizes every definition at link time, so whole-program LTO, a devirtualizer, identical code folding, PreExecuter (runs global constructors at compile time) and PartialExecuter (drops code proven unreachable from known arguments) run before codegen. Its own CFGStackifier (successor to a Relooper) and Registerize (locals allocator) emit final WebAssembly in one step, with no Binaryen wasm-opt post-pass. The vendor credits these mainly with smaller output; for run time the 2023 post claims only parity with Emscripten.

## Compared with alternatives

Among the catalogued wasm entries it is, with the msf/wasmplay Zig build, one of only two whose baseline is Emscripten itself; pick Cheerp when C++ must interoperate tightly with JavaScript and the DOM or ship as smaller output, not for speed, since the wasmplay Zig build reports a measured 1.29x win over em++ while Cheerp claims parity.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (prebuilt: Debian/Ubuntu PPA per the 3.0 post, an npm 'cheerp' package per the cheerp-meta badge, a macOS DMG built in CI; or build from source) |
| **Dependencies** | cheerp-compiler (LLVM/Clang fork) plus cheerp-musl, cheerp-utils and cheerp-libs (libc++/libc++abi built twice, for genericjs and wasm) |
| **Minimum toolchain** | Building from source: CMake and Ninja, with LLVM built with -DCLANG_ENABLE_OPAQUE_POINTERS=OFF; Cheerp 3.0 is rebased on LLVM/Clang 16. Compiled code: most of C++20 (all of it in WebAssembly mode per the FAQ draft). |
| **Platforms** | Output runs in browsers (V8, SpiderMonkey, JavaScriptCore) and Node, or in WASI runtimes such as Wasmtime for -target cheerp-wasm-wasi; WebAssembly SIMD supported since 3.0 |
| **Thread safety** | Single-threaded output in the tagged 3.0 release (WebAssembly atomics and multithreading listed as the missing feature); Web Workers can be used as separate instances |
| **Drop-in for the baseline** | partial: clang-compatible command line, but it replaces emcc with different flags, runtime, JS loader, libc and interop attributes, and some Emscripten-specific APIs and ports have no equivalent |

## Gotchas

- The speed claim is shaky and vendor-only: snippets of the 2.6rc1 post (December 2020, Box2D, Bullet, zlib and LZMA against Emscripten 2.0.9 on V8 and SpiderMonkey, mean of three runs) give about 5% faster and about 3% smaller, but the Cheerp 3.0 post (March 2023, readable in leaningtech/labs) claims only 7% smaller output and 'comparable' execution against Emscripten 3.1.31; its data sits in Google Sheets and leaningtech.com SVG charts that could not be opened here, and no CPU, flags or per-benchmark numbers are given.
- Past vendor comparisons have needed correction by Emscripten's author: issue #8 (2016) found the Cheerp 1.2 '10x faster startup' figure timed from the first executed line to main(), excluding parsing (about 15 ms of the real startup), and the real gap was up to about 2x; issue #76 (2018) found Emscripten 1.37.36 output 23-43% smaller than Cheerp where Cheerp's site claimed 30% smaller, until benchmarks were edited to drop printf.
- Docs drift: the docs badge and changelog stop at 3.0 while master has gained threads, resizable memory and CheerpOS work; the draft porting guide still says exceptions are unsupported (they are opt-in with -fexceptions since 2.7); the default linear heap size is given as 1 MB on the targets page and 8 MB on the -cheerp-linear-heap-size page.
- C++ exceptions are opt-in (-fexceptions), unlike native compilers, and the -cheerp-avoid-wasm-traps flag is needed to stop float-to-int conversions from trapping.

## Known shortcomings

- Vendor-only evidence from snippets (leaningtech.com blocked): the 2.6rc1 post (Dec 2020) says about 5% faster than Emscripten 2.0.9 and the 3.0 post (Mar 2023) says parity; no flags or CPU model; fork of llvm/llvm-project.
- No current speed win: the Cheerp 3.0 post (readable in the leaningtech/labs blog source) claims only 7% smaller output and 'comparable' speed against Emscripten 3.1.31, with its data in unreachable Google Sheets; the 2.6rc1 '5% faster' remains snippet-only. Past vendor claims were corrected by Emscripten's author: issue #8 (Cheerp 1.2 '10x startup' timed first line to main(), parsing excluded) and issue #76 (Emscripten output 23-43% smaller in 2018). Last tag cheerp-3.0 (2023-03); threads only on master.

## Caveats and trade-offs

Snippet only: leaningtech.com, new.leaningtech.com and labs.leaningtech.com did not resolve from this environment, so the speed claim comes from WebSearch snippets of vendor posts. The 5% figure is from the Cheerp 2.6rc1 post (December 2020 era, against Emscripten 2.0.9) and the same snippets give output about 3% smaller; the later Cheerp 3.0 post (March 2023, when Cheerp was relicensed from GPLv2/commercial to Apache-2.0 with LLVM exception) claims about 7% smaller output and execution speed comparable to Emscripten, i.e. parity, not a win. The only independent comparisons found (Palant 2016; i-programmer, Cheerp 1.x) are asm.js-era and had Emscripten ahead or equal. No benchmark in the cheerp-compiler or cheerp-meta READMEs; compiler flags and CPU model never stated. Treat as weak: smaller output, about equal speed.

Compiles C++ to WebAssembly and JavaScript; the vendor 3.0 post says multithreading and WebAssembly atomics were not yet supported at 3.0. Different JS/DOM interop model than Emscripten (can call DOM directly).

## Maintenance

Actively developed by Leaning Technologies (last commit 2026-10-09, used to build CheerpJ, CheerpX and WebVM) and Apache-2.0 WITH LLVM-exception since 3.0, but the last tagged release is cheerp-3.0 from March 2023, so new features such as threads are master-only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Only vendor numbers exist, read from WebSearch snippets of the Cheerp 2.6rc1 release post (Emscripten's public benchmark suite: Box2D, Bullet, zlib, LZMA vs Emscripten 2.0.9 on SpiderMonkey and V8, one MacBook Pro, mean of 3 runs); flags and CPU model are not stated and the post could not be opened, so first-party snippet-only evidence stays C. Neither the cheerp-compiler nor the cheerp-meta README carries a benchmark (cheerp-meta only says 'best performing ... compiler available on the market', no numbers).
- **Verifier notes:** Record is accurate; claim is marginal (5% faster in a 2020 vendor post, parity in the 2023 vendor post) and snippet-only. The vendor post URL set as benchmark_url came from WebSearch results and could not be opened (DNS failure for new.leaningtech.com); license Apache-2.0 WITH LLVM-exception confirmed from LICENSE.TXT and the cheerp-meta README, last commit 2026-10-09 and 363 stars confirmed. Shortcomings: vendor-only, snippet-only, near-parity, stale baseline version, no flags or CPU model.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `hardware`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/leaningtech/cheerp-compiler>
  - <https://github.com/leaningtech/cheerp-compiler/commits/master>
  - <https://raw.githubusercontent.com/leaningtech/cheerp-compiler/master/LICENSE.TXT>
  - <https://raw.githubusercontent.com/leaningtech/cheerp-compiler/master/README.md>
  - <https://raw.githubusercontent.com/leaningtech/cheerp-meta/HEAD/README.md>
  - <https://github.com/orgs/leaningtech/repositories?q=bench>
- **Sources the enricher read:**
  - <https://github.com/leaningtech/cheerp-compiler>
  - <https://raw.githubusercontent.com/leaningtech/cheerp-compiler/master/README.md>
  - <https://raw.githubusercontent.com/leaningtech/cheerp-meta/HEAD/README.md>
  - <https://github.com/leaningtech/cheerp-compiler/commits/master>
  - <https://github.com/leaningtech/cheerp-compiler/tags>
  - <https://github.com/leaningtech/labs>
  - <https://github.com/leaningtech/labs/tree/main/sites>
  - <https://github.com/leaningtech/labs/tree/main/sites/labs/src/content/blog>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/labs/src/content/blog/cheerp-3-now-permissively-licensed.md>
  - <https://github.com/leaningtech/labs/tree/main/sites/cheerp/src/content/docs>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/91-vs-emscripten.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/99-changelog.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/90-faq.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/00-overview.mdx>
  - <https://github.com/leaningtech/labs/tree/main/sites/cheerp/src/content/docs/11-guides>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/11-guides/70-porting.md>
  - <https://github.com/leaningtech/labs/tree/main/sites/cheerp/src/content/docs/12-reference>
  - <https://github.com/leaningtech/labs/tree/main/sites/cheerp/src/content/docs/12-reference/10-command-line-options>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/12-reference/10-command-line-options/10-targets.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/12-reference/10-command-line-options/99-other.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/12-reference/10-command-line-options/70-linear-heap-size.md>
  - <https://raw.githubusercontent.com/leaningtech/labs/main/sites/cheerp/src/content/docs/12-reference/10-command-line-options/45-exceptions.md>
  - <https://github.com/leaningtech/cheerp-meta/issues>
  - <https://github.com/leaningtech/cheerp-meta/issues?q=is%3Aissue+performance>
  - <https://github.com/leaningtech/cheerp-meta/issues/8>
  - <https://github.com/leaningtech/cheerp-meta/issues/76>
  - <https://github.com/leaningtech/cheerp-meta/issues/154>
  - https://docs.google.com/spreadsheets/d/e/2PACX-1vTg2EnhrKAhvDhlig9QQDn6aBjk6XQUH4hg7XncVRO_8QU7D6P0KO415-Ab5tg_tfK7JMyXBZRnqJqu/pubhtml (DNS failure, not read)
  - WebSearch snippets for new.leaningtech.com/cheerp-2-6rc1-released/, new.leaningtech.com/?p=149, new.leaningtech.com/?p=160 and palant.info/2016/02/05/compiling-c-to-javascript-emscripten-vs-cheerp/ (pages not opened)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/leaningtech/cheerp-compiler`) · [data/wave13/enrich/raw/github_com_leaningtech_cheerp_compiler.json](../../../data/wave13/enrich/raw/github_com_leaningtech_cheerp_compiler.json) (enrichment confidence 0.6)

</details>
