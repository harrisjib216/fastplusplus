# Interpreters and VMs

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Interpreters, JIT compilers, embeddable scripting engines and bytecode VMs measured against CPython, Lua, V8 and wasmtime.

**230 entries in 4 categories:** 38 tier A · 66 tier B · 117 tier C · 9 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Bytecode VMs and WebAssembly runtimes](bytecode-vms-and-wasm/README.md) | 57 | 9 | 16 | 28 | 4 | wasmtime, wasmer, WAMR, V8 |
| [Embedded scripting](embedded-scripting/README.md) | 62 | 6 | 29 | 25 | 2 | Lua, Duktape, QuickJS |
| [JIT compilers](jits/README.md) | 61 | 12 | 11 | 37 | 1 | PyPy, LuaJIT, V8, HotSpot |
| [Language interpreters](language-interpreters/README.md) | 50 | 11 | 10 | 27 | 2 | CPython, Lua 5.x, Ruby MRI, V8 (for JS) |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**CPython copy-and-patch JIT**](jits/python-cpython-jits.md) | CPython's built-in experimental copy-and-patch trace JIT; 7.5% (x86-64 Linux) to 11% (macOS arm64) geomean over the plain interpreter. | [JIT compilers](jits/README.md) | **A** | C | Python-2.0 | 🟢 active |
| 2 | [**Julia**](jits/julialang-julia.md) | Dynamic language JIT-compiled through LLVM per concrete argument types; beats LuaJIT, PyPy and Node on loop-heavy CPU code. | [JIT compilers](jits/README.md) | **A** | Julia | MIT | 🟢 active |
| 3 | [**PHP JIT (php-src opcache JIT)**](jits/php-php-src.md) | PHP's built-in opcache JIT: 2-9.5x faster than the plain PHP 8.2 interpreter on numeric benchmarks-game kernels. | [JIT compilers](jits/README.md) | **A** | C | BSD-3-Clause | 🟢 active |
| 4 | [**YJIT (CRuby)**](language-interpreters/ruby-ruby.md) | CRuby's built-in Rust JIT; about 2x the CRuby interpreter on Rails-style apps after warmup on x86-64, 1.7x on Graviton4. | [Language interpreters](language-interpreters/README.md) | **A** | Rust | BSD-2-Clause OR Ruby | 🟢 active |
| 5 | [**.NET runtime (CoreCLR RyuJIT)**](jits/dotnet-runtime.md) | The .NET runtime's RyuJIT tiered JIT runs kostya's brainfuck interpreters 2-7x faster than Node.js, LuaJIT and PyPy, though still behind HotSpot. | [JIT compilers](jits/README.md) | **A** | C# and C++ | MIT | 🟢 active |
| 6 | [**Codon**](language-interpreters/exaloop-codon.md) | LLVM-based ahead-of-time compiler for a statically typed Python subset; 10-90x faster than CPython, mostly ahead of PyPy. | [Language interpreters](language-interpreters/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**QuickJS**](embedded-scripting/bellard-quickjs.md) | Fabrice Bellard's small embeddable C JavaScript interpreter; about 2.3x Duktape on the V8 v7 benchmark suite. | [Embedded scripting](embedded-scripting/README.md) | **A** | C | MIT | 🟢 active |
| 8 | [**Cython**](language-interpreters/cython-cython.md) | Python-to-C/C++ compiler; hand-typed Cython kernels ran 30-190x faster than CPython 3.10, untyped code about 1x. | [Language interpreters](language-interpreters/README.md) | **A** | Python/C | Apache-2.0 | 🟢 active |
| 9 | [**wasm3**](bytecode-vms-and-wasm/wasm3-wasm3.md) | Portable, dependency-free C WebAssembly interpreter; fastest of seven interpreters on scalar MVP code, about 1.6x WAMR fast-interp on Apple M4. | [Bytecode VMs and WebAssembly runtimes](bytecode-vms-and-wasm/README.md) | **A** | C | MIT | 🟢 active |
| 10 | [**Chez Scheme**](jits/cisco-chezscheme.md) | R6RS Scheme compiled to native code at load time; beats LuaJIT, PyPy and Node on integer-heavy interpreter loops, loses badly on boxed-float code. | [JIT compilers](jits/README.md) | **A** | Scheme and C | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
