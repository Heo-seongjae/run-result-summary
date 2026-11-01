#!/usr/bin/env python3
"""run-result-summary PreToolUse 훅: 결과 파일을 고치거나 밖으로 내보내는 도구 호출을 막는다.

Claude Code가 도구를 쓰기 직전에 {"tool_name": ..., "tool_input": {...}}를 stdin으로 준다.
막을 때는 이유를 stderr에 쓰고 종료 코드 2 (Claude Code가 그 호출을 취소하고 이유를 Claude에게 보여 줌).
통과는 종료 코드 0.

막는 것
  1. 결과 파일 쓰기 · 고치기: field_chain_summary.json, 3_results*/ 아래 (요약은 읽기만 한다)
  2. 같은 경로를 Bash로 지우기 · 옮기기 · 덮어쓰기: rm, mv, cp, sed -i, >, >>, tee
  3. 밖으로 나가는 일: git push
"""

from __future__ import annotations

import json
import re
import sys

RESULT_PATH = re.compile(r"(field_chain_summary\.json|/?3_results[^/\s]*/)")
BASH_WRITE = re.compile(r"(\brm\b|\bmv\b|\bcp\b|\bsed\s+-i\b|\btee\b|>>?)[^;&|]*(field_chain_summary\.json|3_results[^/\s]*/)")
GIT_PUSH = re.compile(r"\bgit\s+push\b")


def block(reason: str) -> None:
    print(f"[run-result-summary guard] 막음: {reason}. 원본 결과는 읽기만 한다 — 필요하면 사용자에게 묻는다.",
          file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    tool = event.get("tool_name", "")
    data = event.get("tool_input", {}) or {}
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = str(data.get("file_path") or data.get("notebook_path") or "").replace("\\", "/")
        if RESULT_PATH.search(path):
            block(f"결과 파일 고치기 ({path})")
    elif tool == "Bash":
        command = str(data.get("command", ""))
        if BASH_WRITE.search(command):
            block("결과 파일을 지우거나 덮어쓰는 명령")
        if GIT_PUSH.search(command):
            block("git push (밖으로 나가는 일은 사용자가 직접)")
    sys.exit(0)


if __name__ == "__main__":
    main()
