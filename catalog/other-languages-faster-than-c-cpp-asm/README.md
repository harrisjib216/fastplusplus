# Other languages beating C, C++ and assembly

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Benchmarks where Rust, Zig, Julia, Go, Java and other languages beat the same task written in C, C++ or assembly, with the mechanism behind each win.

**297 entries in 6 categories:** 65 tier A · 15 tier B · 153 tier C · 64 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Concurrency runtimes](concurrency-runtimes/README.md) | 21 | 1 | 1 | 12 | 7 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |
| [Numerics and arrays](numerics-and-arrays/README.md) | 38 | 5 | 1 | 20 | 12 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |
| [Runtime JIT beats ahead-of-time](runtime-jit-beats-aot/README.md) | 46 | 12 | 0 | 21 | 13 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |
| [Strings and text](string-and-text/README.md) | 66 | 16 | 6 | 34 | 10 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |
| [Systems and safety](systems-and-safety/README.md) | 70 | 12 | 3 | 45 | 10 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |
| [Web and serving](web-and-serving/README.md) | 56 | 19 | 4 | 21 | 12 | the same task written in C or C++ at -O3, or hand-written assembly where the source… |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**Rust slice::sort (LangArena Sort::Self) vs C++ std::sort**](systems-and-safety/lang-rust-kostya-langarena-sort-self.md) | Rust's built-in slice::sort (driftsort) sorts 400k int32 about 2.4x faster than libstdc++ std::sort in LangArena Sort::Self. | [Systems and safety](systems-and-safety/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**Zig compiler (zig build-exe) compile throughput vs gcc and…**](systems-and-safety/lang-zig-nordlow-compiler-benchmark-compile-throughput.md) | Zig's self-hosted x86-64 backend and linker build a 40,000-function test file 3.6-4.1x faster than gcc, about level with clang. | [Systems and safety](systems-and-safety/README.md) | **A** | Zig | MIT | 🟢 active |
| 3 | [**Zig std.sort.pdq (LangArena Sort::Self) vs C++ std::sort**](systems-and-safety/lang-zig-kostya-langarena-sort-self.md) | Zig's standard-library pdqsort (std.sort.pdq) sorts 400k int32 about 1.2x faster than libstdc++ std::sort in LangArena Sort::Self. | [Systems and safety](systems-and-safety/README.md) | **A** | Zig | MIT | 🟢 active |
| 4 | [**Kestrel (ASP.NET Core HTTP server, HttpArena kestrel entry)**](web-and-serving/dotnet-aspnetcore.md) | ASP.NET Core's managed HTTP server; in HttpArena it beats nginx on pipelined and cleartext HTTP/2 but loses on plain HTTP/1.1, TLS and HTTP/3. | [Web and serving](web-and-serving/README.md) | **A** | C# | MIT | 🟢 active |
| 5 | [**actix-web**](web-and-serving/actix-actix-web.md) | Full-featured Rust HTTP/1.1 and HTTP/2 web framework; in HttpArena it beats Drogon and Cutelyst (C++) but trails nginx and h2o. | [Web and serving](web-and-serving/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 6 | [**Nim ref-object binary trees (LangArena Binarytrees::Obj) vs…**](systems-and-safety/lang-nim-kostya-langarena-binarytrees-obj.md) | Nim 2.2.12 ref objects (default ORC, Nim's own allocator) build and free depth-20 trees 1.35x faster than the best make_unique C++ build. | [Systems and safety](systems-and-safety/README.md) | **A** | Nim | MIT | 🟢 active |
| 7 | [**Quarkus (Vert.x/Netty, JDK 21)**](web-and-serving/quarkusio-quarkus.md) | Java framework (Jakarta REST on Vert.x/Netty) that beats nginx's HTTP/2-over-TLS path on HttpArena but loses every scored HTTP/1.1 profile. | [Web and serving](web-and-serving/README.md) | **A** | Java | Apache-2.0 | 🟢 active |
| 8 | [**Eclipse Vert.x (HttpArena vertx entry)**](web-and-serving/eclipse-vertx-vert-x.md) | JVM event-loop HTTP toolkit on Netty; beats some C++ servers on HttpArena but trails nginx, h2o and mongoose on scored profiles. | [Web and serving](web-and-serving/README.md) | **A** | Java | EPL-2.0 OR Apache-2.0 | 🟢 active |
| 9 | [**Odin compiler compile throughput vs gcc and g++ in…**](systems-and-safety/lang-odin-nordlow-compiler-benchmark-compile-throughput.md) | The Odin compiler at its default -o:minimal builds a 40,000-procedure generated file 1.3-2.7x faster than GCC compiles the C twin, but slower than clang. | [Systems and safety](systems-and-safety/README.md) | **A** | Odin | Zlib | 🟢 active |
| 10 | [**C3 compiler (c3c) compile throughput vs gcc and g++ in…**](systems-and-safety/lang-c3-nordlow-compiler-benchmark-compile-throughput.md) | C3's c3c compiler at -O0 builds a 40,000-function generated file 1.8-3.7x faster than GCC compiles the C equivalent, but slower than clang. | [Systems and safety](systems-and-safety/README.md) | **A** | C3 | MIT (compiler source under… | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
