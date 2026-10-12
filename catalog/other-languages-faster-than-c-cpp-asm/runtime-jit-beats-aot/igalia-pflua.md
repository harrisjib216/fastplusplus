# pflua (pflang packet-filter compiler on LuaJIT) vs libpcap BPF interpreter and Linux kernel BPF JITs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Lua` · `Apache-2.0` · 🔴 abandoned

> LuaJIT library that compiles tcpdump (pflang) filter expressions to Lua; 1.3-7.1x libpcap's BPF interpreter in its authors' benchmarks.

| | |
|---|---|
| **Beats** | libpcap's user-space BPF interpreter (pcap_offline_filter in the Debian system libpcap, version and build flags not stated) running bytecode from pcap_compile with libpcap's optimizer on; also the 2011 Linux kernel BPF JIT and the 2014 Linux eBPF JIT (C, built with gcc -O3 as user-space shared objects in pflua-bench), whose filters run as JIT-emitted machine code |
| **Claimed result** | pflua-bench README conclusion: 'In many circumstances, pflua is the fastest pflang implementation out there, by a long shot.' (the pflua README says 'by a wide margin'). Medians of the 20 runs in results/ping-flood (derived from page data), MPPS pflua vs libpcap vs linux-bpf vs linux-ebpf: 'tcp' 89.9 vs 37.9 vs 62.2 vs 56.1; 'tcp port 5555' 89.9 vs 37.9 vs 61.8 vs 57.6; 'icmp' 89.9 vs 54.8 vs 83.5 vs 77.7; 'ip' 91.6 vs 68.0 vs 85.3 vs 78.7; 'accept all' 127.9 vs 92.1 vs 109.8 vs 95.4. About 2.4x libpcap and 1.45x the 2011 Linux BPF JIT on 'tcp'. The bpf-lua engine (libpcap's BPF translated to Lua) gets 88.4 MPPS on 'tcp', within 2% of pflua. |
| **Workload** | Run pflang (tcpdump filter language) expressions 'accept all', 'ip', 'tcp', 'tcp port 5555' and 'icmp' over a 60-64 MB capture of 961,180 ICMP ping packets ('tcp' and 'tcp port 5555' match none of them), in millions of packets per second (MPPS). One discarded warm-up set, then 20 sets per engine in one process (bench.mk ITERATIONS?=20; the README says 50); each measurement loops over all packets for at least 0.1 s and checks the expected match count. Results committed 2015-02-03. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3770 (x86-64), Debian GNU/Linux (3.14-2), otherwise unloaded machine (pflua-bench README) |
| **Compiler and flags** | pflua and bpf-lua: LuaJIT from the pflua submodule built with its default make. linux-bpf-jit and linux-ebpf-jit: gcc -g -Wall -fPIC -O3 (their Makefiles; gcc version not stated). libpcap: Debian system library loaded with ffi.load("pcap"), version and build flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Source (pflua README, Performance section): LuaJIT trace compilation emits machine code specialised to the traffic actually seen; pflua can hoist and eliminate bounds checks while BPF must check every packet access; it works in network byte order while BPF converts to host order; it uses LuaJIT's register allocator and optimizer whereas the Linux kernel JIT has a limited optimizer. |
| **Adoption** | 312 stars (pflua); 26 stars (pflua-bench); written for the Snabb user-space networking toolkit |
| **Last commit** | 2017-01-30 |
| **Links** | [repository](https://github.com/Igalia/pflua) · [benchmark](https://github.com/Igalia/pflua-bench/tree/master/results/ping-flood) |

## Verdict

pflua-bench's ping-flood test (961,180 ICMP packets, i7-3770, Debian, one warm-up, then 20 runs in one LuaJIT process, results committed 2015-02-03) gave a median of 89.9 MPPS for pflua on 'tcp', against 37.9 for Debian's system libpcap interpreter (optimizer on, version unstated), 62.2 for the 2011 Linux BPF JIT and 56.1 for the 2014 eBPF JIT (both built with gcc -O3 as user-space .so files). Every baseline was called per packet through LuaJIT's FFI, while pflua's Lua predicate was inlined.

## Use it when

- Filtering packets with tcpdump-syntax expressions inside a LuaJIT data plane such as Snabb, where the predicate inlines into your own packet loop.
- Replacing libpcap's user-space BPF interpreter in a LuaJIT program: across the 18 filter rows of the four pflua-bench captures, pflua's median was 1.30x (wingolog-2 'net 178.79.150.0/24') to 7.1x ('portrange 0-5') libpcap's.
- Homogeneous high-rate traffic that keeps one hot trace: on the ping-flood capture, 'tcp' ran at 89.9 MPPS against 37.9 for libpcap and 62.2 for the 2011 Linux BPF JIT.
- As a worked example of compiling a filter DSL to Lua source (parse, optimize, ANF, SSA, residualize) and letting a tracing JIT specialise it.

## Skip it when

- C or C++ programs. There is no C API, so you would have to embed LuaJIT, and against JIT-compiled BPF pflua lost 5 of 18 rows: on the 1 GB capture, 'tcp port 5555' 23.6 vs 25.2 MPPS and 'portrange 0-6000' 22.0 vs 24.2 against linux-bpf; on wingolog-2, 'portrange 0-6000', 'host 178.79.150.233' and 'net 178.79.150.0/24'.
- Mixed real-world traffic where filters match. The pflua-bench README attributes the wingolog-2 losses to LuaJIT trace state-transfer costs, and there bpf-lua also beat pflua on 'portrange 0-6000' (56.9 vs 47.5 MPPS).
- When you need exact libpcap semantics. Open issues cover port/portrange edge cases (#243), negative numbers (#82), keyword elision (#157), IPv6 extension headers (#239), an internal error on 'ip dst 10' (#254) and encapsulations other than Ethernet (#21). The README itself warns of bugs and differences against libpcap.
- When you need a maintained upstream: the last commit was 2017-01-30, there is no API documentation beyond pf.lua, and later fixes live only in Snabb's lib/pflua copy.
- Workloads that need stable timing: issue #66 reports about 2x run-to-run variance (2014, garbage collection suspected) and is still open.

## How it is fast

The pure-Lua pipeline parses the expression, lowers it to a primitive AST, and optimizes it: constant and test folding, range inference on packet offsets, and hoisting of assertions. It then converts to A-normal form with common-subexpression elimination, then to SSA for control-flow optimization, and emits Lua source. The emitted code does one hoisted length check (e.g. 'if length &lt; 34 then return false end'), where the BPF translation checks bounds before each load. It compares 16-bit fields in network byte order through ffi.cast loads. LuaJIT's tracing JIT then compiles only the branches the traffic actually takes. bpf-lua, which runs libpcap's own bytecode through the same LuaJIT path, landed within 2% of pflua on ping-flood, so most of the gain comes from LuaJIT trace compilation and inlining rather than from pflua's optimizer.

## Compared with alternatives

Pick pflua when the job is runtime-compiled packet filters inside LuaJIT; ClangJIT and Proteus cover runtime specialisation of C++/CUDA/HIP code, and lua-resty-core and the LuaJIT FFI call-loop entries show cheap C calls from LuaJIT rather than a filter compiler. No sibling is a pflang implementation.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | LuaJIT with FFI (bundled as the deps/luajit submodule from SnabbCo/luajit, installed as luajit-2.0.3); DynASM (luapower/dynasm, deps/dynasm) for the native=true backend; the system libpcap, loaded through ffi.load("pcap"), only for the libpcap and bpf pipelines |
| **Minimum toolchain** | LuaJIT 2.0 with FFI (the Makefile builds the bundled copy); gcc to build the DynASM helper library |
| **Platforms** | x86-64 Linux is the only platform benchmarked (Debian, i7-3770); the native backend uses DynASM's x86 encoder; other architectures not documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — it takes the same filter strings as pcap_compile, but returns a LuaJIT function rather than a bpf_program, so only LuaJIT code can call it |

## Gotchas

- Harness flaw against the main baseline: bench.lua calls libpcap (and the Linux JITs) through an FFI call per packet, after writing a pcap_pkthdr, while pflua's predicate inlines into the LuaJIT trace of the timing loop. The project's own native C driver (test-native/pf_test_native.c, gcc -O3, committed 2014-08-27) measured libpcap on the same ping-flood capture at 73.9 MPPS for 'icmp' and 110.6 MPPS for accept-all. The bench.lua CSVs of 2015-02-03 have 54.8 and 92.1. That is a cross-run comparison from different dates and harness versions, but against the native figure pflua's 'icmp' lead (89.9 MPPS) shrinks from 1.64x to 1.22x (derived from page data). Its README still says the two drivers give 'similar' results.
- On ping-flood, pflua's four real filters ('ip', 'tcp', 'tcp port 5555', 'icmp') all land at 89.9-91.6 MPPS, and bpf-lua's at 88.2-90.5. The accept-all loop, which never reads packet bytes, runs at 127.9. Throughput does not move with filter complexity, so this workload mostly measures a shared per-packet cost plus call overhead, not filter code quality, and it cannot separate pflua's optimizer from bpf-lua.
- The pflua-bench README prose ('180 MPPS', 'all results are faster than the accept all loop', 50 runs) does not match the committed CSVs: accept-all is the fastest column for every engine, and bench.mk sets ITERATIONS?=20. The pflua-native engine is listed in bench.mk, but no pflua-native CSV is committed for any scenario.
- Snabb's vendored copy fixed a native-codegen bug ('fix typo bug in native codegen (xor/or emission)', 2020-02-07) and made register allocation architecture-independent; the upstream Igalia repo has neither fix, so use the Snabb copy if you need native=true.

## Known shortcomings

- First-party 2015 data (20 runs, not 50) with the libpcap build and gcc version unstated; the harness favours pflua (its filter is inlined into the LuaJIT loop while libpcap and the Linux JITs pay an FFI call per packet), and after subtracting the accept-all time the icmp lead over the Linux JITs disappears; bpf-lua ties pflua, so the win is the LuaJIT trace, not pflua's optimizer; libpcap's optimizer was on.
- Harness flaw: the project's own native C driver (test-native/pf_test_native.c, gcc -O3, 2014-08-27) measured libpcap 'icmp' at 73.9 MPPS and accept-all at 110.6, against 54.8 and 92.1 in the bench.lua CSV, so pflua's icmp lead shrinks from 1.64x to 1.22x (cross-run) although the README calls the two drivers similar. Filters plateau at 89.9-91.6 MPPS whatever the filter and bpf-lua ties; pflua loses to the Linux BPF JIT in 5 of 18 rows (1 GB capture, wingolog-2) and beats libpcap 1.30-7.1x in all 18. Snabb's lib/pflua holds later fixes (native codegen xor/or bug, 2020).

## Caveats and trade-offs

First-party benchmark by the pflua authors; libpcap version and flags and the gcc version are not stated, so tier C. The comparison is LuaJIT-compiled code against a C interpreter (libpcap) and two other runtime JITs (Linux BPF/eBPF), not against AOT-compiled C doing the same work, so it is a weak fit for runtime-jit-beats-aot. Harness asymmetry: pflua and bpf-lua predicates are Lua functions inlined into the LuaJIT trace of the timing loop, while libpcap (pcap_offline_filter, plus a pcap_pkthdr written per packet) and the Linux JITs (run_filter in a .so) are called through the FFI per packet; the 'accept all' row, which does no filtering, already differs (127.9 vs 92.1 vs 109.8 vs 95.4 MPPS). Subtracting the 'accept all' time per packet (derived from page data), the 'tcp' filter costs about 3.3 ns in pflua vs 15.5 ns in libpcap and 7.0 ns in linux-bpf, but the 'icmp' filter costs 3.3 ns in pflua vs 2.9 ns (linux-bpf) and 2.4 ns (linux-ebpf), so pflua's 'icmp' lead over the Linux JITs is call overhead. libpcap runs with its optimizer on (pf/libpcap.lua passes optimize=true), so it is not an unoptimised interpreter. The workload is homogeneous and 'tcp' filters match no packet, which suits a tracing JIT; on the real-world wingolog.org-2 capture pflua is sometimes slower than libpcap and the Linux JITs (README blames LuaJIT trace state-transfer costs). The README prose (about 180 MPPS, 'all results are faster than the accept all loop') does not match the committed CSVs, where 'accept all' is the fastest row for every engine. Results date from 2015-02-03; last commits 2017-01-30 (pflua) and 2016-12-05 (pflua-bench). [retier] The project's own native C driver (test-native/pf_test_native.c, gcc -O3) measured libpcap 'icmp' at 73.9 MPPS and accept-all at 110.6 against 54.8 and 92.1 in the bench.lua CSV, so pflua's icmp lead shrinks from 1.64x to 1.22x (cross-run). Filters plateau at 89.9-91.6 MPPS whatever the filter and bpf-lua ties; pflua loses to the Linux BPF JIT in 5 of 18 rows and beats libpcap 1.30-7.1x in all 18. Snabb's lib/pflua holds later fixes (native codegen xor/or bug, 2020).

Needs LuaJIT; filters are compiled at run time and the speed depends on LuaJIT trace behaviour; pflua is a filter engine only, not a full libpcap replacement, and the project says there may be bugs or differences against libpcap.

## Maintenance

Abandoned upstream since 2017-01-30 (Apache-2.0, 312 stars), with a maintained copy in Snabb's lib/pflua (fixes to 2020). Copyable for LuaJIT users, but the headline margin over libpcap is inflated by the per-packet FFI harness: the project's own C driver measured libpcap 'icmp' at 73.9 MPPS against 54.8 through bench.lua.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Igalia benchmark with public driver code (pflua-bench bench.lua, bench.mk, results/ping-flood/\*.csv) and a stated CPU (i7-3770); the Linux BPF/eBPF JIT shared objects are built with gcc -O3 per their Makefiles, but the main libpcap baseline is the Debian system libpcap with version and build flags unstated and no gcc version is given, so it falls short of A.
- **Verifier notes:** Numbers re-derived from the five ping-flood CSVs and match the record (20 runs, not 50). Main shortcomings: first-party, libpcap build unstated, per-packet FFI call overhead favours pflua (its icmp lead over the Linux JITs disappears after subtracting the accept-all loop), win is LuaJIT trace compilation not pflua's optimizer (bpf-lua ties it), weak category fit (JIT vs interpreter and other JITs), 2015 data.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Igalia/pflua>
  - <https://github.com/Igalia/pflua/commits/master>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/README.md>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf/libpcap.lua>
  - <https://github.com/Igalia/pflua-bench>
  - <https://github.com/Igalia/pflua-bench/commits/master>
  - <https://github.com/Igalia/pflua-bench/tree/master/results/ping-flood>
  - <https://github.com/Igalia/pflua-bench/commits/master/results/ping-flood>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/bench.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/bench.mk>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/linux-bpf-jit/Makefile>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/linux-ebpf-jit/Makefile>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/pflua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/bpf-lua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/libpcap.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/linux-bpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/linux-ebpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/filters>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/Makefile>
- **Sources the enricher read:**
  - <https://github.com/Igalia/pflua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/README.md>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf/libpcap.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf/utils.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf/savefile.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/src/pf/backend.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Igalia/pflua/HEAD/doc/portrange-0-6000.md>
  - <https://github.com/Igalia/pflua/issues>
  - <https://github.com/Igalia/pflua/issues/66>
  - <https://github.com/Igalia/pflua-bench>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/bench.lua>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/bench.mk>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/Makefile>
  - <https://github.com/Igalia/pflua-bench/tree/master/test-native>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/test-native/README.md>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/test-native/pf_test_native.c>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/test-native/Makefile>
  - <https://github.com/Igalia/pflua-bench/commits/master/test-native>
  - <https://github.com/Igalia/pflua-bench/commits/master/results/ping-flood>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/filters>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/pflua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/bpf-lua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/libpcap.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/linux-bpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/ping-flood/linux-ebpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/filters>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/pflua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/bpf-lua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/libpcap.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/linux-bpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/1gb-1kb-tcp-port-5555/linux-ebpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/filters>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/pflua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/bpf-lua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/libpcap.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/linux-bpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-1/linux-ebpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/filters>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/pflua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/bpf-lua.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/libpcap.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/linux-bpf.csv>
  - <https://raw.githubusercontent.com/Igalia/pflua-bench/HEAD/results/wingolog.org-2/linux-ebpf.csv>
  - <https://github.com/snabbco/snabb/tree/master/lib>
  - <https://github.com/snabbco/snabb/commits/master/lib/pflua>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/igalia/pflua`) · [data/wave14/enrich/raw/github_com_igalia_pflua.json](../../../data/wave14/enrich/raw/github_com_igalia_pflua.json) (enrichment confidence 0.65)

</details>
