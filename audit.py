# -*- coding: utf-8 -*-
"""按 rules.md 审计目录中的 Python 文件。"""

import sys
import ast
import os
from pathlib import Path


def find_issues(path, relative_path):
    data = path.read_bytes()
    findings = set()

    lines = data.splitlines()
    blank_run = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_run += 1
            if blank_run >= 3:
                findings.add("E_BLANK")
        else:
            blank_run = 0

        indentation = line[: len(line) - len(line.lstrip(b" \t"))]
        if b"\t" in indentation:
            findings.add("E_TAB")

    if data and not data.endswith(b"\n"):
        findings.add("E_NOEOF")

    try:
        tree = ast.parse(data, filename=str(path))
    except (SyntaxError, ValueError):
        findings.add("E_SYNTAX")
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                findings.add("E_STAR")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                findings.add("E_NORET")

            arguments = node.args
            parameters = (
                arguments.posonlyargs
                + arguments.args
                + arguments.kwonlyargs
            )
            if arguments.vararg is not None:
                parameters.append(arguments.vararg)
            if arguments.kwarg is not None:
                parameters.append(arguments.kwarg)

            for parameter in parameters:
                if parameter.arg not in ("self", "cls") and parameter.annotation is None:
                    findings.add("E_NOARG")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                findings.add("E_EVAL")

        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.add("E_BAREEXC")

    return findings


def iter_python_files(root):
    for directory, directory_names, file_names in os.walk(root):
        directory_names.sort()
        file_names.sort()
        directory_path = Path(directory)
        for file_name in file_names:
            if file_name.endswith(".py"):
                path = directory_path / file_name
                yield path, path.relative_to(root).as_posix()


def audit(root):
    findings = []
    for path, relative_path in iter_python_files(Path(root)):
        for code in find_issues(path, relative_path):
            findings.append((code, relative_path))

    return sorted(findings)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    findings = audit(target)
    if findings:
        sys.stdout.write("\n".join(f"{code} {path}" for code, path in findings) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
