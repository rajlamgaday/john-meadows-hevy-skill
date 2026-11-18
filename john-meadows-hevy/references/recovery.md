# After a failed or uncertain write

Hevy has no rollback, and a write that "failed" may have gone through. Retrying blindly is how duplicates happen.

## Any write that errors, times out, or returns something unclear

1. Stop. Don't start the next write.
2. Don't assume it failed. Re-read the relevant data with the read-only tools (`get_user_routines`, `get_hevy_routine_folders`, or `search_hevy_exercises`).
3. If the change is there and correct, mark it done. Don't repeat it.
4. If it's definitely absent, retry once, and only if the original approval still covers it.
5. If you still can't tell, stop and ask the user.
6. Never delete, overwrite, or recreate anything to recover.

On a 429, stop calling Hevy entirely and tell the user. Don't wait and hammer.

## Multi-routine imports

Keep three lists: saved and confirmed, pending, and uncertain. Stop the import at the first unresolved write. To resume, re-scan the folder, then continue from the first routine confirmed missing. Never restart from W1 D1 without checking what already exists.

On the preview path the user does the saving. If they report a save error or skip a card, re-scan before rendering anything again.

## Folders and custom exercises

After an uncertain create, check whether the folder or exercise now exists before doing anything else. Never create a second copy. If you need to try again, get fresh approval.

## Reporting

Tell the user what was confirmed saved, what failed or is uncertain, whether each uncertain change exists in Hevy, what's left, and what you need from them.
