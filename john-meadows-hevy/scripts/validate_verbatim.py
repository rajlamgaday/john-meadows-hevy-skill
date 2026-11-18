#!/usr/bin/env python3
"""Check that formatted exercise notes keep Meadows' words exactly.

The notes template moves his sidebar data into labeled lines and drops
layout debris, so this does not demand identical order. It enforces:

1. Every word in the formatted notes comes from the source, and every source
   word appears in the formatted notes, except:
   - declared drops (header, exercise name, video captions): each must exist
     in the source exactly once and is removed before comparing;
   - sidebar boilerplate, which turns into labels:
       "N total work sets" / "1 total work set"       -> "Work Sets: N"
       "These sets are (all|an) RPE of X", "This set is
        RPE of X", or a bare "RPE 8-11"               -> "RPE: X"
       "Example:"                     -> "Example:"
       "Pro Tip"                      -> "Pro Tip:"
2. Every formatted line, with its label removed, is an unbroken run of words
   from the source. Lines can move as blocks; words inside a line cannot.
3. Each label appears as many times as its boilerplate does in the source.
4. Trailing "Vid: https://youtu.be/<11-char id>" lines are allowed, last.
5. Bullet glyphs are formatting and ignored on both sides.

Usage:
    python validate_verbatim.py --batch pairs.json
pairs.json: [{"id": "...", "original": "...", "formatted": "...", "dropped": ["..."]}]

Exit 0 when all pass, 1 when any fail, 2 on bad input. This proves word
preservation only; it doesn't prove the source matches the PDF.
"""
import argparse
import json
import re
import sys
from collections import Counter

VID_LINE = re.compile(r"^Vid: https://youtu\.be/[A-Za-z0-9_-]{11}$")
LABELS = {"Work Sets:": "work", "RPE:": "rpe", "Example:": "example", "Pro Tip:": "tip"}
BOILERPLATE = {  # label kind -> source phrasings removed when the label is used
    "work": [["total", "work", "sets"], ["total", "work", "set"]],
    "rpe": [["These", "sets", "are", "all", "an", "RPE", "of"], ["These", "work", "sets", "are", "an", "RPE", "of"],
            ["These", "sets", "are", "all", "RPE", "of"], ["These", "sets", "are", "an", "RPE", "of"],
            ["These", "sets", "are", "RPE", "of"], ["This", "set", "is", "an", "RPE", "of"],
            ["This", "set", "is", "RPE", "of"],
            ["RPE", "<number>"]],  # bare "RPE 8-11": only when a number follows
    "example": [["Example:"]],
    "tip": [["Pro", "Tip"]],
}


def _match(tokens, i, run):
    if run[-1] == "<number>":
        return (i + 1 < len(tokens) and tokens[i] == run[0]
                and re.match(r"^\d", tokens[i + 1]) is not None)
    return tokens[i:i + len(run)] == run


def find_boilerplate(tokens, runs):
    """Positions of non-overlapping boilerplate phrases, longest phrasing first."""
    hits, used = [], set()
    for run in sorted(runs, key=len, reverse=True):
        width = 1 if run[-1] == "<number>" else len(run)
        for i in range(len(tokens)):
            span = set(range(i, i + width))
            if not (span & used) and _match(tokens, i, run):
                hits.append((i, width))
                used |= span
    return hits


def remove_run(tokens, run):
    """Remove the first occurrence of a contiguous token run. Returns (tokens, found)."""
    n = len(run)
    for i in range(len(tokens) - n + 1):
        if tokens[i:i + n] == run:
            return tokens[:i] + tokens[i + n:], True
    return tokens, False


def count_run(tokens, run):
    n = len(run)
    return sum(tokens[i:i + n] == run for i in range(len(tokens) - n + 1))


def has_run(tokens, run):
    return count_run(tokens, run) > 0


# PDF-to-text soft hyphens (\x02, U+00AD) sit inside words at line-break points.
# They are layout, not his writing: removed from both sides, and reported if left in notes.
SOFT_HYPHENS = re.compile("[\x02\u00ad]")
BULLET = re.compile("•")


def check(original, formatted, dropped=()):
    problems = []
    if SOFT_HYPHENS.search(formatted):
        problems.append("notes still contain PDF soft-hyphen characters (\\x02 / U+00AD); strip them")
    original, formatted = SOFT_HYPHENS.sub("", original), SOFT_HYPHENS.sub("", formatted)
    # Bullets are formatting: the template may add them to his unbulleted example lines.
    original, formatted = BULLET.sub(" ", original), BULLET.sub(" ", formatted)
    dropped = [SOFT_HYPHENS.sub("", d) for d in dropped]
    src = original.split()

    for d in dropped:
        run = d.split()
        if count_run(src, run) != 1:
            problems.append(f"declared drop not found exactly once in source: {d!r}")
        else:
            src, _ = remove_run(src, run)

    lines = formatted.rstrip().split("\n")
    while lines and lines[-1].strip().startswith("Vid:"):      # one or more trailing video lines
        if not VID_LINE.match(lines[-1].strip()):
            problems.append(f"malformed video line: {lines[-1].strip()!r}")
        lines = lines[:-1]
    if any(l.strip().startswith("Vid:") for l in lines):
        problems.append("video lines must come last")

    labels = Counter()
    body_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        for label, kind in LABELS.items():
            if s.startswith(label):
                labels[kind] += 1
                s = s[len(label):].strip()
                break
        if s:
            body_lines.append(s)

    # Source boilerplate must match label counts; remove it before comparing words.
    for kind, runs in BOILERPLATE.items():
        hits = find_boilerplate(src, runs)
        if len(hits) != labels[kind]:
            label = next(k for k, v in LABELS.items() if v == kind)
            problems.append(f"{label!r} used {labels[kind]}x but its source phrase occurs {len(hits)}x")
        drop = {j for i, w in hits for j in range(i, i + w)}
        src = [t for j, t in enumerate(src) if j not in drop]

    scoped = list(src)
    for s in body_lines:
        if not has_run(scoped, s.split()):
            problems.append(f"line is not an unbroken run of source words: {s[:80]!r}")

    out = [t for s in body_lines for t in s.split()]
    missing = Counter(src) - Counter(out)
    added = Counter(out) - Counter(src)
    if missing:
        problems.append(f"source words missing: {dict(missing)}")
    if added:
        problems.append(f"words not in source: {dict(added)}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--batch", required=True, help="JSON list of {id, original, formatted, dropped?}")
    args = ap.parse_args(argv)
    try:
        with open(args.batch, encoding="utf-8") as f:
            pairs = json.load(f)
        assert isinstance(pairs, list) and all({"id", "original", "formatted"} <= p.keys() for p in pairs)
    except (OSError, ValueError, AssertionError) as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2

    failures = 0
    for p in pairs:
        problems = check(p["original"], p["formatted"], p.get("dropped", []))
        if problems:
            failures += 1
            print(f"FAIL  {p['id']}")
            for pr in problems:
                print(f"  - {pr}")
        else:
            print(f"PASS  {p['id']}")
    print(f"\n{len(pairs) - failures}/{len(pairs)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
