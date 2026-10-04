#!/usr/bin/env python3
"""Build the 5-minute "Stop Comparing" Krishna video with Seedance 2.0 (fal.ai) at 1080p.

Steps, in order (each caches its output, so re-running resumes where it stopped):
  voice     narration for every shot (ElevenLabs, or your own files in build/vo/)
  plan      fit shot lengths to the target runtime, print the cost estimate
  ref       Krishna reference frame that keeps his look consistent across shots
  clips     one Seedance 2.0 clip per shot (costs money: needs --yes)
  assemble  crossfades, narration, music bed, captions, chapters, thumbnail frame

  python make_video.py all --mock                      free dry run with placeholder clips
  python make_video.py voice && python make_video.py plan
  python make_video.py ref --yes                       then look at build/ref/krishna.png
  python make_video.py clips --yes
  python make_video.py assemble --music music/bansuri.mp3
  python make_video.py clips --redo d05,e03 --yes      re-roll shots you don't like
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import shots as S

HERE = Path(__file__).resolve().parent

T2V = "bytedance/seedance-2.0/text-to-video"
R2V = "bytedance/seedance-2.0/reference-to-video"

# Estimated fal price per generated second. Seedance bills tokens (width x height x 24 fps / 1024)
# at $0.014 per 1K, which gives fal's published $0.3034/s at 720p.
PRICE_PER_SEC = {"480p": 0.13, "720p": 0.30, "1080p": 0.68}

W, H, FPS = 1920, 1080, 24
RATE = 48000          # narration sample rate
LEAD = 0.5            # narration starts this long after its shot begins (= crossfade, so it never overlaps)
XFADE = 0.5           # crossfade between shots
MIN_TAIL = 0.8        # minimum silence after each line before the next shot
MIN_CLIP, MAX_CLIP = 4, 15
MAX_STRETCH = 1.35    # a clip may be slowed this much to cover a long line; beyond it the last frame holds
REF_SECONDS = 5

ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"  # ElevenLabs premade "Adam"; set ELEVENLABS_VOICE_ID to change


# ---------------------------------------------------------------- helpers

class Paths:
    def __init__(self, mock: bool):
        self.build = HERE / ("build-mock" if mock else "build")
        self.out = HERE / ("out-mock" if mock else "out")
        self.vo = self.build / "vo"          # raw narration (yours or ElevenLabs)
        self.vo48 = self.build / "vo48"      # trimmed 48 kHz mono wav used for timing and mixing
        self.ref = self.build / "ref"
        self.clips = self.build / "clips"
        self.norm = self.build / "norm"
        self.plan = self.build / "plan.json"
        for d in (self.build, self.out, self.vo, self.vo48, self.ref, self.clips, self.norm):
            d.mkdir(parents=True, exist_ok=True)


def run(cmd: list, cwd: Path | None = None) -> None:
    res = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"command failed: {' '.join(map(str, cmd))[:300]}\n{res.stderr[-2000:]}")


def ffmpeg(*args, cwd: Path | None = None) -> None:
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], cwd=cwd)


def duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def words(text: str) -> int:
    return len(text.split())


def prompt_for(shot: dict) -> str:
    body = f"{S.KRISHNA_LOCK} {shot['prompt']}" if shot.get("krishna") else shot["prompt"]
    return f"{body} {S.STYLE}"


def need_key(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        sys.exit(f"{name} is not set. See README.md, or run with --mock for a free dry run.")
    return val


def fal():
    need_key("FAL_KEY")
    try:
        import fal_client
    except ImportError:
        sys.exit("fal-client is not installed: pip install -r requirements.txt")
    return fal_client


def download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dest)


def clock(t: float, srt: bool = False) -> str:
    if srt:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    s = int(t)
    return f"{s // 60}:{s % 60:02}"


# ---------------------------------------------------------------- voice

def eleven_tts(text: str, dest: Path) -> None:
    key = need_key("ELEVENLABS_API_KEY")
    voice = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE)
    body = json.dumps({
        "text": text,
        "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15,
                           "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(ELEVEN_URL.format(voice=voice), data=body, method="POST", headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode(errors='replace')[:500]}")


def step_voice(p: Paths, args) -> None:
    for shot in S.SHOTS:
        sid, text = shot["id"], shot["vo"]
        out = p.vo48 / f"{sid}.wav"
        if not text or out.exists():
            continue
        raw = next((f for f in sorted(p.vo.glob(f"{sid}.*"))), None)
        if raw is None:
            if args.mock:
                raw = p.vo / f"{sid}.wav"   # quiet tone as long as the line would take to read
                ffmpeg("-f", "lavfi", "-i", f"sine=frequency=220:duration={words(text) / 2.2:.2f}",
                       "-af", "volume=0.05", raw)
            else:
                raw = p.vo / f"{sid}.mp3"
                print(f"  voice {sid}: {text[:60]}")
                eleven_tts(shot.get("tts", text), raw)
        # trim leading/trailing silence so timing is exact, optionally slow the delivery
        trim = ("silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                "silenceremove=start_periods=1:start_threshold=-50dB,areverse")
        tempo = f",atempo={args.voice_tempo}" if args.voice_tempo != 1.0 else ""
        af = (trim if not args.mock else "anull") + tempo
        ffmpeg("-i", raw, "-af", af, "-ar", RATE, "-ac", 1, "-sample_fmt", "s16", out)
    print(f"voice ready in {p.vo48}")


# ---------------------------------------------------------------- plan

def step_plan(p: Paths, args) -> dict:
    rows = []
    for shot in S.SHOTS:
        vo = p.vo48 / f"{shot['id']}.wav"
        if shot["vo"] and not vo.exists():
            sys.exit(f"missing narration for {shot['id']}: run the voice step first")
        vo_dur = duration(vo) if shot["vo"] else 0.0
        need = LEAD + vo_dur + MIN_TAIL if shot["vo"] else shot.get("hold", 4.5)
        rows.append({"id": shot["id"], "section": shot["section"], "vo_dur": round(vo_dur, 3),
                     "dur": need, "words": words(shot["vo"])})

    def total() -> float:
        return sum(r["dur"] for r in rows) - XFADE * (len(rows) - 1)

    # spread any spare time over shots that can take it, so the cut lands on the target runtime
    spare = args.target - total()
    while spare > 0.01:
        room = [r for r in rows if r["dur"] < MAX_CLIP - 0.01]
        if not room:
            break
        share = spare / len(room)
        for r in room:
            add = min(share, MAX_CLIP - r["dur"])
            r["dur"] += add
            spare -= add

    t = 0.0
    for r in rows:
        r["dur"] = round(r["dur"], 3)
        r["start"] = round(t, 3)
        t += r["dur"] - XFADE
        r["request"] = int(min(MAX_CLIP, max(MIN_CLIP, math.ceil(r["dur"]))))
        r["stretch"] = round(max(1.0, min(MAX_STRETCH, r["dur"] / r["request"])), 3)

    plan = {"resolution": args.resolution, "total": round(total(), 3), "shots": rows}
    p.plan.write_text(json.dumps(plan, indent=2))

    secs = sum(r["request"] for r in rows) + REF_SECONDS
    cost = secs * PRICE_PER_SEC[args.resolution]
    print(f"{'shot':5} {'start':>6} {'clip':>5} {'ask':>4} {'voice':>6}  section")
    for r in rows:
        flag = "  slowed" if r["dur"] > r["request"] else ""
        print(f"{r['id']:5} {clock(r['start']):>6} {r['dur']:5.1f} {r['request']:4} "
              f"{r['vo_dur']:6.1f}  {r['section']}{flag}")
    print(f"\nruntime {clock(plan['total'])} ({plan['total']:.1f}s, target {args.target:.0f}s), "
          f"{len(rows)} shots, {sum(r['words'] for r in rows)} words")
    print(f"Seedance: {secs}s at {args.resolution} = about ${cost:,.0f} for one take of every shot")
    if total() > args.target + 1:
        print("note: the narration runs longer than the target; nothing was cut")
    return plan


def load_plan(p: Paths) -> dict:
    if not p.plan.exists():
        sys.exit("no plan yet: run the voice and plan steps first")
    return json.loads(p.plan.read_text())


# ---------------------------------------------------------------- reference frame

def step_ref(p: Paths, args) -> str:
    png, url_file = p.ref / "krishna.png", p.ref / "krishna_url.txt"
    if not png.exists():
        if args.mock:
            ffmpeg("-f", "lavfi", "-i", f"color=c=0x2a4d9b:s={W}x{H}", "-frames:v", 1, png)
        else:
            if not args.yes:
                sys.exit(f"the reference portrait costs about ${REF_SECONDS * PRICE_PER_SEC[args.resolution]:.2f}; "
                         "re-run with --yes, or put your own image at build/ref/krishna.png")
            print("generating the Krishna reference portrait...")
            res = fal().subscribe(T2V, arguments={
                "prompt": f"{S.REF_PROMPT} {S.STYLE}", "resolution": args.resolution,
                "duration": str(REF_SECONDS), "aspect_ratio": "16:9", "generate_audio": False,
                "seed": args.seed})
            clip = p.ref / "krishna_ref.mp4"
            download(res["video"]["url"], clip)
            ffmpeg("-ss", "2", "-i", clip, "-frames:v", 1, png)
        url_file.unlink(missing_ok=True)
    if url_file.exists():
        return url_file.read_text().strip()
    url = "mock://krishna.png" if args.mock else fal().upload_file(png)
    url_file.write_text(url)
    print(f"reference frame: {png}")
    return url


# ---------------------------------------------------------------- clips

def make_clip(shot: dict, row: dict, ref_url: str, p: Paths, args, seed: int) -> str:
    dest = p.clips / f"{shot['id']}.mp4"
    if args.mock:
        ffmpeg("-f", "lavfi", "-i", f"testsrc2=s=1280x720:r={FPS}:d={row['request']}",
               "-pix_fmt", "yuv420p", dest)
        return "mock"
    arguments = {"prompt": prompt_for(shot), "resolution": args.resolution,
                 "duration": str(row["request"]), "aspect_ratio": "16:9",
                 "generate_audio": False, "seed": seed}
    endpoint = T2V
    if shot.get("krishna"):
        endpoint, arguments["image_urls"] = R2V, [ref_url]
    for attempt in (1, 2):
        try:
            res = fal().subscribe(endpoint, arguments=arguments)
            download(res["video"]["url"], dest)
            meta = {"endpoint": endpoint, "arguments": arguments, "result": res}
            (p.clips / f"{shot['id']}.json").write_text(json.dumps(meta, indent=2))
            return res["video"]["url"]
        except Exception as e:  # network blips and queue timeouts get one retry
            if attempt == 2:
                raise
            print(f"  {shot['id']}: {e}; retrying in 15s")
            time.sleep(15)
    return ""


def step_clips(p: Paths, args) -> None:
    plan = load_plan(p)
    if plan["resolution"] != args.resolution:
        sys.exit(f"plan was made for {plan['resolution']}; re-run plan with --resolution {args.resolution}")
    if [r["id"] for r in plan["shots"]] != [s["id"] for s in S.SHOTS]:
        sys.exit("shots.py changed since the plan was made: run voice and plan again")
    rows = {r["id"]: r for r in plan["shots"]}
    redo = {s for s in (args.redo or "").split(",") if s}
    for sid in redo:
        (p.clips / f"{sid}.mp4").unlink(missing_ok=True)
    todo = [s for s in S.SHOTS if not (p.clips / f"{s['id']}.mp4").exists()]
    if not todo:
        print("all clips already generated")
        return
    secs = sum(rows[s["id"]]["request"] for s in todo)
    if not args.mock and not args.yes:
        sys.exit(f"{len(todo)} clips, {secs}s at {args.resolution}, about "
                 f"${secs * PRICE_PER_SEC[args.resolution]:,.0f}. Re-run with --yes to generate.")
    if not args.mock:
        fal()
    ref_url = step_ref(p, args) if any(s.get("krishna") for s in todo) else ""
    print(f"generating {len(todo)} clips with {args.workers} at a time...")
    failed = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {}
        for s in todo:
            index = next(i for i, x in enumerate(S.SHOTS) if x["id"] == s["id"])
            seed = random.randint(1, 2**31 - 1) if s["id"] in redo else args.seed + index
            jobs[pool.submit(make_clip, s, rows[s["id"]], ref_url, p, args, seed)] = s["id"]
        for fut in as_completed(jobs):
            sid = jobs[fut]
            try:
                fut.result()
                print(f"  done {sid}")
            except Exception as e:
                failed.append(sid)
                print(f"  FAILED {sid}: {e}")
    if failed:
        sys.exit(f"{len(failed)} clips failed ({','.join(sorted(failed))}); re-run the same command to retry "
                 "them. If fal rejected the resolution, re-plan with --resolution 720p.")


# ---------------------------------------------------------------- assemble

def caption_cues(text: str, start: float, length: float) -> list:
    chunks, cur = [], ""
    for w in text.split():
        cand = f"{cur} {w}".strip()
        if len(cand) > 84 and cur:
            chunks.append(cur)
            cur = w
        else:
            cur = cand
        if cur.endswith((".", "?", "!", ":")) and len(cur) > 30:
            chunks.append(cur)
            cur = ""
    if cur:
        chunks.append(cur)
    total_chars = sum(len(c) for c in chunks)
    cues, t = [], start
    for c in chunks:
        d = length * len(c) / total_chars
        cues.append((t, t + d, "\n".join(textwrap.wrap(c, 42))))
        t += d
    return cues


def build_voice_track(p: Paths, plan: dict, dest: Path) -> None:
    buf = bytearray(int(round(plan["total"] * RATE)) * 2)
    for r in plan["shots"]:
        if not r["vo_dur"]:
            continue
        with wave.open(str(p.vo48 / f"{r['id']}.wav")) as w:
            data = w.readframes(w.getnframes())
        at = int(round((r["start"] + LEAD) * RATE)) * 2
        end = min(at + len(data), len(buf))
        buf[at:end] = data[:end - at]
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(buf))


def step_assemble(p: Paths, args) -> None:
    plan = load_plan(p)
    rows, total = plan["shots"], plan["total"]
    if [r["id"] for r in rows] != [s["id"] for s in S.SHOTS]:
        sys.exit("shots.py changed since the plan was made: run voice and plan again")
    missing = [r["id"] for r in rows if not (p.clips / f"{r['id']}.mp4").exists()]
    if missing:
        sys.exit(f"missing clips: {','.join(missing)}; run the clips step first")

    print("normalising clips to 1920x1080 at 24 fps...")
    for r in rows:
        src, dst = p.clips / f"{r['id']}.mp4", p.norm / f"{r['id']}.mp4"
        stamp = dst.with_suffix(".txt")
        vf = (f"setpts=PTS*{r['stretch']},"
              f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
              f"fps={FPS},tpad=stop_mode=clone:stop_duration=10,trim=duration={r['dur']},"
              f"setpts=PTS-STARTPTS,format=yuv420p,setsar=1")
        if (dst.exists() and dst.stat().st_mtime > src.stat().st_mtime
                and stamp.exists() and stamp.read_text() == vf):
            continue
        ffmpeg("-i", src, "-an", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", 14, dst)
        stamp.write_text(vf)

    voice = p.build / "voice_track.wav"
    build_voice_track(p, plan, voice)

    srt, n = [], 0
    for r, shot in zip(rows, S.SHOTS):
        if shot["vo"]:
            for a, b, text in caption_cues(shot["vo"], r["start"] + LEAD, r["vo_dur"]):
                n += 1
                srt.append(f"{n}\n{clock(a, True)} --> {clock(b, True)}\n{text}\n")
    captions = p.out / "captions.srt"
    captions.write_text("\n".join(srt), encoding="utf-8")

    # video: chain of crossfades, fade in from and out to black
    graph, prev = [], "0:v"
    for k in range(1, len(rows)):
        graph.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XFADE}:"
                     f"offset={rows[k]['start']:.3f}[v{k}]")
        prev = f"v{k}"
    subs = ""
    if args.burn_captions:
        shutil.copy(captions, p.build / "captions.srt")
        subs = (",subtitles=captions.srt:force_style='FontName=DejaVu Sans,FontSize=20,"
                "Outline=2,Shadow=0,MarginV=36'")
    graph.append(f"[{prev}]fade=t=in:d=1,fade=t=out:st={total - 1.5:.3f}:d=1.5{subs}[vout]")

    # audio: narration, optional ducked music bed, loudness for YouTube (-14 LUFS)
    nv = len(rows)
    inputs = [x for r in rows for x in ("-i", f"norm/{r['id']}.mp4")] + ["-i", "voice_track.wav"]
    vo = f"[{nv}:a]aformat=sample_rates={RATE}:channel_layouts=stereo"
    music = Path(args.music).resolve() if args.music else None
    if music:
        if not music.exists():
            sys.exit(f"music file not found: {music}")
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        graph += [
            f"{vo},asplit=2[vo1][vo2]",
            f"[{nv + 1}:a]aformat=sample_rates={RATE}:channel_layouts=stereo,atrim=duration={total:.3f},"
            f"asetpts=PTS-STARTPTS,volume={args.music_gain},afade=t=in:d=3,"
            f"afade=t=out:st={total - 4:.3f}:d=4[m]",
            "[m][vo1]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=600[md]",
            "[md][vo2]amix=inputs=2:duration=first[mx]",
            f"[mx]loudnorm=I=-14:TP=-1.5:LRA=11,aresample={RATE}[aout]",
        ]
    else:
        print("no --music given: narration only")
        graph.append(f"{vo},loudnorm=I=-14:TP=-1.5:LRA=11,aresample={RATE}[aout]")
    (p.build / "graph.txt").write_text(";\n".join(graph))  # for debugging only

    final = p.out / f"stop_comparing_{H}p.mp4"
    print(f"rendering {final.name} ({clock(total)})...")
    ffmpeg(*inputs, "-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", args.preset, "-crf", 18, "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-r", FPS, "-g", FPS * 2, "-c:a", "aac", "-b:a", "192k",
           "-ar", RATE, "-movflags", "+faststart", "-t", f"{total:.3f}", final.resolve(), cwd=p.build)

    thumb = next((r for r, s in zip(rows, S.SHOTS) if s.get("thumb")), rows[0])
    ffmpeg("-ss", f"{thumb['dur'] / 2:.2f}", "-i", p.norm / f"{thumb['id']}.mp4", "-frames:v", 1,
           "-vf", "scale=1280:720", "-q:v", 2, p.out / "thumbnail_base.jpg")

    seen, chapters = set(), []
    for r in rows:
        if r["section"] not in seen:
            seen.add(r["section"])
            chapters.append(f"{clock(0 if not chapters else r['start'])} {S.SECTIONS[r['section']]}")
    (p.out / "description.txt").write_text(
        f"{S.TITLE}\n\n{S.DESCRIPTION.format(chapters=chr(10).join(chapters))}\n"
        f"Tags: {', '.join(S.TAGS)}\n", encoding="utf-8")

    print(f"\n{final}  {clock(duration(final))}")
    print(f"{captions}\n{p.out / 'description.txt'}\n{p.out / 'thumbnail_base.jpg'}")


# ---------------------------------------------------------------- shot list

def step_shotlist(p: Paths, args) -> None:
    lines = [f"# Shot list: {S.TITLE}", "",
             "Generated from `shots.py` by `python make_video.py shotlist`. Edit `shots.py`, not this file.", ""]
    for shot in S.SHOTS:
        kind = "Krishna (reference-to-video)" if shot.get("krishna") else "Scene (text-to-video)"
        lines += [f"## {shot['id']} · {S.SECTIONS[shot['section']]} · {kind}", "",
                  f"**Voice-over:** {shot['vo'] or '(music only)'}", "",
                  f"**Prompt:** {shot['prompt']}", ""]
    (HERE / "SHOTLIST.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {HERE / 'SHOTLIST.md'}")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["voice", "plan", "ref", "clips", "assemble", "all", "shotlist"])
    ap.add_argument("--mock", action="store_true", help="placeholder voice and clips, no API calls, no cost")
    ap.add_argument("--yes", action="store_true", help="confirm paid Seedance generation")
    ap.add_argument("--resolution", default="1080p", choices=list(PRICE_PER_SEC))
    ap.add_argument("--target", type=float, default=300, help="runtime to aim for, in seconds")
    ap.add_argument("--workers", type=int, default=4, help="Seedance jobs to run at once")
    ap.add_argument("--seed", type=int, default=108, help="base seed; shot n uses seed + n")
    ap.add_argument("--redo", help="comma-separated shot ids to regenerate with a new seed")
    ap.add_argument("--voice-tempo", type=float, default=1.0, help="e.g. 0.92 slows the narration 8%%")
    ap.add_argument("--music", help="music bed (mp3/wav), looped and ducked under the narration")
    ap.add_argument("--music-gain", type=float, default=0.18, help="music level before ducking")
    ap.add_argument("--burn-captions", action="store_true",
                    help="burn English captions into the picture (off by default: upload captions.srt so "
                         "auto-dubbed audiences don't see English text)")
    ap.add_argument("--preset", default="slow", help="x264 preset for the final render")
    args = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("ffmpeg and ffprobe must be installed and on PATH")
    p = Paths(args.mock)
    if args.mock:
        args.yes = True
    steps = {"voice": step_voice, "plan": step_plan, "ref": step_ref, "clips": step_clips,
             "assemble": step_assemble, "shotlist": step_shotlist}
    for name in (["voice", "plan", "clips", "assemble"] if args.step == "all" else [args.step]):
        print(f"== {name}")
        steps[name](p, args)


if __name__ == "__main__":
    main()
