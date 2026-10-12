# Language interpreters

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md)</sub>

**What these beat:** CPython, Lua 5.x, Ruby MRI, V8 (for JS)  
**50 entries:** 11 tier A · 10 tier B · 27 tier C · 2 tier D · 50 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**YJIT (CRuby)**](ruby-ruby.md) | CRuby's built-in Rust JIT; about 2x the CRuby interpreter on Rails-style apps after warmup on x86-64, 1.7x on Graviton4. | **A** | Rust | BSD-2-Clause OR Ruby | 🟢 active |
| 2 | [**Codon**](exaloop-codon.md) | LLVM-based ahead-of-time compiler for a statically typed Python subset; 10-90x faster than CPython, mostly ahead of PyPy. | **A** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**Cython**](cython-cython.md) | Python-to-C/C++ compiler; hand-typed Cython kernels ran 30-190x faster than CPython 3.10, untyped code about 1x. | **A** | Python/C | Apache-2.0 | 🟢 active |
| 4 | [**LuaJIT**](luajit-luajit.md) | Tracing JIT compiler and assembler-written interpreter for Lua 5.1; runs Lua code several times faster than PUC-Rio Lua 5.4. | **A** | C | MIT | 🟢 active |
| 5 | [**PyPy**](pypy-pypy.md) | Alternative Python interpreter with a meta-tracing JIT; runs pure-Python CPU-bound code 1.5-42x faster than CPython. | **A** | Python | MIT | 🟢 active |
| 6 | [**GraalPy**](oracle-graalpython.md) | Python 3.13 runtime on GraalVM Truffle; JIT-compiled pure Python runs many times faster than CPython, but mostly behind PyPy. | **A** | Java/Python | UPL-1.0 | 🟢 active |
| 7 | [**jrsonnet**](deltarocks-jrsonnet.md) | Rust Jsonnet interpreter, CLI and libjsonnet-compatible library; 1.9x to thousands of times faster than C++ jsonnet. | **A** | Rust | MIT | 🟢 active |
| 8 | [**Loko Scheme**](gitlab-com-weinholt-loko.md) | Self-hosted R6RS/R7RS Scheme compiling ahead of time to static amd64 binaries; beats Guile 3 on most r7rs-benchmarks. | **A** | Scheme | EUPL-1.2 | 🟢 active |
| 9 | [**rsjsonnet (Rust jsonnet)**](eduardosm-rsjsonnet.md) | Rust Jsonnet 0.22 interpreter and library crate; about 4.8x faster than go-jsonnet and about 36x faster than C++ jsonnet across a third-party suite. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 10 | [**Wangshu (望舒)**](liam0205-wangshu.md) | Pure-Go embeddable Lua 5.1 VM with NaN-boxing, a Wasm tier and a native method JIT; 2-18x faster than gopher-lua on numeric scripts. | **A** | Go | Apache-2.0 | 🟢 active |
| 11 | [**katsu**](tamnd-katsu.md) | Pre-alpha JavaScript runtime in Rust (bytecode interpreter today) that starts a hello world about 16x faster than Node and 3x faster than Bun. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 12 | [**Wren**](wren-lang-wren.md) | Tiny embeddable class-based scripting VM in C; fastest on method-dispatch benchmarks, slower than Lua 5.4 elsewhere. | **B** | C | MIT | 🟢 active |
| 13 | [**Janet**](janet-lang-janet.md) | Embeddable Lisp-family scripting language in one C99 file; roughly CPython speed, ahead only on interpreter-bound object and float code. | **B** | C | MIT | 🟢 active |
| 14 | [**TruffleRuby**](oracle-truffleruby.md) | Ruby 4.0 implementation on GraalVM/Truffle with a partial-evaluation JIT; peak-throughput wins over CRuby and YJIT on CPU-bound pure-Ruby code. | **B** | Java/Ruby | EPL-2.0 OR GPL-2.0-only OR… | 🟢 active |
| 15 | [**Pythran**](serge-sans-paille-pythran.md) | Ahead-of-time compiler from a NumPy-flavoured Python subset to C++17 extension modules; 11x-2096x faster than CPython on loop kernels. | **B** | Python | BSD-3-Clause | 🟢 active |
| 16 | [**Gambit Scheme**](gambit-gambit.md) | Scheme-to-C compiler and runtime whose executables run about 2x faster than Guile 3.0.11 on the R7RS benchmark suite. | **B** | Scheme/C | Apache-2.0 OR LGPL-2.1 | 🟢 active |
| 17 | [**lo (just-js)**](just-js-lo.md) | Small V8-based JavaScript runtime with C++ bindings; scores 1.09-1.41x Node 26 on the v8-v7 suite. | **B** | C++ | MIT | 🟢 active |
| 18 | [**sjsonnet**](databricks-sjsonnet.md) | Databricks' Scala Jsonnet interpreter (JVM, Scala Native, GraalVM, Scala.js); about 5-9x faster than go-jsonnet on real-world configs. | **B** | Scala | Apache-2.0 | 🟢 active |
| 19 | [**lumen (Rust JavaScript engine with ARM64 template JIT)**](lucid-softworks-lumen.md) | Std-only Rust JavaScript engine with an ARM64 template JIT; about 2.2x QuickJS on V8-v7 on Apple Silicon, slower on x86-64. | **B** | Rust | MIT | 🟢 active |
| 20 | [**Bigloo Scheme**](manuel-serrano-bigloo.md) | Optimizing Scheme-to-C (and JVM) compiler; about 1.6x faster than Guile 3.0.11 on the ecraven R7RS suite, slower than Chez. | **B** | Scheme/C | GPL-2.0-or-later (compiler… | 🟢 active |
| 21 | [**LuaAOT (lua-aot-5.4)**](hugomg-lua-aot-5-4.md) | Patched Lua 5.4.3 plus a bytecode-to-C compiler (luaot); compiled modules ran 1.2x to 2.6x faster than the stock interpreter. | **B** | C | MIT | 🟡 stale |
| 22 | [**CPython tail-calling interpreter**](python-cpython.md) | Opt-in CPython 3.14+ interpreter loop in which opcodes tail-call each other; 3-5% faster than computed-goto (Clang 19), 15-20% faster than switch dispatch (MSVC). | **C** | C | Python-2.0 | 🟢 active |
| 23 | [**mypyc**](python-mypy.md) | mypyc: compiles type-annotated Python modules to CPython C extensions; about 1.5x geomean on unannotated code, 2.4-22x on tuned code. | **C** | Python | MIT | 🟢 active |
| 24 | [**Nuitka**](nuitka-nuitka.md) | Python-to-C compiler that runs unmodified CPython 2.6-3.14 code; about 3.4x CPython 2.7 on pystone, far less on typical code. | **C** | Python | AGPL-3.0 | 🟢 active |
| 25 | [**LLRT (Low Latency Runtime)**](awslabs-llrt.md) | AWS Labs JavaScript runtime for Lambda (Rust plus QuickJS-NG, no JIT) that cuts Node.js 20 cold starts. | **C** | Rust | Apache-2.0 | 🟢 active |
| 26 | [**Monty (pydantic/monty)**](pydantic-monty.md) | Rust Python-subset sandbox for LLM-written code; sub-millisecond sandbox checkout versus 16 ms to 2.7 s for WASI, Docker, Pyodide and hosted sandboxes. | **C** | Rust | MIT | 🟢 active |
| 27 | [**scriptc (Vercel Labs TypeScript to native compiler)**](vercel-labs-scriptc.md) | Ahead-of-time TypeScript-to-native compiler; executables start in about 2 ms against tens of milliseconds for Node and Bun, but run hot loops slower. | **C** | TypeScript | Apache-2.0 | 🟢 active |
| 28 | [**Porffor (AOT JavaScript/TypeScript to Wasm and C)**](canadahonk-porffor.md) | Ahead-of-time JavaScript/TypeScript compiler emitting C and native binaries; first-party V8-suite score beats QuickJS and Node --jitless, not JIT engines. | **C** | JavaScript | MIT | 🟢 active |
| 29 | [**Spinel**](matz-spinel.md) | Ahead-of-time Ruby-subset-to-C compiler by Matz; README geomean 8.5x faster than CRuby 4.0.4 with YJIT. | **C** | C | MIT | 🟢 active |
| 30 | [**pocketpy**](pocketpy-pocketpy.md) | Embeddable Python-subset interpreter in C11 for game scripting; about 1.2x CPython 3.8 on one old benchmark, slower than Lua. | **C** | C | MIT | 🟢 active |
| 31 | [**KPHP**](vkcom-kphp.md) | VK's ahead-of-time compiler from strictly typed PHP to C++; first-party 5-7x over PHP 7.4 on Zend benchmarks. | **C** | C++ | GPL-3.0 | 🟢 active |
| 32 | [**pocketlang**](thakeenathees-pocketlang.md) | Tiny embeddable C99 bytecode VM with Ruby-flavoured Python syntax; roughly CPython speed, well behind Lua 5.3. | **C** | C | MIT | 🟢 active |
| 33 | [**Shed Skin**](shedskin-shedskin.md) | Ahead-of-time transpiler from implicitly statically typed Python 3 to C++; README claims 12x median over CPython 3.14. | **C** | Python | GPL-3.0 (compiler)… | 🟢 active |
| 34 | [**Pyccel**](pyccel-pyccel.md) | Ahead-of-time transpiler from type-annotated Python to C or Fortran extension modules; 5x-2000x faster than CPython on scalar-loop numeric kernels. | **C** | Python | MIT | 🟢 active |
| 35 | [**Regorus**](microsoft-regorus.md) | Rust Rego interpreter (OPA's policy language), embeddable from C/C++; about 10x faster than an opa eval CLI run on one ACI policy. | **C** | Rust | MIT | 🟢 active |
| 36 | [**bc and dc (Gavin Howard)**](gavinhoward-bc.md) | POSIX bc/dc in C, plus the bcl library; its bignum math beats GNU bc 1.07.1, its interpreter loop does not. | **C** | C | BSD-2-Clause | 🟢 active |
| 37 | [**Paserati**](nooga-paserati.md) | Pure-Go TypeScript/JavaScript bytecode interpreter, about 1.2-1.7x faster than goja on V8 v7; native QuickJS is about 3x faster. | **C** | Go | MIT | 🟢 active |
| 38 | [**newLISP Neo**](kimtg-newlisp-neo.md) | newLISP 10.7.6 rebuilt with a computed-goto bytecode VM, tail calls and a nursery GC; beats CPython 3.14 on fib(30). | **C** | C | GPL-3.0 | 🟢 active |
| 39 | [**Mobius**](bholcomb-mobius.md) | Embeddable C-syntax scripting language with a register bytecode VM; about 16% less total time than Lua 5.4 on its own micro-suite. | **C** | C++ | MIT | 🟢 active |
| 40 | [**WeavePy**](weavefoundry-weavepy.md) | Experimental Rust Python 3.14 interpreter with a Cranelift JIT; about 2x CPython 3.14.8 on its own fixtures. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 41 | [**cpy**](moonlite-br-cpy.md) | Tree-walking interpreter for a Python subset in portable C; claims 1.2x-50x over CPython 3.12 with no published benchmark scripts. | **C** | C | MIT | 🟢 active |
| 42 | [**Pyston**](pyston-pyston.md) | CPython 3.8 fork plus pip-installable JIT module (DynASM baseline JIT, quickening, inline caches); about 10-30% faster than stock CPython 3.8. | **C** | C | Python-2.0 (CPython license… | 🟡 stale |
| 43 | [**MiniVM**](fastvm-minivm.md) | Small C register VM running a Lua subset; 2022 build beat luajit -joff on fib(35) but lost to LuaJIT's JIT. | **C** | C | MIT | 🟡 stale |
| 44 | [**Lightstorm**](dragonruby-lightstorm.md) | Ahead-of-time compiler from mruby 3.0 bytecode to C via MLIR/EmitC; about 1.4x faster than the mruby VM on aobench. | **C** | C++ | MIT | 🟡 stale |
| 45 | [**prometeo**](zanellia-prometeo.md) | Typed-Python-subset DSL transpiled to self-contained C on BLASFEO; beats CPython, Nuitka and PyPy on a Fibonacci loop. | **C** | Python | BSD-2-Clause | 🔴 abandoned |
| 46 | [**pqR (a pretty quick implementation of R)**](radfordneal-pqr.md) | Radford Neal's fork of GNU R 2.15 with a faster interpreter, GC and builtins; beats R-3.4/3.5 on many operations. | **C** | C | GPL-2.0-only OR GPL-3.0-only | 🔴 abandoned |
| 47 | [**cperl**](perl11-cperl.md) | Diverged Perl 5 fork with types, faster signatures and FNV1a hashing; about 6% faster than perl 5.30.0 on PerlBench. | **C** | C | GPL-1.0-or-later OR… | 🔴 abandoned |
| 48 | [**Dino**](dino-lang-dino.md) | Research scripting language and VM in C (RTL bytecode, type-inferred specialization, GCC-based JIT); beats Python 3.4 and Ruby 2.1 interpreters. | **C** | C | GPL-2.0-or-later (DINO… | 🔴 abandoned |
| 49 | [**TypeScriptCompiler (ASDAlexander77, LLVM-based TypeScript…**](asdalexander77-typescriptcompiler.md) | LLVM/MLIR ahead-of-time and JIT compiler for a TypeScript subset; no published speed comparison against Node/V8. | **D** | C++ | MIT | 🟢 active |
| 50 | [**TurboPython / tpy (typed Python to C++ without GC)**](trozen-tpy-lang.md) | Pre-1.0 compiler from annotated Python to C++23 binaries without GC or refcounting; no published speed numbers against CPython. | **D** | Python | Apache-2.0 WITH… | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
