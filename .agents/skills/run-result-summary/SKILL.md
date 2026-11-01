---
name: run-result-summary
description: >-
  라벨 블라인드 3차원 영역 실행의 결과 파일(field_chain_summary.json) 하나를 랩미팅용 요약표 5줄
  (조건 · 짝 · 찾은 연결재 · 상면 중심 오차 · 카메라 위치 오차)과 한 줄 요약으로 옮기고, 줄마다 JSON 키를 출처로 단다.
  끝내기 전에 scripts/check_result.py로 표의 숫자를 원본과 대조한다.
  쓸 때: "Run64 결과 요약해 줘", "이 field_chain_summary.json 랩미팅용 표로 정리해 줘".
  쓰지 않을 때: 분석을 새로 돌리거나 사진을 찍을 때, 여러 실행을 비교 · 해석하는 글이나
  원고 · 발표 문장을 쓸 때, 결과 파일을 고칠 때.
---

# 실행 결과 요약표

정보가 없으면 추정하지 말고 묻는다. 어느 결과 파일인지 정해지지 않았으면 묻고, 파일에 없는 값은 "파일에 없음"으로 적는다.
키 뜻 · 결과 폴더 4종 · 함정은 `references/research.md`.

## 워크플로

| 단계 | 할 일 | 꺼내 놓을 중간 결과 | 관문 (통과해야 다음으로) |
|---|---|---|---|
| 1 파일 정하기 | 요청에서 결과 파일 하나를 정한다 | 파일 경로, 폴더 이름으로 정한 자세 · 규칙 | 파일 하나. 후보가 여럿이면 후보 표를 보여 주고 묻는다 |
| 2 입력 검사 | `python .agents/skills/run-result-summary/scripts/check_result.py --input <json>` | `RESULT:` 줄과 FAIL · WARN 줄 | PASS. FAIL이면 표를 만들지 않고 FAIL 줄을 보여 주고 묻는다 |
| 3 계획 | 계획 블록을 보여 주고 "이대로 쓸까요?"라고 묻는다 | 계획 블록 | 사용자가 진행하라고 답함. 답 전에는 파일을 쓰지 않는다 |
| 4 표 쓰기 | 출력 형식대로 쓴다 | `reports/<실행>_<결과 폴더>.md` | — |
| 5 검증 | 같은 스크립트에 `--summary <md>`를 더해 돌린다 | `RESULT:` 줄 | PASS. FAIL이면 표를 고쳐 다시. 두 번 넘게 FAIL이면 멈추고 묻는다 |
| 6 전달 | 결과를 보여 준다 | 표 · 한 줄 요약 · `RESULT:` 줄 · md 경로 | — |

## 계획

표를 쓰기 전에 아래 블록을 보여 주고 확인을 받는다. 답을 받기 전에는 `reports/`에 아무것도 쓰지 않는다. 사용자가 고칠 점을 말하면 블록을 고쳐 다시 묻는다.

```text
입력: <json 경로>  →  조건: <자세> · <규칙> (폴더 이름)
입력 검사: <RESULT 줄>
없는 값: <키 목록 또는 없음>
쓸 파일: reports/<실행>_<결과 폴더>.md   (원본 JSON은 읽기만)
이대로 쓸까요?
```

## 검증

- `scripts/check_result.py` 입력 검사: 필수 값, 개수 ≥ 0 정수, 틀린 간선 ≤ 간선, 찾은 연결재 ≤ 84, 오차 최소 ≤ 중앙 ≤ p95 ≤ 최대, 폴더 이름 ↔ JSON(완전 투영 규칙 · 대조군 자세 0).
- 출력 검사(`--summary`): 표 하나 · 5줄 순서, 표와 요약 줄의 숫자가 모두 JSON 값, 분포 꼴과 소수 셋째 자리, 출처 키가 JSON에 있음, 없는 값은 "파일에 없음", 값 칸에 설명 문장 없음.
- 종료 코드 1 = FAIL. 통과시키려고 원본 JSON을 고치지 않는다.

## 훅·권한

하지 말 것: 결과 JSON 쓰기 · 지우기, 빈 값을 다른 키 · README · 기억으로 메우기, `git push`.
`scripts/guard.py`(PreToolUse 훅)가 결과 JSON · `3_results*/`를 고치는 Edit · Write · Bash와 `git push`를 막는다(종료 코드 2). 메우기는 훅으로 못 막으므로 출력 검사가 잡는다.

```json
{
  "permissions": { "deny": ["Edit(**/3_results*/**)", "Write(**/3_results*/**)", "Bash(git push:*)"] },
  "hooks": { "PreToolUse": [ { "matcher": "Edit|Write|Bash",
    "hooks": [ { "type": "command", "command": "python .agents/skills/run-result-summary/scripts/guard.py" } ] } ] }
}
```

## 서브에이전트

| 조각 | 목표 | 결과 모양 | 도구 | 경계 |
|---|---|---|---|---|
| 후보 찾기 | 파일이 정해지지 않은 요청("Run64 요약해 줘")에서 후보 결과 파일을 빠짐없이 찾는다 | 후보 표(경로 · 폴더 이름 · 자세 · 규칙) | Glob, Read | 고르지 않는다(고르는 건 사용자) |
| 실행별 요약 | 실행 여러 개를 한 번에 요약할 때 실행 하나의 표를 쓰고 검사한다 | md 한 개 + `RESULT:` 줄 | Read, Write(`reports/`만), Bash(check_result) | 자기 파일만, 비교 · 해석 안 함 |

메인 세션은 사용자와 묻고 답하기, 계획 확인, 최종 전달만 한다. 실행 여러 개면 계획 블록을 실행마다 한 줄씩 묶어 한 번에 확인받는다.

## 출력 형식

| 항목 | 값 | 출처 (JSON 키) |
|---|---|---|
| 조건 | 사진 n장 · 자세 · 규칙 · 노드 게이트 | 폴더 이름, `observation_count_by_route`, `frame_complete_band_rule`, `observation_gate.node_gate` |
| 짝 (간선) | 받아들임 N · 틀림 M | `endpoints.accepted_edge_count`, `endpoints.accepted_false_edge_count` |
| 찾은 연결재 | N/84 (섞인 영역 M) | `spatial_reassociation.final_unique_pure_connector_count`, `spatial_reassociation.final_mixed_cluster_count` |
| 상면 중심 오차 (mm) | 최소 – 최대 (중앙 X) | `spatial_reassociation.top_centre_error_mm` |
| 카메라 위치 오차 (mm) | 중앙 X · 최대 Y | `pnp_pose_error.position_median_mm`, `pnp_pose_error.position_max_mm` (최소는 이 파일에 없음) |

한 줄 요약: 표의 결과만 한 문장으로.

## 규칙

- 숫자는 이 JSON에서만 가져온다. README · 다른 실행 · 기억으로 메우지 않는다.
- 실수는 소수 셋째 자리, 개수는 정수. 값 칸에는 값만 — 대조군 · 파일에 없음 같은 설명은 조건 줄이나 출처 칸에.
- 표 하나 5줄만. 단계별 표 · 주의 목록 · 다른 실행과의 비교 · 원인 해석을 붙이지 않는다.
