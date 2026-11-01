# run-result-summary — 배경 · 용어 · 기준

저장소 README.md에서 옮겼다. SKILL.md 본문에 다 넣지 않고 필요할 때 읽는다.

## 1. 배경

- 강거더 위 전단연결재 84개는 모양이 같고 거의 한 평면에 있다. 사진 여러 장에서 번호 없이 헤드를 짝짓고, 짝지은 헤드의 시선 원뿔이 모두 겹치는 곳(3차원 지지영역)으로 위치를 찾는다.
- **실행 하나** = 사진 묶음 하나를 분석한 것. 분석이 끝나면 결과 폴더가 4개 생기고, 폴더마다 `field_chain_summary.json`이 하나 있다.

| 결과 폴더 | 카메라 자세 | 짝 맞추기 규칙 |
|---|---|---|
| `3_results` | 마커 PnP (실제 절차) | 상호 유일 |
| `3_results_framecomplete_diagnostic` | 마커 PnP | 상호 유일 + 화면 안 완전 투영 |
| `3_results_truthpose_control` | 촬영 자세 (대조군) | 상호 유일 |
| `3_results_truthpose_control_framecomplete_diagnostic` | 촬영 자세 (대조군) | 상호 유일 + 화면 안 완전 투영 |

- 어느 폴더가 "주 결과"인지는 실행 전에 정해 둔다(근접 10장 계획은 화면 안 완전 투영이 주). 요약을 부탁받으면 이 표로 조건을 적는다.
- 이 요약은 실행이 끝날 때마다, 그리고 매주 랩미팅 전에 한다(10월에만 Run61 · 62 · 63 · 64 네 번).

## 2. 용어

| 용어 | 뜻 | JSON 키 |
|---|---|---|
| 사진 수 | 분석에 쓴 사진 장수 | `observation_count_by_route`의 항목 수 |
| 간선 | 두 사진 사이에서 짝으로 받아들인 헤드 쌍 | `endpoints.accepted_edge_count` |
| 틀린 간선 | 채점해 보니 다른 연결재끼리 짝지은 간선 | `endpoints.accepted_false_edge_count` |
| 찾은 연결재 | 정답이 하나만 든 최종 영역이 있는 연결재 수 (84개 중) | `spatial_reassociation.final_unique_pure_connector_count` |
| 섞인 영역 | 정답이 둘 이상 든 최종 영역 수 | `spatial_reassociation.final_mixed_cluster_count` |
| 상면 중심 오차 | 최종 영역에서 구한 헤드 상면 중심과 정답의 거리 (mm) | `spatial_reassociation.top_centre_error_mm` (min · median · p95 · max) |
| 카메라 위치 오차 | 마커 PnP로 구한 카메라 위치와 실제 촬영 위치의 거리 (mm) | `pnp_pose_error.position_median_mm` · `position_max_mm` (최소는 이 파일에 없다) |
| 화면 안 완전 투영 | 상대 사진이 그 헤드가 있을 수 있는 범위를 전부 담을 때만 짝 인정 | `frame_complete_band_rule` (null이면 적용 안 함) |
| 노드 게이트 | 마스크 면적이 문턱보다 작으면 짝 후보에서 뺌 | `observation_gate.node_gate` |

## 3. 기준 (연구실 보고 규약)

- 분포는 `최소 – 최대 (중앙 X)` 꼴, 필요하면 p95를 괄호에 더한다. 소수 셋째 자리, 단위 mm.
- 숫자는 결과 파일에서만 가져오고, 어느 키에서 왔는지 같이 적는다. 기억 · README · 다른 실행에서 가져와 메우지 않는다.
- 대조군 폴더(`truthpose_control`)의 카메라 위치 오차 0은 정답 자세를 넣었기 때문이다. PnP 성능으로 읽지 않는다.
- 요약은 결과를 옮기는 일이다. 원인 해석 · 다음 실험 제안은 하지 않는다(부탁받으면 따로).
