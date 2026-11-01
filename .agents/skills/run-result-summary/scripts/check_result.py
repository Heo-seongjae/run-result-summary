#!/usr/bin/env python3
"""run-result-summary 검사 (check_result.py).

입력 검사: field_chain_summary.json에 요약에 필요한 키가 있고 값이 말이 되는지 본다.
출력 검사(--summary를 주면): 요약표가 5줄 꼴을 지키고, 표의 숫자가 모두 그 JSON에 있는 값인지 본다.
하나라도 FAIL이면 종료 코드 1.

    python check_result.py --input <field_chain_summary.json> [--summary <요약.md>] [--json out.json]

읽기만 한다. 아무 파일도 고치지 않는다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CONNECTORS = 84
VALUE_CELL_MAX = 40               # 값 칸 글자 수 상한 (설명 문장이 들어가면 넘는다)
ROWS = ["조건", "짝 (간선)", "찾은 연결재", "상면 중심 오차 (mm)", "카메라 위치 오차 (mm)"]
REQUIRED = [                      # 요약표에 들어가는 값. 없으면 표에 "파일에 없음"이어야 한다
    "observation_count_by_route",
    "endpoints.accepted_edge_count",
    "endpoints.accepted_false_edge_count",
    "spatial_reassociation.final_unique_pure_connector_count",
    "spatial_reassociation.final_mixed_cluster_count",
    "spatial_reassociation.top_centre_error_mm.min",
    "spatial_reassociation.top_centre_error_mm.median",
    "spatial_reassociation.top_centre_error_mm.max",
    "pnp_pose_error.position_median_mm",
    "pnp_pose_error.position_max_mm",
]
MISSING = object()
NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, group: str, name: str, ok: bool, detail: str = "", warn: bool = False) -> bool:
        status = "PASS" if ok else ("WARN" if warn else "FAIL")
        self.rows.append({"group": group, "check": name, "status": status, "detail": detail})
        return ok

    @property
    def failed(self) -> list[dict]:
        return [r for r in self.rows if r["status"] == "FAIL"]


def get(data: dict, dotted: str):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return MISSING
        node = node[part]
    return node


def leaf_numbers(node) -> set[float]:
    """JSON 안의 모든 숫자 (표에 쓸 수 있는 값)."""
    if isinstance(node, bool):
        return set()
    if isinstance(node, (int, float)):
        return {round(float(node), 3)}
    if isinstance(node, dict):
        node = list(node.values())
    if isinstance(node, list):
        return set().union(*(leaf_numbers(v) for v in node)) if node else set()
    return set()


def check_input(c: Checks, path: Path, data: dict) -> list[str]:
    missing = [k for k in REQUIRED if get(data, k) is MISSING or get(data, k) is None]
    c.add("입력", "필수 값", not missing, "모두 있음" if not missing else "없음: " + ", ".join(missing))

    counts = {k: get(data, k) for k in REQUIRED[1:5]}
    bad = [f"{k}={v}" for k, v in counts.items() if v is not MISSING and not (isinstance(v, int) and v >= 0)]
    c.add("입력", "개수는 0 이상 정수", not bad, "; ".join(bad) or "이상 없음")
    edges, false = counts["endpoints.accepted_edge_count"], counts["endpoints.accepted_false_edge_count"]
    if isinstance(edges, int) and isinstance(false, int):
        c.add("입력", "틀린 간선 ≤ 간선", false <= edges, f"{false} ≤ {edges}")
    found = counts["spatial_reassociation.final_unique_pure_connector_count"]
    if isinstance(found, int):
        c.add("입력", f"찾은 연결재 ≤ {CONNECTORS}", found <= CONNECTORS, f"{found}/{CONNECTORS}")

    for block in ("spatial_reassociation.top_centre_error_mm",):
        d = get(data, block)
        if isinstance(d, dict):
            order = [d.get(k) for k in ("min", "median", "p95", "max") if isinstance(d.get(k), (int, float))]
            c.add("입력", "오차 최소 ≤ 중앙 ≤ p95 ≤ 최대", order == sorted(order) and all(v >= 0 for v in order),
                  " ≤ ".join(f"{v:.3f}" for v in order))

    photos = get(data, "observation_count_by_route")
    if isinstance(photos, dict):
        c.add("입력", "사진 2장 이상", len(photos) >= 2, f"{len(photos)}장")

    folder = path.parent.name
    fc = get(data, "frame_complete_band_rule")
    c.add("입력", "폴더 이름 ↔ 화면 안 완전 투영", ("framecomplete" in folder) == (fc not in (None, MISSING)),
          f"폴더 {folder}, frame_complete_band_rule {'null' if fc in (None, MISSING) else '있음'}")
    pos = get(data, "pnp_pose_error.position_max_mm")
    if isinstance(pos, (int, float)):
        control = "truthpose_control" in folder
        c.add("입력", "폴더 이름 ↔ 카메라 자세", (pos == 0) == control,
              f"{'대조군(촬영 자세)' if control else '마커 PnP'} 폴더, 위치 오차 최대 {pos:.3f} mm")
    gate = get(data, "observation_gate.node_gate")
    c.add("입력", "노드 게이트 값", gate is not MISSING, "있음" if gate is not MISSING else "파일에 없음 — 표에 그대로 적는다",
          warn=True)
    return missing


def parse_table(text: str) -> tuple[list[list[str]], int]:
    tables, current = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            current.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    rows = [r for r in tables[0][2:]] if tables else []
    return rows, len(tables)


def check_summary(c: Checks, data: dict, text: str, missing: list[str]) -> None:
    rows, n_tables = parse_table(text)
    c.add("출력", "표 하나", n_tables == 1, f"표 {n_tables}개")
    names = [r[0].replace("**", "") for r in rows]
    c.add("출력", "5줄 · 항목 순서", names == ROWS, " / ".join(names) or "표 없음")
    if not rows:
        return

    allowed = leaf_numbers(data) | {float(CONNECTORS)}
    photos = get(data, "observation_count_by_route")
    if isinstance(photos, dict):
        allowed |= {float(len(photos))} | {float(i) for i in range(1, len(photos) + 1)}   # 사진 수, R1–Rn
    invented = []
    for r in rows:
        value = r[1] if len(r) > 1 else ""
        for token in NUMBER.findall(value.replace(",", "")):
            if round(float(token), 3) not in allowed:
                invented.append(f"{r[0]}: {token}")
    c.add("출력", "표 숫자가 모두 JSON 값", not invented, "; ".join(invented) or "이상 없음")

    dist_bad = []
    forms = {3: (r"\d+\.\d{3}\s*–\s*\d+\.\d{3}\s*\(중앙\s*\d+\.\d{3}", "최소 – 최대 (중앙 X)", "top_centre_error_mm"),
             4: (r"^중앙\s*\d+\.\d{3}\s*·\s*최대\s*\d+\.\d{3}", "중앙 X · 최대 Y", "pnp_pose_error")}
    for i, (pattern, form, block) in forms.items():
        value = rows[i][1] if i < len(rows) and len(rows[i]) > 1 else ""
        if any(block in k for k in missing):
            ok = "파일에 없음" in value
        else:
            ok = bool(re.search(pattern, value))
        if not ok:
            dist_bad.append(f"{ROWS[i]}: '{value}' (꼴 {form})")
    c.add("출력", "분포 꼴 · 소수 셋째 자리", not dist_bad, "; ".join(dist_bad) or "이상 없음")

    long_cells = [f"{r[0]}: {len(r[1])}자" for r in rows[1:] if len(r) > 1 and len(r[1]) > VALUE_CELL_MAX]
    c.add("출력", f"값 칸에 값만 (조건 줄 밖 ≤ {VALUE_CELL_MAX}자)", not long_cells, "; ".join(long_cells) or "이상 없음")

    keys_bad = []
    for r in rows:
        source = r[2] if len(r) > 2 else ""
        for key in re.findall(r"`([A-Za-z_][\w.]*)`", source):
            if "." in key or key in data:
                if get(data, key) is MISSING and key not in missing:
                    keys_bad.append(key)
    c.add("출력", "출처 키가 JSON에 있음", not keys_bad, ", ".join(keys_bad) or "이상 없음")

    if missing:
        blocks = {"top_centre_error_mm": 3, "pnp_pose_error": 4, "final_unique_pure": 2, "final_mixed": 2,
                  "accepted_": 1, "observation_count": 0}
        unmarked = []
        for key in missing:
            row = next((i for frag, i in blocks.items() if frag in key), None)
            if row is not None and row < len(rows) and "파일에 없음" not in rows[row][1]:
                unmarked.append(f"{ROWS[row]} ({key})")
        c.add("출력", "없는 값은 '파일에 없음'", not unmarked, "; ".join(sorted(set(unmarked))) or "표시함")

    after = text.split("한 줄 요약", 1)
    c.add("출력", "한 줄 요약", len(after) == 2, "있음" if len(after) == 2 else "없음")
    if len(after) == 2:
        line = after[1].strip().splitlines()[0] if after[1].strip() else ""
        extra = [t for t in NUMBER.findall(line.replace(",", "")) if round(float(t), 3) not in allowed]
        c.add("출력", "요약 줄 숫자도 JSON 값", not extra, ", ".join(extra) or "이상 없음")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    c = Checks()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        c.add("입력", "JSON 읽기", True, str(args.input))
    except (OSError, ValueError) as exc:
        c.add("입력", "JSON 읽기", False, f"{args.input}: {exc}")
        data = None
    if data is not None:
        missing = check_input(c, args.input, data)
        if args.summary:
            check_summary(c, data, args.summary.read_text(encoding="utf-8"), missing)

    width = max(len(r["check"]) for r in c.rows)
    print(f"check_result — {args.input}" + (f" · {args.summary}" if args.summary else ""))
    for r in c.rows:
        print(f"  [{r['status']}] {r['group']} {r['check']:{width}s}  {r['detail']}")
    warns = sum(r["status"] == "WARN" for r in c.rows)
    verdict = "FAIL" if c.failed else "PASS"
    print(f"RESULT: {verdict}  (검사 {len(c.rows)} · 실패 {len(c.failed)} · 경고 {warns})")
    if args.json:
        args.json.write_text(json.dumps({"result": verdict, "checks": c.rows}, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    sys.exit(1 if c.failed else 0)


if __name__ == "__main__":
    main()
