# Roto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Statically typed, Cranelift-JIT-compiled scripting language for Rust hosts; about 1.3x faster than Lua 5.5 (mlua) on a Rust-object sort benchmark.

| | |
|---|---|
| **Beats** | Lua 5.5 (via mlua) and QuickJS (via rquickjs) |
| **Claimed result** | 12.04 ms vs 15.47 ms for Lua 5.5 (mlua) and 36.38 ms for QuickJS (rquickjs) on Sort Rust objects (about 1.3x and 3.0x faster, derived from page data); Koto 49.33 ms, Boa 79.99 ms, Rhai 112.02 ms in the same chart. Slower than Luau (11.82 ms), Wasmi (7.04 ms) and Wasmtime (2.71 ms). |
| **Workload** | Generate 10,000 random 8-23 character strings wrapped in Rust userdata objects, then quicksort them in the script using a Rust-implemented comparison (criterion 'Sort Rust objects', one bench() call per iteration). |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max, macOS 27.0 (README Environment table) |
| **Compiler and flags** | rustc 1.99.0; cargo criterion with [profile.bench] opt-level=3, lto="fat", codegen-units=1 (Cargo.toml); criterion sample_size 10; mlua Lua 5.5 vendored build, rquickjs 0.14.0; roto 0.12.0 with default-features=false |
| **Adoption** | 558 stars on the GitHub mirror (project moved to Codeberg; described as used by Rotonda) |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/NLnetLabs/roto) · [benchmark](https://github.com/khvzak/script-bench-rs) |

## Verdict

In khvzak/script-bench-rs (mlua author, refreshed 2026-10-03; rustc 1.99.0, opt-level 3, fat LTO, codegen-units 1, criterion sample size 10, Apple M5 Max, macOS 27.0), Roto 0.12.0 took 12.04 ms to build 10,000 random strings as Rust objects and quicksort them with a Rust comparison, against 15.47 ms for vendored Lua 5.5 through mlua 0.12.2 and 36.38 ms for QuickJS through rquickjs 0.14.0 (about 1.3x and 3.0x, derived from page data). Roto's README itself makes no speed claim.

## Use it when

- Rust host that needs user-editable filters or policies over its own Rust types (the Rotonda BGP-filter use case: IP addresses, prefixes, routes).
- Workloads dominated by calls between script and Rust: the shootout calls a registered Rust comparison inside an in-script quicksort of 10,000 Rust objects and Roto beat mlua Lua 5.5 (12.04 vs 15.47 ms) and rquickjs (36.38 ms).
- You want type errors caught when the script is loaded, not at run time, and can accept a statically typed language for scripting.
- Hot-reloadable logic where the host recompiles scripts at run time and keeps typed function handles (TypedFunc is Send + Sync).

## Skip it when

- You need existing Lua or JavaScript scripts, a large standard library or an ecosystem: Roto has no generics, no first-class functions and no maps/dictionaries yet (README 'Pending features').
- Untrusted scripts in-process: the README says a script can exhaust memory through infinite recursion, loop forever with while, or be large enough to slow compilation; there is no instruction budget, so it recommends a separate process with a timeout.
- Peak speed on this kind of workload: in the same chart Luau through mlua with its JIT enabled (11.82 ms), Wasmi (7.04 ms) and Wasmtime (2.71 ms) are faster than Roto.
- Non-Rust hosts: the embedding API is Rust-only, and registered types must be Clone (or wrapped in Rc/Arc), PartialEq, Send + Sync and 'static.
- You need a stable language: 0.x releases keep breaking syntax and API (0.11 changed comments, match arms, negation and the string type).

## How it is fast

Scripts are type-checked ahead of time and compiled to native machine code with the Cranelift JIT (opt_level "speed"), so there is no bytecode interpreter loop and no dynamic type checks. Registered Rust types are passed by value with no serialization or userdata boxing, and registered Rust functions are called directly from the generated code. Runtime data structures are implemented in Rust: List is a type-erased Arc&lt;Mutex&lt;Vec&gt;&gt;-like shared array (one lock per operation) and String is Arc&lt;str&gt;.

## Compared with alternatives

Pick Roto over Luau (faster in the same chart, 11.82 ms) or Lua 5.5 via mlua when the host is Rust and you want typed scripts that work on registered Rust types directly with no userdata glue. Pick Luau or Lua when you need a mature dynamic language with sandboxing and existing scripts. Lua-CSharp and the other siblings target other hosts (.NET, C, Go).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cranelift, cranelift-codegen, cranelift-jit (0.127 in release 0.12.0, 0.136 on main), ariadne, inetnum, symbol_table, indexmap, sealed, libc, log, unicode-ident, rustc-literal-escaper, roto-macros; clap optional (default 'cli' feature, disable with default-features = false) |
| **Minimum toolchain** | Rust 1.89 (rust-version of crates.io 0.12.0, edition 2024); main now declares 1.96 |
| **Platforms** | Hosts with a Cranelift native back end (cranelift::native picks the running ISA); benchmark measured on Apple M5 Max (aarch64). Panics on x86_64 were fixed on main after 0.12.0 (Cranelift 0.136 upgrade plus is_pic). |
| **Thread safety** | TypedFunc and compiled module data are marked Send + Sync (unsafe impl); registered types must be Send + Sync; Lists lock an internal Mutex on every operation. No other concurrency documentation found. |
| **Drop-in for the baseline** | no |

## Gotchas

- The only cross-engine numbers measure script-to-Rust interop, not interpreter speed. The Roto script was tuned by the Roto maintainer (script-bench-rs PRs #17 and #18 made list swap a native Rust call) while the Lua and JS ports swap in-script; the Roto charset has 15 characters against 16; the JS port builds each string with new Array(len) and then pushes, so it joins a 2\*len holey array; the Lua 5.5 run replaces table.create with a Rust callback. Each run is validated as sorted with 10,000 elements, so no no-op timing was found.
- Lists are shared by reference (Arc&lt;Mutex&gt;): passing a list to a function mutates the caller's list, and every get, push or swap takes a mutex lock (Roto's own insertion_sort bench notes that cloning a List does not copy it).
- Release 0.12.0 on crates.io still uses Cranelift 0.127; the fix for panics on x86_64 (#461, merged 2026-09-22) is only on main, so x86_64 users should test or build from main.
- Roto relies on unsafe code to call generated machine code; the README treats any unsoundness as a high-priority bug and runs tests under Valgrind in CI, but a JIT bug is a memory-safety bug in the host. The 0.12 changelog lists miscompilation fixes (#446).

## Known shortcomings

- The script-bench-rs Roto script was tuned by the Roto maintainer (native list swap, PRs #17 and #18) while the other ports were not; a single interop-bound workload (12.04 vs Lua 5.5 15.47 and rquickjs 36.38 ms), slower than Luau, Wasmi and Wasmtime. Rust.
- Enricher: script-bench-rs checks every engine's output (sorted, count 10000), but the JS port builds strings via new Array(len) then push (joining a 2\*len holey array) and the Lua 5.5 run swaps table.create for a Rust callback; Roto 0.12.0 on crates.io still uses Cranelift 0.127 with the x86_64 panic fix (#461, Cranelift 0.136 plus is_pic) unreleased on main; lists are Arc&lt;Mutex&gt; with one lock per operation.

## Caveats and trade-offs

Single benchmark (Sort Rust objects: build 10,000 random 8-23 char strings as Rust userdata, then an in-script quicksort calling a Rust comparison), dominated by script-to-Rust interop rather than pure interpreter speed. Numbers exist only in the chart image 'Sort Rust objects.png' (criterion typical estimate, sample_size 10), not as text. Per-language scripts are hand-written ports and not identical: the Roto script was tuned by the Roto maintainer (script-bench-rs PRs #17 'remove some conversions from the Roto script' and #18 'make list swap a native function'), so Roto swaps list elements through a native Rust function while Lua and JS swap in-script; the Roto charset is 15 characters ('9' missing) against 16 in the Lua/JS scripts. Lua 5.5 is the mlua vendored build and QuickJS is reached through rquickjs, not standalone C Lua or QuickJS. Roto is slower than Luau (11.82 ms), Wasmi (7.04 ms) and Wasmtime (2.71 ms) in the same chart. Apple M5 Max only. The Roto README makes no performance claim; the shootout is by the mlua author (independent of Roto, MIT-licensed since July 2026, results refreshed 2026-10-03).

Statically typed, compiled embedded language for Rust hosts, not Lua- or JS-compatible, so existing scripts cannot be reused. Rust-only embedding API. Commit log shows a Cranelift upgrade to fix panics on x86_64, so the JIT back end is still moving.

## Maintenance

Actively developed by NLnet Labs (main on Codeberg, GitHub mirror last commit 2026-09-22, crate 0.12.0 released 2026-08-14, about 25.7k crates.io downloads, used by Rotonda and iocaine), BSD-3-Clause, but pre-1.0 with breaking changes in each release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** khvzak/script-bench-rs publishes the harness (benches/roto.rs, benches/mlua_lua55.rs, benches/rquickjs.rs, src/\*.rs, scripts/sort_userdata.{roto,lua,js}, bench.py), Cargo.toml [profile.bench] opt-level=3, lto=fat, codegen-units=1, rustc v1.99.0 and Apple M5 Max in the README Environment table; the chart 'Sort Rust objects.png' shows roto 12.04 ms vs mlua_lua55 15.47 ms and rquickjs 36.38 ms.
- **Verifier notes:** Chart numbers match the record exactly (12.04 / 15.47 / 36.38 ms; 1.28x and 3.02x derived from page data). Harness validates the sorted output for each engine, so no no-op timing; main flaw is that the Roto script was optimized by its own maintainer (native list swap) while the other ports were not, plus the narrow single-workload scope. Metadata checked: BSD-3-Clause, 558 stars, GitHub mirror of codeberg.org/NLnetLabs/roto, last commit 2026-09-22.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/khvzak/script-bench-rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/Sort%20Rust%20objects.png>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/bench.py>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/roto.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/mlua_lua55.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/rquickjs.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/roto.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/mlua.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/rquickjs.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.roto>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.lua>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.js>
  - <https://github.com/khvzak/script-bench-rs/commits>
  - <https://github.com/NLnetLabs/roto>
  - <https://github.com/NLnetLabs/roto/commits>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/NLnetLabs/roto/commits>
  - <https://github.com/NLnetLabs/roto/tree/main/benches>
  - <https://github.com/NLnetLabs/roto/tree/main/src>
  - <https://github.com/NLnetLabs/roto/tree/main/src/value>
  - <https://github.com/NLnetLabs/roto/tree/main/src/runtime>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/Changelog.md>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/benches/fibonacci.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/benches/insertion_sort.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/benches/primes.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/benches/script_bench_rs/main.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/benches/script_bench_rs/sort_userdata.roto>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/value/list.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/value/string.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/runtime/mod.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/runtime/func.rs>
  - <https://raw.githubusercontent.com/NLnetLabs/roto/HEAD/src/codegen/mod.rs>
  - <https://crates.io/api/v1/crates/roto>
  - <https://crates.io/api/v1/crates/roto/0.12.0/dependencies>
  - <https://crates.io/api/v1/crates/roto/reverse_dependencies>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/bench.py>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/roto.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/mlua.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/src/rquickjs.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/roto.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/mlua_lua55.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/benches/rquickjs.rs>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.roto>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.lua>
  - <https://raw.githubusercontent.com/khvzak/script-bench-rs/HEAD/scripts/sort_userdata.js>
  - <https://github.com/khvzak/script-bench-rs/commits>
  - https://codeberg.org/NLnetLabs/roto/issues (EGRESS_BLOCKED)
  - https://docs.rs/roto/latest/roto/ (blocked by proxy, 403)
  - WebSearch: Roto NLnet Labs scripting language Rust Cranelift performance benchmark Lua (snippets only; blog.nlnetlabs.nl posts not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nlnetlabs/roto`) · [data/wave12/enrich/raw/github_com_nlnetlabs_roto.json](../../../data/wave12/enrich/raw/github_com_nlnetlabs_roto.json) (enrichment confidence 0.75)

</details>
