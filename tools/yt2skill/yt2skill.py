#!/usr/bin/env python3
"""
yt2skill — Turn YouTube videos into Claude agent skills.

Pipeline:
  1. Download video + transcript (yt-dlp)
  2. Extract frames on scene changes (ffmpeg)
  3. Vision pass: Claude reads frames, transcribes on-screen code/slides verbatim
  4. Compile transcript + visuals into SKILL.md + references/
  5. Package as skills/<name>.skill (zip)

Setup:
  sudo apt install -y ffmpeg
  pip install yt-dlp anthropic --break-system-packages
  export ANTHROPIC_API_KEY=sk-ant-...
"""
import argparse, base64, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

import anthropic

WORK = Path("/tmp/yt2skill-work")

def slugify(s):
    s = re.sub(r"https?://\S*[?&]v=", "", s)
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")[:60] or "video"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r

def download(url, workdir):
    workdir.mkdir(parents=True, exist_ok=True)
    run(["yt-dlp", "--write-info-json", "--write-auto-subs", "--write-subs",
         "--sub-langs", "en.*", "--sub-format", "vtt",
         "-f", "bv*[height<=720]+ba/b[height<=720]",
         "-o", str(workdir / "video.%(ext)s"), url])
    info = json.loads(next(workdir.glob("*.info.json")).read_text())
    video = next(p for p in workdir.iterdir()
                 if p.suffix in (".mp4", ".webm", ".mkv"))
    vtts = sorted(workdir.glob("*.vtt"))
    transcript = clean_vtt(vtts[0].read_text()) if vtts else "(no captions)"
    return {"title": info.get("title", ""), "description": info.get("description", ""),
            "duration": info.get("duration", 0), "url": url,
            "video_path": video, "transcript": transcript}

def clean_vtt(vtt):
    lines, seen, out = vtt.splitlines(), set(), []
    ts = None
    for ln in lines:
        m = re.match(r"(\d+:\d+:\d+)\.\d+ -->", ln)
        if m:
            ts = m.group(1)
            continue
        ln = re.sub(r"<[^>]+>", "", ln).strip()
        if not ln or ln in ("WEBVTT",) or ln.startswith(("Kind:", "Language:")):
            continue
        if ln not in seen:
            seen.add(ln)
            out.append(f"[{ts}] {ln}" if ts else ln)
    return "\n".join(out)

def extract_frames(video, workdir, max_frames, duration):
    fdir = workdir / "frames"
    fdir.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(video),
         "-vf", "select='gt(scene,0.22)'", "-vsync", "vfr",
         "-q:v", "3", str(fdir / "f_%04d.jpg")])
    frames = sorted(fdir.glob("f_*.jpg"))
    if len(frames) < 5 and duration:  # static video fallback: even sampling
        for f in frames: f.unlink()
        interval = max(duration // max_frames, 10)
        run(["ffmpeg", "-y", "-i", str(video),
             "-vf", f"fps=1/{interval}", "-q:v", "3", str(fdir / "f_%04d.jpg")])
        frames = sorted(fdir.glob("f_*.jpg"))
    return frames[:max_frames]

def analyze_frames(client, model, frames):
    results = []
    for i in range(0, len(frames), 4):
        batch = frames[i:i+4]
        content = []
        for f in batch:
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg",
                "data": base64.b64encode(f.read_bytes()).decode()}})
        content.append({"type": "text", "text":
            "For each image in order: transcribe ALL on-screen code VERBATIM in fenced "
            "blocks, capture slide text, terminal output, notes, diagram labels. "
            "Label each 'FRAME <filename>'. Skip pure talking-head frames with 'FRAME x: (speaker only)'."})
        msg = client.messages.create(model=model, max_tokens=4000,
                                     messages=[{"role": "user", "content": content}])
        results.append(msg.content[0].text)
    return "\n\n".join(results)

def compile_skill(client, model, info, visual, name, outdir):
    name = name or slugify(info["title"])
    prompt = (f"Compile a Claude agent skill from this YouTube video.\n"
              f"TITLE: {info['title']}\nURL: {info['url']}\n"
              f"DESCRIPTION:\n{info['description'][:3000]}\n\n"
              f"TRANSCRIPT:\n{info['transcript'][:60000]}\n\n"
              f"ON-SCREEN CONTENT (verbatim from frames):\n{visual[:40000]}\n\n"
              "Output ONLY a complete SKILL.md: YAML frontmatter with name "
              f"'{name}' and a trigger-rich description, then the distilled "
              "methodology — exact numbers, thresholds, code, and frameworks "
              "preserved verbatim. Nothing invented.")
    msg = client.messages.create(model=model, max_tokens=8000,
                                 messages=[{"role": "user", "content": prompt}])
    skill_md = msg.content[0].text

    sdir = outdir / name
    (sdir / "references").mkdir(parents=True, exist_ok=True)
    (sdir / "SKILL.md").write_text(skill_md)
    (sdir / "references" / "transcript.md").write_text(info["transcript"])
    (sdir / "references" / "frame-extractions.md").write_text(visual)

    pkg = outdir / f"{name}.skill"
    with zipfile.ZipFile(pkg, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sdir.rglob("*"):
            z.write(p, p.relative_to(outdir))
    return pkg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--name")
    ap.add_argument("--frames", type=int, default=30)
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--out", default="skills")
    ap.add_argument("--keep-work", action="store_true")
    args = ap.parse_args()

    for tool in ("ffmpeg", "yt-dlp"):
        if not shutil.which(tool):
            sys.exit(f"Missing {tool}. Install: sudo apt install ffmpeg && pip install yt-dlp")

    client = anthropic.Anthropic()
    outdir = Path(args.out); outdir.mkdir(exist_ok=True)
    workdir = WORK / slugify(args.url)

    info = download(args.url, workdir)
    frames = extract_frames(info["video_path"], workdir, args.frames, info["duration"])
    visual = analyze_frames(client, args.model, frames)
    pkg = compile_skill(client, args.model, info, visual, args.name, outdir)

    if not args.keep_work:
        shutil.rmtree(workdir, ignore_errors=True)

    print(f"\nDone → {pkg}")
    print(f"Unpacked folder → {pkg.with_suffix('')}/")
    print("Install: copy the folder into ~/.claude/skills/ (Claude Code) "
          "or upload the .skill file in claude.ai Settings → Capabilities.")

if __name__ == "__main__":
    main()
