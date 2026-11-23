# HOW TO TEST CROWD CONTROL YOURSELF

Honest warning: the GDScript has **never been run**. Parts 1 and 2 are known to pass. Parts 3 to 5 are the first real run, so expect some errors. Copy any error text back to me and I will fix it.

## Part 1. Get the code (any computer with Git)

```bash
git clone https://github.com/wigojese/crowd_control.git
```

```bash
cd crowd_control && git checkout claude/affectionate-planck-p2bk56
```

## Part 2. Python checks (needs Python 3 only, about 5 seconds)

```bash
python3 --version
```

```bash
scripts/check_all.sh
```

Pass: the last line is `CHECK_ALL: OK`. This tests the rules, levels, camera, audio, settings and layout on the Python reference. On Windows use Git Bash or WSL.

For the longer 283-check suite:

```bash
python3 -I scripts/stage16_checks.py
```

(about one minute; pass: `STAGE16 RESULT: ALL PASS`).

## Part 3. Run the game on a computer (Godot 4.7.2)

1. Download **Godot 4.7.2 stable** (standard, not .NET) from https://godotengine.org/download/archive/ and unzip it. No install needed.
2. Start Godot, press **Import**, choose `project.godot` in the repo folder, open it. Let it import (first time takes a minute). Errors in the bottom panel: copy them to me.
3. Run the engine tests. Put `godot` on your PATH or use its full path:

```bash
godot --headless --path . --script res://tools/test_runner.gd
```

Pass: every line PASS, no script errors. This is the first time these run: **failures here are expected and useful**.

```bash
godot --headless --path . --quit-after 2
```

Pass: it prints `BOOT_STATE=READY`.

## Part 4. Play the graybox (L01)

The main scene is a blank boot screen. To see the game, in the editor open `src/app/graybox.tscn` and press **F6** (Run Current Scene). You should see the map, dots for walkers, queue numbers and the sign. Keys:

| Key | Does |
|---|---|
| A / B | choose the sign's junction (North Gate / Canal Turn) |
| 1 2 3 4 | point the sign N, E, S, W |
| Space | run / pause |
| R | retry |
| H | high contrast |

Things to try, and what you should see (from the Python model, so the engine should match):
1. Press Space with no sign: most walkers jam at the bridge, you **fail** (fewer than 16 of 20).
2. Retry (R), pick junction B (Canal Turn), press 2 (East), Space: the walkers go around and you **pass**.
3. Retry, try other headings: some pass, some fail. Notice which junction and heading matter.

The goal is 16 of 20 arrived before 0:32. Check that the numbers shown match: no one walks through gaps with no street, retry resets everything.

## Part 5. Compare engine against the reference

```bash
godot --headless --path . --script res://tools/run_level.gd -- res://data/levels/cc_l01_r1.json B E
```

It prints a result and writes events and a replay file. Compare with `data/replays/CC-L01-R1__east_at_canal_turn.json`: `arrived` and `event_hash` should be **2120841323** and 20 arrived. A different hash means the GDScript port differs from the reference: tell me the numbers.

## Part 6. On a phone (needs more setup)

1. Install Android Studio's SDK tools, then in Godot: **Editor > Manage Export Templates** (download 4.7.2 templates), **Project > Export > Add > Android**, set the SDK path in Editor Settings.
2. Enable USB debugging on the phone, plug it in, press the **Remote Debug** (phone) icon top right.
3. Test: drag/tap with one thumb, rotate the sign, pinch, small-screen legibility. Note anything that feels wrong.
4. Turn on **Settings > Developer options > Profile GPU rendering** or use Godot's **Debugger > Monitors** to read frame time. Write down your phone model.

Godot's Android export is one thing I have never tested, so expect to ask for help.

## Part 7. Show it to people

Follow `docs/PLAYTEST.md` with 5 to 10 people. Do not explain the sign. Fill in the grid and send it to me.

## What to send back

Any red error text, the output of Parts 3 and 5, and screenshots of Part 4. That is what unblocks Stage 16 and Stage 17.
