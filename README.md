# run-result-summary — 랩미팅 요약표 스킬

**3차원 영역 분석 실행이 남기는 결과 파일 `field_chain_summary.json` 하나를 랩미팅용 요약표 5줄 + 한 줄 요약으로 옮기는 Claude Code 스킬.**
줄마다 숫자를 가져온 JSON 키를 적고, 끝내기 전에 표의 숫자를 원본과 대조한다.

> 부경대학교 토목공학과 허성재 · 최적화와기계학습 5 · 6주차 과제

## 1. 왜 만들었나

- 연구 분석은 실행 하나가 끝날 때마다 결과 폴더 4개에 `field_chain_summary.json`을 하나씩 남긴다(10월에만 네 번).
- 실행마다, 그리고 매주 랩미팅 전에 같은 숫자를 표로 옮긴다. 손으로 하면 비슷한 다른 키의 값을 쓰거나, README 숫자를 섞거나, 해석을 덧붙이는 실수가 났다.

## 2. 쓰는 법

요청 예: `examples/run64/3_results_framecomplete_diagnostic/field_chain_summary.json 랩미팅용 표로 정리해 줘`

순서: 파일 정하기 → 입력 검사 → **계획 확인**(답 전에는 파일을 쓰지 않음) → 표 쓰기 → **검증** → 전달

검사만 직접 돌릴 때:

```bash
python .agents/skills/run-result-summary/scripts/check_result.py --input examples/run64/3_results_framecomplete_diagnostic/field_chain_summary.json
python .agents/skills/run-result-summary/scripts/check_result.py --input <json> --summary reports/<표>.md
```

## 3. 출력 예 (Run64, 검사 PASS 18)

| 항목 | 값 | 출처 (JSON 키) |
|---|---|---|
| 조건 | 사진 10장 · 마커 PnP · 상호 유일 + 화면 안 완전 투영 · 노드 게이트 없음 (8 px 이상 전부 노드) | 폴더 이름, `observation_count_by_route`, `frame_complete_band_rule`, `observation_gate.node_gate`, `observation_gate.area_px` |
| 짝 (간선) | 받아들임 346 · 틀림 0 | `endpoints.accepted_edge_count`, `endpoints.accepted_false_edge_count` |
| 찾은 연결재 | 84/84 (섞인 영역 0) | `spatial_reassociation.final_unique_pure_connector_count`, `spatial_reassociation.final_mixed_cluster_count` |
| 상면 중심 오차 (mm) | 1.559 – 29.512 (중앙 7.770) | `spatial_reassociation.top_centre_error_mm` |
| 카메라 위치 오차 (mm) | 중앙 18.966 · 최대 33.351 | `pnp_pose_error.position_median_mm`, `pnp_pose_error.position_max_mm` (최소는 이 파일에 없음) |

## 4. 이 저장소

| 경로 | 내용 |
|---|---|
| `.agents/skills/run-result-summary/SKILL.md` | 스킬 본문: 워크플로 · 계획 · 검증 · 훅·권한 · 서브에이전트 · 출력 형식 |
| `.agents/skills/run-result-summary/references/research.md` | 연구 배경, 키 뜻, 결과 폴더 4종, 함정 |
| `.agents/skills/run-result-summary/scripts/check_result.py` | 입력 검사 10개 · 출력 검사 8개 (FAIL이면 종료 코드 1) |
| `.agents/skills/run-result-summary/scripts/guard.py` | PreToolUse 훅: 결과 파일 고치기 · `git push`를 막음 (종료 코드 2) |
| `examples/run64/<결과 폴더>/field_chain_summary.json` | 시험 입력: 시뮬레이션 실행 Run64의 결과 파일 4개 |

## 5. 한계

- `check_result.py`는 표의 숫자가 JSON에 **있는지**만 본다. p95를 최대 자리에 쓰는 식의 자리 바꿈은 잡지 못한다.
- 예시 숫자는 BIM 모델을 렌더링한 시뮬레이션 사진의 결과다. 현장 정확도가 아니다.
