# -*- coding: utf-8 -*-
"""验收：拿被测的 audit.py 跑九个目标，逐目标比对发现集合。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = {
 "src/packaging": [],
 "fixtures/f_syntax": [
  "E_SYNTAX pkg.py"
 ],
 "fixtures/f_star": [
  "E_STAR pkg.py"
 ],
 "fixtures/f_tab": [
  "E_TAB pkg.py"
 ],
 "fixtures/f_noeof": [
  "E_NOEOF pkg.py"
 ],
 "fixtures/f_types": [
  "E_NOARG pkg.py",
  "E_NORET pkg.py"
 ],
 "fixtures/f_eval": [
  "E_EVAL pkg.py"
 ],
 "fixtures/f_bare": [
  "E_BAREEXC pkg.py"
 ],
 "fixtures/f_blank": [
  "E_BLANK pkg.py"
 ]
}


def run_audit(target):
    res = subprocess.run([sys.executable, os.path.join(HERE, "audit.py"), target],
                         cwd=HERE, capture_output=True, text=True)
    lines = [line.strip() for line in (res.stdout or "").splitlines() if line.strip()]
    return sorted(lines), res.returncode


def main():
    bad = 0
    for target in TARGETS:
        want = sorted(TARGETS[target])
        got, code = run_audit(os.path.join(HERE, target))
        if got == want:
            print("通过", target, "=", len(got), "条发现")
        else:
            bad += 1
            print("不过", target, "期望", want, "实际", got)
    print("通过率 %d/%d" % (len(TARGETS) - bad, len(TARGETS)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
