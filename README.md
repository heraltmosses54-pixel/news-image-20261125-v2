[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/heraltmosses54-pixel/news-image-20261125-v2/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/heraltmosses54-pixel/news-image-20261125-v2/reward.svg)](https://make.fun/bounty/news-image-20261125)

# THE WORLD — 25 November 2026

A one-page dense broadsheet newspaper rendered as a PNG, built with **pure
Python standard library only** — no third-party packages, no network, fully
deterministic.

## What it is

`main.py` draws a 1024x1024 newspaper front page for Wednesday 25 November
2026: a navy masthead, a lead story on the Strait of Hormuz tanker attacks,
a dotted world map (red pins mark the day's story locations), a by-the-numbers
rail, 12 story cards across six continents, 9 briefs, and a sport footer.
23 stories in total, all real news reported on that date.

The program includes its own 5x7 pixel font and its own PNG encoder
(`zlib` + `struct`), so it runs anywhere Python 3 runs — including under
`python3 -S` with no site-packages.

## Run

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 -S main.py
# writes /tmp/out/entry.png (1024x1024, under 1 MiB)
```
