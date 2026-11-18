# John Meadows → Hevy

A Claude skill that imports John Meadows (Mountain Dog) training programs from a PDF or pasted text into [Hevy](https://www.hevyapp.com/) routines.

- One Hevy folder per program, with routines named `W1 D1 - Pull`, `W1 D2 - Legs`, …
- His exercise notes copied word for word into each exercise
- Sets, reps, warm-ups, drop sets and supersets mapped to Hevy's set fields
- Asks before creating folders or custom exercises and before changing existing routines, and checks for duplicates first

## Requirements

- A Claude account with Skills enabled
- The **Hevy** connector connected in Claude, so Claude can read and write your routines
- Your Meadows program PDF

## Install

**Claude.ai / Claude desktop app**

1. Download [`john-meadows-hevy.skill`](john-meadows-hevy.skill) from this repo.
2. In Claude, go to **Settings → Capabilities → Skills**.
3. Click **Upload skill** and choose the file you downloaded.
4. Turn the skill on.

**Claude Code**

Copy the `john-meadows-hevy` folder into `~/.claude/skills/`:

```bash
git clone https://github.com/rajlamgaday/john-meadows-hevy-skill.git
cp -r john-meadows-hevy-skill/john-meadows-hevy ~/.claude/skills/
```

## Use

Attach your program PDF and say something like:

> Put this Meadows program in Hevy.

Claude extracts the program and asks you which Hevy exercises to use. It then shows a preview card for each routine, and you tap **Save** on each card, top to bottom. A full program runs 25–35 routines, so expect to use more than one chat. Claude gives you a file to attach so the next chat continues where you left off.

## Disclaimer

This is an unofficial community tool. It isn't affiliated with John Meadows, Mountain Dog Training or Hevy. You need your own copy of the programs.
