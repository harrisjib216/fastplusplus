# ncruces/wasm2go (Wasm to Go compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Ahead-of-time Wasm-to-Go source translator; cgo-free, runtime-free alternative to embedding wazero, faster on most trie queries.

| | |
|---|---|
| **Beats** | wazero v1.10.1 (go-marisa's wazero-based bindings at commit 37cde21, Wasm blob built with -msimd128; wazero execution mode not stated on the page) |
| **Claimed result** | benchstat sec/op, wasm2go against wazero: geomean 109.5us -&gt; 92.58us (-15.45%); Trie/Go125/Lookup 96.77ns -&gt; 70.31ns (-27.34%); Trie/Words/ReverseLookup 123.65ns -&gt; 73.63ns (-40.45%); Trie/Words/Lookup 344.2ns -&gt; 306.8ns (-10.87%); Trie/Words/WriteTo 11.383us -&gt; 2.541us (-77.68%); CommonPrefixSearchSeq -12% to -18%. Slower: Trie/Words/Build 349.4ms -&gt; 406.9ms (+16.46%), Trie/Go125/Build +34.67%, Trie/Words/UnmarshalBinary 323.6us -&gt; 634.8us (+96.16%). Keys/s geomean 2.525M -&gt; 2.802M (+10.97%). |
| **Workload** | pgaskin/go-marisa BenchmarkTrie (a WebAssembly build of the MARISA trie called from Go, Words and Go125 datasets): build, ReadFrom, WriteTo, marshal and unmarshal, lookup, reverse lookup, predictive and common-prefix search; wazero-bound build against wasm2go-transpiled build, benchstat of 6 runs. |
| **Metric** | latency |
| **Hardware** | Lenovo T14s Gen 6, Intel(R) Core(TM) Ultra 7 258V (linux/amd64, 8 threads), performance mode |
| **Compiler and flags** | Go 1.26 (go1.26.0): CGO_ENABLED=0 go1.26.0 test -v -run='^\$' -bench=BenchmarkTrie -count=6 in github.com/pgaskin/go-marisa. The two hashes on the page are go-marisa commits, not wasm2go/wazero commits: wasm2go side = go-marisa 075b64a04783d6c188ac9f66ea52688bc71edb9e ('mmap wip'; its src/Dockerfile pins wasm2go ecc45fd41abc75bace101eb275d9cb7c72aa76c4 and builds the Wasm with wasi-sdk 29 clang++ -O3 -mmutable-globals -mbulk-memory -mmultivalue -mnontrapping-fptoint -msign-ext, no SIMD, plus wasm-opt -O3 --gufa --converge); wazero side = go-marisa 37cde21a937175ff0928e5e6035b00a08be91daa (go.mod wazero v1.10.1; Wasm built with the same flags plus -msimd128 and wasm-opt --enable-simd). |
| **Adoption** | 237 stars; adopted by ncruces/go-sqlite3 and pgaskin/go-marisa |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ncruces/wasm2go) · [benchmark](https://github.com/ncruces/go-sqlite3/discussions/361) |

## Verdict

pgaskin ran go-marisa's BenchmarkTrie (MARISA trie built to Wasm, called from Go) six times per side on an Intel Core Ultra 7 258V with Go 1.26.0: wasm2go-translated bindings against wazero v1.10.1 bindings (compiler mode by default, compile excluded); ncruces's benchstat gives a -15.45% geomean in sec/op, with lookups 11-40% faster and WriteTo 78% faster but Build 16-35% and UnmarshalBinary 96% slower, and the two sides used different Wasm blobs (SIMD only on the wazero side).

## Use it when

- A fixed C/C++/Rust library compiled once to Wasm that you want to ship inside a Go module without cgo (the go-sqlite3, go-re2, go-marisa and libavif/jpegli bindings listed in USERS.md follow this pattern).
- Query-heavy calls into the module: in pgaskin's go-marisa run, lookups were 11-27% faster and reverse lookups up to 40% faster than the same library under wazero v1.10.1 (Intel Core Ultra 7 258V, Go 1.26.0).
- Platforms where wazero runs as an interpreter: generated Go is compiled by the Go toolchain for whatever GOARCH you build, and discussion #361 names 'slow performance on interpreter targets, and slow startup on compiler targets' as the reasons go-sqlite3 left wazero.
- Programs that care about startup: there is no per-process Wasm compilation (wazero must compile the module at first use, which this benchmark excluded from timing).

## Skip it when

- Modules that use SIMD128: code.go rejects every 0xFD opcode with 'unsupported opcode (SIMD)' (issue #16 closed wontfix, #50 still open), so you must rebuild without -msimd128 and lose vectorized paths; go-marisa's SIMD-heavy trie Build ran 16-35% slower for that reason.
- Loading arbitrary Wasm at run time or running untrusted modules: it is a build-time translator that assumes trusted input (README says to run a verifier first); keep wazero for plugins.
- Very large modules: compiling the generated SQLite source took about 40 s and 4 GiB RAM (discussion #361), and issue #41 (open) reports transpiled libraries with extremely large functions (LightningCSS) that the Go compiler cannot build without -gcflags='-N -l', producing multi-gigabyte binaries.
- Build, serialize and deserialize-heavy workloads: the same benchmark showed UnmarshalBinary 96% slower and Build 16-35% slower, and the go-marisa README for the released wasm2go bindings says they are about 50% slower at building/reading/writing tries than the old wazero bindings.
- Modules that need GC or exception-handling proposals beyond what clang emits (0xFB GC opcodes are rejected); the supported target is the clang/Lime1 subset.

## How it is fast

Static translation: each Wasm function becomes a Go function (control flow lowered to goto and labels, linear memory a Go []byte), so the Go compiler's optimizer and register allocator produce the native code and there is no runtime compile step and no Go-to-Wasm call trampoline. Its own passes (internal/passes: opt, gotos, switch, checks) clean up the generated code, issue #49 (closed 2026-08-20) covered eliding bounds checks for constant addresses within the memory minimum, and the optional -unsafe flag replaces encoding/binary loads and stores with unaligned pointer loads that keep an explicit bounds check. The output is still fully bounds-checked Go, so speed depends on what the Go compiler makes of goto-heavy code.

## Compared with alternatives

Pick it over wazero-family runtimes (wazy) when the Wasm module is fixed at build time and you want pure Go with no runtime compile or interpreter fallback; it is the Go-target counterpart of wasm2c (WABT) and w2c2, which emit C and therefore need cgo from Go. goccy/wasm2go is a separate project with the same name and its own wazero comparison (cold compile 8.4x); prefer ncruces/wasm2go when you want the translator that go-sqlite3, go-re2 and the gen2brain image bindings already depend on.

## Integration

| | |
|---|---|
| **Form** | code generator (CLI) emitting a single Go source file per module, vendored as a package |
| **Dependencies** | generated code: Go standard library only (sync, sync/atomic, unsafe with -unsafe); the translator itself needs golang.org/x/tools |
| **Minimum toolchain** | Go 1.26.0 (go.mod of the translator); no tags or releases, pin a commit |
| **Platforms** | any GOARCH Go supports; -unsafe fast loads and -nanbox NaN canonicalization are tested on amd64 and arm64 only (README says nanbox is broken on most other architectures) |
| **Thread safety** | not documented for a generated Module; threads/atomics are supported as a Wasm feature, and go-sqlite3 uses one isolated instance per connection |
| **Drop-in for the baseline** | partial: replaces wazero only for modules known at build time; the host API changes from wazero's api.Module calls to generated Go methods and import interfaces |

## Gotchas

- Benchmark scope: go-marisa's BenchmarkTrie calls marisa.Initialize() before the timers, so wazero's module compilation is excluded and only steady-state calls are compared; the benchmark code is byte-identical at both go-marisa commits, but the two sides ran different bindings (wazero side 37cde21 with a SIMD-built blob; wasm2go side 075b64a 'mmap wip' with a non-SIMD blob and imported memory), and the -77.68% WriteTo result did not survive into the released bindings (README: about 50% slower at building/reading/writing).
- Correctness history: issue #31 (optimization introduced in 428ad44 on 2026-05-26 corrupted memory, fixed in 227474f) and issue #61 (memory.fill/copy/init and table ops did not trap past the end after memory.grow/table.grow, fixed 2026-10-04); the March 2026 benchmark predates both. README advises retrying with -noopt before reporting a suspected miscompile.
- memory.grow is implemented with Go append on the []byte linear memory, so growth can reallocate and copy the whole memory, and each instance is capped at 4 GB (no mmap_size in go-sqlite3 for that reason).
- Generated code is deliberately unreadable (goto, mangled names, conversions) and float operations need explicit conversions to keep Wasm semantics; tail calls are accepted but tail behavior is not guaranteed.

## Known shortcomings

- Mixed result in ncruces/go-sqlite3 discussion #361 (Core Ultra 7 258V, Go 1.26, wazero v1.10.1): geomean -15.45% but Build +16-35% and UnmarshalBinary +96% slower; the wazero side ran a SIMD128 Wasm blob while the wasm2go side ran a non-SIMD blob from a work-in-progress go-marisa commit; the hashes on the page are go-marisa commits, not wasm2go or wazero commits.
- Enricher: code.go rejects every SIMD opcode (0xFD 'unsupported opcode (SIMD)'; #16 wontfix, #50 open), so the wasm2go blob was built without SIMD, which explains Build +16-35%. marisa.Initialize() runs before the timers, so wazero's compile time is excluded and the startup advantage is not measured; the bindings differ on each side, and the go-marisa README now says the released wasm2go bindings are about 50% slower at build, read and write. Bugs after the March bench: #31 memory-corruption miscompile, #61 bulk operations did not trap after memory.grow (fixed 2026-10-04); #41 huge functions will not compile; memory.grow uses append and can copy the whole memory.

## Caveats and trade-offs

Mixed result on one workload and one machine: queries, WriteTo, ReadFrom (-7.74%) and PredictiveSearchSeq (-15.19%) are faster, while Build (+16.46% Words, +34.67% Go125), UnmarshalBinary (+96.16%) and LookupAvg (+5.67%) are slower, so the -15.45% geomean hides regressions up to +96%. The raw runs are pgaskin's (go-marisa author, not the wasm2go author); the benchstat summary was posted by ncruces, the wasm2go author. The two sides are not the same Wasm blob: the wazero side's blob was built with SIMD128 and the wasm2go side's without SIMD, from a different (work-in-progress 'mmap wip') go-marisa commit with imported memory, so the comparison is binding-versus-binding rather than engine-versus-engine on identical input; ncruces attributes the Build regression to that 'SIMD-heavy part'. The go-marisa README now summarises the switch from wazero (v1.0.2 and older) as 'slightly faster at querying, but about 50% slower at building/reading/writing tries'. Not the go-sqlite3 workload that the discussion is about. Separate project from goccy/wasm2go.

Translates a Wasm module to self-contained Go source with no dependencies beyond Go, so no runtime and no cgo; the output is deliberately unreadable (goto labels, type conversions) and its speed depends on the Go compiler's assembly. A static translation: runtime loading of arbitrary modules still needs wazero (stated in the discussion). Large generated files cost compile time and memory (a commenter in discussion #361 reported about 40 seconds and 4 GB of RAM to compile). Each module instance keeps its own memory up to 4 GB.

## Maintenance

Very active single-maintainer project (commits through 2026-10-06, no tagged releases, two open issues), MIT-licensed and copyable, already the engine behind ncruces/go-sqlite3; pin a recent commit because miscompile and trap bugs were fixed as late as October 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Discussion #361 has pgaskin's raw go test output (2026-03-10) and ncruces's benchstat of it (2026-03-18) with Go 1.26.0, the exact command, CPU Intel Core Ultra 7 258V and the go-marisa commits for both sides; the benchmark code (go-marisa BenchmarkTrie) and the Wasm build flags (src/Dockerfile at each commit) are public, so the run is reproducible.
- **Verifier notes:** Numbers match ncruces's benchstat table in discussion #361 (geomean 109.5us to 92.58us, -15.45%; Go125/Lookup -27.34%; Words/ReverseLookup -40.45%; Words/WriteTo -77.68%; Build and UnmarshalBinary slower). Record called the go-marisa commit hashes wasm2go/wazero commits and said the wazero version was unstated; corrected to wazero v1.10.1 from go.mod at 37cde21. Shortcomings: mixed result with regressions up to +96%, wazero side ran a SIMD-built blob while the wasm2go side did not, wazero not one of the category's listed baselines.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** same-blob comparison; same-feature blobs with compile time included
- **Pages the verifier opened:**
  - <https://github.com/ncruces/go-sqlite3/discussions/361>
  - <https://github.com/ncruces/wasm2go>
  - <https://github.com/ncruces/wasm2go/commits>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/HEAD/README.md>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/HEAD/src/Dockerfile>
  - <https://github.com/pgaskin/go-marisa/commit/075b64a04783d6c188ac9f66ea52688bc71edb9e>
  - <https://github.com/pgaskin/go-marisa/commit/37cde21a937175ff0928e5e6035b00a08be91daa>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/37cde21a937175ff0928e5e6035b00a08be91daa/go.mod>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/075b64a04783d6c188ac9f66ea52688bc71edb9e/go.mod>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/075b64a04783d6c188ac9f66ea52688bc71edb9e/src/Dockerfile>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/37cde21a937175ff0928e5e6035b00a08be91daa/src/Dockerfile>
- **Sources the enricher read:**
  - <https://github.com/ncruces/wasm2go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/README.md>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/go.mod>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/USERS.md>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/main.go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/translate.go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/module.go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/code.go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/helpers/helpers.go>
  - <https://raw.githubusercontent.com/ncruces/wasm2go/HEAD/helpers/helpers_unsafe.go>
  - <https://github.com/ncruces/wasm2go/tree/main/internal>
  - <https://github.com/ncruces/wasm2go/tree/main/internal/passes>
  - <https://github.com/ncruces/wasm2go/issues?q=is%3Aissue>
  - <https://github.com/ncruces/wasm2go/issues/16>
  - <https://github.com/ncruces/wasm2go/issues/31>
  - <https://github.com/ncruces/wasm2go/issues/41>
  - <https://github.com/ncruces/wasm2go/issues/50>
  - <https://github.com/ncruces/wasm2go/commits>
  - <https://github.com/ncruces/go-sqlite3/discussions/361>
  - <https://raw.githubusercontent.com/ncruces/go-sqlite3/HEAD/README.md>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/HEAD/README.md>
  - <https://github.com/pgaskin/go-marisa/tree/075b64a04783d6c188ac9f66ea52688bc71edb9e>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/075b64a04783d6c188ac9f66ea52688bc71edb9e/trie_test.go>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/37cde21a937175ff0928e5e6035b00a08be91daa/trie_test.go>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/075b64a04783d6c188ac9f66ea52688bc71edb9e/trie.go>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/37cde21a937175ff0928e5e6035b00a08be91daa/trie.go>
  - <https://github.com/pgaskin/go-marisa/tree/37cde21a937175ff0928e5e6035b00a08be91daa/internal>
  - <https://raw.githubusercontent.com/pgaskin/go-marisa/37cde21a937175ff0928e5e6035b00a08be91daa/internal/flags.go>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ncruces/wasm2go`) · [data/wave12/enrich/raw/github_com_ncruces_wasm2go.json](../../../data/wave12/enrich/raw/github_com_ncruces_wasm2go.json) (enrichment confidence 0.75)

</details>
