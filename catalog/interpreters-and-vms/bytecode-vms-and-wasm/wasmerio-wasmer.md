# Wasmer (LLVM backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Rust` · `MIT (repository); BUSL-1.1 for the LLVM and Singlepass compiler crates from Wasmer 6.0` · 🟢 active

> Rust WebAssembly runtime whose optional LLVM backend runs WASI code about 1.15x faster than Wasmtime and 1.34x faster than V8.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift) and V8 (Node.js) |
| **Claimed result** | Frank Denis libsodium CSVs (2022-12, 69 rows): wasmer-llvm 0.872x wasmtime's time and 0.747x node's (0.841x and 0.753x on rows at or above 5000 units); against WasmEdge 0.819x overall but 1.031x (slower) on rows at or above 5000 and 1.104x above 100000, so the WasmEdge win rests on about 18 tiny rows; 0.858x of wasmer-cranelift (about 1.17x, 0.902x on rows at or above 5000), not the README's 50%. WAMR iwasm (1.277x faster, wins 68 of 69) and wasm2c are faster in the same data (derived from page data). |
| **Workload** | Libsodium's built-in crypto benchmark suite (about 70 primitives such as AEAD, hashes, signatures, box) compiled once to WASI and run in each runtime, December 2022 edition, wasmer with its LLVM compiler backend. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the 2022-12 edition. The 2021-Q1 edition README (same repo) says all runtimes were built from git in release mode, the wasm came from libsodium's dist/wasm32-wasi.sh --bench with LLVM 11.1.0 and wasm-opt -O4, identical wasm files for every runtime. |
| **Adoption** | 21.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/wasmerio/wasmer) · [benchmark](https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res) |

## Verdict

Frank Denis's December 2022 run of libsodium's built-in benchmark suite compiled once to WASI (about 70 crypto primitives, the same wasm for every runtime, compile time excluded; per a snippet of his post, a Zen 2 CPU pinned to one core, with runtime versions and flags unstated) gives wasmer-llvm 0.872x Wasmtime's per-test time and 0.747x Node/V8's. These are geomeans over 69 shared tests, faster on 54 and 60 respectively (derived from page data). I reproduced both figures exactly from the CSVs; dropping the tiny rows gives 0.841x and 0.753x, and WAMR's iwasm and wasm2c stay faster than wasmer-llvm.

## Use it when

- Long-running, CPU-bound WASI modules (crypto, codecs, numeric kernels) where steady-state throughput matters more than compile latency, and compiled modules can be cached or serialized.
- You already embed Wasmer (Rust or C API, WASIX) on its default Cranelift backend: swapping in LLVM gave a 0.858x geomean time (about 1.17x) on the 2022-12 libsodium suite, or about 1.08-1.10x on the non-trivial rows (derived from page data).
- Ahead-of-time pipelines: compile with LLVM on a build machine (cross-compilation is supported), ship the serialized artifact and run it headless without LLVM on the target.
- x86-64 or aarch64 hosts on Linux, macOS or Windows where an LLVM 22 toolchain can be installed for the build.

## Skip it when

- Startup- or compile-latency-sensitive work (cold starts, untrusted uploads, blockchains): LLVM compiles far slower than Cranelift or Singlepass. Wasmer's own Singlepass README recommends Singlepass where JIT bombs are a risk, and the 7.1 changelog says huge functions had to drop optimization (Python compile time from about 90 s to about 10 s). A Wasmer 2.2 blog snippet (page blocked) describes a module where Cranelift took about 10 minutes and the LLVM compile was stopped after 3 hours.
- When peak steady-state speed is the only goal: in the same 2022-12 data WAMR's iwasm (wasmer-llvm takes 1.277x its time, faster on 1 of 69 tests) and wasm2c (1.171x) are faster. WasmEdge is also faster on every row large enough to measure well (see gotchas).
- Production use of Wasmer 6.0 or later with the LLVM backend when you are not a paying Wasmer sponsor: the crate is BUSL-1.1. The last MIT release of wasmer-compiler-llvm is 5.0.6 (2025-05-02).
- SIMD-heavy or unusual store patterns: open issues report large LLVM-backend slowdowns for v128.bitselect feeding extends (#6535), i64x2 shifts by 32..63 (#6529), dynamic i8x16 shifts (#6521), store16 and rem_u-addressed stores (#6491, #6489), f64.convert_i64_u (#6083) and memory.size (#6147).
- Code written against the Wasmtime embedding API or Node's WASI: this is a different runtime and API, not a drop-in replacement.

## How it is fast

Each Wasm function is lowered to its own LLVM IR module (via inkwell) and the functions are compiled in parallel on a rayon pool. Ordinary-size functions get a hand-picked function-level pass list (SCCP, early-CSE, SROA, aggressive-instcombine, jump threading, GVN, DSE, loop-rotate, indvars, memcpyopt), and code generation runs at OptimizationLevel::Aggressive with the host CPU's feature flags. Statically reserved linear memories rely on guard pages instead of explicit bounds compares (dynamic memories get a check marked likely-in-bounds with llvm.expect). Memory 0's base pointer is passed as a hidden first argument (the 'm0' or pass-params optimization, on by default since 7.1), and memory accesses carry per-memory TBAA tags. There is no cross-function inlining because each function is its own module, and functions above a size threshold drop to an O1-style pipeline; both cap how close it gets to whole-module LLVM AOT runtimes such as WAMR's wamrc, wasm2c or WAVM.

## Compared with alternatives

Pick it over Wasmtime and V8 (and over Wasmer's own Cranelift default) when you are already on Wasmer and want steady-state throughput on long-running modules. If peak throughput is the only goal, the WAMR (iwasm) and wasm2c siblings were faster on the same libsodium data. For startup-bound work, interpreters such as Wasmi, wasm3 or Fizzy are the right choice.

## Integration

| | |
|---|---|
| **Form** | crate (wasmer plus wasmer-compiler-llvm), C API library (lib/c-api), or the wasmer CLI |
| **Dependencies** | A system LLVM 22 install (llvm-config-22 on PATH or LLVM_SYS_221_PREFIX; on Debian also libpolly-22-dev); inkwell 0.10 and rayon; Cranelift is the default compiler when LLVM is not enabled |
| **Minimum toolchain** | Rust 1.96 (workspace rust-version, edition 2024) and LLVM 22.1.x exactly |
| **Platforms** | The LLVM backend initializes targets for x86-64, aarch64, riscv64 and loongarch64. BUILD.md covers Linux, macOS and Windows (LLVM 22.1 installer). Prebuilt CLI assets exist for linux amd64/aarch64/riscv64, darwin arm64 and windows; the changelog says LLVM was added to the macOS ARM64 binaries in 5.0.1, but whether every prebuilt binary includes LLVM is not documented. |
| **Thread safety** | Engine and Module are shared through cheap clones (cloning a Module is a shallow copy); every call takes &mut Store, so one thread drives a Store at a time. Compilation itself runs in parallel across functions (num_threads defaults to available_parallelism). |
| **Drop-in for the baseline** | partial: inside Wasmer it is a one-line compiler swap (Store::new(LLVM::new()) or --llvm); against Wasmtime or V8 it is a different runtime with a different API |

## Gotchas

- Licence split: the repository and its badge say MIT, but wasmer-compiler-llvm and wasmer-compiler-singlepass from 6.0.0 (2025-04-24) are under the Business Source License 1.1 (crates.io lists them as 'non-standard'). Production use is allowed only for Wasmer sponsors; each version becomes MPL 2.0 four years after publication. The last MIT LLVM crate is 5.0.6 (2025-05-02). The benchmarked 2022 build was MIT-era (release dates suggest 3.0.x to 3.1.0; the version is not stated).
- The build needs LLVM 22 exactly: BUILD.md says any other version silently disables the backend, so check the 'Enabled Compilers:' banner.
- Semantics knobs: by default, user memory loads and stores on static memories are marked volatile so LLVM cannot delete them, which costs speed (issue #3987 shows a dead load emitted before each store). Non-volatile memops are faster but the code calls them 'not 100% SPEC compliant'; they are switched on automatically for WASIX modules (PR #6212), with --disable-non-volatile-memops to opt out. NaN canonicalization is off by default.
- Harness flaw in the benchmark: about 18 of the 70 libsodium rows are tiny (values under 5000 for every runtime; onetimeauth2 is recorded as 0 or 1). The 2022 run's units and timer are undocumented: today's cmptest.h, with ITERATIONS=200 and a microsecond clock, could only print multiples of 5000. The wins over Wasmtime and V8 survive dropping those rows (0.841x and 0.753x on 51 rows at 5000 or above). The apparent geomean win over WasmEdge (0.819x on 69 rows, but faster on only 31) comes from the tiny rows: on rows at 5000 or above, wasmer-llvm takes 1.031x WasmEdge's time (faster on 15 of 51), and 1.104x on rows at 100000 or above. The first-party README claim of 'about 50% faster' than Cranelift is not reproduced: 0.858x wasmer-cranelift's time (about 1.17x faster) on 70 rows, 0.902x on rows at 5000 or above (all derived from page data).

## Known shortcomings

- In the Frank Denis libsodium CSVs behind the 0.872x-of-wasmtime and 0.747x-of-node figures, WAMR iwasm (a listed baseline) is faster (wasmer-llvm takes 1.277x its time and wins 1 of 69 tests) and wasm2c is faster too; no CPU model or versions. The LLVM and Singlepass backends are BUSL-1.1 from Wasmer 6.0 (usability mixed) while the measured numbers come from the old MIT-era backend; the 2026 Denis post snippets put Wasmer ahead of Wasmtime.
- Enricher: about 18 of the 70 libsodium rows are tiny (under 5000 units, onetimeauth2 at 0 or 1) with the 2022 units and timer undocumented (today's cmptest.h uses ITERATIONS=200 on a microsecond clock, so values are multiples of 5000); the wins over wasmtime and node survive on rows at or above 5000 (0.841x and 0.753x), but the apparent win over WasmEdge (0.819x, faster on 31 of 69) comes only from the tiny rows and WasmEdge is faster on rows at or above 5000 (1.031x, 1.104x above 100000). The README's 'LLVM about 50% faster than Cranelift' is not reproduced (0.858x of wasmer-cranelift time, 0.902x on rows at or above 5000). Per-function LLVM modules with no inlining, volatile memory ops by default (#3987), requires exactly LLVM 22 (other versions silently disable the backend), BUSL-1.1 from 6.0.0 with the last MIT crate 5.0.6 (2025-05-02); open LLVM performance issues #6535, #6529, #6521, #6491, #6489.

## Caveats and trade-offs

Ratios are derived from the raw per-benchmark CSVs (wasmer-llvm.csv, wasmtime.csv, node.csv; values are libsodium's per-iteration times from test/default/cmptest.h, lower is better) in the author's benchmark repo (ISC, archived 2026-08-19), geometric mean over 69 shared rows. The 2022-12 folder has no README; the matching post (00f.net, 2023-01-04, blocked here, snippet only) says the runs used a Zen 2 CPU pinned to one core with each test run 200 times, but no exact CPU model, runtime versions or flags are reachable. Compile time is not part of the measured numbers (LLVM compile is far slower). In the same dataset WAMR's iwasm, a listed baseline, beats wasmer-llvm: wasmer-llvm takes 1.277x iwasm's time (faster on 1 of 69) and 1.171x wasm2c's time (faster on 10 of 70) (derived from page data), and the 2023 post (snippet only) names iwasm the top runtime; so wasmer-llvm beats Wasmtime and V8 but not WAMR AOT on this workload. The 2021-Q1 README by the same author ranked WAVM about 15% ahead of wasmer-llvm. Snippets of the author's 2026 posts (blocked) say Wasmer was the best performer with WAVM, WAMR and Wasmtime close, and that wasm2c used 0.887x Wasmer's time and 0.814x Wasmtime's (Wasmer about 8% faster than Wasmtime, derived from snippet data); not checked on the page. The win is specific to the LLVM backend (wasmer-cranelift ties Wasmtime at 1.02x, singlepass is 3.12x slower) and to this crypto-heavy workload. LICENCE WARNING: the repo root is MIT, but lib/compiler-llvm/LICENSE and lib/compiler-singlepass/LICENSE are Business Source License 1.1 for Wasmer LLVM/Singlepass 6.0.0 or later, with production use allowed only for Wasmer sponsors (change date four years after publication, change licence MPL 2.0); the December 2022 numbers were measured on the older MIT-era LLVM backend. Wasmer is itself a named baseline; this entry is evidence that its LLVM backend beats Wasmtime's default and V8 on steady-state throughput. [retier] No CPU model or versions; about 18 of 70 rows are tiny (under 5000 units, onetimeauth2 at 0 or 1) with the 2022 units and timer undocumented. WAMR iwasm, a listed baseline, is faster. The LLVM and Singlepass backends are BUSL-1.1 from Wasmer 6.0 (last MIT crate 5.0.6, 2025-05-02), so usability is mixed, and the measured numbers come from the old MIT-era backend; per-function LLVM modules with no inlining, volatile memory ops by default (#3987), requires exactly LLVM 22. 2026 Denis post snippets put Wasmer ahead of Wasmtime. Rust.

The LLVM backend compiles far slower than Cranelift and needs a matching LLVM install (LLVM 22 now); for startup-sensitive use the Cranelift or Singlepass backends are the practical choices. Wasmer is a runtime with its own WASIX layer, not a drop-in for the Wasmtime embedding API.

## Maintenance

Actively maintained (7.5.0 released 2026-10-01, commits on 2026-10-06, 21.1k stars) and usable as a crate or CLI, but the LLVM backend's BUSL-1.1 licence since 6.0 limits production use to Wasmer sponsors unless you pin the MIT 5.0.6 release; the speedup was measured on a 2022 MIT-era build with undocumented units for the tiny rows.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by Frank Denis (libsodium author, not affiliated with Wasmer) with public benchmark code (libsodium dist/wasm32-wasi.sh --bench) and raw per-runtime CSVs; the 2022-12 edition states no CPU model, runtime versions or flags, so not A.
- **Verifier notes:** Derived geomeans reproduce exactly from the CSVs (0.872 vs wasmtime on 69 rows, faster on 54; 0.747 vs node, faster on 60; cranelift 1.019; singlepass 3.119). Main shortcomings: WAMR iwasm (listed baseline) and wasm2c are faster than wasmer-llvm in the same data, no hardware or versions for the 2022-12 edition, fast backend now BUSL-1.1. The record's statement that the 2026 post puts Wasmtime ahead of Wasmer conflicts with the snippets I saw (Wasmer best, Wasmtime close); I replaced it in caveats.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res>
  - <https://github.com/jedisct1/webassembly-benchmarks>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-singlepass.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/master/test/default/cmptest.h>
  - <https://github.com/wasmerio/wasmer>
  - <https://github.com/wasmerio/wasmer/commits/main>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/LICENSE>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-singlepass/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/LICENSE>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-cranelift/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-singlepass/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/api/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/docs/BUILD.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/src/config.rs>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/src/compiler.rs>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler-llvm/src/translator/code.rs>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/compiler/src/lib.rs>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/api/src/entities/store/mod.rs>
  - <https://raw.githubusercontent.com/wasmerio/wasmer/HEAD/lib/api/src/entities/module/mod.rs>
  - <https://github.com/wasmerio/wasmer>
  - <https://github.com/wasmerio/wasmer/commits/main>
  - <https://github.com/wasmerio/wasmer/tree/main/lib/compiler-llvm/src>
  - <https://github.com/wasmerio/wasmer/issues?q=is%3Aissue+llvm+performance>
  - <https://github.com/wasmerio/wasmer/issues?q=is%3Aissue+llvm+miscompil+OR+llvm+%22wrong+result%22>
  - <https://github.com/wasmerio/wasmer/issues/3987>
  - <https://github.com/wasmerio/wasmer/issues/6052>
  - <https://github.com/wasmerio/wasmer/security/advisories>
  - <https://github.com/wasmerio/wasmer/releases/tag/v7.5.0>
  - <https://github.com/wasmerio/wasmer/releases/expanded_assets/v7.5.0>
  - <https://crates.io/api/v1/crates/wasmer-compiler-llvm>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmer-singlepass.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasmedge.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wazero.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/bun.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2022-12/res/wasm3.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/master/test/default/cmptest.h>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/dist-build/wasm32-wasi.sh>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/1.0.18-RELEASE/dist-build/wasm32-wasi.sh>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/1.0.19-RELEASE/dist-build/wasm32-wasi.sh>
  - <https://github.com/jedisct1/libsodium/tree/master/dist-build>
  - https://00f.net/2023/01/04/webassembly-benchmark-2023/ (WebSearch snippet only)
  - https://wasmer.io/posts/wasmer-2_2 (WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasmerio/wasmer`) · [data/wave12/enrich/raw/github_com_wasmerio_wasmer.json](../../../data/wave12/enrich/raw/github_com_wasmerio_wasmer.json) (enrichment confidence 0.62)

</details>
