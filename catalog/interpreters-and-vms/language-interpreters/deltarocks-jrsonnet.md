# jrsonnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust Jsonnet interpreter, CLI and libjsonnet-compatible library; 1.9x to thousands of times faster than C++ jsonnet.

| | |
|---|---|
| **Beats** | google/jsonnet C++ reference implementation (v0.22.0-rc1); also go-jsonnet v0.22.0-rc1 and Sjsonnet 0.6.2 |
| **Claimed result** | C++ perf_test 'Large string join': jrsonnet 2.6 ms vs C++ 39.7 ms (15.44x) and Go 46.4 ms. C++ 'Tail call' benchmark: 865.2 us vs C++ 18,460.1 us (21.34x) and Go 2,559.0 us (2.96x). GraalVM CI: 34.4 ms vs Go 600.3 ms (17.47x), C++ did not finish within an hour. Kube-prometheus manifests: 43.6 ms vs Go 1,068.4 ms (24.52x), C++ took hours. Ratios as printed in the doc. |
| **Workload** | Jsonnet evaluation wall time: real-world GraalVM CI and kube-prometheus manifests, the C++ jsonnet perf_tests and benchmarks suites, and Go jsonnet builtin benchmarks; mean and sigma tables per implementation. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 9950X3D 16-Core Processor, 32 threads |
| **Compiler and flags** | Built and run by the repo's nix flake at doc commit 4824700 (docs/benchmarks.adoc 'chore: re-run benchmarks', 2026-04-01). Toolchains pinned by flake.lock: nixpkgs a124a10ea33a and rust-overlay 9922ff9f99a6 (both 2026-02-07); rustc comes from rust-toolchain.toml (channel stable) via rust-overlay. jrsonnet 0.5.0-pre97 uses Cargo [profile.release] opt-level 3, lto fat, codegen-units 1, panic abort, --features=mimalloc. C++ jsonnet (google/jsonnet rev d33798d, reported as v0.22.0-rc1) is built with its Makefile `make jsonnet` (CXX g++, OPT ?= -O3) under nix stdenv. Both are wrapped with --max-stack 200000. Driver: hyperfine -N -w4 -m20 (nix/benchmarks.nix). Compiler version numbers are not printed in the doc. |
| **Adoption** | 374 stars, 1,281 commits |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/deltarocks/jrsonnet) · [benchmark](https://github.com/deltarocks/jrsonnet/blob/master/docs/benchmarks.adoc) |

## Verdict

With hyperfine (-N, 4 warm-ups, at least 20 runs) on a Ryzen 9 9950X3D and nix-pinned toolchains, a jrsonnet git build (fat LTO, mimalloc) beat C++ jsonnet v0.22.0-rc1 (g++ -O3 via its Makefile) on all 18 rows C++ finished, from 1.89x (Lazy array) and 2.20x (Simple recursive call) up to 4,069x (base64Decode), and beat go-jsonnet v0.22.0-rc1 17.5x on GraalVM CI and 24.5x on kube-prometheus, where C++ was not run. All timings are whole-process wall time, and outputs were not compared.

## Use it when

- Rendering large real-world Jsonnet trees (kube-prometheus, Grafana/Mimir/Loki manifests, CI generators) where C++ jsonnet takes minutes to hours and go-jsonnet takes about a second: GraalVM CI 34.4 ms vs Go 600.3 ms, kube-prometheus 43.6 ms vs Go 1,068.4 ms.
- Configs heavy on std builtins (sort, foldl, base64, manifestTomlEx, string joins), where C++ jsonnet's Jsonnet-level stdlib is 70x to 4,000x slower in the repo's tables.
- Short CLI invocations in build pipelines: on the small-input rows jrsonnet's whole-process time is about 0.75-0.92 ms against 1.4-5.4 ms for Go, 1.8-3.0 ms for sjsonnet's native images and 16 ms or more for C++.
- Rust services that want to embed Jsonnet as a library, or C/C++ programs that currently link libjsonnet.so and only use the evaluate entry points.

## Skip it when

- Workloads dominated by deep object-inheritance recursion or lazy arrays: sjsonnet native beats it on Inheritance recursion (46.7 vs 160.1 ms), Simple recursive call (18.0 vs 35.8 ms) and Comparison for primitives (174.8 vs 218.1 ms), and rsjsonnet beats it on Lazy array (10.7 vs 54.8 ms), Inheritance recursion (115.6 ms) and base64 of byte arrays.
- Teams that need a stable, packaged release: crates.io stable and Homebrew are still 0.4.2 (issue #231 asks for a release supporting jsonnet 0.22.0), and the benchmarked code is a git build labelled 0.5.0-pre97; the newest prerelease is 0.5.0-pre98 (2026-05-05).
- C/C++ embedders that rely on libjsonnet's GC tuning, custom allocators or error returns: jsonnet_gc_min_objects and jsonnet_gc_growth_trigger are no-ops, jsonnet_realloc assumes a 16-byte old allocation and is documented in its own comment as 'most definitely broken' (safe only with a malloc-style allocator), invalid arguments panic and release builds abort, and the library is publish = false, so it must be built from source.
- Programs that need multiple independent VMs on different threads with different stack limits: evaluator state is Rc/RefCell and thread-local, and jsonnet_max_stack sets a global depth limit, ignoring its VM argument.

## How it is fast

The evaluator works directly on the parsed IR with lazy thunks, interned strings (jrsonnet-interner IStr), FxHash maps and a reference-counted cycle collector (jrsonnet-gcmodule Cc), and the CLI is built with fat LTO, one codegen unit, panic=abort and mimalloc. Most of the largest gaps come from the standard library: jrsonnet implements 159 std builtins natively in Rust, while C++ jsonnet at the benchmarked revision defines std.sort, std.base64Decode, std.manifestTomlEx, std.parseInt and std.foldl in Jsonnet in stdlib/std.jsonnet. Current master also adds a static-analysis pass that resolves locals to numeric slots and marks which object fields depend on self/super so independent nested objects are built once; that pass did not exist at the benchmarked commit 4824700.

## Compared with alternatives

Against sjsonnet, the catalogued sibling for the same workload, pick jrsonnet when you want a single native binary or a C ABI with no JVM: it is 1.9x to 4.7x faster on the real-world rows (GraalVM CI 34.4 vs 65.1-69.6 ms, kube-prometheus 43.6 vs 183.7-204.6 ms). Prefer sjsonnet only when inheritance-recursion-heavy configs dominate or a JVM is already in the stack.

## Integration

| | |
|---|---|
| **Form** | crate (jrsonnet-evaluator, jrsonnet-stdlib) plus CLI binary; C ABI cdylib/staticlib (libjsonnet) built from bindings/jsonnet |
| **Dependencies** | jrsonnet-gcmodule, jrsonnet-interner, rustc-hash, stacker, smallvec, serde/serde_json, hi-doc (default explaining-traces feature), md5/sha1/sha2/sha3 for std hashing; mimalloc optional for the CLI |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85 or newer); README says latest stable and gives no MSRV policy |
| **Platforms** | Linux x86-64 and aarch64 (benchmark derivations), macOS (Homebrew), Windows (flake cross-build), WASM (JSR/NPM package) |
| **Thread safety** | Single-threaded per evaluator (Rc/RefCell state, thread-local STATE); libjsonnet's default interop-threading feature lets a VM move between threads, not share one |
| **Drop-in for the baseline** | partial — libjsonnet.so C API (evaluate_file/snippet, multi, stream; reports v0.22.0) is implemented for C/C++ hosts, but GC tuning calls are no-ops, jsonnet_realloc and panic behaviour differ, and experimental syntax is only on when built with exp-\* features |

## Gotchas

- Harness: hyperfine runs with --output=pipe, so outputs of the six implementations are never compared (only a non-zero exit fails a run), and every binary is launched through a nix makeWrapper shell wrapper that adds --max-stack 200000, so the microsecond rows (jrsonnet floor about 750-920 us: Tail call, String strips, Big object, manifestJsonEx, manifestTomlEx, parseInt, substr) measure process plus wrapper startup more than evaluation.
- The headline &gt;50x ratios against C++ (Array sorts 1,531x, base64Decode 4,069x, manifestTomlEx 692x, Inheritance function recursion 1,061x) compare native Rust builtins with C++ jsonnet's Jsonnet-level stdlib. Over the 18 rows C++ completed, the geomean is about 70x, but on the six evaluator-bound rows (Tail call, Inheritance recursion, Simple recursive call, Lazy array, Big object, Large string join) it is about 7.6x, ranging 1.89x to 21.3x (derived from page data). C++ was skipped on the real-world rows as taking hours.
- Allocator and build asymmetry: jrsonnet is measured with --features=mimalloc and fat LTO, C++ jsonnet with its Makefile's g++ -O3 and glibc malloc; embedding through libjsonnet uses the host's allocator, so library users may not see the CLI numbers.
- Master has moved past the benchmarked commit (static analysis pass added; issue #239, opened 2026-10-06, reports State::import_resolved leaving a file marked 'evaluating' after a static analysis error), and the doc still uses sjsonnet 0.6.2 (issue #234 asks for a rerun with 0.7.0).

## Known shortcomings

- docs/benchmarks.adoc is generated by the public nix/benchmarks.nix at 4824700 (hyperfine -N -w4 -m20, Ryzen 9 9950X3D, toolchains pinned by flake.lock, Cargo release profile, google/jsonnet Makefile -O3); compiler versions are pinned but not printed. Outputs are never compared, the microsecond rows are startup-dominated, C++ jsonnet is skipped on the heavy workloads and Scala native sjsonnet wins 3 rows.
- Enricher: every binary runs through a makeWrapper shell script, so the microsecond rows (about 750-920 us floor) measure startup; hyperfine --output=pipe never compares outputs. The large C++ ratios come from the C++ jsonnet stdlib being written in Jsonnet (std.sort, base64Decode, manifestTomlEx in std.jsonnet at d33798d) against 159 native Rust builtins: geomean about 70x over the 18 C++ rows but about 7.6x on the 6 evaluator-bound rows (derived from page data). Allocator asymmetry mimalloc vs glibc. rsjsonnet also beats jrsonnet on Inheritance recursion (115.6 vs 160.1 ms) and the base64 byte array row, not only Lazy array. libjsonnet C API: GC calls are no-ops, jsonnet_realloc is self-described broken, panics abort, jsonnet_max_stack is global. Stable release still 0.4.2; analyze.rs was added after the benchmarked commit 4824700.

## Caveats and trade-offs

This is the maintainer's own benchmark. It is reproducible through the pinned nix flake (nix/benchmarks.nix), but the hyperfine driver never compares outputs between implementations. Rows in microseconds (Tail call, Inheritance function recursion, String strips, Big object, manifestJsonEx, manifestTomlEx, parseInt, substr) sit at a \~750-900 us floor for jrsonnet and are dominated by process startup. C++ jsonnet was not run on the heaviest workloads (GraalVM CI, kube-prometheus, Large string template, Realistic 1/2, String strips, base64, Comparison for array/primitives) because it took hours. Where C++ did run, jrsonnet is faster on every row, by a smallest margin of 1.89x on Lazy array and 2.20x on Simple recursive call (derived from page data). Several &gt;50x rows (Array sorts 1,531x, base64Decode 4,069x, Inheritance function recursion 1,061x) reflect C++ jsonnet's algorithmic slowness rather than a like-for-like engine. jrsonnet is not the fastest on every row: Scala native wins Inheritance recursion, Simple recursive call and Comparison for primitives, rsjsonnet wins Lazy array, and Scala GraalVM wins std.base64 (byte array). The C++ and Go baselines are release candidates (v0.22.0-rc1). The repo was renamed from CertainLach/jrsonnet, which redirects to deltarocks/jrsonnet. [retier] Ratios against C++ jsonnet are dominated by the C++ stdlib being written in Jsonnet (std.sort, base64Decode, manifestTomlEx) versus jrsonnet's native Rust builtins: about 70x geomean over the 18 C++ rows but about 7.6x on the 6 evaluator-bound rows (derived from docs/benchmarks.adoc at 4824700). Every binary runs through a makeWrapper script so the microsecond rows are startup; outputs are never compared; mimalloc vs glibc allocator asymmetry. rsjsonnet beats jrsonnet on Inheritance recursion, base64 byte array and Lazy array; Scala native sjsonnet wins 3 rows. Stable release still 0.4.2.

Rust library and CLI; also ships libjsonnet.so-compatible C/C++ bindings plus Python (rjsonnet), WASM/JavaScript and in-progress Java bindings, so it is callable from C++. Adds experimental syntax extensions beyond standard Jsonnet (features guide). Jsonnet is a data templating language, so this only loosely fits the language-interpreter category.

## Maintenance

Actively maintained by a single author (last commit 2026-08-31, about 1.2M crates.io downloads of jrsonnet-evaluator), MIT-licensed and packaged in nixpkgs and Homebrew. Packaged stable releases lag at 0.4.2, so getting the benchmarked performance means building from git or using a 0.5.0 prerelease.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. docs/benchmarks.adoc is the generated output of the public nix derivation nix/benchmarks.nix at commit 4824700 (hyperfine -N -w4 -m20, with the 'takes longer than a hour' note and table format matching). The toolchains are pinned by flake.lock (nixpkgs a124a10ea33a and rust-overlay 9922ff9f99a6, both 2026-02-07; rustc from rust-toolchain.toml channel stable). Flags are public: jrsonnet's Cargo [profile.release] (opt-level 3, fat LTO, codegen-units 1, mimalloc), and C++ jsonnet rev d33798d built with its Makefile (g++, OPT ?= -O3). The CPU is stated (Ryzen 9 9950X3D). Compiler version numbers are not printed, only pinned; if the orchestrator requires named versions, this falls back to C.
- **Verifier notes:** All claimed numbers match docs/benchmarks.adoc: Large string join 2.6 ms vs C++ 39.7 (15.44x) vs Go 46.4; Tail call 865.2 us vs C++ 18,460.1 us (21.34x) vs Go 2,559.0 us (2.96x); GraalVM CI 34.4 ms vs Go 600.3 (17.47x); kube-prometheus 43.6 vs Go 1,068.4 (24.52x). The upgrade to A rests on the pinned public nix harness. Shortcomings to record: outputs are not compared, the microsecond rows are startup-dominated, C++ is omitted on the heavy workloads, and Scala native beats jrsonnet on 3 rows. The same doc already raised databricks/sjsonnet to B, so the two records should stay consistent. MIT, last commit 2026-08-31, 374 stars.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** output equivalence check and printed compiler versions; evaluator-bound comparison with outputs compared
- **Pages the verifier opened:**
  - <https://github.com/deltarocks/jrsonnet/blob/master/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://github.com/deltarocks/jrsonnet>
  - <https://github.com/deltarocks/jrsonnet/commits>
  - <https://github.com/deltarocks/jrsonnet/commits/master/docs/benchmarks.adoc>
  - <https://github.com/deltarocks/jrsonnet/tree/master/nix>
  - <https://github.com/CertainLach/jrsonnet>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/jrsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/flake.lock>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/flake.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/nix/jrsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/Cargo.toml>
  - <https://raw.githubusercontent.com/google/jsonnet/d33798d495d50df427dac0dc6934220e366976fb/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/README.adoc>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/jrsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/go-jsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/sjsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/nix/rsjsonnet.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/LICENSE>
  - <https://github.com/deltarocks/jrsonnet/tree/master/crates/jrsonnet-evaluator/src>
  - <https://github.com/deltarocks/jrsonnet/tree/master/bindings/jsonnet>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/bindings/jsonnet/README.adoc>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/bindings/jsonnet/Cargo.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/bindings/jsonnet/src/lib.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/crates/jrsonnet-evaluator/src/lib.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/crates/jrsonnet-evaluator/src/analyze.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/crates/jrsonnet-evaluator/src/gc.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/crates/jrsonnet-evaluator/Cargo.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/crates/jrsonnet-evaluator/src/analyze.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/4824700/crates/jrsonnet-evaluator/Cargo.toml>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/crates/jrsonnet-stdlib/src/lib.rs>
  - <https://raw.githubusercontent.com/deltarocks/jrsonnet/HEAD/docs/features.adoc>
  - <https://raw.githubusercontent.com/google/jsonnet/d33798d495d50df427dac0dc6934220e366976fb/stdlib/std.jsonnet>
  - <https://github.com/deltarocks/jrsonnet/issues>
  - <https://github.com/deltarocks/jrsonnet/issues/234>
  - <https://github.com/deltarocks/jrsonnet/issues/231>
  - <https://github.com/deltarocks/jrsonnet/releases>
  - <https://github.com/deltarocks/jrsonnet/commits/master>
  - <https://crates.io/api/v1/crates/jrsonnet-evaluator>
  - <https://pypi.org/pypi/rjsonnet/json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/deltarocks/jrsonnet`) · [data/wave12/enrich/raw/github_com_deltarocks_jrsonnet.json](../../../data/wave12/enrich/raw/github_com_deltarocks_jrsonnet.json) (enrichment confidence 0.8)

</details>
