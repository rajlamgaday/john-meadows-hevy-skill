# Validation (Stage 4) and post-save verification (Stage 7)

Give every check one status: **PASS** (verified), **FAIL** (confirmed discrepancy), or **UNRESOLVED** (couldn't verify). A check you didn't perform is UNRESOLVED. Say which checks were mechanical (script, arithmetic, ID comparison) and which were by eye.

## Before publishing — per routine

1. **Exercise count:** every prescribed exercise present, none duplicated.
2. **Exercise order:** matches the source.
3. **Exercise identity:** each template ID is the intended movement, equipment, and variation, and the one the user chose when several matched.
4. **Warm-up sets:** count and `warmup` type match where he gives a count.
5. **Working sets:** count matches. Cluster segments and drops count as part of one work set.
6. **Reps:** `reps` for fixed counts, `rep_range` for ranges, both null where he gives no number.
7. **Set types:** only `warmup`, `normal`, `dropset`; failure sets are `normal`.
8. **Weights:** only prescribed working weights are filled, and each `weight_kg` converts back to his exact pound value.
9. **Rest:** `rest_seconds` matches a single prescribed rest; null where none is prescribed or it varies.
10. **Supersets:** the right exercises share a `superset_id`, in his order.
11. **Notes:** every note follows the approved template and passed `scripts/validate_verbatim.py` with its declared drops.
12. **Progression:** week-specific changes are in the right weeks' routines.
13. **Videos:** every `Vid:` line is from the official channel and the matching movement.
14. **Name:** follows `W{week} D{day} - {Focus} ({qualifier})`.
15. **Folder:** the correct existing folder, or one the user approved creating.
16. **Duplicates:** no existing routine for the same week and day in the folder (or the folder is new).

A routine with any FAIL, or an unresolved item that changes the workout, isn't published. Fix it and re-check. Ask the user only about genuine ambiguities in his prescription, not about checks you can settle yourself.

A program the user already approved for publishing doesn't need per-routine approval.

## After saving (Stage 7)

Re-read the folder's routines with `get_user_routines` and compare each against what was validated:

- It's in the right folder, with the right title.
- The routine order in the folder matches week/day order.
- Exercises, sets, types, reps, and rest match.
- Weights display back as his pound values.
- Notes are intact; Hevy shouldn't truncate them, but check the ends.

Report anything that doesn't match, plus anything you couldn't verify. Only call the import complete once this passes.
