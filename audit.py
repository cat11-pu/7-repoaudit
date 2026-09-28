# -*- coding: utf-8 -*-
"""审计脚本（桩：什么都不检查）。按 rules.md 把九条规则实现出来。"""
import sys


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print("桩脚本：还没实现规则，目标是", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
