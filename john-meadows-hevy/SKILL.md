---
name: "john-meadows-hevy"
description: Import John Meadows (Mountain Dog / mountaindog1) training programs from PDFs or pasted text into Hevy routines, one folder per program, keeping his exercise notes word for word and protecting the user's existing exercises and history. Use this whenever the user shares a Meadows program, asks to load, convert, or set up a Meadows or Mountain Dog program in Hevy, wants routines built from one of his PDFs, or wants to fix or check routines already imported from one, even if they only say "put this program in Hevy".
---

# John Meadows → Hevy

Turns a Meadows program into Hevy routines that match his prescriptions exactly, with his own words in each exercise's notes. Two things matter more than speed: his text stays verbatim, and the user's Hevy account is never damaged. Duplicate exercises split training history, and stray folders or overwritten routines are hard to clean up.

Do only the stages the user asks for. Loading this skill is not permission to write to Hevy.

## Ground rules

- **His words are authoritative.** Keep spelling, punctuation, repetition, and tone exactly. Notes follow the user's approved template (`references/ingestion.md`), which drops layout debris and labels his sidebar data but never changes a word of his.
- **Never invent training data.** No sets, reps, weights, rest, or exercises he didn't prescribe. If something is unclear, flag it and ask.
- **Separate approval for each kind of account change.** Creating a folder, creating each custom exercise, and changing an existing routine each need their own explicit yes. Approval to publish routines covers none of them.
- **No duplicates** of routines, folders, or custom exercises.
- **Fail closed.** An error, timeout, or 429 is never an empty result. Stop, report it, and don't retry in bursts.
- **Report honestly.** A check you didn't perform is UNRESOLVED, not PASS. Never say an import is complete while any write is failed or unverified.

## Workflow

| Stage | What happens | Gate to move on |
|---|---|---|
| 1. Ingest | Extract all programming verbatim (`references/ingestion.md`) | Completeness audit PASS |
| 2. Format | Build notes in the approved template, run `scripts/validate_verbatim.py`, add videos only if verifiable (`references/videos.md`) | Every note passes the checker |
| 3. Prepare | Preflight, folder, duplicate scan, exercise matching, structured sets | Open decisions answered |
| 4. Validate | Run the checks in `references/validation.md` | No FAIL, no unresolved critical item |
| 5. Preview | One `render_hevy_routine` card per routine | User reviews |
| 6. Publish | User saves cards in order (or direct save on request) | Each write confirmed |
| 7. Verify | Re-read saved routines and compare (`references/validation.md`) | Discrepancies reported |

For a full import, run straight through and stop only for approvals or real questions. Report progress as: current stage, done, remaining, blockers, approvals needed. Skip routine-by-routine chatter.

When resuming in a new conversation, re-read Hevy's actual state. Never trust earlier chat history about what was saved.

## Preflight (before any Hevy-dependent step)

Read-only. Skip it only for offline extraction or formatting.

1. `get_user_preferences` succeeds, and `weight_unit` is `lbs` (the API's spelling). If the unit is anything else, report it before preparing weights.
2. `get_hevy_routine_folders` and `get_user_routines` each return page 1.
3. `search_hevy_exercises` returns results.

This proves access only. The folder and routine endpoints cap at 10 items per page, so the full inventory happens once, in Stage 3, not here as well. A preflight from an earlier conversation proves nothing about now.

## Publishing path

`render_hevy_plan` and `create_hevy_plan` take no `folder_id`, so they can't put routines in the program folder. Don't use them here.

- **Default:** call `render_hevy_routine` once per routine with the program's `folder_id`. Nothing saves until the user taps Save. Render in ascending week/day order and tell the user to save top to bottom, because Hevy orders routines by save time.
- **Direct save, only when the user explicitly says to skip the preview:** call `create_hevy_routine` one routine at a time with `folder_id`, confirming each before the next.

If any write errors or times out, follow `references/recovery.md` before doing anything else.

## Folder

One folder per program, named after the program.

- Read every folder page and look for the program, including near-matches ("Pain & Glory" vs "Pain and Glory").
- Reuse a match's `folder_id`. If there's none, ask before calling `create_hevy_routine_folder`. Never borrow an unrelated folder to avoid asking.
- If the existing folder already holds routines, tell the user two things before rendering: new routines land after everything already there (saving W1 into a folder holding Weeks 4–14 puts W1 at the bottom), and whether the existing titles use a different naming scheme from `W{week} D{day}`.

## Routine names and order

Format: `W{week} D{day} - {Focus}` plus an optional ` ({qualifier})`. No leading zeros, no program name. Examples: `W1 D1 - Pull`, `W2 D4 - Push (pump)`. `D` counts training days within the week, skipping OFF days (Mon, Tue, Wed, Fri, Sat = D1–D5). Take the focus from the day's actual exercises (Legs, Push, Pull, or the muscle groups), since his weekly overview pages sometimes mislabel days; take "(pump)" from the overview, the only place it's recorded.

Order is ascending by week, then day, sorted numerically (W10 comes after W9). The last day of the last week should land last in the folder.

## Duplicate check

If the program's folder doesn't exist yet, nothing can be in it: skip the scan.

Otherwise scan all routines once per import with `get_user_routines` (`pageSize: 10`). Read `page_count` from page 1 and fetch every page up to it; don't stop on a short page, since an account with exactly 240 routines has a full last page. Large accounts return each page as a saved file; parse them with a script rather than reading them into context. Keep the routines whose `folder_id` matches. Re-scan only before resuming after a failure.

Keep the whole scan, not just the program folder: it shows which exercise templates the user actually logs, which settles exercise matching below.

A routine is a likely duplicate if its title matches (ignoring case and spacing) or it represents the same week and day under a different title. Stop on that routine, show the existing one, and ask: keep, update, or cancel. If the scan can't complete, don't publish.

## Exercise matching

Search with `search_hevy_exercises` (it takes an array, so batch the queries). Query Meadows' exact wording first ("1 arm barbell row", "Smith machine row"), then generic Hevy names. Generic queries miss the user's customs: "Single Arm Barbell Row" didn't find his custom "1 Arm Barbell row". Match movement, equipment, and variation, not just the name.

When there's a routine scan, check which candidate the user logs in existing routines, especially his other Meadows folders. If one candidate is clearly what he logs for that movement, use it and say so. Otherwise ask, and show in the question which option his past routines use.

- **Several plausible matches with no clear history:** list each with its ID, whether it's custom, and where he's used it, then ask. History lives on whichever one he logs, so a name-based pick can split it. If his answer conflicts with what his past routines use, point that out once before rendering. Reuse the answer for the rest of the import.
- **No match:** stop that exercise, name the closest alternatives without choosing one, and ask. Only create a custom exercise after explicit approval for that specific exercise, and search again right before creating it. `create_custom_exercise` saves to the account immediately, even if the routine is only previewed. Free accounts get 7 custom exercises in total.

## Hevy field mapping

Each exercise has structured fields plus `notes` in the approved template (`references/ingestion.md`). Keep everything in the notes even when it's also in the structured fields.

**Set types:** use only `warmup`, `normal`, and `dropset`, which are confirmed working in this account. Sets "to failure" are `normal`, with his wording in the notes; the user doesn't use the `failure` type.

| Prescription | Fields |
|---|---|
| Fixed reps ("8") | `reps: 8`, `rep_range: null` |
| Range ("8-10") | `rep_range: {start: 8, end: 10}`, `reps: null` |
| No number ("to failure", "max reps") | both null |
| Warm-ups | Every lift gets at least one `warmup` set (timed holds excepted). If his example lists rows before the work sets, each is a warm-up with the row's reps ("60 x 20, 80 x 20, 100 x 10, 125 x 10, 125 x 10" with 2 work sets = warm-ups of 20, 20, 10). Counted feeders ("2 feeder sets of 5") are warm-ups too. Take the largest of the three |
| Drop set | first set `normal`, each drop `dropset`. If he points to his example for how the drop works, take the drop reps from it; weights stay blank |
| Cluster set | first segment `normal`, each later segment `dropset`, same weight unless he says otherwise; counts as one work set. Rest-paused singles ("10 singles, rest 10 seconds") = one `normal` of 1 plus a `dropset` of 1 per remaining single |
| Superset | same `superset_id` on the linked exercises, in his order |
| Partials, rest-pause, forced reps, tempo, bands, holds | notes only, unless the user has approved a mapping |

**Weights:** the tools take `weight_kg`, but the user logs in pounds. Fill it only for a working weight he actually prescribes, never an illustrative example. Convert with `lb × 0.45359237` at full precision; rounding makes 225 lb show as 224.9. Before publishing, confirm `kg ÷ 0.45359237`, rounded to one decimal, equals his pound value.

**Rest:** `rest_seconds` is one value per exercise. His programs set rest by goal phase on a program-wide page ("Rest Breaks"): Activation and pump 2:00, Training explosively 3:00, Supramax pump 2:00, Train from stretch position 1:30. Use the exercise's "Goal" for this; with two goals, the first one listed. An exercise-specific between-set rest ("I want 60 second breaks", "45 seconds between sets") overrides it. Pauses inside a cluster ("rest 20 seconds") are not between-set rest; they stay in the notes. If the program has no rest page and he prescribes nothing, leave it null. Always read the program-wide pages; a pasted single day misses them.

## Whole programs

A full program is 25–35 routines and 200+ exercises. Do the reading, formatting, matching, and checking with scripts over files, and print compact summaries, not raw text. Ask all exercise questions in one batch up front. Then save every validated routine to one JSON file (`[{week, weekday, title, folder_id, routine}]`) and send it to the user before rendering anything.

Each preview card costs roughly 20k tokens of conversation, so one chat holds about one week of cards. When the user starts a new chat with that file attached, skip straight to rendering: run the preflight, re-read the folder to see what's already saved, and render the next unsaved routines in order from the file without re-deriving them. The file is already validated.

## Updating an existing routine

Only with explicit approval for that specific change. `update_hevy_routine` replaces the whole routine, so build the payload from the fetched routine, change only what was approved, and send every exercise, set, note, and the `folder_id`. Anything omitted is deleted. Show a before/after diff first.

## Reference files

- `references/ingestion.md` — extraction scope, layout debris, the approved notes template. Read in Stages 1–2.
- `references/videos.md` — official-channel verification and link format. Read before adding any video.
- `references/video-map.md` — videos already verified. Check it before searching.
- `references/validation.md` — pre-publish checks and post-save verification. Read in Stages 4 and 7.
- `references/recovery.md` — what to do after a failed or uncertain write. Read the moment a write misbehaves.
- `scripts/validate_verbatim.py` — deterministic check that templated notes keep every word of the source. It proves word preservation only, not extraction accuracy, exercise matching, or video ownership.
