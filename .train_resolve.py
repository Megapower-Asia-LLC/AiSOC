#!/usr/bin/env python3
"""Train conflict resolver for the recurring tracker shapes (session tool, not shipped).

Usage: python3 .train_resolve.py <file> <mode>
  modes:
    union        -> ours + theirs for every hunk
    theirs       -> theirs for every hunk
    roadmap      -> theirs, deduping repeated 'claim-to-gate matrix stands at' paragraphs
Run from the worktree root. Refuses to leave markers behind.
"""
import re
import sys
import pathlib

CONFLICT = re.compile(
    r"^<<<<<<< [^\n]*\n(.*?)(?:^\|\|\|\|\|\|\| [^\n]*\n.*?)?^=======\n(.*?)^>>>>>>> [^\n]*\n",
    re.DOTALL | re.MULTILINE,
)


def merge_checkboxes(ours: str, theirs: str) -> str:
    """Same line set modulo [x]/[ ]: checked wins per line. Falls back to union."""
    ol, tl = ours.splitlines(True), theirs.splitlines(True)
    norm = lambda s: s.replace("- [x]", "- [ ]", 1)
    if len(ol) == len(tl) and all(norm(a) == norm(b) for a, b in zip(ol, tl)):
        return "".join(a if "- [x]" in a else b for a, b in zip(ol, tl))
    return ours + theirs


def merge_matrix(ours: str, theirs: str) -> str:
    """Union of table rows from both sides, then a single trailing non-row block
    (theirs'), for hunks spanning appended matrix rows + the Summary."""
    def split(block: str):
        rows, rest, in_rows = [], [], True
        for line in block.splitlines(True):
            if in_rows and line.startswith("|"):
                rows.append(line)
            else:
                in_rows = False
                rest.append(line)
        return rows, "".join(rest)

    orows, orest = split(ours)
    trows, trest = split(theirs)
    seen, rows = set(), []
    for r in orows + trows:
        if r not in seen:
            seen.add(r)
            rows.append(r)
    return "".join(rows) + (trest if trest.strip() else orest)


def dedupe_matrix_paragraph(text: str) -> str:
    paras = [p for p in text.split("\n\n") if p.strip()]
    firsts = [p for p in paras if p.lstrip().startswith("The claim-to-gate matrix stands at")]
    if len(firsts) > 1:
        return firsts[0] + "\n\n"
    return text


def main() -> None:
    path, mode = sys.argv[1], sys.argv[2]
    p = pathlib.Path(path)
    t = p.read_text()
    out, idx, n = [], 0, 0
    for m in CONFLICT.finditer(t):
        ours, theirs = m.group(1), m.group(2)
        if mode == "union":
            r = ours + theirs
        elif mode == "theirs":
            r = theirs
        elif mode == "roadmap":
            r = dedupe_matrix_paragraph(theirs)
        elif mode == "checkboxes":
            r = merge_checkboxes(ours, theirs)
        elif mode == "matrix":
            r = merge_matrix(ours, theirs)
        else:
            raise SystemExit(f"unknown mode {mode}")
        out.append(t[idx : m.start()])
        out.append(r)
        idx = m.end()
        n += 1
    out.append(t[idx:])
    res = "".join(out)
    if re.search(r"^(<<<<<<< |>>>>>>> |=======$)", res, re.MULTILINE):
        raise SystemExit(f"{path}: markers left behind")
    p.write_text(res)
    print(f"{path}: {n} hunks -> {mode}")


if __name__ == "__main__":
    main()
