# RGC (Recursive Group Coding)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Tiny MIT C entropy coder (Recursive Group Coding) that compresses large-alphabet data better than static AC, claiming about 2x its speed.

| | |
|---|---|
| **Beats** | static 8-bit arithmetic coder (AC); TurboRC rcc2senc() range coder also listed |
| **Claimed result** | README: 'running about twice as fast as the simplest static 8-bit AC' and 'about twice as fast as a range coder' with moderate optimization. Table on tst.dat (1 MB): RGC 224,071 bytes in 0.01 s versus TurboRC rcc2senc() 237,380 bytes in 0.03 s (3x, derived from page data, at 0.01 s timer resolution); AC 8-bit 261,695 bytes with no time given. The 2009 paper (paper/recursive_group_coding_2009.pdf, Table 1, Calgary corpus average) reports 17.89 ms encode and 17.72 ms decode for RCGS versus 36.80 ms and 38.05 ms for a static assembler AC (about 2.1x, derived from page data), on a Delphi implementation. |
| **Workload** | Entropy coding of tst.dat, 1 MB of quantized DCT coefficients from 32x32 image blocks (rgc_demo.c); the headline result is compression ratio on large alphabets. |
| **Metric** | throughput |
| **Compiler and flags** | MSVC 'cl /O2 /MD rgc_demo.c' shown as the build example, not stated as the benchmark build |
| **Adoption** | 2 stars; also on PyPI as rgclib |
| **Last commit** | 2026-03-20 |
| **Links** | [repository](https://github.com/mykola-ponomarenko-ua/rgc) · [benchmark](https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/README.md) |

## Verdict

The repo times one 1 MB file of quantized 32x32 DCT coefficients: RGC 0.01 s and 224,071 bytes versus TurboRC rcc2senc() 0.03 s and 237,380 bytes, with no CPU, compiler flags, repeat count or AC timing. The 2009 paper's Calgary average (17.89 ms encode and 17.72 ms decode versus 36.80 and 38.05 ms, about 2.1x, derived from page data) measured a Delphi implementation against an unnamed assembler static AC on unstated hardware, not this C code.

## Use it when

- Final stage of a pipeline on large-alphabet or block-structured data with residual neighbour correlation, such as quantized DCT coefficients (the repo's 1 MB tst.dat: 224,071 bytes versus 237,380 for TurboRC rcc2senc() and 261,695 for 8-bit AC).
- BWT plus distance-coding pipelines; the README reports about 20% smaller output than BWT + DC + AC on traffic time stamps (no data shipped for that case).
- When you want a two-file, dependency-free, MIT-licensed coder you can read in one sitting (rgc.c is about 500 lines) and a Python binding from PyPI.
- Statistically homogeneous blocks of tens of kilobytes or more, where the group symbol lists per recursion level are small relative to the payload.

## Skip it when

- Untrusted compressed input: rgc_decode() reads offsets, a group count (one byte, up to 255) and length fields straight from the stream without bounds checks, while group_sizes and group_symbols hold only 16 groups, so a crafted stream can overflow stack buffers and read outside the input.
- Throughput-critical coding where rANS, FSE or Huff0 are options: the only timing of this C code is 0.01 s for 1 MB at timer resolution, and the paper's 2x speed claim is against a 2009 hand-written assembler AC, not against modern interleaved rANS or table Huffman.
- Random or near-uniform 8-bit data, where the README says it loses to AC by about 1-2%, and files of only a few kilobytes, where group lists dominate.
- Adaptive or streaming use: the model is static over the whole buffer, the API is one-shot in-memory, and there is no block or streaming interface.
- Very large buffers: sizes are int32_t, encode allocates about 20x the input (a 9x compressed scratch buffer, a 9x one-byte-per-bit suffix buffer, plus prefix and working copies), and the int32 suffix bit counter can overflow above roughly 268 MB of high-entropy input (inferred from the code).

## How it is fast

It follows Ryabko-style grouping (the 2009 paper calls it RCGS): symbols sorted by frequency are split into at most 16 power-of-two groups of near-equal probability, each symbol becomes a 4-bit group id plus a raw, uncoded suffix index of 0-8 bits. Neighbouring group ids are packed in pairs into a new byte stream half as long, and the procedure recurses until fewer than 200 bytes remain, which are stored raw. Per symbol the coder does only table lookups, a shift and an OR, with no multiplications or renormalisation; the recursion also picks up pair and longer-run statistics, which is why it can beat order-0 entropy on correlated data.

## Compared with alternatives

Pick RGC over TurboRC, FSE/Huff0 or rANS coders such as ryg_rans or hypersonic-rANS when compressed size on large-alphabet, block-structured data matters more than raw throughput and you want the smallest, simplest MIT code. Those siblings publish far higher measured throughput and harden their decoders better, so they win on speed and on untrusted input.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library and libm for log()); Python wrapper needs CPython 3.9+ |
| **Minimum toolchain** | C99 compiler (uses stdint.h); README builds with MSVC 'cl /O2 /MD' |
| **Platforms** | any (portable scalar C, no SIMD); PyPI metadata lists Windows, macOS and Linux |
| **Thread safety** | Not documented; the code has no global state and allocates per call, so concurrent calls on separate buffers look safe. The Python extension does not release the GIL. |
| **Drop-in for the baseline** | no |

## Gotchas

- Speed claims are in prose; examples/rgc_demo.c only round-trips tst.dat and prints the size, with no timing or TurboRC code, so the 0.01 s versus 0.03 s figures cannot be reproduced from the repo.
- Encoding computes log2 in double precision for each candidate group to decide group sizes (threshold 1.02), so the model build, not only the per-symbol path, costs time; the per-symbol path is the multiplication-free part.
- Compression gains on tst.dat partly come from the recursion exploiting position and neighbour structure (1024-byte DCT blocks), so the comparison with an order-0 8-bit AC is not like-for-like.
- Version 0.1.2, first public release in March 2026 and marked Development Status 3 - Alpha on PyPI; tests are one test_basic.py.

## Known shortcomings

- Tier C: rgc_demo.c has no timing code and no TurboRC comparison; the only speed figure is the 2009 paper's Table 1 (about 2.1x over an assembler arithmetic coder, Delphi era).
- rgc_decode has no bounds checks: it reads a one-byte group count (up to 255) from the stream into group_sizes[16] and group_symbols[16][256], so a crafted stream overflows the stack (security bug). Encode uses about 20x input memory. The int32 suffix bit counter can overflow above about 268 MB (inferred from code). The 0.01 s per MB timing is not reproducible from the repo. The paper's 2x is a Delphi build against a 2009 assembler arithmetic coder. On tst.dat part of the size gain comes from positional structure, so not like-for-like with order-0 AC.

## Caveats and trade-offs

The speed claim is mostly prose; the only timing table is a single 1 MB file with no CPU, no repeat count and no AC time, and the repo's rgc_demo.c contains no timing or TurboRC code, so the 0.01 s versus 0.03 s figures cannot be reproduced from the repo. Most of the table is compression ratio, not speed. The 2009 peer-reviewed paper (Telecommunications and Radio Engineering 68(20)) measured a Delphi implementation against an unnamed hand-written assembler AC with unstated hardware, not this C code. Author-run, so C.

Two-file C library (rgc.c, rgc.h) plus Python wrapper. Needs statistically homogeneous data; loses to AC by about 1-2% on random 8-bit data and is unsuited to files of a few kilobytes because group symbol lists dominate. Targets large alphabets (up to 1024-byte symbols).

## Maintenance

Active as of March 2026 (v0.1.2, 12 commits, 2 stars) and MIT-licensed, so copyable, but young and unhardened; vendor it only for trusted data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table times one 1 MB file (RGC 0.01 s versus TurboRC rcc2senc() 0.03 s) with no CPU, no repeat count and no timing code; examples/rgc_demo.c only encodes, decodes and checks the round trip, it does not time anything or run TurboRC. The 2009 peer-reviewed paper (checked into the repo) shows about 2x faster encode and decode than a static arithmetic coder, but for a Delphi implementation against an unnamed in-house assembler AC, not this C library, so it does not lift the entry to B.
- **Verifier notes:** README numbers match the record. I opened the checked-in 2009 paper and added its Table 1 timings to claimed_speedup; it supports the 2x-versus-AC prose but not for this implementation. Metadata confirmed: MIT (also rgclib 0.1.2 on PyPI, MIT), 2 stars, last commit 2026-03-20, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; first-party claim
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/README.md>
  - <https://github.com/mykola-ponomarenko-ua/rgc>
  - <https://github.com/mykola-ponomarenko-ua/rgc/commits>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/examples/rgc_demo.c>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/main/paper/recursive_group_coding_2009.pdf>
  - <https://pypi.org/pypi/rgclib/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/README.md>
  - <https://github.com/mykola-ponomarenko-ua/rgc>
  - <https://github.com/mykola-ponomarenko-ua/rgc/tree/main/tests>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/src/rgc/rgc.h>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/src/rgc/rgc.c>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/src/rgc/__init__.py>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/src/rgc/_rgcmodule.c>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/examples/rgc_demo.c>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/examples/prep.py>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/setup.py>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/mykola-ponomarenko-ua/rgc/main/paper/recursive_group_coding_2009.pdf>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/mykola-ponomarenko-ua/rgc`) · [data/wave9/enrich/raw/github_com_mykola_ponomarenko_ua_rgc.json](../../../data/wave9/enrich/raw/github_com_mykola_ponomarenko_ua_rgc.json) (enrichment confidence 0.75)

</details>
