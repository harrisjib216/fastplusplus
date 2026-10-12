# SuperFast Codecs (fre:ac multi-threaded codec drivers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0` · 🔴 abandoned

> fre:ac encoder drivers that run several Opus/AAC/MP3/Speex encoder instances on overlapping chunks to use multiple cores for one output file.

| | |
|---|---|
| **Beats** | fre:ac's regular single-threaded codec drivers: libopus (Opus), FAAC and Core Audio AAC in the initial release; FDK-AAC, LAME and Speex drivers added later |
| **Claimed result** | Text: 'Using four threads, the conversion is already three times faster than with the regular drivers, which use only a single thread in this mode' (single file mode); in multi file mode the SuperFast drivers are 'only slightly faster'. Chart readings (approximate, unit-less y axis, derived from page data): single file mode, regular drivers about 24 (FAAC) and 29 (Opus) at every thread setting; SuperFast about 8.2 / 9.0 at 4 threads (about 2.9x / 3.2x) and 5.3 / 6.1 at 8 threads (about 4.5x / 4.8x); SuperFast at 1 thread is about 4% faster from decode/encode thread separation. Multi file mode gains are about 1-10%. Only FAAC and Opus are charted; Core Audio, FDK-AAC, LAME and Speex have no published numbers. |
| **Workload** | Converting one input file to one output file (single file mode) or several files in parallel (multi file mode) in fre:ac with 1, 4 or 8 threads, FAAC and Opus only. Each worker runs its own codec instance on overlapping blocks: the 2017 PDF describes 128-frame blocks with 8-frame overlap, while the archived repo's Opus driver uses 256-frame blocks with an overlap of at least 24 frames, and the LAME driver uses 128-frame blocks with 4x1152/frameSize overlap plus a frame repacker. Default thread count is cores + (logical CPUs - cores)/2. |
| **Metric** | throughput |
| **Hardware** | Not stated (the text mentions a 6 core CPU) |
| **Adoption** | 65 stars; code merged into mainline fre:ac (BoCA) |
| **Last commit** | 2020-12-10 |
| **Links** | [repository](https://github.com/enzo1982/superfast) · [benchmark](https://raw.githubusercontent.com/enzo1982/superfast/master/doc/SuperFast%20Codecs.pdf) |

## Verdict

In the author's own PDF, fre:ac converts one file in single-file mode about 3x faster with four SuperFast threads than with the regular single-threaded FAAC and Opus drivers (chart readings about 2.9-3.2x at 4 threads and 4.5-4.8x at 8). In multi-file mode the gain is only about 1-10%. Charts have no units, the only machine detail is 'a 6 core CPU', and no compiler, OS, codec version or script is given; LAME, FDK-AAC, Core Audio and Speex have no published numbers here.

## Use it when

- Encoding one long input (an album joined into one file, an audiobook, a long recording) to Opus or AAC on a 4-16 thread desktop, where stock fre:ac drivers use a single core.
- Batch jobs with fewer output files than cores; mainline fre:ac only engages SuperFast when the number of output files is at most half the logical CPUs.
- 48 kHz input to Opus (or input already at the MP3 output rate for LAME), the paths where the chunking runs in parallel without a serial resampler in front.
- As a design template for parallelizing any codec with constant frame sizes and interceptable packets; use the BoCA mainline source, not this archived copy.

## Skip it when

- You need output bit-identical to a single-threaded encode, or a quality guarantee: seams differ, and the only quality evidence is the author's difference-signal plots, with no listening test or objective metric.
- Many files at once: multi-file mode gains only about 1-10% because per-file parallelism already fills the cores.
- Non-48 kHz Opus input or LAME with resampling: the Opus resampler stays single-threaded, and the LAME driver disables SuperFast when the input rate differs from the MP3 output rate.
- Vorbis, FLAC or WMA: the author says block-size switching or closed packet APIs make the method unworkable for them.
- Code from this archived repo as is: it predates fixes shipped in fre:ac 1.1.1/1.1.2 (a SuperFast crash and several CBR MP3 issues) and has the short-input and mono-MP3 bugs listed under gotchas.

## How it is fast

High-level data parallelism over encoder instances, the 'split into fragments' approach that LAME MT abandoned because it cannot be bit-identical. Opus blocks are 256 frames with an overlap of max(24, ceil(24\*960/frameSize)) frames, FAAC 128 frames with 8, and LAME 128 frames with 4\*1152/frameSize; the overlap frames re-adapt encoder state and their packets are discarded. Worker encoders are not reset between blocks (Opus and FAAC reuse one handle per worker; LAME flushes with lame_encode_flush_nogap after each block), so each block starts from stale state left by that worker's previous block. For MP3 a serial repacker unpacks frames, rebuilds the bit reservoir across seams and makes the worker re-encode, after feeding dummy frames to fill the reservoir, when a frame does not fit. Even at one thread, decoding and encoding run on separate threads, which the PDF credits for a small gain.

## Compared with alternatives

Pick it, through BoCA mainline, when you need multi-core encoding of one stream with the stock libopus, FAAC/FDK-AAC or LAME. SuperLAME is a standalone CLI that ports this LAME driver and repacker and publishes numbers with a named CPU (Ryzen 7 5800X3D), so it is the better-documented choice for MP3 alone. The faster single-threaded codecs (opus-pure, libopus-rs, ruopus) speed up each instance and could be combined with this chunking.

## Integration

| | |
|---|---|
| **Form** | shared lib (BoCA encoder components loaded by fre:ac) |
| **Dependencies** | smooth class library, BoCA component framework, plus the codec libraries loaded at run time (libopus/libogg, FAAC/mp4v2, FDK-AAC, LAME, Speex, Core Audio on Windows/macOS) |
| **Minimum toolchain** | not documented (GNU make with BoCA's Makefile-commands; C++ with the smooth framework) |
| **Platforms** | Windows, macOS, Linux and FreeBSD builds were published (x86-64 and i686; macOS universal binary includes PPC) |
| **Thread safety** | One encoder object per conversion with its own worker threads. The archived code signals workers through plain Bool flags with 1 ms sleep polling, an unsynchronized pattern that BoCA mainline replaced with semaphores and atomic access. |
| **Drop-in for the baseline** | partial: inside fre:ac it replaces the regular driver for the same codec and settings, but output is not bit-identical and the components are not usable outside BoCA |

## Gotchas

- Archived LAME driver, mono input: lame_encode_buffer gets samplesBuffer (the block start) as the left channel for every frame, so mono MP3 output repeats each block's first frame. BoCA mainline passes the per-frame offset. Found by code reading, not run.
- Archived Opus, FAAC and LAME drivers advance by framesToProcess - overlap even on the final flush, so an input shorter than the overlap (under about 0.48 s for Opus at 20 ms frames) makes framesProcessed negative and the memmove runs out of bounds. Mainline uses (flush ? 0 : overlap). Found by code reading.
- The Opus overlap formula uses 960 (a 20 ms frame at 48 kHz) at every sample rate, so the overlap is 72/256 frames at 16 kHz and 144/256 at 8 kHz (28% and 56% of the work discarded), and with 5-10 ms frames at 8-16 kHz it exceeds the 256-frame block (e.g. 288 at 8 kHz/10 ms), which drives the block loop backwards with negative offsets. Still present in BoCA mainline; found by code reading.
- The published numbers come from the 2017 proof of concept (128-frame blocks, 8-frame overlap); the repo's Opus driver now uses 256/24 and was not re-measured. Issue #3 reports intermittent 'Could not process file' errors with superopus only (2018 alpha build), closed without a fix when the repo was archived.

## Known shortcomings

- fre:ac SuperFast drivers: the speedup is parallel codec instances (about 3x at 4 threads, 4.5-4.8x at 8 threads, derived from PDF charts covering only FAAC and Opus; no y-axis unit, machine only '6 core CPU'), with overlap frames adding work, output not bit-identical to the single-instance encoder, no quality or bitrate data, and LAME's bit reservoir repacked. Last commit 2020-12-10.
- The charted FAAC and Opus numbers come from the 2017 128/8 prototype (block/overlap) while the repo's Opus driver is now 256/24 and was not re-measured; workers reuse one encoder across blocks without reset (stale state), contrary to the record's 'fresh state' caveat. Archived-code bugs by reading: the LAME mono path passes the block start as buffer_l every frame (repeats the first frame; fixed in BoCA), flush advances framesToProcess minus overlap so input shorter than the overlap gives a negative memmove (fixed in BoCA), and the Opus overlap 24\*960/frameSize ignores the sample rate and exceeds the 256-frame block at 8-16 kHz with 5-10 ms frames (loop runs backwards; still in BoCA). fre:ac 1.1.1 and 1.1.2 fixed SuperFast crashes and CBR MP3 issues; issue #3 reports random superopus failures. MSIVST/SuperLAME (also listed) derives its repacker from this code.

## Caveats and trade-offs

First-party PDF whose numbers are only in chart images with no y-axis unit; CPU model, OS, compiler and codec versions are not stated (the text only says 'even on a 6 core CPU'), and no benchmark script is published, so tier C. The measured code does different work from the baseline: it is the same codec run as several parallel instances against one single-threaded instance, not a faster codec implementation, and total CPU work rises because overlap frames are encoded and then discarded (6.25% at 8/128 in the PDF, about 9.4% at 24/256 in the final Opus driver). Output is not bit-identical to a single-threaded encode: every chunk starts from fresh encoder state, and the PDF's difference-signal plots show residual differences the author calls 'unnoticeable' without any listening test, objective quality metric or bitrate/size comparison. For MP3 the LAME driver unpacks and repacks frames to rebuild the bit reservoir across chunk seams, with rate-control limits and re-encoding when a frame does not fit. In multi file mode the gain is small (about 1-10%). The Opus resampler stays single-threaded, so non-48 kHz input gains less, and conversions are often limited by decoding speed. Repo archived 2020-12-11 (last commit 2020-12-10, last code change 2018-09-01); the code lives on in enzo1982/BoCA.

Chunked parallelism over several codec instances, so output is not bit-identical to a single-threaded encode and the 8/128 overlap caps speedup at 16x. Works for Opus, AAC, Speex and MP3 drivers; the author says Vorbis, FLAC and WMA do not fit. Needs the fre:ac BoCA and smooth class libraries to build. It speeds up a driver, not the codec library itself.

## Maintenance

Archived 2020-12-11 and superseded by enzo1982/BoCA, where SuperFast is on by default and later fixes landed. GPL-2.0 and tied to the BoCA/smooth frameworks, so it is only copyable as a design or into GPL code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own PDF (doc/SuperFast Codecs.pdf) gives the '3x with four threads' sentence and two bar charts (FAAC and Opus, 1T/4T/8T, regular vs SuperFast) with no units, CPU model, OS, compiler or codec versions; no benchmark script is in the repo. First-party with no methodology, so C.
- **Verifier notes:** Quote and both modes check out against the PDF; the chart image shows only FAAC and Opus at 1T/4T/8T, so I added approximate chart readings and the overlap/quality trade-off from components/opus/opus.cpp and components/lame/lame.cpp. No machine is named.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/doc/SuperFast%20Codecs.pdf>
  - <https://github.com/enzo1982/superfast>
  - <https://github.com/enzo1982/superfast/commits>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/Readme.md>
  - <https://github.com/enzo1982/superfast/tree/master/components>
  - <https://github.com/enzo1982/superfast/tree/master/components/opus>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/opus.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/lame/lame.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/lame/worker.cpp>
- **Sources the enricher read:**
  - <https://github.com/enzo1982/superfast>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/Readme.md>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/doc/SuperFast%20Codecs.pdf>
  - <https://github.com/enzo1982/superfast/tree/master/components>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/opus.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/opus.h>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/worker.h>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/opus/Makefile>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/lame/lame.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/lame/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/faac/faac.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/faac/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/components/Makefile>
  - <https://raw.githubusercontent.com/enzo1982/superfast/master/Makefile>
  - <https://github.com/enzo1982/superfast/issues?q=is%3Aissue>
  - <https://github.com/enzo1982/superfast/issues/3>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/opus/opus.cpp>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/opus/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/faac/faac.cpp>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/faac/worker.cpp>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/lame/lame.cpp>
  - <https://raw.githubusercontent.com/enzo1982/BoCA/master/components/encoder/lame/worker.cpp>
  - <https://github.com/enzo1982/freac>
  - <https://github.com/enzo1982/freac/releases>
  - <https://github.com/enzo1982/freac/issues?q=is%3Aissue+superfast>
  - <https://github.com/enzo1982/freac/issues/103>
  - <https://sourceforge.net/p/bonkenc/discussion/85470/thread/a930b53f7e/>
  - <https://github.com/MSIVST/SuperLAME>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/enzo1982/superfast`) · [data/wave10/enrich/raw/github_com_enzo1982_superfast.json](../../../data/wave10/enrich/raw/github_com_enzo1982_superfast.json) (enrichment confidence 0.75)

</details>
