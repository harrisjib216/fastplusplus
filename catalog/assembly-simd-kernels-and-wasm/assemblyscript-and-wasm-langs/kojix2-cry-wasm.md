# cry-wasm (Ruby methods compiled to WebAssembly through Crystal)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Crystal` · `MIT` · 🟢 active

> Experimental Ruby gem that compiles type-annotated Ruby methods to Crystal, then Wasm; about 11-14x CRuby on recursive fib(40).

| | |
|---|---|
| **Beats** | CRuby (pure Ruby interpreter) running the same function |
| **Claimed result** | README Benchmark.bmbm, fib(40) user time: ruby 5.305503 s, wasmtime 0.462232 s, wasmer 0.381384 s (about 11.5x and 13.9x faster than CRuby, derived from page data; README says 10x faster); Wasmer about 10% faster than Wasmtime as of December 2022; Wasm about twice as slow as native Crystal per the author's unpublished measurements. |
| **Workload** | Recursive Fibonacci fib(40) from examples/fib_bench.rb (Benchmark.bmbm with rehearsal): the same Ruby method run by CRuby versus compiled to Crystal (Int32 signature) and Wasm, called from Ruby via wasmtime-rb or wasmer-ruby; a Benchmark.plot over n = 1..20 shows first-call overhead for both Wasm runtimes. |
| **Metric** | latency |
| **Compiler and flags** | lib/cry/compiler.rb builds 'crystal build &lt;tmp&gt; -o /dev/stdout --target wasm32-wasi --link-flags="--export &lt;fn&gt;"' through wasm-ld with the wasm32-wasi libs; the :release option is accepted but never added to the command, so the module is a non-release Crystal build; Ruby, Crystal, wasmtime-rb and wasmer-ruby versions not stated |
| **Adoption** | 33 stars, 0 forks, 174 commits; no GitHub releases |
| **Last commit** | 2026-06-19 |
| **Links** | [repository](https://github.com/kojix2/cry-wasm) · [benchmark](https://github.com/kojix2/cry-wasm) |

## Verdict

The README's Benchmark.bmbm output from December 2022 (examples/fib_bench.rb, no CPU, Ruby, Crystal or runtime versions given) shows one fib(40) call taking 5.31 s user time in CRuby, against 0.462 s for the same method compiled to Crystal Int32 code and Wasm under wasmtime-rb and 0.381 s under wasmer-ruby, about 11.5x and 13.9x (derived from page data). The Wasm module was built at Crystal's default -O0, and the claim that Wasm is about twice as slow as native Crystal is the author's unpublished measurement.

## Use it when

- Experiments with a small, self-contained numeric Ruby method (integer or float scalars in, scalar out) that is called once and runs for a long time, like the fib(40) benchmark, where the single Ruby-to-Wasm crossing is negligible.
- When you want a sandboxable Wasm artifact of a Ruby hot loop and already have Crystal, wasm-ld and the wasm32-wasi libs on macOS or Linux.
- Prototyping how much static typing alone buys over CRuby before writing a C, Rust or Crystal native extension.

## Skip it when

- Methods that return arrays or take large arrays: every element is copied through Wasm memory, the Wasmer adapter reads it byte by byte in Ruby, and the README warns this can be slower than pure Ruby.
- Code that relies on Ruby Integer semantics: the Int32 signature makes arithmetic fixed-width, so the benchmark's own fib definition overflows Int32 at fib(47) where CRuby would return a Bignum; overflow behaviour inside Wasm is not documented.
- Production use: version 0.0.0, labelled experimental, not published on RubyGems, Windows unsupported, CI badge failing as of 2026-10-12, and it needs wasmer-ruby and wasmtime-rb from git master (wasmer-ruby's last commit is from October 2023 and its README lists Ruby 2.6-3.0).
- Short, frequently called methods: both runtimes are slower on the first call (README plot at n = 1), and each call goes through a Ruby-level wrapper that builds argument arrays.
- Comparisons against a modern CRuby: the baseline Ruby version and whether YJIT was on are not stated, so the 10x figure may shrink with a JIT-enabled CRuby (not measured).

## How it is fast

The speedup is ahead-of-time static typing: once the method is Crystal code with fixed-width Int32 arguments, the recursion compiles (through LLVM to Wasm, then the Wasm runtime's compiler to machine code) into direct calls with machine-integer arithmetic, removing CRuby's method dispatch and its tagged-Integer arithmetic with overflow-to-Bignum checks. There is no algorithmic change; the gem only translates the same Ruby source.

## Compared with alternatives

Pick it only when the host program is Ruby: the other wasm-language siblings (Speedy.js, wasm-perf, AutoZig, msf/wasmplay's Zig build) compile to Wasm for JavaScript or WASI hosts and beat V8 JavaScript or Emscripten C++, while cry-wasm is the one entry that accelerates CRuby methods, at a much lower maturity level than those.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Crystal compiler, wasm-ld (LLVM lld), wasm32-wasi libs from lbguilherme/wasm-libs (rake vendor:wasi_libs), sorcerer gem, wasmer-ruby and/or wasmtime-rb from git master (Rust toolchain to build them) |
| **Minimum toolchain** | Ruby &gt;= 2.7 (gemspec); CI uses Ruby 3.2 with the latest Crystal from crystal-lang.org/install.sh; no Crystal version pinned |
| **Platforms** | macOS and Ubuntu (CI); Windows not supported |
| **Thread safety** | not documented; each class holds one Wasm instance and store shared by all its objects |
| **Drop-in for the baseline** | partial: the Ruby method body is reused unchanged, but the class must extend Cry::Wasm, every compiled method needs a `cry` signature and a `cry_build` call, and only Crystal-compatible code with the supported argument types can be compiled |

## Gotchas

- Benchmark harness: the Wasm module is a Crystal -O0 build, because Compiler#set_options stores :release but build_command never adds --release (Crystal's default is -O0; --release means -O3 --single-module), so the 11.5x and 13.9x come from unoptimised Crystal output that only the Wasm runtime's own compiler optimises. fib_bench.rb makes one fib(40) call per report, so it measures recursion inside Wasm, not the Ruby-to-Wasm call path, and the README names no CPU, Ruby, Crystal, wasmtime-rb or wasmer-ruby version. Both arms run the same recursion and fib(40) = 102,334,155 fits in Int32, so no correctness bug sits behind the numbers.
- Bug in lib/cry/compiler.rb: `if (options.output = '/dev/stdout')` is an assignment, not a comparison, so passing an output path to cry_build (wasm_out) makes build_wasm return the compiler's empty stdout instead of reading the written file; only the default stdout path works.
- Every array or String argument is copied into a fresh Pointer.malloc buffer in Wasm memory on each call and never released (the wrapper ends with '# FIXME: Release memory').
- The WASI sandbox is opened wide: the Wasmtime adapter passes the full host ENV and ARGV and inherits stdout/stderr; the Wasmer adapter maps the host current directory using test-program boilerplate ('wasi_test_program', '--test'); and each `Klass.new` re-runs the module's `_start` on the class's shared instance.

## Known shortcomings

- One microbenchmark (fib(40) 5.31 s Ruby vs 0.46/0.38 s) with no CPU or versions; compiler.rb never passes --release; feature work ended in 2022.
- The Wasm module is built at Crystal -O0: the :release option is stored but never passed (Crystal's default is -O0; --release means -O3 --single-module), so the 11.5x and 13.9x come from unoptimised Crystal output optimised only by the Wasm runtime. One fib(40) call per report; CRuby version and YJIT status unstated; fib(40) fits Int32, so no correctness bug behind the numbers. Bugs: 'if (options.output = '/dev/stdout')' in compiler.rb is an assignment, so cry_build(wasm_out) returns empty bytes; per-call buffers are never freed (FIXME); WASI exposes the full host ENV (Wasmtime) and the current directory (Wasmer). CI badge failing; v0.0.0, not on RubyGems; wasmer-ruby last commit October 2023.

## Caveats and trade-offs

One recursive microbenchmark with no CPU model, from December 2022; the latest commit is only a dependency/CI bump, feature work dates from 2022. Baseline is CRuby, not the category's TypeScript/V8 or Emscripten baselines; shown here because Crystal-to-Wasm is a wasm-targeting route.

Needs type annotations on Ruby methods and the Crystal toolchain. Returning arrays from Wasm to Ruby is slow and can be slower than pure Ruby (README). Wasmer and Wasmtime first call is slower.

## Maintenance

Experimental and effectively dormant: feature work ended in December 2022 (last code commit 'Use to_unsafe to create a pointer', 2022-12-26), later commits through 2026-06-19 are Renovate CI bumps, the CI badge reads failing, and the gem is version 0.0.0 and not on RubyGems; MIT-licensed and small enough to read in an afternoon.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Benchmark.bmbm output in the README from public code (examples/fib_bench.rb) comparing pure CRuby with the Crystal-compiled Wasm under wasmtime-rb and wasmer-ruby; no CPU model, Ruby, Crystal or runtime versions stated, so C.
- **Verifier notes:** Numbers match the README; one call-heavy integer microbenchmark from December 2022, labelled experimental, with the Wasm built without --release and the CRuby baseline without YJIT or version info. README itself warns that returning arrays can be slower than pure Ruby; last commit 2026-06-19 is a CI action bump, feature work ended 2022-12.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-65 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kojix2/cry-wasm>
  - <https://github.com/kojix2/cry-wasm/commits>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/examples/fib_bench.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/compiler.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/wasm.rb>
- **Sources the enricher read:**
  - <https://github.com/kojix2/cry-wasm>
  - <https://github.com/kojix2/cry-wasm/commits>
  - <https://github.com/kojix2/cry-wasm/actions>
  - <https://github.com/kojix2/cry-wasm/actions/workflows/ci.yml/badge.svg>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/examples/fib_bench.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/examples/fib_simple.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/compiler.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/wasm.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/wasmtime.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/wasmer.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/codegen.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/codegen/crystallizer.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/codegen/allocation_functions.cr>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/lib/cry/wasm/version.rb>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/cry-wasm.gemspec>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/Gemfile>
  - <https://raw.githubusercontent.com/kojix2/cry-wasm/HEAD/.github/workflows/ci.yml>
  - <https://rubygems.org/api/v1/gems/cry-wasm.json>
  - <https://github.com/wasmerio/wasmer-ruby>
  - <https://github.com/wasmerio/wasmer-ruby/commits>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/master/src/compiler/crystal/command.cr>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/kojix2/cry-wasm`) · [data/wave13/enrich/raw/github_com_kojix2_cry_wasm.json](../../../data/wave13/enrich/raw/github_com_kojix2_cry_wasm.json) (enrichment confidence 0.8)

</details>
