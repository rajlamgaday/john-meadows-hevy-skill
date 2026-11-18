"""Parse a Mountain Dog 2.0 program PDF (Odin Force layout) into days -> exercises with main/side/tip text and video links, using page geometry. Starting point: adapt per program; check output against page images."""
import json
import re
import sys

import pdfplumber

PDF = sys.argv[1] if len(sys.argv) > 1 else "program.pdf"
DAY_RE = re.compile(r"^WEEK (\d+) - (MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$")
EX_RE = re.compile(r"^(\d+)/\s*(.+?)\s*\|\s*(.+)$")


def regions(p):
    boxes = [c for c in list(p.curves) + list(p.rects)
             if c["x1"] > 760 and (c["x1"] - c["x0"]) > 250 and 60 < (c["bottom"] - c["top"]) < 400 and c["top"] > 150]
    edges = [e for e in p.edges if abs(e["x0"] - e["x1"]) < 1 and e["height"] > 40 and 300 < e["x0"] < 700]
    dividers = [e for e in edges if not any(abs(e["x0"] - b["x0"]) < 4 and b["top"] - 10 < e["top"] < b["bottom"] for b in boxes)]
    return boxes, dividers


def classify(w, boxes, dividers):
    for i, b in enumerate(boxes):
        if b["x0"] - 2 <= w["x0"] and b["top"] - 2 <= w["top"] <= b["bottom"]:
            return f"tip{i}"
    for d in dividers:
        if d["top"] - 10 <= w["top"] <= d["bottom"] + 10 and w["x0"] >= d["x0"] - 1:
            return "side"
    return "main"


def lines_of(words):
    """Group words into rows (by top) then into lines; keep fonts."""
    rows = []
    for w in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
        if rows and abs(rows[-1][0]["top"] - w["top"]) < 3:
            rows[-1].append(w)
        else:
            rows.append([w])
    out = []
    for r in rows:
        r.sort(key=lambda w: w["x0"])
        out.append({"top": r[0]["top"], "x0": r[0]["x0"], "text": " ".join(w["text"] for w in r),
                    "bold": "SemiBold" in r[0]["fontname"] or "Bold" in r[0]["fontname"],
                    "size": r[0]["size"], "font": r[0]["fontname"]})
    return out


def main():
    pdf = pdfplumber.open(PDF)
    days, cur_day, cur_ex = [], None, None
    for pi in range(int(sys.argv[2]) if len(sys.argv) > 2 else 0, len(pdf.pages)):
        p = pdf.pages[pi]
        words = [w for w in p.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
                 if 5 < w["top"] < 985]
        boxes, dividers = regions(p)
        title = [w for w in words if "Oswald" in w["fontname"]]
        title_text = " ".join(w["text"] for w in sorted(title, key=lambda w: (round(w["top"]), w["x0"])))
        m = DAY_RE.match(title_text.strip())
        if title and not m:          # week overview / OFF day page: ends the current day
            cur_day, cur_ex = None, None
            continue
        if m:
            cur_day = {"week": int(m.group(1)), "weekday": m.group(2).title(), "page": pi + 1, "exercises": [], "debris": []}
            days.append(cur_day)
            cur_ex = None
        if cur_day is None:
            continue
        by_region = {}
        for w in words:
            if "Oswald" in w["fontname"]:
                continue
            by_region.setdefault(classify(w, boxes, dividers), []).append(w)
        items = []
        for reg, ws in by_region.items():
            for ln in lines_of(ws):
                ln["region"] = reg
                items.append(ln)
        links = [{"top": h["top"], "x0": h["x0"], "bottom": h["bottom"], "x1": h["x1"], "uri": h["uri"]}
                 for h in p.hyperlinks if "youtu" in h["uri"]]
        headers = sorted([it for it in items if it["region"] == "main" and it["size"] >= 17 and EX_RE.match(it["text"])],
                         key=lambda it: it["top"])
        day_table_bottom = max([w["bottom"] for w in title] + [0]) + 90 if m else -1
        carried = cur_ex
        page_ex = []
        for it in sorted(items, key=lambda it: it["top"]):
            if it in headers:
                g = EX_RE.match(it["text"])
                cur_ex = {"num": int(g.group(1)), "muscle": g.group(2), "name": g.group(3).strip(), "page": pi + 1,
                          "main": [], "side": [], "tips": {}, "links": []}
                cur_day["exercises"].append(cur_ex)
                page_ex.append((it["top"], cur_ex))
                continue
            if m and it["top"] < (headers[0]["top"] if headers else 9999) and it["top"] < day_table_bottom:
                cur_day["debris"].append(it["text"])
                continue
            if cur_ex is None:
                cur_day["debris"].append(it["text"])
                continue
            owner = cur_ex  # lines are processed top-down, so the latest header above owns them
            if it["region"].startswith("tip"):
                owner["tips"].setdefault(f"{pi + 1}:{it['region']}", []).append(it["text"])
            else:
                owner[it["region"]].append(it["text"])
        for h in links:
            above = [e for t, e in page_ex if t <= h["top"] + 2]
            owner = above[-1] if above else carried
            if owner is not None:
                cap = " ".join(w["text"] for w in words if h["x0"] - 2 <= w["x0"] <= h["x1"] and h["top"] - 3 <= w["top"] <= h["bottom"] + 1)
                owner["links"].append({"uri": h["uri"], "caption": cap})
    json.dump(days, open("parsed.json", "w"), ensure_ascii=False, indent=1)
    print("days", len(days), "exercises", sum(len(d["exercises"]) for d in days))


if __name__ == "__main__":
    main()
