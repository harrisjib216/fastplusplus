# rsjsonnet (Rust jsonnet)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust Jsonnet 0.22 interpreter and library crate; about 4.8x faster than go-jsonnet and about 36x faster than C++ jsonnet across a third-party suite.

| | |
|---|---|
| **Beats** | go-jsonnet (v0.22.0-rc1 per the doc; nix pin b5ef4cd9c4e24f2f14a68ef3bda0ca3079e11e78); also C++ jsonnet (d33798d4) and sjsonnet 0.6.2 in the same tables |
| **Claimed result** | jrsonnet docs/benchmarks.adoc (third-party, run by the author of competing jrsonnet): Kube-prometheus manifests rsjsonnet 57.9 +/- 2.6 ms vs Go 1068.4 +/- 16.5 ms vs Scala native 204.6 +/- 2.3 ms (C++ omitted, takes hours); Realistic 1: 7.8 ms vs Go 3158.3 ms; Realistic 2: 163.4 vs Go 3160.3 ms; Graalvm CI: 68.5 vs Go 600.3 ms; Large string join: 12.4 vs Go 46.4 vs C++ 39.7 ms; Tail call: 1200.9 vs Go 2559.0 vs C++ 18460.1 microseconds (the table unit is us, not ms). Derived from page data: rsjsonnet is faster than Go in all 26 shared rows (geomean about 4.8x, min 1.09x on 'Comparsion for array', max about 405x on Realistic 1) and faster than C++ in all 18 shared rows (geomean about 36x, min 1.97x on Simple recursive call); versus sjsonnet native it wins 19 of 27 rows (geomean about 1.4x) and loses 8 (for example Inheritance recursion 115.6 vs 46.7 ms); jrsonnet beats rsjsonnet in 24 of 27 rows. |
| **Workload** | hyperfine -N -w4 -m20 wall time per run of the Jsonnet CLI on 27 programs: real-world kube-prometheus manifests and GraalVM CI, C++ jsonnet perf_tests and benchmarks, and go-jsonnet builtin benchmarks (std.base64, std.foldl, std.manifestJsonEx and others). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 9950X3D 16-Core Processor, 32 threads |
| **Compiler and flags** | Built by nix at jrsonnet commit 4824700 (flake.lock nixpkgs a124a10ea33a, 2026-02-07): rsjsonnet via rustPlatform.buildRustPackage at commit 27be31532180c611383ceb2b7f03193ab1253487 with its release profile (lto=true, codegen-units=1, panic=abort, strip debuginfo); go-jsonnet b5ef4cd9 via buildGoModule (cmd/jsonnet); C++ jsonnet d33798d4 via its Makefile 'jsonnet' target under stdenv; every implementation wrapped with --max-stack 200000; timing by hyperfine -N -w4 -m20. Compiler versions are implied by the nixpkgs pin, not printed. |
| **Adoption** | 30 stars |
| **Last commit** | 2026-05-18 |
| **Links** | [repository](https://github.com/eduardosm/rsjsonnet) · [benchmark](https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/docs/benchmarks.adoc) |

## Verdict

In a third-party run by the jrsonnet author (hyperfine -N, warmup 4, at least 20 runs, Ryzen 9 9950X3D), all implementations were built by nix from pinned commits: rsjsonnet 27be3153 with LTO, codegen-units=1 and panic=abort; go-jsonnet b5ef4cd9; C++ jsonnet d33798d4. Each row times a whole process. rsjsonnet beat go-jsonnet on all 26 shared programs (geomean about 4.8x, from 1.09x on array comparison to about 405x on Realistic 1) and C++ jsonnet on all 18 shared programs (geomean about 36x) (derived from page data).

## Use it when

- CI or deploy pipelines that render large Kubernetes or monitoring manifest trees and are bottlenecked on go-jsonnet (kube-prometheus 57.9 ms vs 1068.4 ms; GraalVM CI config 68.5 ms vs 600.3 ms in the third-party run).
- Replacing the C++ jsonnet binary: it was slower on all 18 shared programs, from 1.97x (simple recursive call) to over 1000x (std.base64Decode), and could not finish most real-world cases in under an hour.
- Deeply recursive or huge-template Jsonnet where go-jsonnet hits OS stack exhaustion ('Large string template': Go has no result, rsjsonnet 3.3 ms), because evaluation runs on an explicit heap stack.
- Embedding Jsonnet evaluation in a Rust service or tool when you want an evaluator crate compiled with #![forbid(unsafe_code)].
- x86 Linux (manylinux2014) or Windows machines, using the prebuilt release binaries without a Rust toolchain.

## Skip it when

- When raw speed is the only criterion: jrsonnet beat it on 24 of 27 rows of the same run (std.foldl 2.2 vs 26.7 ms, Foldl string concat 3.7 vs 96.0 ms, Large string join 2.6 vs 12.4 ms).
- Inheritance- or recursion-heavy code, byte arrays and deep comparisons: sjsonnet's native binary won 8 of 27 rows (Inheritance recursion 46.7 vs 115.6 ms, Comparsion for primitives 174.8 vs 432.2 ms, std.base64 byte array 7.1 vs 14.3 ms).
- Parallel evaluation inside one interpreter instance: the Program state is built on Rc and Cell, so it is single-threaded.
- Memory-constrained or long-lived embeddings: no memory figures are published, and since 0.3.0 the AST, IR and interned strings live in an arena that is never collected while the Program exists.
- If you need the Go library API, jsonnetfmt or a linter: the repo ships only the CLI and the two Rust library crates. There are no prebuilt binaries for macOS or aarch64 (build with cargo install).

## How it is fast

Source is parsed, then lowered (program/analyze.rs) into an IR allocated in a bumpalo arena, with interned identifiers and foldhash-keyed maps. Evaluation is not recursive: the evaluator drives an explicit Vec of states plus typed value, string, array and object stacks, so deep Jsonnet recursion does not use the native stack. Heap values (lazy thunks, objects, arrays, functions) are managed by a custom Rc/Weak mark-and-sweep collector that runs only once the live-object count has doubled since the last collection, and the CLI links mimalloc. The repo has no profiling notes, so how much each technique contributes to the gap over Go is not documented.

## Compared with alternatives

Choose jrsonnet when speed alone decides: it beat rsjsonnet on 24 of 27 rows in the same run. Pick rsjsonnet over jrsonnet if you want a small, unsafe-free evaluator crate or your code resembles lazy arrays (10.7 vs 54.8 ms) or inheritance recursion (115.6 vs 160.1 ms), the rows where it led. Pick it over sjsonnet when you want a single native binary or Rust crate without a JVM or Scala Native build, accepting that sjsonnet wins some recursion-heavy and byte-array rows.

## Integration

| | |
|---|---|
| **Form** | crate (rsjsonnet-lang and rsjsonnet-front libraries) plus a CLI binary (cargo install --locked rsjsonnet or prebuilt release archives) |
| **Dependencies** | rsjsonnet-lang: bumpalo, foldhash, hashbrown, saphyr-parser (std.parseYaml), md-5, sha1, sha2, sha3; the CLI adds clap and mimalloc (global allocator) |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | any Rust target (pure Rust, no unsafe in rsjsonnet-lang); prebuilt binaries for Linux x86_64/i686 (manylinux2014) and Windows x86_64/i686 |
| **Thread safety** | Not documented. The Program evaluator holds Rc-based GC handles and Cell state, so it is single-threaded (not Send or Sync); use one Program per thread. |
| **Drop-in for the baseline** | partial — the CLI accepts the official flags and its CI runs google/jsonnet v0.22.0's test_suite against the golden outputs (stdout checks skipped for unparse.jsonnet because of float rounding, and for trace.jsonnet). It is not a drop-in for go-jsonnet's Go library API, and the default stack limit is 500 frames. |

## Gotchas

- Harness: every row times a whole CLI process launched through a nix makeWrapper bash script (go-jsonnet, C++, sjsonnet and jrsonnet are wrapped the same way, so the comparison is symmetric), and the eight microsecond-unit rows sit at a 1.17-1.54 ms per-process floor for rsjsonnet vs 1.40-5.38 ms for Go. Those rows measure startup, not evaluation.
- The benchmark never compares outputs between implementations. Correctness rests on rsjsonnet's separate CI conformance run against the official v0.22.0 test_suite.
- The run passed --max-stack 200000 to every implementation; with the default 500 frames, deeply recursive programs like the Tail call and Inheritance recursion benchmarks may fail with a stack-limit error.
- In the doc, go-jsonnet and C++ are labelled v0.22.0-rc1 (the --version string), but the nix files pin 2026-03-23 commits (b5ef4cd9, d33798d4). Both the CLI and jrsonnet link mimalloc, so the allocator is the same for the two Rust entries but differs from Go's runtime allocator and C++'s glibc malloc.

## Known shortcomings

- Same jrsonnet docs/benchmarks.adoc harness (pinned nix build at jrsonnet 4824700, Ryzen 9 9950X3D): jrsonnet is faster in 24 of 27 rows, 8 microsecond rows are startup-bound (every binary runs through a wrapper script), outputs are never compared, and the Tail call row is in microseconds, not milliseconds.
- Enricher: the eight microsecond rows sit at a 1.17-1.54 ms per-process floor for rsjsonnet vs 1.40-5.38 ms for Go, so they measure startup; outputs are never compared (correctness rests on rsjsonnet's separate conformance CI against the v0.22.0 test suite); every implementation ran with --max-stack 200000 while the default 500 frames may fail the Tail call and Inheritance recursion programs; go-jsonnet and C++ are labelled v0.22.0-rc1 but the nix files pin 2026-03-23 commits; both Rust entries link mimalloc against Go's runtime allocator and C++'s glibc malloc. 30 stars, one developer.

## Caveats and trade-offs

The only numbers live in the jrsonnet repo (generated 2026-04-01), not in rsjsonnet's own repo or README (no own benchmarks). The table author maintains jrsonnet, which is shown fastest: jrsonnet beats rsjsonnet in 24 of the 27 rows (derived), and rsjsonnet is labelled 'Rust (alternative)'. rsjsonnet is slower than sjsonnet (Scala native) in 8 rows and C++ jsonnet has no row on the real-world cases and several others (too slow). Each row times a whole CLI process, so startup is included: the eight microsecond-unit rows (Tail call, Inheritance function recursion, String strips, Big object, manifestJsonEx, manifestTomlEx, parseInt, substr; about 1.2 to 1.5 ms per rsjsonnet process vs 1.4 to 5.4 ms for Go) mostly measure startup, and the harness never compares outputs. The doc labels go-jsonnet and C++ as v0.22.0-rc1 while the nix files pin 2026-03-23 commits. 30 stars, low adoption.

Targets Jsonnet 0.22 with a CLI similar to the official one plus two library crates (rsjsonnet-lang, rsjsonnet-front); MSRV Rust 1.85. Memory use is not measured in the doc. Pre-built binaries for Linux and Windows.

## Maintenance

Actively maintained by one developer: 322 commits, 0.5.0 released on crates.io 2026-03-28, last commit 2026-05-18, 0 open issues. Dual MIT/Apache-2.0 and easy to adopt via cargo or prebuilt binaries, but adoption is low (30 stars, 1 fork; rsjsonnet-lang has about 16k total crates.io downloads and no reverse dependencies outside its own workspace).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party table jrsonnet docs/benchmarks.adoc, generated at jrsonnet commit 4824700 (2026-04-01) by the public nix derivation nix/benchmarks.nix (hyperfine -N -w4 -m20), with rsjsonnet built from source at pinned commit 27be3153 by nix/rsjsonnet.nix (its release profile: lto=true, codegen-units=1, panic=abort), go-jsonnet b5ef4cd9 and C++ jsonnet d33798d4 pinned, toolchains pinned by flake.lock (nixpkgs a124a10ea33a, 2026-02-07) and the CPU stated (Ryzen 9 9950X3D). Same basis as the jrsonnet entry's tier A from this doc; compiler version numbers are pinned rather than printed, so if named versions are required it falls to B (independent measurement).
- **Verifier notes:** Every quoted number and every derived count (Go 26/26, C++ 18/18, sjsonnet native 19 of 27, jrsonnet ahead in 24 of 27) re-derived from the adoc; only fix is the Tail call row unit (microseconds, not ms). Tier A kept for consistency with the jrsonnet entry from the same doc (batch 75), with the same pinned-not-printed compiler caveat; sjsonnet sits at B only because it was a prebuilt binary. Metadata confirmed on github.com: Apache-2.0 OR MIT, 30 stars, not a fork or archived, last commit 2026-05-18.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** output-checked comparison on evaluator-bound rows
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://github.com/CertainLach/jrsonnet/commits/master/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/rsjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/go-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/flake.lock>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/rsjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/go-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/27be31532180c611383ceb2b7f03193ab1253487/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/README.md>
  - <https://github.com/eduardosm/rsjsonnet>
  - <https://github.com/eduardosm/rsjsonnet/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/27be31532180c611383ceb2b7f03193ab1253487/rsjsonnet/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/README.md>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-front/Cargo.toml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet/src/main.rs>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/src/lib.rs>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/src/gc/mod.rs>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/src/program/mod.rs>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/rsjsonnet-lang/src/program/eval/mod.rs>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/eduardosm/rsjsonnet/HEAD/ci/external-tests.sh>
  - <https://github.com/eduardosm/rsjsonnet>
  - <https://github.com/eduardosm/rsjsonnet/tree/main/rsjsonnet-lang/src>
  - <https://github.com/eduardosm/rsjsonnet/tree/main/rsjsonnet-lang/src/program>
  - <https://github.com/eduardosm/rsjsonnet/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/rsjsonnet>
  - <https://crates.io/api/v1/crates/rsjsonnet-lang>
  - <https://crates.io/api/v1/crates/rsjsonnet-lang/reverse_dependencies>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/rsjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/go-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/sjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/nix/jrsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/4824700/flake.nix>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/eduardosm/rsjsonnet`) · [data/wave12/enrich/raw/github_com_eduardosm_rsjsonnet.json](../../../data/wave12/enrich/raw/github_com_eduardosm_rsjsonnet.json) (enrichment confidence 0.82)

</details>
