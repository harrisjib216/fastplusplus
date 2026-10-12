# I/O and filesystem

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** iostreams, fstream, std::filesystem, fread/fwrite  
**4 entries:** 1 tier A · 0 tier B · 3 tier C · 0 tier D · 4 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**reckless**](mattiasflodin-reckless.md) | Asynchronous C++ logging library, drastically lower caller-side latency than std::fstream/fprintf and other async loggers. | **A** | C++ | MIT | 🔴 abandoned |
| 2 | [**fastcpp::io::buffered_writer (developer source)**](private-developer-source-io-and-filesystem.md) | Header-only C++ output buffer that coalesces small writes into 64 KiB flushes instead of issuing write(2) per call. | **C** | C++ | MIT | 🟢 active |
| 3 | [**CPath**](braedonwooding-cpath.md) | Single-header C directory traversal library; faster than `find`, TinyDir, Cute Files, and Python os.walk on recursive walks. | **C** | C | MIT | 🔴 abandoned |
| 4 | [**FastReader**](georgiifirsov-fastreader.md) | Windows memory-mapped line reader using memchr; \~4x faster line iteration than std::ifstream::getline on a 9 KB file. | **C** | C++ | GPL-3.0 | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
