# Krishna motivation video kit (Seedance 2.0, 1080p)

This kit builds a 5-minute faceless video, "Stop Comparing! What Is Meant for You Is Still Growing", in the style of the Shri Krishna Motivation channel. Every shot is a Seedance 2.0 clip, with narration from ElevenLabs over a ducked bansuri music bed. The video is assembled at 1920×1080, 24 fps, at -14 LUFS for YouTube.

The 31 shots, their narration and their prompts live in `shots.py`. `SHOTLIST.md` shows the same list in a readable form.

## What you need

- **Python 3.9+** and **ffmpeg 6+**, both on your PATH.
- **A fal.ai API key** (`FAL_KEY`). The kit uses Seedance 2.0's standard tier, because the fast tier has no 1080p.
- **An ElevenLabs API key** (`ELEVENLABS_API_KEY`) and a deep, calm voice (`ELEVENLABS_VOICE_ID`, which defaults to the premade "Adam"). You can use your own recordings instead.
- **A music bed.** Any royalty-free bansuri or tanpura track works, for example one from the YouTube Audio Library.

## Cost

| Resolution | Seedance seconds | Estimated cost |
| --- | --- | --- |
| 1080p (as requested) | about 333 | about $226 |
| 720p, upscaled to 1080p at render | about 333 | about $100 |

These cover one take of every shot plus the 5-second reference portrait. fal bills Seedance by tokens. The 720p figure matches fal's published $0.3034/s; the 1080p figure is extrapolated from the same token rate. Re-rolls cost extra. Narration is about 3,000 ElevenLabs characters.

## Steps

```bash
pip install -r requirements.txt
export FAL_KEY=...  ELEVENLABS_API_KEY=...  ELEVENLABS_VOICE_ID=...

python make_video.py all --mock     # free dry run: placeholder clips, checks ffmpeg and timing
python make_video.py voice          # narration -> build/vo48/
python make_video.py plan           # fits the shots to 5:00 and prints the cost
python make_video.py ref --yes      # Krishna reference frame -> build/ref/krishna.png  (look at it!)
python make_video.py clips --yes    # 31 Seedance clips, 4 at a time, about 3-5 min each
python make_video.py assemble --music music/bansuri.mp3
```

Everything lands in `out/`:

- `stop_comparing_1080p.mp4`, the finished video
- `captions.srt`, English captions timed to the narration
- `description.txt`, with the title, the description, chapters that match the cut, and tags
- `thumbnail_base.jpg`, a Krishna frame to put the thumbnail text on

Each step caches its output, so if something fails, run the same command again and it resumes.

## Getting it right

- **Check the reference frame before running `clips`.** Every Krishna shot copies its face, crown and clothing. If you don't like it, delete `build/ref/krishna.png` and run `ref` again. You can also drop your own 16:9 artwork at that path.
- **Watch every clip in `build/clips/`.** Re-roll the bad ones with a new seed using `python make_video.py clips --redo d05,e03 --yes`, then run `assemble` again.
- **To use your own voice,** put `<shot id>.mp3` or `.wav` files in `build/vo/` before running `voice`. To redo a single line, delete `build/vo48/<id>.wav`.
- **If the narration is too fast,** delete `build/vo48/`, then run `voice --voice-tempo 0.92` and `plan`.
- **To change words or prompts,** edit `shots.py`, then run `voice` and `plan` again. Keep each line to about 22 words so it fits inside a 15-second clip.
- **720p is cheaper.** To save about half, pass `--resolution 720p` to `plan`, `ref` and `clips`. The final render is still 1080p.

## Uploading

- **Title, description and tags:** take them from `out/description.txt`.
- **Captions:** upload `captions.srt` as English subtitles. They are not burned into the picture by default, so viewers watching an auto-dubbed track don't see English text. Add `--burn-captions` to `assemble` if you want them burned in.
- **Thumbnail:** add the text "YOUR TIME IS COMING" to `thumbnail_base.jpg`.
- **Altered or synthetic content:** answer Yes, because the village and farmer scenes are realistic AI footage.
- **Auto-dubbing:** turn it on in YouTube Studio if your channel has it.
- **Monetization:** write an original story and script for each upload. YouTube's inauthentic-content policy targets channels that mass-produce near-identical videos.

## Running it in a Claude Code cloud session

The environment's network access must allow these hosts:

- `fal.run`, `queue.fal.run`, `rest.fal.ai`, `v3.fal.media` and `v3b.fal.media`
- `falrun.com` and `queue.falrun.com`, which fal falls back to
- `api.elevenlabs.io`

Add `FAL_KEY` and `ELEVENLABS_API_KEY` as environment secrets.
