# Monty (pydantic/monty)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust Python-subset sandbox for LLM-written code; sub-millisecond sandbox checkout versus 16 ms to 2.7 s for WASI, Docker, Pyodide and hosted sandboxes.

| | |
|---|---|
| **Beats** | CPython-based sandboxes (WASI/wasmtime with precompiled CPython 3.14.7, local Docker python:3.14-alpine, Pyodide in Deno via mcp-run-python, a Daytona sandboxing service) and starlark-rust; the same page also times plain unsandboxed CPython (in-process eval/exec and a python -c subprocess). No CPython execution-throughput claim in the repo docs. |
| **Claimed result** | docs/index.md and docs/alternatives.md: OSS Monty new sandbox 0.80 ms (checkout from an already-open pool; 0.77 ms median of 20 after 1 s idle; 5 ms when the pool is created) vs WASI/wasmtime 16 ms, local Docker 195 ms, sandboxing service 1500 ms, Pyodide in Deno 2700 ms; 10-command agent run 0.40 ms vs 180 ms, 700 ms, 400 ms and 35 ms; combined 1.20 ms vs 200 ms, 900 ms, 1900 ms and 2700 ms. Plain unsandboxed CPython on the same page: eval about 0.1 ms and ten exec calls 0.3 ms (faster than Monty), python -c subprocess about 30 ms and ten replayed subprocesses about 180 ms. starlark-rust first parse+eval 1.3 ms. |
| **Workload** | scripts/startup_performance.py: time to get a fresh sandbox and run 1 + 1, and an agent run of 10 REPL commands (AGENT_BLOCKS) against an existing sandbox; sandboxes without a persistent interpreter replay commands 1..n for command n. |
| **Metric** | startup |
| **Hardware** | Apple M3 Max, 96 GB, macOS 26.5.2 (driven from CPython 3.14.7); Full Monty rows measured in linux/arm64 Docker containers on one machine |
| **Compiler and flags** | monty worker binary built with the workspace release profile (lto = "fat", codegen-units = 1, strip = true); rustc version not stated (rust-version 1.96 minimum) |
| **Adoption** | 8.6k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/pydantic/monty) · [benchmark](https://github.com/pydantic/monty/blob/main/docs/alternatives.md) |

## Verdict

Vendor run of scripts/startup_performance.py on an Apple M3 Max (macOS 26.5.2, driven from CPython 3.14.7): getting a sandbox from an open OSS Monty pool and running 1 + 1 took 0.77 ms (median of 20; 4.5 ms including pool creation) versus 16 ms for precompiled CPython 3.14.7 WASI in wasmtime 48, 195 ms for docker run python:3.14-alpine, about 1500 ms for a Daytona EU sandbox and 2700 ms for Pyodide in Deno via mcp-run-python (single samples); ten REPL commands took 0.40 ms versus 35-700 ms for those baselines replaying the commands. In-process CPython eval and exec were faster than Monty (0.1 ms and 0.3 ms), and no interpreter-speed comparison with CPython is published.

## Use it when

- Running short LLM-written Python (code mode, programmatic tool calling) per request, where 1 ms sandbox checkout matters more than full CPython compatibility.
- Agents that issue many small REPL commands against one session: 10 feeds took 0.40 ms in the vendor run, against 35-700 ms for the replaying Pyodide, WASI and Docker setups.
- Workflows that pause on a slow host call or a human approval and resume later or on another machine, using the kilobyte-sized snapshot (dump/load).
- Hosts that want enforced memory, per-feed duration, recursion and host-round-trip limits without operating containers; each worker is about 2 MB baseline plus its memory limit (vendor docs).

## Skip it when

- Code that needs real Python: no class inheritance, no generators (yield), no match, no del, no user-defined exceptions, no @property/@classmethod, no third-party packages, and a partial stdlib (no enum, io, struct, hashlib, logging and others).
- Trusted code where plain in-process CPython is acceptable: exec/eval takes about 0.1 ms and ten exec calls 0.3 ms on the vendor's own table, faster than Monty's 0.8 ms and 0.4 ms.
- CPU-heavy scripts: no throughput comparison with CPython is published (monty-bench's CPython runs stay local and off CodSpeed), and third-party coverage quotes 'between 5x faster and 5x slower' than CPython (search snippet only).
- Threat models that need OS-level isolation by default: it is a language-level sandbox with no seccomp, container or VM; a worker escape runs with the application's OS privileges on the application host (OS isolation is the commercial Full Monty).
- Anything relying on lazy iterators: enumerate, zip, map, filter and reversed are eager, so map(f, itertools.count()) runs until a limit trips.

## How it is fast

The speed claim is about startup, not throughput: a new sandbox is one protobuf message to an already-running worker process from a pool, so there is no container, VM or Wasm module to start and no CPython initialisation. The REPL session persists between feeds, so an agent's tenth command does not replay the first nine, which is what the stateless baselines must do. Release binaries use fat LTO with one codegen unit (Cargo.toml).

## Compared with alternatives

Pick Monty over pocketpy when the code is untrusted LLM output and you need resource limits, host-call suspension and snapshots from Python, JS or Rust rather than a Python subset embedded in a C++ app; for raw Python throughput PyPy, Cython or Codon are the catalogued choices, and LLRT is the analogous startup-latency play for JavaScript.

## Integration

| | |
|---|---|
| **Form** | Python package (pydantic-monty plus the pydantic-monty-runtime worker binary), npm package @pydantic/monty, and Rust crates (monty in-process, monty-pool for worker subprocesses) |
| **Dependencies** | Python package: pydantic-monty-client and pydantic-monty-runtime (prebuilt `monty` binary, 11-15 MB wheels). Rust: ruff_python_parser, ty crates for optional type checking, num-bigint, fancy-regex and others; no C dependencies inside the sandbox. |
| **Minimum toolchain** | Rust 1.96 (edition 2024) to build; Python 3.10+ for the Python package |
| **Platforms** | Prebuilt workers for macOS x86-64 and arm64, manylinux x86-64, aarch64, armv7l, i686, ppc64le and s390x, musllinux x86-64 and aarch64, Windows win32 and amd64 (pydantic-monty-runtime 1.1.0 on PyPI) |
| **Thread safety** | Each session runs in its own worker subprocess and a crash only kills that worker; a session takes one feed at a time, and cancelling MontyRepl.feed_run_async poisons the session (open issue #533). Thread safety of the in-process monty crate is not documented. |
| **Drop-in for the baseline** | partial — it runs a CPython 3.14 subset with documented divergences, behind a different API (pool, checkout, feed_run with external_lookup), not as a python executable or embeddable CPython |

## Gotchas

- Benchmark asymmetry: Monty's 0.77 ms is the median of 20 checkouts from a pool whose worker already exists, while the WASI, Docker, Daytona and Pyodide rows are single samples starting from nothing; Monty's 0.40 ms agent run is one back-to-back sample taken right after an identical warm-up run, although the docs state back-to-back checkouts are about 20x faster than after a 1 s idle (0.04 vs 0.77 ms). The pool-creation figure (4.5 ms, median of 7) comes from pydantic-monty 0.0.21 and the checkout figure from 1.0.0b3, so one table mixes versions.
- The agent-run baselines replay commands 1 to n because the chosen wrappers keep no state (python.wasm via _start, docker exec python -c, mcp-run-python's fresh-globals eval); a persistent CPython REPL inside the same container or Pyodide instance would avoid the replay, so the 35-700 ms figures measure those wrappers more than the runtimes (inference from scripts/startup_performance.py).
- max_memory and both duration limits are off unless set, and the Rust pool has no request timeout by default; max_recursion_depth and max_suspensions default to 1000 and cannot be disabled. Recent hardening issues include a stack-overflow abort (#649), a type-checker crash (#717) and a panic on container mutation from a guest __eq__ (#729), all closed, while #921 (functools.partial can kill a memory-limited worker) and #788 (truncating writes destroy mounted files while charging 0 bytes) are open.
- docs/alternatives.md says the package is about a 4.5 MB download, but the 1.1.0 pydantic-monty-runtime wheels on PyPI are 11.4-15.0 MB; third-party write-ups quoting 0.004 ms startup describe the earlier in-process design, before the subprocess pool raised a new sandbox to about 0.8 ms (search snippet).

## Known shortcomings

- Measures sandbox startup against Docker, WASI and Pyodide, not interpreter speed against CPython: plain in-process CPython exec is faster (0.1 ms vs 0.8 ms), Monty comes from a warm pool while rivals start cold, and Pydantic sells the hosted Full Monty product (vendor evidence). Script in docs/alternatives.md, M3 Max, release profile.
- Enricher: the Monty figure is the median of 20 checkouts from a pre-spawned pool while the baselines are single cold samples; the agent-run row is one hot back-to-back sample (docs give 0.04 ms back-to-back vs 0.77 ms after idle); pool-creation and checkout rows come from different versions (0.0.21 vs 1.0.0b3); replay baselines time the chosen stateless wrappers (mcp-run-python, docker exec), not the runtimes. No throughput numbers vs CPython. Docs say a 4.5 MB download while 1.1.0 runtime wheels are 11.4-15.0 MB; limits are off by default; open issues #921 and #788.

## Caveats and trade-offs

The claim is sandbox startup latency against container, Wasm and hosted sandboxes, not interpreter throughput against CPython, so it does not meet the category baselines; against plain in-process CPython (0.1 ms eval, 0.3 ms for ten exec calls) Monty is slower. Monty's number is a checkout from an already-created pool (median of 20) while the others start from nothing with a single sample, and Monty was re-measured on 2026-09-24 while most other rows date from 2026-09-03. Vendor documentation: Pydantic sells Full Monty. Monty implements a Python subset (no class inheritance, limited stdlib, no third-party packages). A monty-bench crate (Criterion) compares Monty with CPython but publishes no numbers in the repo; a search snippet of project material said runtime speed is generally between 5x faster and 5x slower than CPython (snippet only). pydantic.dev docs site blocked here; the same text is in docs/ in the repo.

Minimal Python sandbox interpreter written in Rust for AI-generated code: no filesystem, environment or network unless functions and mounts are passed in; not a drop-in CPython replacement. Python, JavaScript and Rust packages; a commercial server variant (Full Monty) exists.

## Maintenance

Very active (v1.1.0 released 2026-10-05, 823 commits, 8.6k stars, v1.0.0 declared production-ready in September 2026) and MIT licensed, but the evidence is vendor documentation from Pydantic, which sells the Full Monty server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor numbers (Pydantic sells the commercial Full Monty) from public code (scripts/startup_performance.py) on a named CPU (Apple M3 Max) with the release profile in Cargo.toml, but the rustc version is not stated and the comparison is sandbox startup latency, not interpreter speed against CPython; vendor rule keeps it at C.
- **Verifier notes:** Numbers match docs/index.md; docs/alternatives.md carries the methodology (script path, M3 Max, CPython 3.14.7, sample counts), so it is the better benchmark_url. Shortcomings to record: startup-latency comparison against sandboxes rather than CPython speed, slower than in-process CPython exec, pooled-vs-cold asymmetry, vendor evidence, Python subset.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `hardware`, `compiler_and_flags`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** independent cold-start comparison including in-process CPython; cold-vs-cold comparison on one version
- **Pages the verifier opened:**
  - <https://github.com/pydantic/monty>
  - <https://github.com/pydantic/monty/commits>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/README.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/alternatives.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/limitations/index.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/scripts/startup_performance.py>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/crates/monty-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/pydantic/monty>
  - <https://github.com/pydantic/monty/commits/main>
  - <https://github.com/pydantic/monty/issues?q=is%3Aissue+sandbox+escape+OR+security+OR+performance+OR+slow>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/README.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/alternatives.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/limitations/index.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/quickstart/rust.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/security.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/resource-limits.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/docs/snapshots.md>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/scripts/startup_performance.py>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/crates/monty-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/crates/monty-bench/benches/main.rs>
  - <https://raw.githubusercontent.com/pydantic/monty/HEAD/LICENSE>
  - <https://pypi.org/pypi/pydantic-monty/json>
  - <https://pypi.org/pypi/pydantic-monty-runtime/json>
  - <https://crates.io/api/v1/crates/monty>
  - WebSearch: pydantic monty interpreter benchmark vs CPython speed faster slower (snippets from pydantic.dev/articles/pydantic-monty and victorstack-ai.github.io; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pydantic/monty`) · [data/wave12/enrich/raw/github_com_pydantic_monty.json](../../../data/wave12/enrich/raw/github_com_pydantic_monty.json) (enrichment confidence 0.6)

</details>
