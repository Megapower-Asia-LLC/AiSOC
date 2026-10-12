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

CONFLICT = re.compile(r"<<<<<<< [^\n]*\n(.*?)(?:\|\|\|\|\|\|\| [^\n]*\n.*?)?=======\n(.*?)>>>>>>> [^\n]*\n", re.DOTALL)


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
        else:
            raise SystemExit(f"unknown mode {mode}")
        out.append(t[idx : m.start()])
        out.append(r)
        idx = m.end()
        n += 1
    out.append(t[idx:])
    res = "".join(out)
    if "<<<<<<<" in res or ">>>>>>>" in res:
        raise SystemExit(f"{path}: markers left behind")
    p.write_text(res)
    print(f"{path}: {n} hunks -> {mode}")


if __name__ == "__main__":
    main()
