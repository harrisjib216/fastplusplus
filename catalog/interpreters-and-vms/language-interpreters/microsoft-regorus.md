# Regorus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust Rego interpreter (OPA's policy language), embeddable from C/C++; about 10x faster than an opa eval CLI run on one ACI policy.

| | |
|---|---|
| **Beats** | OPA (Open Policy Agent, Go) opa eval |
| **Claimed result** | regorus eval 4.6 ms +/- 0.2 ms vs opa eval 45.2 ms +/- 0.6 ms (about 10x, derived from page data). |
| **Workload** | README Performance section: hyperfine on 'regorus eval -b tests/aci -d tests/aci/data.json -i tests/aci/input.json data.framework.mount_overlay=x' vs the same 'opa eval' command line, whole-process timing of both CLIs (regorus 422 runs, OPA 62 runs). |
| **Metric** | latency |
| **Compiler and flags** | Cargo release profile via 'cargo install --example regorus --path .' (README); rustc version and OPA version/build unstated |
| **Adoption** | 350 stars, 542 commits |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/microsoft/regorus) · [benchmark](https://github.com/microsoft/regorus) |

## Verdict

First-party hyperfine runs in the README: 'regorus eval' on the Azure Container Instances policy (tests/aci, query data.framework.mount_overlay=x) took 4.6 ms +/- 0.2 ms over 422 runs versus 45.2 ms +/- 0.6 ms over 62 runs for the same 'opa eval' command line, about 10x (derived from page data). Both are whole-process CLI timings recorded by January 2024 on unstated hardware with unstated rustc and OPA versions (the README at that commit cited conformance with OPA v0.60.0), using one policy and one query.

## Use it when

- Evaluating Rego authorization or admission policies inside a C, C++ or Rust process where running OPA as a sidecar or linking a Go runtime is unwanted.
- Short-lived or per-request policy checks where OPA CLI or Go start-up dominates (the README's ACI example: 4.6 ms vs 45.2 ms per whole-process run).
- Constrained or confidential-computing targets: no_std builds (opa-no-std feature), a freestanding C binding without libc, WASM, and feature flags to strip unneeded builtins.
- Projects that want a memory-safe evaluator: the library sets forbid(unsafe_code) outside Verus verification builds.

## Skip it when

- Policies that rely on builtins Regorus lacks: JWT and other cryptographic builtins (unsupported by design), net.cidr_\* functions, graphql, providers.aws, rego.parse_module, rego.metadata.\*, strings.render_template and some glob cases (README OPA Conformance list).
- When you need the OPA server feature set (REST API, bundle service, decision logs); the README documents only a library and an example CLI.
- Long-running services that compile a policy once and evaluate many times: the published 10x includes OPA process start-up and compilation, and no in-process comparison against OPA's Go API or 'opa bench' is published.
- If you need ready-made packages for Go, Python, Java or .NET: the README says bindings are not published and must be built yourself.

## How it is fast

Native Rust evaluator with no Go runtime or garbage collector to start, so short-lived evaluations avoid OPA's process and compiler start-up cost; a comment in examples/regorus/main.rs says eval_rule skips query parsing and is faster than eval_query. Newer releases add RVM, a register-based bytecode VM with fixed-width 32-bit instructions, pooled per-frame register windows, load-time-resolved literal and builtin tables and rule caching (docs/rvm/architecture.md). LRU caches hold compiled regex and glob patterns across evaluations (cache feature), and features can be compiled out to shrink the binary (6.3 MB default, 1.9 MB with no default features).

## Compared with alternatives

No sibling interprets Rego; the closest analogue is sjsonnet, another configuration-language interpreter benchmarked against its Go reference implementation. Pick Regorus when the job is evaluating OPA/Rego policies in-process from C++ or Rust without a Go runtime; the general-purpose interpreters in this category (LuaJIT, PyPy, Wren) do not apply.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); static or shared library for C/C++ via the cbindgen FFI crate built with Corrosion |
| **Dependencies** | Core: anyhow, serde, serde_json, lazy_static, thiserror, num-bigint, num-traits, spin and vstd (Verus std, pinned to a dated pre-release); the default full-opa feature adds regex, globset, chrono/chrono-tz, jsonschema, url, uuid, semver, yaml_serde, lru, parking_lot, data-encoding and ipnet. |
| **Minimum toolchain** | Rust 2021 edition, no rust-version declared on crates.io; C++ binding needs C++17 and CMake 3.12+ (Corrosion fetched by FetchContent). |
| **Platforms** | Any Rust target; no_std and WASM builds; CI cross-compiles musl targets (xtask test-musl). |
| **Thread safety** | Engine is a mutable single-owner object; the C++ wrapper exposes Engine::clone() for per-thread copies. With the default arc feature values use Arc and extensions must be Send + Sync. Concurrency guarantees beyond that are not documented. |
| **Drop-in for the baseline** | partial — same Rego semantics and the same JSON result format as opa eval (README shows a diff of the two outputs), but missing builtins, a library API instead of OPA's server and Go API, and a CLI default of strict builtin errors where OPA is non-strict. |

## Gotchas

- The README Performance commands are stale: tests/aci/framework.rego is Rego v0 syntax (rule bodies without 'if'), the regorus CLI now defaults to Rego v1 (the parser bails with "`if` keyword is required before rule body") and OPA 1.x also defaults to v1. Rerun verbatim with current versions, both commands probably time a parse error; add --v0 to regorus and --v0-compatible to OPA. The published numbers were already in the README by January 2024 (commit aabf329), when both tools defaulted to v0.
- The benchmark times two whole CLI processes, including file loading, parsing and compiling a 54 KB policy and Go runtime start-up for OPA (OPA user time 68.8 ms exceeds its 45.2 ms wall time). The in-repo Criterion bench (benches/aci_benchmark.rs) times only regorus eval_rule, so no evaluation-only ratio against OPA exists.
- The regorus CLI turns strict builtin errors on unless --non-strict is passed ('default behavior of OPA'), so builtin errors that OPA treats as undefined are raised as errors.
- Cargo.toml and crates.io list the licence as 'MIT AND Apache-2.0 AND BSD-3-Clause', not plain MIT; check the bundled-code notices before vendoring.

## Known shortcomings

- README hyperfine numbers (4.6 ms vs opa eval 45.2 ms, about 10x) time whole CLI processes, so Go startup is included in the OPA figure; one policy, one query, no hardware, OPA or rustc version stated. benches/aci_benchmark.rs times regorus only.
- Enricher: the README perf commands are stale. tests/aci/framework.rego is Rego v0 while the regorus CLI now defaults to v1 (the parser bails with 'if keyword is required before rule body') and OPA 1.x is v1 too, so a verbatim re-run probably times a parse error on both sides; it needs --v0 and --v0-compatible. The README numbers date from 2024-01 (commit aabf329) when both defaulted to v0. The CLI uses strict builtin errors by default (OPA is non-strict), and the crate licence is 'MIT AND Apache-2.0 AND BSD-3-Clause', not plain MIT.

## Caveats and trade-offs

Whole-process timings of two CLIs: Go runtime startup and per-invocation policy compilation probably account for much of OPA's 45 ms (OPA user time 68.8 ms exceeds its 45.2 ms wall time, so it ran multi-threaded), so the evaluation-only ratio is unknown; the README's in-process ACI test times (cargo test -r --test aci, about 3.6-5.0 ms per test) have no OPA counterpart such as opa bench. No hardware, OPA version or rustc version stated; benches/aci_benchmark.rs is a Criterion benchmark of regorus only, with no OPA comparison. Single policy (Azure Container Instances) and single query. Regorus does not yet support all OPA builtins (README: mostly compliant with OPA v1.2.0). Rego is a policy language, not one of the category's general-purpose interpreter baselines.

Rego (OPA policy language) interpreter in Rust; mostly compliant with the OPA v1.2.0 test suite but not all builtins are implemented; no_std capable. Bindings for C, C++ (cbindgen with corrosion-rs CMake integration), C#, Go, Java, JavaScript/WASM, Python and Ruby.

## Maintenance

Active Microsoft project (crates.io 0.12.0 released 2026-09-01, last commit 2026-10-01, about 2.64 million crates.io downloads, 1.28 million recent); copyable under the triple licence above, but the README's benchmark commands need --v0 flags to reproduce today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine output in the README Performance section (regorus eval 4.6 ms +/- 0.2 ms vs opa eval 45.2 ms +/- 0.6 ms on tests/aci); commands and policy files are public and the README gives the cargo release build command, but hardware, OPA version and rustc version are not stated, so not A, and no independent measurement was found.
- **Verifier notes:** README numbers match the record exactly (about 10x, derived from page data). Shortcomings: CLI whole-process timing that includes Go startup, one policy and one query, no hardware or versions, in-repo Criterion bench measures regorus alone. Metadata checked on github.com: MIT, 350 stars, 542 commits, last commit 2026-10-01, not archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** in-process comparison with versions and hardware; in-process re-run with matching Rego versions
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/README.md>
  - <https://github.com/microsoft/regorus>
  - <https://github.com/microsoft/regorus/commits>
  - <https://github.com/microsoft/regorus/tree/main/benches>
  - <https://github.com/microsoft/regorus/blob/main/benches/aci_benchmark.rs>
  - <https://github.com/morryyrrom/yata-cli/issues/5>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/benches/aci_benchmark.rs>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/examples/regorus/main.rs>
  - <https://github.com/microsoft/regorus/tree/main/tests/aci>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/tests/aci/framework.rego>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/tests/aci/api.rego>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/tests/aci/policy.rego>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/tests/aci/main.rs>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/tests/aci/input.json>
  - <https://github.com/microsoft/regorus/blame/main/README.md>
  - <https://github.com/microsoft/regorus/commit/aabf329088e1c0de03a2427549e52f22b8b24450>
  - <https://raw.githubusercontent.com/microsoft/regorus/746f815a891082f9d333bd6a0cda7d297d635fae/README.md>
  - <https://raw.githubusercontent.com/microsoft/regorus/aabf329088e1c0de03a2427549e52f22b8b24450/README.md>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/src/parser.rs>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/src/compiled_policy.rs>
  - <https://github.com/microsoft/regorus/tree/main/docs>
  - <https://github.com/microsoft/regorus/tree/main/docs/rvm>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/docs/rvm/architecture.md>
  - <https://github.com/microsoft/regorus/issues?q=is%3Aissue+performance>
  - <https://crates.io/api/v1/crates/regorus>
  - <https://github.com/microsoft/regorus/tree/main/bindings/cpp>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/bindings/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/regorus/HEAD/bindings/cpp/regorus.hpp>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/microsoft/regorus`) · [data/wave12/enrich/raw/github_com_microsoft_regorus.json](../../../data/wave12/enrich/raw/github_com_microsoft_regorus.json) (enrichment confidence 0.65)

</details>
