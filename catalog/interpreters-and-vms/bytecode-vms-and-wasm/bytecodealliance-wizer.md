# Wizer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Build-time Wasm pre-initializer: snapshots a module's initialized memory and globals so startup skips init (1.35x-6.00x vs plain Wasmtime).

| | |
|---|---|
| **Beats** | Wasmtime instantiating and running the same module without Wizer pre-initialization (the benches build a 'control' module and a wizened one on a wasmtime Engine; Wizer embeds Wasmtime) |
| **Claimed result** | regex 248.85 us -&gt; 183.99 us (1.35x faster); UAP 98.297 ms -&gt; 16.385 ms (6.00x faster); README: 'between 1.35 to 6.00 times faster instantiation and initialization with Wizer, depending on the workload'. |
| **Workload** | Time to instantiate and initialize two Wasm programs with and without Wizer snapshotting their initialized state: a regex program and a UAP (user-agent parser) program. |
| **Metric** | startup |
| **Adoption** | 1.1k stars; crates.io wizer about 171k downloads, wasmtime-wizer about 144k |
| **Last commit** | 2026-03-10 |
| **Links** | [repository](https://github.com/bytecodealliance/wizer) · [benchmark](https://github.com/bytecodealliance/wizer) |

## Verdict

First-party criterion runs from December 2020 on Wasmtime of that era: instantiate plus initialize plus one call took 248.85 us without Wizer versus 183.99 us with it for a one-regex program, and 98.297 ms versus 16.385 ms for a program that builds a uap-core RegexSet; no hardware, Rust or Wasmtime version is stated, and the UAP call matches only a 5-byte prefix, so it is a pure startup measurement.

## Use it when

- Wasm modules whose own initialization dominates per-instance cost: large regex sets, parsed config or tables, interpreter or JS-engine heaps, built before the first request
- Instance-per-request serverless or plugin hosts on Wasmtime, where every request pays instantiate plus init (UAP: 98.3 ms to 16.4 ms in the 2020 run)
- Deterministic initialization that touches no host state, or only WASI calls you explicitly allow at build time
- Pipelines that already post-process Wasm, where adding a snapshot step and then wasm-opt to strip init-only code is cheap

## Skip it when

- Cheap initializers: the regex case gains only 1.35x (249 us to 184 us), and modules with little init gain nothing
- Web or network delivery where module size matters: the README warns Wizer often grows the Data section
- Modules that mutate tables or GC objects: the validator rejects any table.set/grow/fill/copy/init, elem.drop, data.drop, struct.set or array.set anywhere in the code, and mutable reference-typed globals
- Modules that import globals, tables or memories, or whose init needs host imports, files, sockets or wall-clock values (open issues #24 file reads with --dir, #21 listening on a port, #125 monotonic clock offsetting)
- As a substitute for a faster engine: it does not change compile time or execution speed, only how much guest init runs at instantiation

## How it is fast

Ahead-of-time state snapshotting: the expensive one-time setup (compiling a regex set, parsing YAML, building a JS heap) runs once at build time instead of on every instantiation, and instantiation becomes copying data segments into linear memory. The snapshot scans each Wasm page for non-zero runs (in parallel with rayon), merges segments separated by small gaps and caps output at 10,000 segments by merging the smallest gaps; with Wasmtime's memfd/copy-on-write memory initialization (which the current UAP bench forces) those segments map rather than copy.

## Compared with alternatives

It is complementary to the runtimes listed (Wasmi, wasm3, Fizzy, tinywasm and other fast-startup interpreters cut engine compile and instantiate cost; Wizer cuts the guest's own init cost), so pick it when profiling shows the module's initializer, not code translation, dominates startup; it composes with Wasmtime or any engine that loads core Wasm.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Wasmtime (Cranelift backend) with wasmparser and wasm-encoder; rayon (default feature, parallel snapshotting); wasmtime-wasi in the standalone wizer crate and the CLI |
| **Minimum toolchain** | wasmtime-wizer 48.0.x declares Rust 1.95.0 (50.0.0-rc.1: Rust 1.97.0); standalone wizer 11.0.3 builds on wasmtime 42; guest can be any language that exports an init function |
| **Platforms** | Output is a standard core Wasm module usable by any engine; the tool runs wherever Wasmtime with Cranelift builds (host list not stated in the README); disable the rayon feature for single-threaded targets |
| **Thread safety** | not documented (snapshotting is internally parallel via rayon) |
| **Drop-in for the baseline** | partial — a build step in front of Wasmtime (or any engine); the guest must export an initializer and be written so runtime paths do not redo init (e.g. LazyLock, as the bench guests do) |

## Gotchas

- UAP benchmark harness flaw (current wasmtime crates/wizer/benches/uap.rs and the original v1.1.0 harness): run() is called with length 5, so the regex set matches only 'Mozil', not the full Firefox user-agent string it allocates and copies; assert_eq!(result, 0) passes only because of that truncation (a check against uap-core's current regexes.yaml with Python re finds 2 user-agent patterns matching the full string). The 6.00x therefore measures instantiate plus init with almost no matching work; real per-request parsing in a fresh instance adds the same cost to both columns and lowers the ratio.
- The README table is from December 2020 (old Wasmtime, no CPU, Rust or Wasmtime version given); the 2020-era harness reused one Store for all iterations, while the current one creates a fresh Store per iteration and the UAP bench forces memfd memory init, so the published numbers are not what the current code would print.
- Old-repo issue #126 (open): wizer truncated the DataCount to 10,000 on a module with 80,390 data segments, producing invalid output that crashed wasm-opt; the upstream rewrite now writes previous + new segment counts, so it looks fixed in wasmtime-wizer, but the issue was never closed.
- The export name and API changed between versions: 'wizer.initialize' with Wizer::new().allow_wasi(true)?.run(&bytes) in the standalone README versus 'wizer-initialize' and an async run(&mut store, &bytes, instantiate_closure) upstream; the upstream README snippet still shows a non-async closure.

## Known shortcomings

- December 2020 first-party numbers with no hardware or versions, comparing Wasmtime with and without Wizer only (bench code now at bytecodealliance/wasmtime crates/wizer/benches/regex.rs and uap.rs). Pre-initialization tool, not a runtime; Rust.

## Caveats and trade-offs

First-party numbers with no hardware, toolchain or Wasmtime version stated; the README table dates from December 2020 (README commits of 2020-12-09), so it reflects a 2020 Wasmtime, and later Wasmtime features such as memfd/copy-on-write memory initialization change the baseline cost; the benches/ links in the bytecodealliance/wizer README now 404 because the sources moved to bytecodealliance/wasmtime crates/wizer/benches (regex.rs, uap.rs, regex-bench, uap-bench), where the current criterion code runs, but the numbers were not re-derived; development moved upstream into Wasmtime ('wasmtime wizer' subcommand, crate wasmtime-wizer), although the wizer repo is not archived and still publishes releases (v11.0.3 on 2026-03-10); the comparison is with and without the technique on one engine, not against another runtime, and the gain depends on how much work the module's initializer does (Wizer can also grow the Data section).

It is a pre-initialization tool, not an engine: it runs a module's init function and writes the resulting memory and globals back as Data segments, so the module can grow (hurting network transfer) and not every program benefits; the init code must be deterministic and free of host state.

## Maintenance

Active but relocated: development continues in bytecodealliance/wasmtime crates/wizer (wasmtime-wizer, 'wasmtime wizer'), while the old repo (1.1k stars, not archived, 20 open issues) still publishes the wizer crate as a thin re-export (v11.0.3, 2026-03-10); Apache-2.0 WITH LLVM-exception per Cargo.toml.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (regex 248.85 us vs 183.99 us, UAP 98.297 ms vs 16.385 ms) matches the record; the criterion benchmark code is public in bytecodealliance/wasmtime crates/wizer/benches/regex.rs and uap.rs (control vs wizened module on wasmtime Engine), but no CPU model, toolchain or Wasmtime version is given for the December 2020 numbers, so first-party tier C.
- **Verifier notes:** Numbers, Apache-2.0, 1.1k stars and crates.io downloads (wizer 171,371; wasmtime-wizer 144,187) verified; last commit 2026-03-10 so active. Correction: the bench code is not lost, it lives at bytecodealliance/wasmtime crates/wizer/benches; the wizer repo is not archived. Shortcomings: 2020 numbers without hardware or versions, with/without comparison on one engine only.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytecodealliance/wizer>
  - <https://github.com/bytecodealliance/wizer/commits>
  - <https://github.com/bytecodealliance/wizer/commits/main/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/HEAD/Cargo.toml>
  - <https://github.com/bytecodealliance/wasmtime/tree/main/crates/wizer>
  - <https://github.com/bytecodealliance/wasmtime/tree/main/crates/wizer/benches>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/regex.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/uap.rs>
  - <https://crates.io/api/v1/crates/wizer>
  - <https://crates.io/api/v1/crates/wasmtime-wizer>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/HEAD/src/lib.rs>
  - <https://github.com/bytecodealliance/wizer>
  - <https://github.com/bytecodealliance/wizer/issues>
  - <https://github.com/bytecodealliance/wizer/issues/126>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/v1.1.0/benches/uap.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/v1.6.0/benches/uap.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wizer/v1.6.0/benches/uap-bench/src/lib.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/src/lib.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/src/snapshot.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/src/rewrite.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/regex.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/uap.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/regex-bench/src/lib.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/uap-bench/src/lib.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/regex-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/crates/wizer/benches/uap-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/wasmtime-wizer>
  - <https://raw.githubusercontent.com/ua-parser/uap-core/master/regexes.yaml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bytecodealliance/wizer`) · [data/wave12/enrich/raw/github_com_bytecodealliance_wizer.json](../../../data/wave12/enrich/raw/github_com_bytecodealliance_wizer.json) (enrichment confidence 0.75)

</details>
