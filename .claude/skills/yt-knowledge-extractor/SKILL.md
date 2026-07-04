---
name: yt-knowledge-extractor
description: >
  Extract complete knowledge from a YouTube video — real transcript, scene-change screenshots, page source/metadata — and compile it into a single structured knowledge base Claude can reason over. Use this skill whenever the user provides a YouTube URL and wants to learn from it, summarize it, extract notes/code/slides shown on screen, build a knowledge base from it, or asks anything like "watch this video", "pull everything from this video", "get the transcript and screenshots", or "what does this video teach". Also use when the user wants on-screen text, code, whiteboard content, or slides captured from a video, not just the audio transcript.
---

# YouTube Knowledge Extractor

Turns a YouTube video into a knowledge base with three layers:

1. **Transcript** — real captions (manual if available, else auto-generated), timestamped.
2. **Scene screenshots** — frames captured only when the visual content changes (slide flips, code scrolls, whiteboard updates). Each frame is timestamped so it aligns with the transcript.
3. **Page source & metadata** — full video metadata (title, description, chapters, uploader, upload date) plus the raw description which often contains notes, links, and resources.

Everything lands in one output folder with a `knowledge.md` index that stitches transcript segments to the frames shown at that moment.

## Workflow

### Step 0: Check dependencies (first run only)

```bash
bash scripts/check_deps.sh
```

If anything is missing it prints the exact `apt`/`pip` install commands.

### Step 1: Metadata + transcript

```bash
OUT=./yt-knowledge/<video-slug>
mkdir -p "$OUT/frames"
yt-dlp --skip-download --write-info-json --write-auto-subs --write-subs \
  --sub-langs "en.*" --sub-format vtt -o "$OUT/video" "<URL>"
```

- Prefer manual subs over auto-generated when both exist.
- Convert VTT → timestamped plain text (strip cue noise, merge duplicate rolling-caption lines).
- Pull title, description, chapters, uploader, upload_date, duration from the `.info.json`.

**Fallback (datacenter IP blocked / 403):** extract the signed caption URL from the `.info.json` (`automatic_captions` / `subtitles` fields) and fetch it directly with curl. For frames, fall back to the storyboard sprite sheets (`storyboards` format in info.json) — download sprites, slice tiles with ffmpeg/PIL, run scene-change diff on the tiles. Lower resolution but works when full video download is blocked.

### Step 2: Video download + scene-change frames

```bash
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" -o "$OUT/video.%(ext)s" "<URL>"
ffmpeg -i "$OUT"/video.* -vf "select='gt(scene,0.22)',showinfo" \
  -vsync vfr "$OUT/frames/frame_%04d.jpg" 2> "$OUT/scenes.log"
```

- Parse `showinfo` output in scenes.log for `pts_time` → timestamp each frame.
- Scene threshold 0.22 default. If < 10 frames on a 30+ min video, drop to 0.12. If > 300 frames, raise to 0.35.
- Static/talking-head videos: fall back to 1 frame per 60s.

### Step 3: OCR (only when necessary)

Only OCR frames when the user needs on-screen text/code, or frames clearly contain slides/code/whiteboards. Read the frame images directly (Claude vision) — transcribe code VERBATIM, capture slide bullets, tables, and diagram labels. Batch 4–6 frames per pass.

### Step 4: Compile `knowledge.md`

Single file, this structure:

```
# <Video Title>
Source: <URL> · Uploader · Date · Duration
## Metadata & Description (verbatim description, links, chapters)
## Timeline
### [MM:SS] <section/chapter>
Transcript: <cleaned text for this span>
Frames: frame_0007.jpg [12:41] — <what it shows; verbatim code/slide text if OCR'd>
## Key Extracts (all code blocks, formulas, thresholds, numbered frameworks found)
```

Rules: nothing invented — transcript and frames are ground truth. Preserve exact numbers/thresholds verbatim. Every frame reference keeps its timestamp.

### Output

Deliver the folder path + `knowledge.md`. Keep frames unless user says delete.
