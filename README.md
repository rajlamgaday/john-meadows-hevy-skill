# John Meadows → Hevy

A Claude skill that imports John Meadows (Mountain Dog) training programs from a PDF or pasted text into [Hevy](https://www.hevyapp.com/) routines.

- One Hevy folder per program, with routines named `W1 D1 - Pull`, `W1 D2 - Legs`, …
- His exercise notes copied word for word into each exercise
- Sets, reps, warm-ups, drop sets and supersets mapped to Hevy's set fields
- Asks before creating folders or custom exercises and before changing existing routines, and checks for duplicates first

## What you need

- A Claude account (claude.ai or the Claude desktop app)
- A Hevy account
- Your Meadows program PDF

## Setup (one time)

**1. Download the skill**

Click [`john-meadows-hevy.skill`](john-meadows-hevy.skill), then click the **download** button (the ↓ arrow near the top right of the file view). Keep the file as it is. Don't unzip it.

**2. Add it to Claude**

1. In Claude, open **Settings → Capabilities**.
2. Make sure **Code execution and file creation** is turned on.
3. Under **Skills**, click **Upload skill** and choose the file you downloaded.
4. Turn on the switch next to **john-meadows-hevy**.

**3. Connect Hevy**

1. In Claude, open **Settings → Connectors**.
2. Find **Hevy** and click **Connect**.
3. Sign in to Hevy and allow access.

## Use

Attach your program PDF and say something like:

> Put this Meadows program in Hevy.

Claude extracts the program and asks you which Hevy exercises to use. It then shows a preview card for each routine, and you tap **Save** on each card, top to bottom. A full program runs 25–35 routines, so expect to use more than one chat. Claude gives you a file to attach so the next chat continues where you left off.

## Disclaimer

This is an unofficial community tool. It isn't affiliated with John Meadows, Mountain Dog Training or Hevy. You need your own copy of the programs.
