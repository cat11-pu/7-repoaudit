# -*- coding: utf-8 -*-
"""按 rules.md 的九条规则审计目录下所有 .py 文件。"""
import ast
import os
import sys


def check_text(data):
    """基于原始文本的检查：E_TAB / E_NOEOF / E_BLANK。"""
    findings = set()
    if data and not data.endswith(b"\n"):
        findings.add("E_NOEOF")

    blank_run = 0
    for raw in data.splitlines():
        line = raw.decode("utf-8", "replace")
        stripped = line.lstrip()
        if stripped:
            indent = line[: len(line) - len(stripped)]
            if "\t" in indent:
                findings.add("E_TAB")
            blank_run = 0
        else:
            blank_run += 1
            if blank_run >= 3:
                findings.add("E_BLANK")
    return findings


def check_ast(tree):
    """基于 AST 的检查（文件可解析时才跑）。"""
    findings = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.names and any(alias.name == "*" for alias in node.names):
                findings.add("E_STAR")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                findings.add("E_NORET")

            arguments = node.args
            all_args = (
                arguments.posonlyargs
                + arguments.args
                + arguments.kwonlyargs
            )
            extra = [arguments.vararg, arguments.kwarg]
            for arg in all_args + [a for a in extra if a is not None]:
                if arg.arg in ("self", "cls"):
                    continue
                if arg.annotation is None:
                    findings.add("E_NOARG")

        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                findings.add("E_EVAL")

        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.add("E_BAREEXC")

    return findings


def audit_file(path):
    with open(path, "rb") as fh:
        data = fh.read()

    findings = check_text(data)
    try:
        tree = ast.parse(data)
    except SyntaxError:
        findings.add("E_SYNTAX")
    else:
        findings |= check_ast(tree)
    return findings


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = set()
    for root, _dirs, files in os.walk(target):
        for name in files:
            if not name.endswith(".py"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, target)
            for code in audit_file(full):
                results.add((code, rel))

    for code, rel in sorted(results):
        print("%s %s" % (code, rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
