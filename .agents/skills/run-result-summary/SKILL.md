---
name: run-result-summary
description: >-
  라벨 블라인드 3차원 영역 실행의 결과 파일(field_chain_summary.json) 하나를 랩미팅용 요약표 5줄
  (조건 · 짝 · 찾은 연결재 · 상면 중심 오차 · 카메라 위치 오차)과 한 줄 요약으로 옮기고, 줄마다 JSON 키를 출처로 단다.
  쓸 때: "Run64 결과 요약해 줘", "이 field_chain_summary.json 랩미팅용 표로 정리해 줘".
  쓰지 않을 때: 분석을 새로 돌리거나 사진을 찍을 때, 여러 실행을 비교 · 해석하는 글이나
  원고 · 발표 문장을 쓸 때, 결과 파일을 고칠 때.
---

# 실행 결과 요약표

정보가 없으면 추정하지 말고 묻는다. 어느 결과 파일인지 정해지지 않았으면 묻고, 파일에 없는 값은 "파일에 없음"으로 적는다.

## 순서

1. 사용자가 준 `field_chain_summary.json` 하나만 읽는다. 키 뜻과 결과 폴더 4종은 `references/research.md`.
2. 조건을 정한다.
   - 자세: 폴더 이름에 `truthpose_control`이 있으면 촬영 자세(대조군), 없으면 마커 PnP.
   - 규칙: `frame_complete_band_rule`이 null이면 상호 유일만, 아니면 + 화면 안 완전 투영.
   - 노드 게이트: `observation_gate.node_gate`. 사진 수: `observation_count_by_route` 항목 수.
3. 아래 표를 채우고 한 줄 요약을 붙인다.

## 출력 형식

| 항목 | 값 | 출처 (JSON 키) |
|---|---|---|
| 조건 | 사진 n장 · 자세 · 규칙 · 노드 게이트 | 폴더 이름, `observation_count_by_route`, `frame_complete_band_rule`, `observation_gate.node_gate` |
| 짝 (간선) | 받아들임 N · 틀림 M | `endpoints.accepted_edge_count`, `endpoints.accepted_false_edge_count` |
| 찾은 연결재 | N/84 (섞인 영역 M) | `spatial_reassociation.final_unique_pure_connector_count`, `spatial_reassociation.final_mixed_cluster_count` |
| 상면 중심 오차 (mm) | 최소 – 최대 (중앙 X) | `spatial_reassociation.top_centre_error_mm` |
| 카메라 위치 오차 (mm) | 최소 – 최대 (중앙 X) | `pnp_pose_error.position_median_mm`, `pnp_pose_error.position_max_mm` |

한 줄 요약: 표의 결과만 한 문장으로.

## 규칙

- 숫자는 이 JSON에서만 가져온다. README · 다른 실행 · 기억으로 메우지 않는다.
- 실수는 소수 셋째 자리, 개수는 정수.
- 표 하나 5줄만. 단계별 표 · 주의 목록 · 다른 실행과의 비교 · 원인 해석을 붙이지 않는다.
