"""Run with: python -m unittest scripts/test_validate_verbatim.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_verbatim import check, main  # noqa: E402

SRC = ("1/ Back | Goal: Activation Meadows row: Do some warm up sets. Once there do 3 total sets. "
       "Be sure to maintain good form, this is critical! 3 total work sets or Meadows rows version 2 "
       "These sets are all RPE of 10 Pro Tip Example: • Set 1 – 60 lbs x 8 reps • Set 2 – 75 lbs x 8 reps "
       "I want you to really focus. Dont rush.")
DROPS = ["1/ Back | Goal: Activation Meadows row:", "or Meadows rows version 2"]
GOOD = """Do some warm up sets. Once there do 3 total sets.

Be sure to maintain good form, this is critical!

Work Sets: 3

RPE: 10

Example:
     • Set 1 – 60 lbs x 8 reps
     • Set 2 – 75 lbs x 8 reps

Pro Tip: I want you to really focus. Dont rush."""
VID = "\n\nVid: https://youtu.be/dQw4w9WgXcQ"


class Template(unittest.TestCase):
    def test_approved_template_passes(self):
        self.assertEqual(check(SRC, GOOD, DROPS), [])

    def test_trailing_video_line_passes(self):
        self.assertEqual(check(SRC, GOOD + VID, DROPS), [])

    def test_fixed_spelling_fails(self):
        self.assertTrue(check(SRC, GOOD.replace("Dont", "Don't"), DROPS))

    def test_added_word_fails(self):
        self.assertTrue(check(SRC, GOOD.replace("RPE: 10", "RPE: 10 hard"), DROPS))

    def test_dropped_sentence_fails(self):
        self.assertTrue(check(SRC, GOOD.replace(" Dont rush.", ""), DROPS))

    def test_reorder_inside_line_fails(self):
        self.assertTrue(check(SRC, GOOD.replace("Once there do 3 total sets.", "do 3 total sets. Once there"), DROPS))

    def test_unknown_label_fails(self):
        self.assertTrue(check(SRC, GOOD.replace("Work Sets: 3", "Sets: 3"), DROPS))

    def test_missing_label_fails(self):
        self.assertTrue(check(SRC, GOOD.replace("Pro Tip: ", ""), DROPS))

    def test_undeclared_drop_fails(self):
        self.assertTrue(check(SRC, GOOD, DROPS[:1]))

    def test_drop_not_in_source_fails(self):
        self.assertTrue(check(SRC, GOOD, DROPS + ["Calf program #1"]))

    def test_malformed_video_fails(self):
        self.assertTrue(check(SRC, GOOD + "\n\nVid: https://www.youtube.com/watch?v=dQw4w9WgXcQ", DROPS))

    def test_soft_hyphen_must_be_stripped(self):
        src = SRC.replace("really", "real\x02ly")
        self.assertEqual(check(src, GOOD, DROPS), [])
        self.assertTrue(check(src, GOOD.replace("really", "real\x02ly"), DROPS))

    def test_moving_whole_lines_passes(self):
        a, b = GOOD.split("\n\nWork Sets")
        moved = "Be sure to maintain good form, this is critical!\n\nDo some warm up sets. Once there do 3 total sets.\n\nWork Sets" + b
        self.assertEqual(check(SRC, moved, DROPS), [])


class Cli(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            def write(name, obj):
                p = os.path.join(d, name)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(obj, f)
                return p
            good = write("g.json", [{"id": "a", "original": SRC, "formatted": GOOD, "dropped": DROPS}])
            bad = write("b.json", [{"id": "a", "original": SRC, "formatted": GOOD.upper(), "dropped": DROPS}])
            junk = write("j.json", {"not": "a list"})
            self.assertEqual(main(["--batch", good]), 0)
            self.assertEqual(main(["--batch", bad]), 1)
            self.assertEqual(main(["--batch", junk]), 2)


if __name__ == "__main__":
    unittest.main()
