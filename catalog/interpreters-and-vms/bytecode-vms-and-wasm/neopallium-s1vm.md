# s1vm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🔴 abandoned

> Proof-of-concept safe-Rust WebAssembly interpreter that compiles functions to nested closures; beat 2021-era wasmi 2.6x on fib, lost to wasm3.

| | |
|---|---|
| **Beats** | wasmi (paritytech/wasmi as it stood in April 2021, version not stated); also compared with WASM3, which it loses to |
| **Claimed result** | README (2021-04-30): about 2.6x faster than the April 2021 wasmi on fib; the wasmi author's rerun in issue #1 at fib(25) gives s1vm 9.67 ms vs wasmi_v1 12.97 ms, about 1.34x (derived from page data). 2x slower than wasm3 per the README. |
| **Workload** | Recursive Fibonacci (fib.wasm 35 and 41) run on each interpreter. |
| **Metric** | throughput |
| **Compiler and flags** | not stated (Cargo.toml release profile has lto and codegen-units commented out) |
| **Adoption** | 16 stars; crates.io s1vm about 2.9k downloads |
| **Last commit** | 2022-05-07 |
| **Links** | [repository](https://github.com/Neopallium/s1vm) · [benchmark](https://github.com/Neopallium/s1vm) |

## Verdict

The README (2021-04-30) lists wall times for the recursive fib.wasm at n=35 and n=41: s1vm 1.29 s and 22.5 s against wasmi (the 2021 stack-machine engine, version not stated) 3.31 s and 57.6 s, about 2.6x faster (derived from page data), while wasm3 took 0.66 s and 9.8 s, about 2x faster than s1vm. No CPU, compiler flags (the release profile leaves LTO and codegen-units commented out), engine versions or timing command are given.

## Use it when

- As a design reference for writing a fast interpreter in safe Rust: closure compilation plus compile-time operand folding, in about 1,800 lines.
- Running tiny integer-only, call-heavy wasm kernels (fib-like recursion, simple counting loops) inside a codebase that forbids unsafe code, where you are prepared to add the missing opcodes yourself.
- As a starting point for a fork: MIT-licensed, few dependencies, no JIT and no platform-specific code.

## Skip it when

- Any real-world wasm module: no linear memory, globals, floats, mul/div, br_table, call_indirect, drop/select or host imports, so loading such a module panics.
- Untrusted input: unsupported opcodes, block nesting deeper than 4 and malformed control flow are panics (todo!, unreachable!, panic!) rather than errors, and the stated CPU/memory resource limits were never built.
- When speed matters most: wasm3 is about 2x faster on the same fib test, and the wasmi baseline has been replaced by register-based engines (v0.32, then 2.0) that the 2021 numbers say nothing about.
- Anything needing maintenance: abandoned since 2022-05-07, the crates.io release (0.1.1, 2021-04-30) predates the 2022 fixes, and it depends on parity-wasm, which is archived and marked deprecated and unmaintained.

## How it is fast

Closure compilation (closure-threaded code): instead of a fetch-decode match loop, control flow is rebuilt into blocks and each opcode becomes a Box&lt;dyn Fn&gt; closure, so there is no program counter and no single unpredictable dispatch branch. At compile time a symbolic operand stack (Input::Local, Input::Const, Input::Op) folds stack-machine sequences such as local.get / i32.const / i32.add into one closure, removing most runtime value-stack pushes and pops, the same idea wasm3 uses. Local 0 travels as a Rust argument (l0) instead of a stack slot, and since a February 2022 commit functions with zero or one parameter and no locals, which is exactly fib's shape, skip stack-frame setup entirely.

## Compared with alternatives

Only as a study or fork base: wasm3 (C) runs the same fib about 2x faster and is a complete interpreter, and Wasmi is the maintained Rust choice with a newer register-based engine. Pick s1vm over them only if you need a tiny #![forbid(unsafe_code)] code base whose closure-compilation design you intend to extend yourself.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bwasm 0.1.1 and parity-wasm 0.41 (parity-wasm is archived and deprecated) |
| **Minimum toolchain** | Rust 2018 edition; no rust-version declared |
| **Platforms** | any target with Rust std (pure safe Rust, no JIT, no SIMD) |
| **Thread safety** | Not documented. VM::call takes &mut self and the compiled functions are Box&lt;dyn Fn&gt; without Send/Sync bounds, so a State cannot be moved or shared across threads even though the README says a State can be shared between instances; use one VM per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark provenance: the README numbers (2021-04-30) come with no harness, CPU, compiler flags or wasmi/wasm3 versions; fib.wasm 'used in benchmark' was committed only on 2022-02-21, two days after wasmi's author asked in issue #1 how to reproduce the results, and the measured code predates the 0-1-parameter fast path (2022-02-22) and the May 2022 fixes to loops, sub-blocks, local initialisation and multi-parameter calls. His reproduction in issue #1 (fib(25)) had s1vm at 9.67 ms vs wasmi_v0 21.34 ms and wasmi_v1 12.97 ms, a lead of about 1.34x over the then-new wasmi engine, not 2.6x.
- Call-path bugs outside fib's shape (from reading the code, not run): a compiled call to a function with one or fewer parameters always pops one operand as the argument, so calling a zero-parameter function steals an unrelated operand; a one-parameter call passes its argument only in l0 and never pushes it, yet Function::call runs push_frame(1, locals) when the callee has locals, which fails with a spurious StackOverflow trap when the caller's frame has no spare value (and truncates a caller slot when it does). VM::call reads params[0], so calling an exported zero-parameter function panics.
- The deferred Input scheme reads a local only when the consuming closure runs, and local.set/local.tee do not flush pending reads, so 'local.get 0; local.get 0; i32.const 1; i32.add; local.set 0; return' returns the new value instead of the old one; if/else blocks that yield a value leave both branch values on the compile-time operand stack outside the conditional. fib.wat avoids every one of these patterns.
- Functions on the fast path push no frame, so the 1M-value stack limit never checks recursion depth; each wasm call nests several Rust closure calls on the native stack, so very deep recursion would overflow the Rust thread stack and abort instead of trapping (inferred from the code). Cargo.toml declares MIT/Apache-2.0 but only the MIT text is in the repository.

## Known shortcomings

- README numbers against a wasmi baseline from April 2021 (obsolete); 2x slower than wasm3, proof of concept with no host calls, abandoned since 2022-05-07. Rust, not C++.
- Enricher: the README numbers are dated 2021-04-30 while fib.wasm was committed 2022-02-21 after the wasmi author's issue #1 asked how to reproduce, and the measured code predates the 0-1-parameter fast path (2022-02-22) and the May 2022 fixes; the issue #1 rerun at fib(25) gives s1vm 9.67 ms vs wasmi_v1 12.97 ms, about 1.34x rather than 2.6x. Only about 20 opcodes are implemented (the rest todo!() panic at load: no memory, globals, mul/div or floats); code bugs read but not run (zero-parameter call pops a stray operand, one-parameter callee with locals gets a spurious StackOverflow, deferred local reads not flushed by local.set, if/else value results miscompiled), all avoided by fib; parity-wasm dependency archived.

## Caveats and trade-offs

Single recursive-call micro-benchmark (fib.wasm 35 and 41); no hardware, flags, harness command or engine versions stated; the README table dates from the README's first commit (2021-04-30), so the wasmi baseline is a 2021 version and wasmi's engine has been rewritten several times since (register-machine engine in v0.32, then 2.0), making the ratio obsolete; it is about 2x slower than the C interpreter WASM3 and does not beat Wasmtime, Wasmer, WAMR or V8; the author calls it a proof of concept, host-function calls are unimplemented and some opcodes are missing (README TODOs); Cargo.toml declares MIT/Apache-2.0 but only the MIT licence text is in the repository. [retier] Proof of concept with about 20 opcodes implemented (no memory, globals, mul/div or floats; the rest panic at load) and no host calls; the obsolete wasmi baseline dates from April 2021 and fib.wasm was committed only in February 2022 after the reproduction request; code bugs found by reading (stray operand pop on zero-parameter calls, spurious StackOverflow for one-parameter callees with locals, deferred local reads not flushed by local.set, if/else value results miscompiled) are all avoided by fib. parity-wasm dependency archived; abandoned since 2022-05-07. Rust, not C++.

100% safe Rust, no JIT: each function is compiled to a nest of closures instead of a match loop (design ported from WASM3); proof of concept with unfinished opcodes (host function calls are a TODO), no resource limits.

## Maintenance

Abandoned since 2022-05-07 (25 commits, 16 stars, one open issue asking how to reproduce the benchmark); MIT-licensed and small enough to vendor, but it is a proof of concept that only runs fib-like integer code, so its value is the design rather than a usable runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark section lists fib.wasm 35 and 41 wall times for wasm3, s1vm and wasmi that match the record exactly; fib.wasm/fib.wat are in the repo, but there is no harness script, no wasmi or wasm3 version, no compiler flags and no CPU model, so first-party partial methodology is tier C.
- **Verifier notes:** Numbers verified on the README; ratios 2.6x are correctly marked as derived. Shortcomings: obsolete 2021 wasmi baseline, slower than WASM3, no hardware or versions, proof-of-concept with missing opcodes and no host calls, abandoned since 2022-05-07. baseline_in_list false is correct (wave 12 baselines are wasmtime, wasmer, WAMR, V8); wasmi itself is already listed as wasmi-labs/wasmi in wave 12.
- **Fields the verifier corrected:** `baseline`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/Neopallium/s1vm>
  - <https://github.com/Neopallium/s1vm/commits>
  - <https://github.com/Neopallium/s1vm/commits/master/README.md>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/98122ec/README.md>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/LICENSE>
  - <https://crates.io/api/v1/crates/s1vm>
- **Sources the enricher read:**
  - <https://github.com/Neopallium/s1vm>
  - <https://github.com/Neopallium/s1vm/tree/master/src>
  - <https://github.com/Neopallium/s1vm/commits>
  - <https://github.com/Neopallium/s1vm/issues>
  - <https://github.com/Neopallium/s1vm/issues/1>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/Ideas.md>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/fib.wat>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/for_loop.wat>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/compiler.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/vm.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/stack.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/function.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/module.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/value.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/error.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/memory.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/export.rs>
  - <https://raw.githubusercontent.com/Neopallium/s1vm/HEAD/src/bin/main.rs>
  - <https://crates.io/api/v1/crates/s1vm>
  - <https://crates.io/api/v1/crates/parity-wasm>
  - <https://crates.io/api/v1/crates/bwasm>
  - <https://github.com/paritytech/parity-wasm>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/neopallium/s1vm`) · [data/wave12/enrich/raw/github_com_neopallium_s1vm.json](../../../data/wave12/enrich/raw/github_com_neopallium_s1vm.json) (enrichment confidence 0.6)

</details>
