# weval

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Wasm partial evaluator that turns an annotated interpreter into an AOT compiler; about 3.6x over SpiderMonkey's interpreter on Richards.

| | |
|---|---|
| **Beats** | generic SpiderMonkey (StarlingMonkey) JavaScript interpreter running on Wasmtime |
| **Claimed result** | README: '3-5x speedups over the generic interpreter' (no methodology). StarlingMonkey PR #91 (merged 2024-07-31) quotes Richards score 676 with weval AOT versus 189 for the plain interpreter (about 3.6x, derived from page data). The PLDI 2025 paper 'Partial Evaluation, Whole-Program Compilation' (Fallin and Bernstein, PACMPL 9 PLDI, article 160) reports 2.17x on SpiderMonkey and 1.84x on PUC-Rio Lua over the generic interpreters (search snippet only). |
| **Workload** | Octane benchmarks (Richards in the quoted PR) on SpiderMonkey compiled to Wasm and then partially evaluated by weval, run under 'wasmtime serve', versus the same interpreter without weval. |
| **Metric** | throughput |
| **Compiler and flags** | StarlingMonkey built with cmake -DCMAKE_BUILD_TYPE=Release -DUSE_WASM_OPT=OFF -DWEVAL=ON; runtime is wasmtime serve (version not stated). |
| **Adoption** | 149 stars; used by StarlingMonkey and ComponentizeJS for AOT JavaScript on Wasm |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/bytecodealliance/weval) · [benchmark](https://github.com/bytecodealliance/StarlingMonkey/pull/91) |

## Verdict

StarlingMonkey PR #91 (2024-07-31) reports an Octane Richards score of 676 with the weval-compiled SpiderMonkey versus 189 for the plain interpreter, both under `wasmtime serve` with an unstated Wasmtime version and hardware (about 3.6x); the README states 3-5x without methodology. The PLDI 2025 paper reports 2.17x on SpiderMonkey's interpreter tier and 1.84x on PUC-Rio Lua (search snippet only; the PDF, arXiv and ACM pages are blocked here). Every figure is against the same interpreter without weval, not against another runtime.

## Use it when

- You ship a C or C++ interpreter compiled to wasm32 (JavaScript via StarlingMonkey or ComponentizeJS, Lua, a DSL) and the target forbids runtime code generation, so a JIT is not an option.
- Guest code is known at build time (bundled JS, scripts baked into a component), so it can be compiled ahead of time inside the Wizer snapshot.
- Per-request isolation (wasmtime serve, edge functions) where each instance starts from a snapshot and has no time to warm up a JIT.
- Using SpiderMonkey on Wasm already: StarlingMonkey (`cmake -DWEVAL=ON`) and ComponentizeJS (`--aot` / `enableAot: true`) wire it in, along with a prebuilt cache of inline-cache bodies.

## Skip it when

- As a faster Wasm engine: it speeds up an interpreter that runs inside Wasm and does nothing for ordinary compiled C, C++ or Rust modules; for those pick a runtime from the sibling list.
- Guest code that only appears at run time (eval, downloaded scripts) still runs in the unspecialized interpreter.
- Interpreters you cannot or will not annotate: without the context and stack intrinsics in the dispatch loop the partial evaluator has nothing to specialize.
- wasm64 or a 64-bit pointer build: the C++ wrapper static_asserts 32-bit Wasm pointers.
- Tight build-time or module-size budgets: specialization runs per requested function at build time and appends a body for each, and ComponentizeJS documents a roughly 2 GB minimum stack for the weval run.

## How it is fast

It applies the first Futamura projection: constant propagation over the interpreter's SSA (via the waffle IR) with the guest bytecode held constant, reading constant memory from the Wizer snapshot image. `weval_push_context`/`update_context` make the evaluator unroll the dispatch loop per guest pc, so each bytecode becomes straight-line code with its dispatch and operand decoding folded away. Operand-stack and locals virtualization intrinsics (`push.stack`, `read.local`, `sync.stack`) keep interpreter stack slots in Wasm SSA values instead of memory, and specialized loads and stores are elided; the engine's own compiler (Cranelift in Wasmtime) then sees ordinary code.

## Compared with alternatives

None of the sibling Wasm engines (Wasmtime-class JITs, Wasmi, WAMR, wasm3) help a JavaScript or Lua interpreter that itself runs inside Wasm; pick weval when the slow part is that guest interpreter and JIT is not allowed. Wizer, which weval embeds, only pre-initializes state and does not compile guest code; use both together.

## Integration

| | |
|---|---|
| **Form** | CLI binary and Rust crate (`weval` 0.5.0 on crates.io; prebuilt binaries via GitHub releases and the npm package @cfallin/weval), plus the header `include/weval.h` compiled into the interpreter |
| **Dependencies** | Tool: wasmtime 46.0.1 (Cranelift), wasmtime-wizer, waffle 0.2.0, wasm-encoder/wasmparser 0.251, rayon, tokio, sqlite (for --cache), bincode, sha2. Interpreter side: weval.h only (libc malloc/free/memcpy) plus a wasi-sdk clang toolchain. |
| **Minimum toolchain** | Rust edition 2021 (MSRV not documented); interpreter built with wasi-sdk clang (the repo's test uses -std=c++23; the C API is plain C) |
| **Platforms** | Output: any Wasm engine, wasm32 only. Tool: release binaries per host OS and architecture (StarlingMonkey downloads weval-&lt;version&gt;-&lt;arch&gt;-&lt;os&gt;.tar.xz); exact list not documented in the README. |
| **Thread safety** | Not applicable to the output (specialized functions behave like the originals); the tool parallelizes specialization with rayon. The request list in weval.h is a global linked list with no locking, written during single-threaded Wizer initialization. |
| **Drop-in for the baseline** | partial — the specialized module is a drop-in replacement for the interpreter's Wasm build and keeps the generic interpreter as fallback, but you must annotate the interpreter source and add a Wizer snapshot plus weval step to the build |

## Gotchas

- The C++ wrapper `weval::weval(dest, generic, func_id, num_globals, ...)` accepts `func_id` but never stores it: `req->user_id` stays uninitialized malloc memory. The --cache key is bincode of (user_id, args, num_globals) with the generic function index skipped (`#[serde(skip)]` in src/directive.rs), so with the cache enabled, keys can be nondeterministic (cache misses) or, if two generic functions are requested with identical argument bytes and equal garbage ids, collide on one cached body. Set `user_id` yourself or use the C struct API when using --cache.
- Cache entries are also keyed on the SHA-256 of the input module (pre-Wizer bytes for core modules, the snapshotted core module for components), so any rebuild of the interpreter invalidates the cache.
- `StoreArg<T&>` in weval.h constructs `StoreArg<T*>(args, &value)` instead of calling it, so specializing a reference-typed argument does not compile; pass pointers. `weval::weval()` also leaks the request and argument buffer if argument encoding fails (1 MiB argument cap).
- The evaluator constant-folds only integer ops (src/eval.rs has 'TODO: FP and SIMD'), so floating-point-heavy interpreter logic is transcribed rather than folded.

## Known shortcomings

- PR #91's 676 vs 189 is against weval's own generic interpreter; the PLDI 2025 paper (2.17x SpiderMonkey, 1.84x Lua) was seen only in search snippets (cfallin.org and the paper blocked), so a paper-access retier to B is possible. Licence Apache-2.0 WITH LLVM-exception; Rust.
- Only baseline is the project's own interpreter without weval (StarlingMonkey Richards 676 vs 189, no hardware stated); no rival runtime measured. Enricher found a bug in include/weval.h: the C++ wrapper weval::weval() takes func_id but never sets req-&gt;user_id, so it stays uninitialized malloc memory; the cache key is bincode(user_id, args, num_globals) and skips the generic function index, so with --cache keys are nondeterministic and two generic functions given identical argument bytes can collide. StoreArg&lt;T&&gt; does not compile if used. Constant folding is integer-only. PLDI paper unreachable from this environment (cfallin.org 403).

## Caveats and trade-offs

The baseline is the project's own interpreter without weval, not a rival runtime, so the speedup says nothing about how Wasmtime or V8 compare. The README gives a range without methodology, and the PR states neither hardware nor the Wasmtime version. The peer-reviewed paper (cfallin.org PDF, arXiv 2411.10559, ACM DL 10.1145/3729259) was blocked from this environment, so the 2.17x/1.84x averages come from search snippets only and the tier is held at C; once the paper can be read it is a candidate for B. The licence is Apache-2.0 with the LLVM exception.

Needs the interpreter source to be annotated with weval's intrinsics (include/weval.h) and a Wizer snapshot step in the build; the output is Wasm, so it still runs on any Wasm engine, but compile time and module size grow.

## Maintenance

Active Bytecode Alliance project by Chris Fallin (0.5.0 on 2026-09-10 added component support; 24k crates.io downloads; StarlingMonkey pins v0.4.1); Apache-2.0 WITH LLVM-exception and usable today through StarlingMonkey or ComponentizeJS, though building it into your own interpreter takes real annotation work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** StarlingMonkey PR #91 (merged 2024-07-31) reports Richards 676 with weval versus 189 without, using a stated build command but no hardware or Wasmtime version. The peer-reviewed PLDI 2025 paper is visible only as search snippets, since cfallin.org, arXiv and the ACM DL are blocked, so it is held at C.
- **Verifier notes:** Confirmed the PR numbers and the README claim. Licence corrected to Apache-2.0 WITH LLVM-exception (Cargo.toml and LICENSE). The PLDI 2025 paper is real (two search snippets agree on 2.17x SpiderMonkey and 1.84x Lua), but its PDF is EGRESS_BLOCKED, so it is a paper-access retier candidate for B. Shortcoming: the baseline is its own unspecialized interpreter, with no hardware stated.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** benchmark against a rival runtime with hardware stated, fix to user_id initialisation
- **Pages the verifier opened:**
  - <https://github.com/bytecodealliance/weval>
  - <https://github.com/bytecodealliance/weval/commits/main>
  - <https://github.com/bytecodealliance/StarlingMonkey/pull/91>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/bytecodealliance/weval>
  - <https://github.com/bytecodealliance/weval/commits/main>
  - <https://github.com/bytecodealliance/weval/issues>
  - <https://github.com/bytecodealliance/weval/tree/main/src>
  - <https://github.com/bytecodealliance/weval/tree/main/tests/simple>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/include/weval.h>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/src/eval.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/src/directive.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/src/cache.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/src/component.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/tests/simple/simple.cpp>
  - <https://raw.githubusercontent.com/bytecodealliance/weval/HEAD/tests/simple/Makefile>
  - <https://github.com/bytecodealliance/StarlingMonkey/pull/91>
  - <https://raw.githubusercontent.com/bytecodealliance/StarlingMonkey/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/StarlingMonkey/HEAD/cmake/weval.cmake>
  - <https://raw.githubusercontent.com/bytecodealliance/ComponentizeJS/HEAD/README.md>
  - <https://crates.io/api/v1/crates/weval>
  - WebSearch snippet: 'Partial Evaluation, Whole-Program Compilation' (PLDI 2025; cfallin.org PDF and themoonlight.io review EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bytecodealliance/weval`) · [data/wave12/enrich/raw/github_com_bytecodealliance_weval.json](../../../data/wave12/enrich/raw/github_com_bytecodealliance_weval.json) (enrichment confidence 0.75)

</details>
