# Ingestion and notes formatting (Stages 1–2)

## What to extract

Everything that tells the user how to train, word for word:

- Every workout, exercise, and instruction
- Schedules, splits, and which day is which
- Sets, reps, weights, rest, intensity techniques, execution cues
- Week-specific progression and program-wide rules that change how workouts are done
- Training examples and pro tips

Leave out general intros, biography, nutrition and supplement advice, motivation, and philosophy that doesn't change a prescription.

## PDFs

1. Get the page count and look at every page. Scanned pages, tables, and text inside images need visual inspection.
2. Extract each in-scope section completely, keeping page references.
3. Keep an untouched copy of the raw extraction; formatting works on a copy.
4. Never reconstruct unreadable text. Mark it and ask.

Completeness audit before leaving Stage 1: page count, every page inspected, every workout and exercise accounted for, uncertainties listed. Status is PASS, UNRESOLVED (couldn't read or verify something), or FAIL (known content skipped). A matching page count doesn't prove the text is exact.

## Mountain Dog 2.0 layout (Odin Force, Colossus era)

Newer PDFs put the exercise name in the header ("1/ Upper legs | Lying leg curls"), the prose in a left column, his example in a right column behind a vertical divider, Pro Tips in dark boxes, and these lines under the prose: "N total work sets", a video caption, "These sets are … RPE of X", "Goal – <phase>". Read the real PDF with pdfplumber and split columns by geometry: the divider's x-position varies by page, and Pro Tip boxes are filled shapes reaching the right edge. `scripts/mountain_dog_pdf.py` does this and is a starting point for the next program.

- **Goal line:** drop it from the notes (declared drop); it sets the rest phase. Coaching text that follows the phase on the same line stays.
- **Example label:** keep his sentence ("This is an example of what it could look like:", sometimes "…would look like/ what I did:") as the label, with his rows as indented bullets.
- **"Note:" lines** stay, as their own paragraph after RPE.
- **Line-break hyphens** ("De- / scend") are layout: rejoin them unless the hyphenated form appears mid-line elsewhere in the program. List the joins for a quick review.
- **Watermarks** ("Downloaded by…", document IDs) and OFF-day or overview pages are debris.

## Layout debris

His PDFs have a sidebar, and both PDF extraction and pasted text interleave it with the main column. Expect these, and treat them as layout rather than coaching:

- **Day overview counts** ("4 exercises 1 exercise 6 exercises", "12 sets 4 sets 2 sets 18 sets"): leave out of the notes.
- **Exercise header and name** ("1/ Back | Goal: Activation and start pump Meadows row:"): leave out; the routine and the exercise template already carry them.
- **Video captions** ("Meadows rows version 2", "1 arm barbell rows with IFBB Pro Andrew Hudson"): leave out. They often land under the wrong exercise.
- **Page numbers** on their own lines, and the day header block ("WEEK 1 - TUESDAY Chest 4 exercises 10 sets…"), which sits at the bottom of each day's first page: leave out.
- **Soft hyphens:** PDF-to-text output marks hyphenation points with an invisible `\x02` (or U+00AD) inside words ("en\x02gage"). Strip them so the word is whole; they're layout, not his spelling. The checker fails any note that still has one.
- **Stray numbers fused to a header** ("(failure) 103/ Back"): leave out and tell the user. Never attach them to an exercise, because a loose "10" reads as reps.

Sidebar pieces also arrive out of order. Pro Tips are grouped at the bottom of each page, after the last exercise on it, so match each tip to the exercise on that page it's about ("Tilt pinky down" goes with side laterals, not front raises), keeping his words.

## Notes template

The user's approved format. Use it for every exercise and include only the sections his text has:

```
<coaching prose, paragraph 1>

<coaching prose, paragraph 2>

Work Sets: 3

RPE: 10

Example:
     • Warm up 1 – 25 x 12 for 2 sets
     • Set 1 – 60 lbs x 8 reps

Pro Tip: <his tip text>
```

- **Prose:** his coaching text, word for word, in short paragraphs split where the topic shifts (setup, then form or failure notes). Never one sentence per line.
- **Work Sets:** from "N total work sets", as `Work Sets: N`.
- **RPE:** from "These sets are all RPE of X …", as `RPE: X …`. Keep any words that follow the number on the same line ("RPE: 8-10 – it increases each set.").
- **Example:** the label, then each bullet on its own line indented five spaces.
- **Pro Tip:** the label, a space, then the tip text. Goes last.
- **Loose sidebar lines** that fit none of these ("You may be tempted to add more sets…") go on their own line after RPE.
- **Video:** a verified `Vid:` line goes at the very end.

Everything else is fixed: no added, removed, replaced, or reordered words inside a line; no spelling, grammar, or punctuation fixes; no new labels beyond the four above.

## Check every note with the script

```
python scripts/validate_verbatim.py --batch pairs.json
```

`pairs.json` is a list of `{"id", "original", "formatted", "dropped"}`. `original` is that exercise's raw source text; `dropped` lists the exact source strings you left out (header and name, captions). The script fails the note if any word was added, changed, or lost, if a line isn't an unbroken run of his words, if a declared drop isn't in the source, or if label counts don't match the sidebar phrases. A non-zero exit means fix and re-run. Never call text validated without running it.

Tell the user what you dropped beyond headers and captions, such as stray numbers or overview counts.
