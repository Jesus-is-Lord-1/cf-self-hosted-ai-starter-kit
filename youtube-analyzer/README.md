# YouTube Analyzer

Paste any YouTube link and get back, **for every video it contains**:

| Output | What it is |
|---|---|
| `transcript.txt` | Plain-text transcript (manual subtitles preferred, auto-captions as fallback) |
| `transcript.vtt` | The same transcript with timestamps (WebVTT) |
| `frames/` | Screenshots of the video every N seconds (or literally every frame) |
| `page.html` | The raw source code of the video's watch page |
| `metadata.json` | Title, channel, description, duration, views, tags, chapters, ... |

It accepts **all of these as input** and automatically goes video by video:

- a single video: `https://www.youtube.com/watch?v=...`
- a playlist: `https://www.youtube.com/playlist?list=...`
- a channel: `https://www.youtube.com/@SomeChannel`
- search results: `python analyze.py "how to make sourdough" --limit 10`

Progress is saved in `output/analyzed.txt`, so if a big playlist or channel run
gets interrupted, just run the same command again and it resumes where it left
off (already-analyzed videos are skipped).

## Run with Docker (recommended)

From the repository root:

```bash
# build once
docker compose --profile tools build youtube-analyzer

# single video
docker compose run --rm youtube-analyzer \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o /data/shared/youtube

# whole playlist, screenshot every 10 seconds
docker compose run --rm youtube-analyzer \
  "https://www.youtube.com/playlist?list=PL..." --interval 10 -o /data/shared/youtube

# a channel, first 20 videos only
docker compose run --rm youtube-analyzer \
  "https://www.youtube.com/@SomeChannel" --limit 20 -o /data/shared/youtube

# search results
docker compose run --rm youtube-analyzer \
  "self hosted ai" --search --limit 10 -o /data/shared/youtube
```

Results land in `./shared/youtube/` on your machine — which is also visible
inside the n8n container at `/data/shared/youtube`, so n8n workflows can read
the transcripts and frames directly (e.g. to summarize them with Ollama or
index them into Qdrant).

## Run directly (no Docker)

Requires Python 3.10+ and [ffmpeg](https://ffmpeg.org/) on your PATH:

```bash
cd youtube-analyzer
pip install -r requirements.txt
python analyze.py "https://www.youtube.com/watch?v=..."
```

## Options

```
--limit N        max number of videos to process (search defaults to 25)
--search         treat the input as a search query
-o, --output     output directory (default: ./output)
--interval N     seconds between screenshots (default: 5)
--all-frames     extract literally every frame (huge output — use with care)
--max-height N   resolution cap for frame extraction (default: 720)
--lang XX        preferred transcript language (default: en)
--skip-frames    transcript + page source + metadata only (much faster)
--skip-html      don't save the watch-page source
--keep-video     keep the downloaded video file next to the frames
--force          re-process videos already in analyzed.txt
```

## Output layout

```
output/
  analyzed.txt                     # resume tracking
  dQw4w9WgXcQ - Rick Astley - Never Gonna Give You Up/
    metadata.json
    transcript.txt
    transcript.vtt
    page.html
    frames/
      frame_000001.jpg
      frame_000002.jpg
      ...
```

## Notes

- "Frame by frame" literally means ~30 images per second of video — a 10-minute
  video is ~18,000 images. The default (one frame every 5 seconds) is usually
  what you want for feeding screenshots to an AI model; tune with `--interval`.
- YouTube sometimes rate-limits or blocks datacenter IPs. If you hit errors,
  run from your own machine, slow down (`--limit`), or pass cookies by adding
  a `cookies.txt` (see yt-dlp docs) — the tool uses yt-dlp under the hood.
