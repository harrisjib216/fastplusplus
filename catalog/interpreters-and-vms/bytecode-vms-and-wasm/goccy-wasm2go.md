# wasm2go

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Ahead-of-time WebAssembly-to-Go translator; on its author's SQL engine it beats wazero on startup and call-heavy queries, ties on long scans.

| | |
|---|---|
| **Beats** | wazero (an equivalent wazero-driven build of the same wasm module) |
| **Claimed result** | One-time cold compile 4.67 s (wazero) vs 0.56 s (8.4x); select_constant 49.3 us vs 2.7 us (18x); rank_dense_rank 220 ms vs 8.4 ms (26x); lag_lead 229 ms vs 10.0 ms (23x); json_extract_pipeline 878 ms vs 10.8 ms (81x); but q1_lineitem_pricing_summary 64.2 ms (wazero) vs 68.2 ms (0.94x) and q3_shipping_priority 33.9 s vs 37.3 s (0.91x), i.e. within 10% slower on long scan-heavy queries. |
| **Workload** | A roughly 13 MB SQL parser/analyzer wasm module with 22 SQL benchmark queries, run once via wasm2go-generated Go (amd64/arm64 assembly bodies from an SSA register allocator) and once via wazero. |
| **Metric** | latency |
| **Hardware** | macOS on Apple Silicon (model not stated) |
| **Compiler and flags** | go test -bench=. -benchtime=200ms; Go version and wazero version not stated |
| **Adoption** | 87 stars, 7 forks; pkg.go.dev lists github.com/goccy/wasm2go/transpile v0.5.15 |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/goccy/wasm2go) · [benchmark](https://github.com/goccy/wasm2go) |

## Verdict

On the 22-query googlesqlite corpus (go test -bench, -benchtime=200ms, prepared statements re-executed in the timed loop) running the 13 MB GoogleSQL wasm module, the README reports wasm2go against a wazero build of the same module on unspecified Apple Silicon: 8.4x faster first use, 18-81x faster on short scalar, window and JSON queries, and 6-9% slower on TPC-H q1 and q3. The author's later googlesqlite PR #19 re-ran 19 of the queries under Rosetta: 1.04-2.33x on the aggregate and most mixed queries, 4-78x on the scalar, window, JSON and information_schema queries, 0.95x on q1, 1.01x on q3 and 0.91x on wildcard_table_scan. The Go version, CPU model and wazero version are not stated for either run.

## Use it when

- A Go service that embeds a large, fixed C/C++ library compiled to wasm (the GoogleSQL parser/analyzer in goccy/go-googlesql and googlesqlite is the reference user) and must stay cgo-free.
- Workloads that make many short calls into the module, such as scalar SQL expressions, window functions or JSON extraction, where wazero's per-call boundary dominated (77-81x and 25-28x gaps in the author's runs).
- Processes where startup matters: about 0.16-0.56 s init versus 4.35-4.67 s for wazero compiling the same 13 MB module at process start, in the author's runs.
- Shipping one Go binary for linux, darwin, windows and the BSDs without a JIT or an on-disk compilation cache.

## Skip it when

- Modules that must be loaded, swapped or sandboxed at runtime (plugins, user-supplied wasm): the module is baked into Go source at build time, so use wazero or a sibling runtime.
- Long compute-bound runs inside the module: the author's TPC-H rows are within about 10% of wazero either way (0.91-1.01x), so the translation step buys little there.
- Tight build budgets: go-googlesql's README reports about 76 s and 5.6 GB peak memory for a cold build of the generated code and a 63 MB binary, a cost the 'cold compile' row leaves out.
- Callers that are not Go: the output is a Go package, not callable from C++; wasm2c (WABT) or w2c2 fit native hosts.
- Risk-averse production use today: the project started in April 2026 (62 commits) and fixed miscompiles in July and August 2026.

## How it is fast

Calls into the module are plain Go function calls, so there is no host-guest boundary crossing and no runtime compilation at startup, which is where the large wins come from. On amd64 the current gcasm backend compiles the generated pure-Go bodies with the host Go toolchain at generation time, captures the -S listings and rewrites them into ABI0 .s files, adding fused SIMD regions, O(1) jump tables, a leaf inliner and whole-function dead-code elimination. Per the transpile.go doc comment, other architectures build the pure-Go bodies, which the author says beat the retired own-emitter assembly backend (internal/asmgen) in every configuration they measured.

## Compared with alternatives

Pick it over wazero-family runtimes such as wazy when the module is known at build time, the host is Go, and per-call overhead or startup dominates. Pick wasm2c (WABT) or w2c2 when the host is C/C++. Pick a runtime (wazy, Wasmi, WAMR) when modules arrive at runtime or must stay sandboxed in a separate engine.

## Integration

| | |
|---|---|
| **Form** | source-drop (generated Go package with .s files and an embedded data sidecar); the translator itself is a Go module and CLI |
| **Dependencies** | Generated code: Go standard library only (per the README's WASI section). Translator: wazero v1.11.0 (go.mod; the tests use it as a differential oracle) and golang.org/x/sys; tests need wat2wasm from WABT. |
| **Minimum toolchain** | Go 1.25 (go.mod declares go 1.25.0); the amd64 assembly is derived from the host Go compiler's -S output at generation time |
| **Platforms** | amd64 assembly path (CI runs it with GOAMD64=v2); arm64 SIMD and override splices; pure-Go fallback on every other GOOS/GOARCH |
| **Thread safety** | not documented for sharing one instance across goroutines; wasi-threads are supported, with each wasm thread mapped to a goroutine (PR #30) |
| **Drop-in for the baseline** | partial: same wasm module and semantics, but a build-time code-generation step and a generated Go API replace wazero's runtime Instantiate/Call interface |

## Gotchas

- The README's Performance table comes from PR #1 (2026-05-24) and predates both the asmgen backend (PR #7, 2026-06-10) that the README describes and the gcasm backend that replaced it, so the published numbers were not measured on today's code generator. The only public harness is googlesqlite's bench/runner_test.go (the same 22 queries, now wasm2go-only), and googlesqlite PR #19 re-ran the comparison with different results: select_constant 6.5x rather than 18x, q3 1.01x rather than 0.91x, startup 27x rather than 8.4x, and this run was on 'Apple M-class, macOS, Go via Rosetta'.
- Harness flaw: if the README run also used an amd64 Go under Rosetta, as the sibling PR #19 run states, then wazero's runtime-generated machine code went through Rosetta's JIT translation while wasm2go's code was ahead-of-time translated. That handicaps the baseline. The 'cold compile' row times opening a connection plus SELECT 1 (init plus first query) for wasm2go against wazero's runtime compilation of the module, and it excludes the roughly 76 s Go build of the generated code.
- Per the CI workflow comments, amd64 builds at the default GOAMD64=v1 run only the pure-Go fallback: the amd64 assembly splices compile only into v2+ binaries. Build with GOAMD64=v2 or higher to get the fast path.
- Miscompile history: PR #25 (2026-07-10) fixed two bugs on very large modules that made generated code hang; PR #46 (2026-08-13) fixed an amd64 fused-region register clobber and loop-carry bug that produced garbage output on llama.cpp memory64 bundles; the CI notes a const-shuffle scratch clobber that reached a release. Test the generated package against wazero on your own module.

## Known shortcomings

- Harness and the 13 MB module are unpublished; no CPU, Go or wazero version; 6-9% slower than wazero on long TPC-H scans and the cold-compile row leaves out the Go build cost. Off-baseline (wazero); Go, not C++.
- Enricher: the README table comes from PR #1 (2026-05-24), older than the asmgen (PR #7) and current gcasm backends; the author's googlesqlite PR #19 rerun ran Go via Rosetta and disagrees (select_constant 6.5x not 18x, q3 1.01x not 0.91x, cold start 27x not 8.4x), so the README may also have handicapped wazero's JIT under Rosetta; the cold-compile row is connection open plus SELECT 1; amd64 at default GOAMD64=v1 runs only the pure-Go fallback; miscompile fixes in PRs #25 and #46 (amd64 garbage output, 2026-08-13).

## Caveats and trade-offs

First-party table on a roughly 13 MB SQL parser/analyzer module whose harness is not published in the repo (probably the GoogleSQL module behind goccy/go-googlesql, which switched from wazero to wasm2go in v0.3.0, but the README does not name it), so not reproducible; CPU model, Go version, wazero version and wazero mode (compiler or interpreter) are not stated; the wins are call-boundary and compile overhead on short queries, while compute-heavy TPC-H scans are about 6-9% slower than wazero; the cold-compile row excludes wasm2go's own Go build cost of the generated code (go-googlesql's README reports about 76 s and 5.6 GB peak RSS for a cold go test -c); no comparison with Wasmtime, Wasmer, WAMR or V8; github.com/hanzoai/wasm2go (0 stars, not marked as a fork) carries a copy of the same README; unrelated to ncruces' separate wasm2go translator used by ncruces/go-sqlite3. [retier] Harness and the 13 MB module are unpublished; no CPU, Go or wazero version. The README table comes from PR #1 (2026-05-24), older than the asmgen (PR #7) and current gcasm backends; the author's googlesqlite PR #19 rerun (Go via Rosetta) disagrees: select_constant 6.5x not 18x, q3 1.01x not 0.91x, cold start 27x not 8.4x, and if the README also ran under Rosetta the wazero JIT was handicapped. 6-9% slower on long TPC-H scans; the cold-compile row is connection open plus SELECT 1 and leaves out the Go build cost; amd64 at default GOAMD64=v1 runs only the pure-Go fallback; miscompile fixes in PRs #25 and #46 (2026-08-13). Off-baseline (wazero); Go.

Ahead-of-time translator, not a runtime: the wasm module is baked into Go source (plus amd64/arm64 assembly) so the module is fixed at build time rather than loaded at runtime; very large modules produce multi-file output; the pure-Go fallback applies on other architectures; output is Go, not callable from C++.

## Maintenance

Very active (v0.5.15, 2026-09-05; 0 open issues) and MIT-licensed, but five months old with recent miscompile fixes, and the published numbers predate the current backend, so treat it as promising but young and verify output against wazero.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table compares wasm2go with a wazero-driven build of the same module and every number in the record matches it; the 22-query benchmark harness and the 13 MB module are not in the repository (testdata holds only .wat/.wasm regression cases), and CPU model, Go and wazero versions are missing, so first-party tier C (the 81x row also exceeds 50x with methodology unstated).
- **Verifier notes:** Numbers and metadata (MIT, 87 stars, 7 forks, last commit 2026-09-05) verified. Shortcomings: unpublished harness and module, no CPU/Go/wazero versions, slower than wazero on long scans, compile row ignores Go build cost. Possible lead: ncruces' own wasm2go (go-sqlite3 discussion #361) has wazero comparisons on an Intel Core Ultra 7 258V (e.g. go-marisa lookup about 304 vs 343 ns/op), a different project.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/goccy/wasm2go>
  - <https://github.com/goccy/wasm2go/commits>
  - <https://github.com/goccy/wasm2go/tree/main/docs>
  - <https://github.com/goccy/wasm2go/tree/main/testdata>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/README.md>
  - <https://github.com/goccy/go-googlesql>
  - <https://github.com/hanzoai/wasm2go>
  - <https://github.com/ncruces/go-sqlite3/discussions/361>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/README.md>
  - <https://github.com/goccy/wasm2go>
  - <https://github.com/goccy/wasm2go/tree/main/docs>
  - <https://github.com/goccy/wasm2go/tree/main/tools>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/docs/asm-overrides.md>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/go.mod>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/Makefile>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/.github/workflows/ci.yml>
  - <https://github.com/goccy/wasm2go/commits/main>
  - <https://github.com/goccy/wasm2go/commits/main/README.md>
  - <https://github.com/goccy/wasm2go/releases>
  - <https://github.com/goccy/wasm2go/issues?q=is%3Aissue>
  - <https://github.com/goccy/wasm2go/pulls?q=is%3Apr>
  - <https://github.com/goccy/wasm2go/pulls?page=2&q=is%3Apr>
  - <https://github.com/goccy/wasm2go/pull/1>
  - <https://github.com/goccy/wasm2go/pull/7>
  - <https://github.com/goccy/wasm2go/pull/25>
  - <https://github.com/goccy/wasm2go/pull/46>
  - <https://github.com/goccy/wasm2go/tree/main/internal>
  - <https://github.com/goccy/wasm2go/tree/main/transpile>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/transpile/transpile.go>
  - <https://raw.githubusercontent.com/goccy/wasm2go/HEAD/transpile/pure_only_test.go>
  - <https://github.com/goccy/go-googlesql>
  - <https://github.com/goccy/go-zetasqlite>
  - <https://github.com/goccy/googlesqlite>
  - <https://github.com/goccy/googlesqlite/tree/main/bench>
  - <https://raw.githubusercontent.com/goccy/googlesqlite/HEAD/bench/RESULTS.md>
  - <https://raw.githubusercontent.com/goccy/googlesqlite/HEAD/bench/runner_test.go>
  - <https://raw.githubusercontent.com/goccy/googlesqlite/HEAD/bench/render_results.go>
  - <https://raw.githubusercontent.com/goccy/googlesqlite/HEAD/bench/go.mod>
  - <https://github.com/goccy/googlesqlite/commits/main/bench>
  - <https://github.com/goccy/googlesqlite/pull/19>
  - <https://github.com/ncruces/wasm2go>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/goccy/wasm2go`) · [data/wave12/enrich/raw/github_com_goccy_wasm2go.json](../../../data/wave12/enrich/raw/github_com_goccy_wasm2go.json) (enrichment confidence 0.75)

</details>
