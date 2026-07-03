#!/usr/bin/env python3
"""YouTube Analyzer.

Paste any YouTube link -- a single video, a playlist, a channel, or a plain
search query -- and this tool walks it video by video, extracting for each one:

  * transcript      (manual subtitles if available, else auto-generated captions)
  * frames/         (screenshots taken every N seconds, or literally every frame)
  * page.html       (the raw watch-page source code)
  * metadata.json   (title, uploader, duration, views, description, ...)

Results land in one folder per video:

  output/
    <video id> - <title>/
      metadata.json
      transcript.txt
      transcript.vtt
      page.html
      frames/
        frame_000001.jpg
        ...

Progress is tracked in output/analyzed.txt so re-running the same playlist or
channel resumes where it left off instead of starting over.

Examples:
  python analyze.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python analyze.py "https://www.youtube.com/playlist?list=PL..."
  python analyze.py "https://www.youtube.com/@SomeChannel"
  python analyze.py "how to make sourdough" --search --limit 10
  python analyze.py <url> --interval 2 --max-height 1080
  python analyze.py <url> --all-frames          # literal frame-by-frame
  python analyze.py <url> --skip-frames         # transcript + html + metadata only
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp is not installed. Run: pip install -r requirements.txt")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def sanitize_filename(name: str, max_len: int = 80) -> str:
    """Make a string safe to use as a directory name."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    return name[:max_len] or "untitled"


def looks_like_url(text: str) -> bool:
    return bool(re.match(r"^https?://", text, re.IGNORECASE))


def build_target(source: str, search: bool, limit: int | None) -> str:
    """Turn the user's input into something yt-dlp can enumerate."""
    if search or not looks_like_url(source):
        n = limit or 25
        return f"ytsearch{n}:{source}"
    return source


def list_videos(target: str, limit: int | None) -> list[dict]:
    """Expand a video/playlist/channel/search into a flat list of video entries."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "ignoreerrors": True,
    }
    if limit:
        opts["playlistend"] = limit

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(target, download=False)

    if info is None:
        return []

    entries = []
    stack = [info]
    while stack:
        node = stack.pop(0)
        if node is None:
            continue
        if node.get("_type") == "playlist" or "entries" in node:
            # channels expand to nested playlists (Videos / Shorts / Live tabs)
            stack.extend(e for e in (node.get("entries") or []) if e)
        else:
            vid = node.get("id")
            if vid and not any(e["id"] == vid for e in entries):
                entries.append({
                    "id": vid,
                    "title": node.get("title") or vid,
                    "url": node.get("url") or f"https://www.youtube.com/watch?v={vid}",
                })
    if limit:
        entries = entries[:limit]
    return entries


def vtt_to_text(vtt: str) -> str:
    """Convert WebVTT captions to de-duplicated plain text."""
    lines_out: list[str] = []
    for raw in vtt.splitlines():
        line = raw.strip()
        if (not line
                or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE"))
                or "-->" in line
                or re.fullmatch(r"\d+", line)):
            continue
        line = re.sub(r"<[^>]+>", "", line)  # strip inline timing/karaoke tags
        line = html.unescape(line).strip()
        # auto-captions repeat lines as they scroll; keep each once
        if line and (not lines_out or lines_out[-1] != line):
            lines_out.append(line)
    return "\n".join(lines_out)


def fetch_page_source(url: str, dest: Path) -> bool:
    """Save the raw watch-page HTML."""
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"),
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as exc:  # noqa: BLE001 - report and continue with next video
        print(f"    ! could not fetch page source: {exc}")
        return False


def extract_frames(video_file: Path, frames_dir: Path,
                   interval: float, all_frames: bool) -> int:
    """Screenshot the video with ffmpeg. Returns number of frames written."""
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video_file)]
    if not all_frames:
        cmd += ["-vf", f"fps=1/{interval}"]
    cmd += ["-q:v", "2", str(frames_dir / "frame_%06d.jpg")]
    subprocess.run(cmd, check=True)
    return sum(1 for _ in frames_dir.glob("frame_*.jpg"))


# --------------------------------------------------------------------------- #
# per-video processing
# --------------------------------------------------------------------------- #

METADATA_KEYS = [
    "id", "title", "description", "uploader", "uploader_id", "channel",
    "channel_id", "channel_url", "upload_date", "duration", "view_count",
    "like_count", "comment_count", "tags", "categories", "webpage_url",
    "thumbnail", "language", "chapters",
]


def process_video(entry: dict, out_root: Path, args: argparse.Namespace) -> None:
    url = f"https://www.youtube.com/watch?v={entry['id']}"
    video_dir = out_root / f"{entry['id']} - {sanitize_filename(entry['title'])}"
    video_dir.mkdir(parents=True, exist_ok=True)

    # -- metadata + subtitles (one yt-dlp pass, no media download) ----------- #
    sub_langs = [args.lang, f"{args.lang}-*", f"{args.lang}.*"]
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": sub_langs,
        "subtitlesformat": "vtt",
        "outtmpl": str(video_dir / "transcript"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    metadata = {k: info.get(k) for k in METADATA_KEYS}
    (video_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    # yt-dlp names the file transcript.<lang>.vtt; normalize + make plain text
    vtt_files = sorted(video_dir.glob("transcript*.vtt"))
    if vtt_files:
        vtt_path = vtt_files[0]
        canonical = video_dir / "transcript.vtt"
        if vtt_path != canonical:
            vtt_path.replace(canonical)
        for extra in vtt_files[1:]:
            extra.unlink(missing_ok=True)
        text = vtt_to_text(canonical.read_text(encoding="utf-8", errors="replace"))
        (video_dir / "transcript.txt").write_text(text, encoding="utf-8")
        print(f"    transcript: {len(text.splitlines())} lines")
    else:
        print("    ! no subtitles or auto-captions available")

    # -- page source --------------------------------------------------------- #
    if not args.skip_html:
        if fetch_page_source(url, video_dir / "page.html"):
            print("    page source saved")

    # -- frames --------------------------------------------------------------- #
    if not args.skip_frames:
        with tempfile.TemporaryDirectory(prefix="yta_") as tmp:
            dl_opts = {
                "quiet": True,
                "no_warnings": True,
                "format": (f"bestvideo[height<={args.max_height}]"
                           f"/best[height<={args.max_height}]/best"),
                "outtmpl": str(Path(tmp) / "video.%(ext)s"),
            }
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.extract_info(url, download=True)
            video_files = list(Path(tmp).glob("video.*"))
            if video_files:
                if args.keep_video:
                    kept = video_dir / video_files[0].name
                    shutil.copy2(video_files[0], kept)
                count = extract_frames(video_files[0], video_dir / "frames",
                                       args.interval, args.all_frames)
                print(f"    frames: {count} screenshots")
            else:
                print("    ! video download produced no file, skipping frames")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source",
                        help="YouTube video / playlist / channel URL, or a search query")
    parser.add_argument("--search", action="store_true",
                        help="treat SOURCE as a search query even if it looks like a URL")
    parser.add_argument("--limit", type=int, default=None,
                        help="max number of videos to process (default: all; search default: 25)")
    parser.add_argument("-o", "--output", default="output",
                        help="output directory (default: ./output)")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="seconds between frame screenshots (default: 5)")
    parser.add_argument("--all-frames", action="store_true",
                        help="extract literally every frame (large output!)")
    parser.add_argument("--max-height", type=int, default=720,
                        help="max video resolution for frame extraction (default: 720)")
    parser.add_argument("--lang", default="en",
                        help="preferred transcript language (default: en)")
    parser.add_argument("--skip-frames", action="store_true",
                        help="skip video download and frame extraction")
    parser.add_argument("--skip-html", action="store_true",
                        help="skip saving the watch-page source")
    parser.add_argument("--keep-video", action="store_true",
                        help="keep the downloaded video file next to the frames")
    parser.add_argument("--force", action="store_true",
                        help="re-process videos already listed in analyzed.txt")
    args = parser.parse_args()

    if not args.skip_frames and shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found -- install it, or pass --skip-frames.")

    out_root = Path(args.output)
    out_root.mkdir(parents=True, exist_ok=True)
    archive = out_root / "analyzed.txt"
    done: set[str] = set(archive.read_text().split()) if archive.exists() else set()

    target = build_target(args.source, args.search, args.limit)
    print(f"Expanding: {target}")
    videos = list_videos(target, args.limit)
    if not videos:
        sys.exit("No videos found for that input.")
    print(f"Found {len(videos)} video(s)\n")

    failures = 0
    for i, entry in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {entry['title']} ({entry['id']})")
        if entry["id"] in done and not args.force:
            print("    already analyzed, skipping (use --force to redo)")
            continue
        try:
            process_video(entry, out_root, args)
        except KeyboardInterrupt:
            print("\nInterrupted -- progress saved, rerun to resume.")
            return 130
        except Exception as exc:  # noqa: BLE001 - keep going video by video
            failures += 1
            print(f"    ! failed: {exc}")
            continue
        done.add(entry["id"])
        with archive.open("a", encoding="utf-8") as fh:
            fh.write(entry["id"] + "\n")

    print(f"\nDone. {len(videos) - failures}/{len(videos)} succeeded. "
          f"Results in: {out_root.resolve()}")
    return 1 if failures == len(videos) else 0


if __name__ == "__main__":
    sys.exit(main())
