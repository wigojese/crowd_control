# HOW TO TEST CROWD CONTROL: BEGINNER GUIDE

You need: a Windows or Mac computer, an internet connection, about 30 minutes. You do **not** need to know programming. You will only copy, paste and click.

**Important honesty note.** The game code has never been run by anyone yet. So errors may appear. That is normal and useful. When something goes wrong, do not worry: copy the red text or take a screenshot and send it to me (see "How to report a problem" at the bottom).

Words used here:
- **Terminal**: a window where you type a command and press Enter. Windows calls it PowerShell, Mac calls it Terminal.
- **Folder**: a place on your computer that holds files.
- **Godot**: the free program that runs this game.

---

## STEP 1. Download the game files

1. Open your web browser and go to this address (copy and paste it into the address bar):

   `https://github.com/wigojese/crowd_control/archive/refs/heads/claude/affectionate-planck-p2bk56.zip`

2. If GitHub asks you to sign in, sign in with your GitHub account (the project is yours; it may be private). Then paste the address again.
3. A file ending in `.zip` downloads. Find it in your **Downloads** folder.
4. Unzip it:
   - **Windows:** right-click the file, choose **Extract All...**, then **Extract**.
   - **Mac:** double-click the file.
5. You now have a folder named something like `crowd_control-claude-affectionate-planck-p2bk56`. Move it to your **Desktop** so it is easy to find. Open it: you should see files such as `project.godot`, `README.md` and folders named `docs`, `src`, `data`.

## STEP 2. Download Godot (the program that runs the game)

1. Go to `https://godotengine.org/download/archive/`
2. Find **4.7.2** in the list (it must be exactly 4.7.2 and "stable") and click it.
3. Download the **Standard** version for your computer. Choose **Windows** or **macOS**. Do **not** choose ".NET" and do **not** choose "Android" or "Web".
4. Unzip it the same way as step 1.
   - **Windows:** you get a file like `Godot_v4.7.2-stable_win64.exe`. Move it to your Desktop. You do not install it; you just double-click it.
   - **Mac:** you get `Godot` (an app). Drag it into your **Applications** folder. The first time, right-click it and choose **Open**, then **Open** again, because Mac warns about downloaded apps.

## STEP 3. Open the project in Godot

1. Double-click Godot. A window called **Project Manager** appears.
2. Click **Import** (right side).
3. Click **Browse**, go to the folder from step 1, click the file **`project.godot`**, then **Open**, then **Import & Edit**.
4. Wait. The first time it needs a minute to prepare. The editor opens.
5. Look at the **bottom** of the Godot window. There is a panel with tabs named **Output** and **Debugger**. If you see **red text**, that is an error. Take a screenshot of the whole window (see "How to report a problem") and keep going.

## STEP 4. Play the level (the main test)

1. In the left-bottom panel called **FileSystem**, click the small arrow next to **src**, then **app**.
2. Double-click **graybox.tscn**. (The "graybox" is the plain version of the game.)
3. Press the key **F6** on your keyboard. (Or click the small "play scene" button at the top right, the one with a clapper-board icon.)
4. A game window should open showing: a small map with 7 places, dots that are people walking, and numbers.

If the window does not open or is empty, take a screenshot of the Godot window (including the Output panel at the bottom) and send it to me. That is a valid result for this test.

### How to play

Click inside the game window first (so it listens to your keyboard), then use these keys:

| Key | What it does |
|---|---|
| **A** | Choose the sign's place: North Gate (top) |
| **B** | Choose the sign's place: Canal Turn (left, a bit lower) |
| **1** | Sign points up (north) |
| **2** | Sign points right (east) |
| **3** | Sign points down (south) |
| **4** | Sign points left (west) |
| **Space** | Start / pause the walking |
| **R** | Start over (retry) |
| **H** | High contrast colours on or off |

The goal: at least **16 of 20 people** must reach their place (the School at the bottom left, or the Plaza at the bottom right) before the clock reaches **0:32**.

### Three small experiments

**Experiment 1: no sign.** Do not press A, B or a number. Just press **Space**. Watch. Expected: people crowd up at the narrow bridge in the middle, and you do **not** reach 16. Write down how many arrived.

**Experiment 2: the winning move.** Press **R** to restart. Press **B**, then **2**, then **Space**. Expected: the people spread out and you reach **20 of 20**. Write down the number.

**Experiment 3: your own tries.** Press **R**, try other letters and numbers (for example **A** then **3**). Write down each choice and the result in a note, like "A + 3: 14 arrived".

### What to check and write down

Answer these with Yes / No / Not sure, and add a sentence if something looks wrong:
1. Did the game window open at all?
2. Can you see the sign and tell which way it points?
3. Do the people walk only along the streets (never across empty space)?
4. When you press **R**, is everything reset (score back to zero, people back at the start)?
5. Is any text too small or hard to read?
6. Was anything confusing? (This matters a lot: you are the first person to see it.)

## STEP 5. Run the automatic tests (optional but very useful)

These are checks that run by themselves. You need a terminal.

**Open a terminal inside the project folder:**
- **Windows:** open the project folder in File Explorer, click the address bar at the top, type `powershell`, press Enter. A blue window opens.
- **Mac:** open the **Terminal** app. Type `cd ` (the letters c, d, and a space), then drag the project folder from Finder into the Terminal window, then press Enter.

**Run the test:**
- **Windows:** you must tell it where Godot is. Type this, but replace the path with where your Godot file really is (you can drag the Godot file into the window to paste its path), then press Enter:

  `& "C:\Users\YOUR_NAME\Desktop\Godot_v4.7.2-stable_win64_console.exe" --headless --path . --script res://tools/test_runner.gd`

  (If you only have the file without "_console" in its name, use that one. It still works.)
- **Mac:** type this, then press Enter:

  `/Applications/Godot.app/Contents/MacOS/Godot --headless --path . --script res://tools/test_runner.gd`

What you should see: many lines starting with **PASS**. If you see **FAIL** or red error text, copy **all the text in the window** (select it with the mouse, copy with Ctrl+C on Windows or Cmd+C on Mac) and paste it into our chat. Do not try to fix anything.

## STEP 6. Phone testing

Skip this for now. It needs developer tools that are hard for a first try. Do steps 1 to 5 first and tell me the results. When you are ready, I will guide you through the phone part one click at a time.

## STEP 7. Show it to a friend (optional)

Let 1 or 2 people try step 4 **without explaining anything**. Watch silently and note: what did they press first? Were they confused? Send me your notes.

---

## How to report a problem

Send me, in the chat:
1. **A screenshot.** Windows: press the **Windows key + Shift + S**, drag over the Godot window, then paste into the chat. Mac: press **Command + Shift + 4** and drag over the window; the picture saves to your Desktop.
2. **Red text.** Select it in the Output panel at the bottom of Godot, copy it, and paste it into the chat.
3. **What you did just before**, in one sentence ("I pressed F6 on graybox.tscn").

You cannot break anything. If you get stuck at any step, tell me the step number and what you see on the screen, and I will walk you through it.

## For later (developers only)

Advanced commands (Python checks, comparing results with the reference model) are in `docs/TEST_REPORT.md` and `README.md`.
