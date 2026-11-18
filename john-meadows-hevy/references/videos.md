# Official video links

Only videos uploaded by John Meadows' own channel are allowed:

- Channel: `@mountaindog1` — https://www.youtube.com/@mountaindog1
- Channel ID: `UCmSEdfW3LpEKyLiCDWBDdVQ`

## Order of work

1. Check `video-map.md` first. Use a row only if the exercise and variation match exactly.
2. YouTube links embedded in his official program PDF count as verified (the user approved this): they come from his own document. Pull them from the PDF's link annotations, not its text, and attach each to the exercise whose caption it sits on. Convert `watch?v=ID&list=…&t=…` to `https://youtu.be/ID`. Pasted text and PDF-to-text files lose the URLs; ask for the real PDF.
3. Verify a candidate only if you can actually reach YouTube from this session. Web search rarely returns YouTube pages, and direct YouTube fetches are often blocked. If you can't reach it, don't keep trying: skip videos for the import and tell the user once.
4. A missing video never blocks an exercise. If you can't verify one, leave it out.

## Verifying a video

- Confirm the uploader is the channel above, by its channel ID or handle on the video page itself. A title or search snippet mentioning Meadows isn't proof.
- Reject other channels even when he appears in the video, plus reuploads, compilations, and anything you couldn't confirm.
- Confirm the video shows the intended movement and variation.
- Never guess or construct a video ID.

## Format

Short form only, on its own last line of the notes:

```
Vid: https://youtu.be/VIDEO_ID
```

No timestamps, tracking, or playlist parameters, and no placeholders.

## Links already in the PDF

Keep them in the raw extraction, but don't treat them as verified. Leave unverified ones out of the Hevy notes. If a link sits inside his prose and can't be removed without changing his words, flag it and ask.

## Growing the map

The installed skill is read-only, so you can't edit `video-map.md`. At the end of an import, give the user every newly verified video as rows in the map's table format, so they can add them and repackage the skill.
