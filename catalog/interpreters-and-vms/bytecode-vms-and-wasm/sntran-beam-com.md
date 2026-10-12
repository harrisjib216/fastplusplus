# BEAM.com (Erlang/OTP + Elixir single Cosmopolitan binary)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Erlang` · `Apache-2.0` · 🟢 active

> Erlang/OTP 29 plus Elixir 1.20 as one Cosmopolitan executable; beats only its own interpreter build, not stock OTP.

| | |
|---|---|
| **Beats** | beam-emu.com, the same repository's own interpreter-only build (BeamAsm JIT off); no comparison against stock Erlang/OTP is published |
| **Claimed result** | JIT build against the repo's own interpreter build, CI Linux x86_64 (ms, interpreter -&gt; JIT): fib 70 -&gt; 30, lists 249 -&gt; 116, binary 249 -&gt; 133, maps 83 -&gt; 68, ets 70 -&gt; 64, messages 111 -&gt; 117; Linux aarch64: fib 139 -&gt; 12, lists 411 -&gt; 104, binary 290 -&gt; 91; startup is slower with the JIT (--version 142 -&gt; 222 ms on Linux x86_64). Stored kernel/stdlib zip entries cut start of beam.com --version from 193-202 ms to 143-146 ms (local, own earlier variant). No number against stock Erlang/OTP. |
| **Workload** | tests/bench/bench.erl run with the JIT build (beam.com) and the interpreter build (beam-emu.com): fib(32), lists:sort/map/foldl on 1,000,000 numbers, 200,000 map and ETS inserts and lookups, 5 MB binary match, 200,000 messages, startup time; best of 3 runs. |
| **Metric** | throughput |
| **Hardware** | CI runners (shared machines) and a local Linux x86_64 box with 4 CPUs; CPU model not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/sntran/BEAM.com) · [benchmark](https://github.com/sntran/BEAM.com/blob/main/docs/BENCHMARKS.md) |

## Verdict

docs/BENCHMARKS.md compares the repo's own JIT build (beam.com) with its interpreter build (beam-emu.com), both cosmocc 4.0.2 at -O2, on shared CI runners and a 4-CPU Linux x86_64 box with no CPU model: Linux x86_64 fib(32) 70 to 30 ms, lists 249 to 116, binary 249 to 133, messages 111 to 117 (no gain), start 142 to 222 ms (slower); Linux aarch64 fib 139 to 12 ms. Storing kernel and stdlib uncompressed cut start from 193-202 ms to 143-146 ms against its own all-compressed variant; nothing is measured against stock Erlang/OTP.

## Use it when

- You want to ship an Erlang or Elixir CLI tool or service as one file that runs on six operating systems and two CPUs with no Erlang install.
- Long-running Erlang code on aarch64 (Apple Silicon, ARM servers) where the default JIT build is 3-12x faster than its interpreter build on calls, lists and binaries.
- Running a Phoenix or Cowboy app unchanged on Cloudflare Workers, Deno Deploy or in a browser tab via its WebAssembly runtime.
- Short command-line programs where start time matters: use beam-emu.com, which starts 40 to 90 ms faster than the JIT build.

## Skip it when

- As a faster Erlang VM: there is no measurement against stock Erlang/OTP, and several build choices (below) make parts of it slower than a normal OTP install.
- TLS- or crypto-heavy services: OpenSSL 4.0.3 is built with no-asm, so the crypto NIF runs portable C code; the bench's SHA-256 of 64 MB takes 237-254 ms, about 260 MB/s (derived from page data).
- Servers with many concurrent sockets: ERTS is configured with --disable-kernel-poll and the select() backend (no epoll or kqueue), capped at FD_SETSIZE, and without the socket NIF (--disable-esock).
- Projects that need native NIFs or drivers from shared objects, git dependencies, umbrella projects, config/runtime.exs, run_erl, port programs on Windows, or OpenBSD 7.4 and later.
- Production use where maturity counts: 0 stars, one maintainer, first release candidates (v0.1.0-rc.2), and the Cosmopolitan fd-table races it had to patch around.

## How it is fast

Nothing in the VM is faster than stock OTP: the speed numbers compare BeamAsm (OTP's own JIT, x86 and arm backends compiled into one fat binary) with the repo's interpreter build of the same code. The only packaging-level speedup is storing kernel and stdlib uncompressed in the zip so the boot reads them without inflating (start of `--version` 193-202 ms to 143-146 ms, local Linux x86_64, interpreter build). Running from the zip in place avoids the unpack-on-first-run step of Burrito and Bakeware.

## Compared with alternatives

None of the catalogued siblings runs Erlang: they are Wasm and EVM engines, and BEAM.com only embeds WAMR as its Wasm interpreter (no Wasm JIT, no SIMD), so use WAMR or Wasmi directly for WebAssembly. Pick BEAM.com over Burrito or Bakeware when you want one file for every OS and CPU with no unpack step, and over a normal OTP install only for distribution convenience, never for speed.

## Integration

| | |
|---|---|
| **Form** | single prebuilt executable (APE); also an npm package for the WebAssembly runtime |
| **Dependencies** | none at run time (Erlang/OTP 29.1.1, Elixir 1.20.4, OpenSSL 4.0.3, SQLite via esqlite, WAMR and Cosmopolitan Libc are linked in); building it needs cosmocc 4.0.2 |
| **Minimum toolchain** | none to run; build: cosmocc 4.0.2 (GCC-based), OTP CFLAGS -O2 -g, SQLite -Os; Node.js 25+ or Deno 2.9 for the WebAssembly runtime (JSPI) |
| **Platforms** | Linux x86_64/aarch64 (and WSL2), macOS arm64/x86_64, Windows x86_64 (no port programs), FreeBSD, NetBSD and OpenBSD 7.3 via the APE loader; Cloudflare Workers, Deno Deploy, browsers with JSPI |
| **Thread safety** | standard ERTS SMP schedulers; BEAM.com wraps Cosmopolitan close() under the fd-table lock to fix two races (C25, C26 in docs/UPSTREAM.md) that broke about 1 in 100 busy starts and crashed some builds |
| **Drop-in for the baseline** | partial — runs unmodified Erlang/Elixir code and releases built for OTP 29.1.1, but not native NIF .so files, the socket module, kernel poll or Windows port programs |

## Gotchas

- Not unmodified OTP: two patches plus configure overrides (select() poll backend, no esock, no sendfile, no Linux THP alignment, --disable-security-hardening-flags, zstd without assembly, and the JIT built without the native stack on x86_64 too, where stock OTP enables it).
- The headline aarch64 gains (fib 139 to 12 ms, about 11.6x) are JIT against an interpreter the docs call slow (fib 2-3x slower than on x86_64); they say nothing about stock OTP's JIT or interpreter.
- Harness: bench.erl times each workload with timer:tc rounded down to whole ms, best of 3, on shared CI runners with about 10% noise and no CPU model; the start rows take the 5th of 10 sorted runs and include the sh launcher; the first local table compares an x86_64-only interpreter file with the fat JIT file; the performance gate compares a PR only with the edge build of main.
- The WebAssembly runtime runs Erlang code at 1.2-1.4x the time of the native interpreter in Node.js and 25-30% slower again in workerd; on Cloudflare the clock does not move during work, so timer:tc gives no CPU time there.

## Known shortcomings

- Only its own JIT build vs its own interpreter build (stock OTP BeamAsm vs emu), nothing against stock Erlang/OTP, which already ships BeamAsm; the Wasm build is slower than native. 0 stars, Erlang packaging rather than C++. Kept at D under the keep-and-document rule.
- Enricher: slower than stock OTP by build choice (scripts/steps.sh): OpenSSL 4.0.3 built no-asm (SHA-256 of 64 MB in 237-254 ms, about 260 MB/s, derived), --disable-kernel-poll (select() backend with the FD_SETSIZE cap), no esock, JIT enable_native_stack=no on x86_64 too, --disable-security-hardening-flags. The aarch64 11.6x is against an interpreter its own docs call slow. Harness: whole-millisecond timer:tc, best of 3, shared CI noise about 10%, no CPU model, and the first local table compares an x86_64-only interpreter file with a fat JIT file.

## Caveats and trade-offs

Nothing in the repo shows BEAM.com beating stock Erlang/OTP. The BeamAsm JIT it ships is the one stock OTP already has on x86_64 and aarch64, so the fib gains (2.3x on Linux x86_64, about 11.6x on Linux aarch64) are JIT against interpreter, not against the incumbent BEAM. The measurements are first-party, from shared CI machines with noise it puts at about 10%, with no CPU model or compiler flags. The gate tables carry only relative limits. The JIT build starts 40 to 90 ms slower than the interpreter build. The only part faster by design is the packaging: one portable file, and storing kernel and stdlib uncompressed starts about 27% faster than its own all-compressed variant (193-202 ms to 143-146 ms). Its WebAssembly build (docs/WORKERS.md) runs Erlang code at 1.2 to 1.4 times the time of the native interpreter in Node.js, so it is slower there. The repo bundles Erlang/OTP, Elixir, Cosmopolitan Libc, OpenSSL, SQLite and WAMR under their own licenses (NOTICE, licenses/). It is not a C++ library. Kept as tier D because no recognizable baseline is beaten.

Packaging of the unmodified Erlang/OTP 29 ERTS and Elixir 1.20 as one Actually Portable Executable (Cosmopolitan Libc, about 50 MB, also a zip with the OTP applications); runs on Linux, macOS, Windows, FreeBSD, NetBSD and OpenBSD on x86_64 and aarch64; includes OpenSSL, SQLite and WAMR. The JIT adds 2.8 MB and 40 to 90 ms of start time. A second runtime (ERTS compiled to WebAssembly) runs on Cloudflare Workers and Deno Deploy at 1.2 to 1.4 times the time of the native interpreter in Node.js (WORKERS.md, October 2026).

## Maintenance

Very active (511 commits, last commit 2026-10-06, release candidate v0.1.0-rc.2) and Apache-2.0 with bundled third-party licences, but a single-maintainer project with 0 stars whose value is portable packaging, not speed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** docs/BENCHMARKS.md has first-party CI and local tables, but they only compare the repo's own JIT build with its own interpreter build and packaging variants. That is stock OTP BeamAsm against the stock emu flavor, not BEAM.com against stock Erlang/OTP. There are no numbers against a recognizable incumbent, so the tier stays D.
- **Verifier notes:** The numbers in claimed_speedup match BENCHMARKS.md (Linux x86_64 fib 70 to 30, lists 249 to 116, binary 249 to 133, maps 83 to 68, ets 70 to 64, messages 111 to 117; aarch64 fib 139 to 12, lists 411 to 104, binary 290 to 91). They are an internal JIT-vs-emu comparison, not a win over stock OTP. Shortcomings: no comparison against stock Erlang/OTP, 0 stars, Erlang packaging project rather than C++, and the Wasm build is slower than native. Apache-2.0, last commit 2026-10-06, active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** comparison with a stock OTP install; comparison with a stock OTP build
- **Pages the verifier opened:**
  - <https://github.com/sntran/BEAM.com>
  - <https://github.com/sntran/BEAM.com/commits>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/README.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/WORKERS.md>
- **Sources the enricher read:**
  - <https://github.com/sntran/BEAM.com>
  - <https://github.com/sntran/BEAM.com/commits>
  - <https://github.com/sntran/BEAM.com/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/README.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/WORKERS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/JIT.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/INTERNALS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/PLATFORMS.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/UPSTREAM.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/docs/SANDBOX.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/Makefile>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/tests/bench/bench.erl>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/tests/bench/run.sh>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/scripts/steps.sh>
  - <https://raw.githubusercontent.com/sntran/BEAM.com/HEAD/patches/otp/0002-jit.patch>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/sntran/beam.com`) · [data/wave12/enrich/raw/github_com_sntran_beam_com.json](../../../data/wave12/enrich/raw/github_com_sntran_beam_com.json) (enrichment confidence 0.8)

</details>
