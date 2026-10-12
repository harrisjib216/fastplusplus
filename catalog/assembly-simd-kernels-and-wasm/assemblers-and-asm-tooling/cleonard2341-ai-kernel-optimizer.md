# ai-kernel-optimizer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Python` · `MIT` · 🟢 active

> Python driver that prompts an AI for x86-64 asm and races it against GCC -O3; winning kernels unpublished.

| | |
|---|---|
| **Beats** | GCC -O3 compiled C reference kernels (scalar 256-byte-LUT base64 decode, LZ4 1.10.0 fast-path decode, Redis 7.x SipHash 1-2) |
| **Claimed result** | Base64 decode 4.80x (64 B, 50M iters: 1.81 s vs 0.38 s, 1,767 to 8,479 MB/s), 6.23x (1 KiB, 5M iters: 1,825 to 11,365 MB/s), 6.26x (16 KiB, 200K iters: 1,857 to 11,635 MB/s) over the GCC -O3 scalar LUT decoder; LZ4 fast-path decode three runs 1.07x, 0.98x, 1.02x (author: within noise); Redis SipHash 1-2 0.96x (8 B keys), 0.97x (32 B), 0.99x tie (128 B), i.e. GCC 3-4% faster on short keys. |
| **Workload** | Differential-fuzzed x86-64 assembly replacements, written by an AI model with optimize.py as scaffolding, for three extracted kernels: base64 decode (valid-input-only, no padding, length multiple of 4) timed at 64 B, 1 KiB and 16 KiB inputs; LZ4 1.10.0 fast-path decode loop on 4096-byte blocks (10M iterations); Redis 7.x SipHash 1-2 on 8-, 32- and 128-byte keys. Each benchmark is one back-to-back run (GCC then AI) of the same input with CLOCK_MONOTONIC. |
| **Metric** | throughput |
| **Compiler and flags** | Reference kernels: gcc -O3 -march=native (stated in case_studies/SUMMARY.md methodology, the blog post and optimize.py); AI .S assembled with gcc; generic harness built with gcc -O2. GCC version not stated. |
| **Adoption** | 2 stars, 3 commits |
| **Last commit** | 2026-05-17 |
| **Links** | [repository](https://github.com/cleonard2341/ai-kernel-optimizer) · [benchmark](https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/base64/REPORT.md) |

## Verdict

Self-reported and not reproducible from the repo: an AI-written SSSE3 base64 decoder ran 4.80x (64 B), 6.23x (1 KiB) and 6.26x (16 KiB) faster than a scalar 256-byte-LUT C decoder built with gcc -O3 -march=native (about 1.8 GB/s versus 8.5-11.6 GB/s). The CPU and GCC version are unnamed, and each figure is one back-to-back run. The LZ4 fast-path row is a tie at an implausible 2.5 ns per call, and the Redis SipHash 1-2 rewrite is 1-4% slower than GCC.

## Use it when

- As a starting scaffold for experiments with LLM-written x86-64 assembly on Linux and GCC: it extracts gcc -O3 -march=native disassembly and a SysV-ABI prompt for a pure C function.
- To triage a C file for side-effect-free candidate kernels (no I/O, allocation or globals) with scan's heuristic score before hand-optimizing.
- As a template for C-versus-.S differential testing, but only after rewriting the harness so it compares output buffers and feeds inputs that respect the kernel's contract.

## Skip it when

- As a source of fast base64, LZ4 or SipHash code: none of the benchmarked assembly is in the repo; use a maintained SIMD base64 library (the record names aklomp/base64 and simdutf) or upstream LZ4.
- As evidence that a kernel is correct: the published verify/compete harness never compares plain pointer outputs (see gotchas), so its '100K PASS' proves little for kernels that write into a buffer.
- For benchmarks you need to trust: the generated benchmark is one back-to-back run per version on a fixed input, with no warmup or repeats, and a 2% threshold decides the verdict.
- Off Linux x86-64 with GCC and GNU binutils (objcopy, objdump), or for kernels with more than six register arguments, struct-by-value parameters or code the regex parser misreads (it takes the first non-static function matching a simple pattern).

## How it is fast

The one real win, base64 decode, swaps a scalar 256-byte lookup-table decoder for the SSSE3 vector technique: pshufb on the high nibble picks a per-range offset (with a pcmpeqb fix-up for '/'), then pmaddubsw, pmaddwd and pshufb pack 16 ASCII bytes into 12 output bytes per iteration. This is the published Mula-Lemire style vector base64 approach (arXiv 1704.00605, seen as a search result), here without input validation or padding. The LZ4 attempt only widens the match copy to one 16-byte vmovdqu and merges pointer arithmetic into LEA (noise-level). The SipHash attempt reschedules SIPROUND and loses to GCC.

## Compared with alternatives

Pick it only as a small, readable Linux/GCC scaffold for trying LLM-written assembly on one function. STOKE (stochastic superoptimizer with verification), SuperCoder (LLM assembly superoptimization evaluated on a benchmark suite) and SLOTHY (scheduler for crypto and DSP kernels) are research tools with published evaluations, while this repo publishes neither its winning kernels nor a verifier that checks output buffers.

## Integration

| | |
|---|---|
| **Form** | source-drop (single Python script, optimize.py) |
| **Dependencies** | GCC, GNU binutils (objcopy, objdump), Python 3 standard library; an external AI model to write the .S |
| **Minimum toolchain** | Python 3.6+ and GCC with x86-64 support (README); Linux |
| **Platforms** | Linux x86-64 only (prompt assumes the SysV ABI and offers SSE through AVX2, BMI and BMI2) |
| **Thread safety** | not applicable (command-line tool); not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the published verifier: gen_harness classifies every non-const pointer parameter without a struct type (for example uint8_t \*dst or int \*src_consumed) as an input, fills it with random bytes, passes the same array to both versions and never compares it; only return values and struct-pointer outputs are checked. Generated here for the base64 signature b64_decode_kern(const uint8_t \*src, size_t src_len, uint8_t \*dst): the 100,000-iteration fuzz compares only the return value src_len\*3/4, so a decoder that writes wrong bytes passes. The case studies' '100K PASS' came from separate, unpublished harness.c files.
- The generated fuzz uses random bytes and random lengths 0-255 regardless of the kernel's contract (base64 needs valid characters and a length divisible by 4; LZ4's end pointers must point into the same buffer, but each pointer parameter gets its own unrelated array). The generated benchmark fixes every scalar at 42 and fills inputs with j\*7+13, then times GCC and AI once each, back to back.
- The LZ4 row cannot measure the stated workload: 10M iterations in 0.024-0.027 s is about 2.5 ns per call for a 4096-byte block, so the kernel probably returned after a few sequences. The report text is also unreliable in detail: SipHash 1-2 is described as having 2 finalization rounds and then the AI version as using 'all 3 finalization rounds', and a VEX vmovdqu is called an SSE copy.
- The analyze prompt tells the model 'no error checking, inputs valid', so AI kernels drop validation a production decoder needs. 'Provably outperforms GCC -O3' and 'generates optimized x86-64 assembly' overstate a tool that prints a prompt and runs fuzz tests. MIT appears only in the README; there is no LICENSE file and GitHub shows no license.

## Known shortcomings

- The assembly, harness.c, C reference and build_and_test.sh are not in the repo (404; the initial commit holds optimize.py plus three case-study reports), so nothing is rerunnable or copyable; base64 4.80-6.26x is against a naive scalar LUT decoder using the known SSSE3 pshufb technique with no input validation and no SIMD library compared; the LZ4 row (about 2.5 ns per 4 KiB block, derived) is impossible and a tie anyway; SipHash is 0.96-0.99x (GCC wins); CPU model and GCC version unstated, single run, no warmup; MIT in README only, no LICENSE file; 2 stars.
- Enricher: the published optimize.py verify harness (gen_harness) treats non-const non-struct pointer outputs such as uint8_t \*dst as inputs, passes the same array to both versions and never compares it (only return values and struct outputs are checked), so for the b64 signature the fuzz compares only src_len\*3/4 and wrong output bytes pass; the generated fuzz ignores kernel contracts (random lengths 0-255, unrelated end-pointer arrays); the bench fixes scalars at 42 and runs each version once back to back with no warm-up; the LZ4 row (2.5 ns per 4 KiB call) is implausible; the SipHash report contradicts itself (2 vs 3 finalisation rounds); no LICENSE file. Retiered to D.

## Caveats and trade-offs

All numbers are self-reported in case_studies/\*/REPORT.md, case_studies/SUMMARY.md and blog/ai-assembly-vs-gcc-o3.md. The reports list the C reference, the .S assembly, harness.c and build_and_test.sh, and the blog says each case study is 'a single ./build_and_test.sh away from reproducing', but none of those files are in the repo (raw.githubusercontent.com returns 404 for case_studies/base64/b64_decode_kern.c, harness.c, build_and_test.sh, lz4/harness.c, redis/harness.c; the initial commit was 'optimize.py + 3 case study reports'), so nothing can be rerun and the faster assembly itself cannot be copied: only the optimize.py driver (scanner, prompt generator, fuzz/bench harness generator) is published. CPU model and GCC version are not stated; optimize.py's generated benchmark is a single back-to-back run on one fixed input with no warmup or repeats. The baseline is a naive scalar 256-byte-LUT decoder of unstated origin; the AI kernel is the known SSSE3 pshufb nibble-lookup technique (Mula/Lemire style) without input validation (it assumes valid base64 and no padding), and existing SIMD base64 libraries (aklomp/base64, fastbase64, simdutf) were not compared. The LZ4 timings (0.024-0.027 s for 10M iterations, about 2.5 ns per call, derived from page data) are impossible for decoding a 4096-byte block, so the LZ4 row did not measure the stated workload and is not valid evidence; it is a tie anyway (runs 1.07x, 0.98x, 1.02x). SipHash is slower than GCC. The README's 'provably outperforms GCC -O3' is overstated: verification is 100K differential-fuzz iterations per kernel, and two of three kernels are a loss or a tie. MIT is stated only in the README; there is no LICENSE file or copyright notice and GitHub shows no license. No independent coverage found; the Hacker News thread could not be opened (egress blocked).

x86-64 only, SSSE3 for the base64 kernel (BMI2 rorx in the SipHash attempt). The base64 kernel assumes valid input, no padding characters and a length that is a multiple of 4, so it skips the error handling a production decoder needs. Base64 code is about twice the size of GCC's (293 vs 145 bytes). The tool only handles pure kernels with no I/O, allocation or global state; the full LZ4_decompress_safe (856 instructions) was too large, so only its fast path was replaced.

## Maintenance

Three commits (2026-02-15 initial release and blog post, 2026-05-17 FUNDING.yml), 2 stars, 0 forks, no releases. MIT is claimed only in the README, so reuse rights are unclear, and only the Python driver is copyable; none of the benchmarked kernels are published.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** case_studies/base64/REPORT.md (and SUMMARY.md, redis/REPORT.md, lz4/REPORT.md) give first-party timings against the GCC -O3 -march=native scalar C reference, but the case-study harness.c, C references, .S kernels and build_and_test.sh are not in the repo (raw 404, initial commit was 'optimize.py + 3 case study reports'), and CPU model, GCC version and repeat/warmup method are unstated. First-party numbers without reproducible code or hardware: C.
- **Retiered** C to D: Enricher (2026-10-12): the published verifier cannot check output buffers. gen_harness in optimize.py treats non-const pointer outputs as inputs, passes the same array to both versions and never compares it, so kernels that write wrong bytes still pass (for the Base64 signature only src_len\*3/4 input bytes are compared); the generated fuzz ignores kernel contracts and the bench runs each version once with fixed scalars and no warm-up; the LZ4 row (2.5 ns per 4 KiB call) is implausible. No valid measurement (MQF precedent).
- **Verifier notes:** Real but weak entry: base64 decode 4.8-6.3x over a naive scalar LUT decoder is internally consistent (MB/s match iterations x size / time, derived from page data), but the asm, harness and build script are not published, so the speedup is uncheckable and nothing fast is copyable; keep at C with the shortcomings above. LZ4 numbers are implausible (about 2.5 ns per 4 KiB block decode) and SipHash is a GCC win; MIT is README-only. Last commit 2026-05-17 (FUNDING.yml), 2 stars, 0 forks, 3 commits, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier batch-99 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/cleonard2341/ai-kernel-optimizer>
  - <https://github.com/cleonard2341/ai-kernel-optimizer/commits/main>
  - <https://github.com/cleonard2341/ai-kernel-optimizer/tree/main/blog>
  - <https://github.com/cleonard2341/ai-kernel-optimizer/tree/main/case_studies/base64>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/base64/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/lz4/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/redis/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/SUMMARY.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/optimize.py>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/blog/ai-assembly-vs-gcc-o3.md>
- **Sources the enricher read:**
  - <https://github.com/cleonard2341/ai-kernel-optimizer>
  - <https://github.com/cleonard2341/ai-kernel-optimizer/commits/main>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/README.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/optimize.py>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/SUMMARY.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/base64/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/lz4/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/redis/REPORT.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/blog/ai-assembly-vs-gcc-o3.md>
  - <https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/.github/FUNDING.yml>
  - https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/LICENSE (404)
  - https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/base64/b64_decode_kern.c (404)
  - https://raw.githubusercontent.com/cleonard2341/ai-kernel-optimizer/HEAD/case_studies/base64/harness.c (404)
  - WebSearch: no independent coverage found; result list included arXiv 1704.00605 (Faster Base64 Encoding and Decoding Using AVX2 Instructions), not opened
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/cleonard2341/ai-kernel-optimizer`) · [data/wave13/enrich/raw/github_com_cleonard2341_ai_kernel_optimizer.json](../../../data/wave13/enrich/raw/github_com_cleonard2341_ai_kernel_optimizer.json) (enrichment confidence 0.8)

</details>
