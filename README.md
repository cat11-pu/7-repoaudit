# repoaudit

仓库里有一份真实项目源码（`src/packaging`，取自 pypa/packaging，双许可 BSD/Apache，原样保留），
一份九条的规则表（`rules.md`），以及八棵迷你样例树（`fixtures/`，每棵都故意违反特定规则）。
现在的 `audit.py` 是个桩：什么都不检查。

## 你要做的

把 `audit.py` 写成真正的审计脚本，按 `rules.md` 的九条规则扫一个目录，输出格式也照那里写的。

## 跑验收

    python3 check_audit.py

它会拿你的 `audit.py` 跑九个目标：`src/packaging`（必须**零发现**，不许误报真实源码）
与八棵样例树（每棵必须**恰好**报出该报的规则与文件）。全部一致才退出码 0。

## 约束

- 只改 `audit.py`；`check_audit.py`、`rules.md`、`fixtures/`、`src/` 都不要动。
- 只用 Python 标准库（`ast`、`tokenize` 都行），不要引入依赖。
- 规则写粗了会在真实源码上误报，写细了会漏掉样例树——两头都要过。
