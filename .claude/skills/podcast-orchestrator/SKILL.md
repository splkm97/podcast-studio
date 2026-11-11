---
name: podcast-orchestrator
description: 기술 팟캐스트 제작 요청을 주제 발굴부터 자료 수집, 대본, TTS, 영상, YouTube 비공개 업로드와 Transistor.fm 초안 업로드까지 연결한다. "팟캐스트 만들어줘", "이 주제로 에피소드", "회차 제작" 요청이면 이 스킬로 시작한다. 주제가 없거나 후보 추천을 요청하면 podcast-discover로 발굴하고 사용자 선택에서 멈춘다. 주제와 제작 의사가 확정된 뒤에는 podcast-research, podcast-script, tech-term-hangul, podcast-tts, podcast-video, podcast-upload를 순서대로 실행한다. 글감 추천만 요청하면 podcast-discover가 맡는다.
---

# 팟캐스트 오케스트레이터

## 원칙

- **주제 확정 뒤 제작은 무인 실행이다.** 주제 후보 선택과 대화형 setup은 예외다. 제작 중 판단은 아래 규칙으로 정하고 이유를 로그에 남긴다.
- **사람 검토 대신 게이트가 막는다.** 게이트를 통과하지 못한 산출물은 다음 단계로 넘기지 않는다.
- **최종 안전망은 비공개 업로드다.** YouTube는 비공개, Transistor는 초안으로 올린다. 공개 전환과 발행은 사용자가 직접 한다. 이 스킬은 공개 상태를 바꾸지 않는다. Spotify는 Transistor에서 발행된 회차를 RSS로 가져가므로 사람이 발행하기 전에는 Spotify에도 나가지 않는다.
- **AI 생성 콘텐츠로 표시해 올린다.** 음성이 TTS 합성이므로 업로드 시 YouTube의 변경·합성 콘텐츠 항목을 켠다 (`podcast.yaml`의 `youtube.contains_synthetic_media`, 기본 true).
- **멈출 때는 정직하게 멈춘다.** 게이트를 우회하거나 기준을 낮춰 통과시키지 않는다.

## 입력

사용자 메시지에서 **제작 의사**, **주제 또는 관심 분야**, **참고 링크·문서**(없을 수 있음), **회차 제목 힌트**, **기존 회차·탐색 경로 또는 후보 선택**을 꺼낸다.

## 0. 주제 발굴과 선택 (research 이전)

환경 점검·setup·회차 폴더 생성보다 먼저 아래 순서로 라우팅한다. 후보 추천만으로 제작을 승인한 것으로 보지 않는다.

| 요청 상태 | 처리 |
|---|---|
| 기존 회차 제작 재개 | 해당 brief.md의 확정 주제·선택 스냅샷과 state.json을 기준으로 사전 점검 후 마지막 통과 단계 다음부터 재개한다. 탐색 파일의 현재 선택으로 기존 회차를 재승인하거나 주제를 바꾸지 않는다 |
| 기존 탐색의 후보 선택·재개 | discovery.md와 사용자 선택을 읽고 아래 선택 게이트를 적용한다. 후보 목록을 다시 만들지 않는다 |
| 주제가 없거나, 주제·링크가 있어도 후보·대안 추천을 명시 | podcast-discover를 실행한다. 분야·키워드·사용자 링크와 원래 제작 요청 여부를 전달하고, 결과를 보여 준 뒤 선택에서 멈춘다 |
| 주제가 확정된 제작 요청, 추천 요청 없음 | discover를 건너뛰고 사전 점검 후 1단계로 간다. 참고 링크가 없어도 가능하다 |
| 제작 없이 글감·키워드·블로그 추천만 요청 | podcast-discover 결과만 반환하고 종료한다 |

**선택 게이트:**

- `discoveries/<id>/discovery.md`의 후보 ID와 사용자의 명시적 선택이 일치해야 한다. 후보 ID만 주어져 어느 탐색인지 알 수 없으면 경로를 확인한다. 선택이 모호하거나 없으면 status를 `awaiting_selection`으로 유지한다. 무인 실행(`claude -p`)도 후보를 임의로 고르지 않고 파일 경로와 선택 필요를 알린 뒤 종료한다.
- 새 회차로 선택을 인계하기 전에는 discovery.md에 사용자 표현·선택 시각·확정 질문·범위·출처·주의점을 남기고 status를 `selected`, selected_candidate를 해당 ID로 갱신한다. 회차 생성 전 저장된 선택으로 재개할 때도 선택 기록과 후보의 일치를 확인한다. blocked 상태는 새 회차로 넘기지 않는다.
- **제작 의사도 필요하다.** 원래 요청이 제작이었다면 저장된 production_requested가 true이므로 선택 후 사전 점검으로 진행한다. 추천만 요청했던 경우 후보 선택만으로 제작하지 않는다. 사용자가 별도로 제작을 요청했을 때만 production_requested를 true로 갱신하고 진행한다.
- 사전 점검 통과 후 회차의 brief.md에 **선택 스냅샷**을 남긴다: 탐색 파일 경로, 선택 ID, 확정 질문·포함/제외 범위, 선택한 사용자 표현·선택 시각, 제작 의사, 관련 출처와 원래 제공자(사용자/검색), 미확인 사항. 확정 당시의 내용을 복사하며 현재 탐색 파일을 가리키는 포인터만 남기지 않는다. 이 기록은 해당 회차의 선택 근거로 고정한다. 이후 탐색에서 다른 후보를 선택해도 기존 brief.md는 바꾸지 않는다. research는 이 스냅샷을 입력으로 상세 검증하며 추천 판정을 사실 검증으로 간주하지 않는다.

선택 전에는 회차 폴더·state.json·report.md를 만들지 않는다. 탐색 상태와 결과는 discovery.md에만 두고, 후보와 다음 선택을 채팅에 보고한다. 선택 대기는 실패 게이트나 재시도 대상이 아니다.

`podcast.yaml`의 `tts.engine`이 `dryrun`이면 **드라이런**이다. API 비용 없이 흐름만 검증하는 모드라서 `stt` 게이트와 업로드를 건너뛰고, report.md 첫 줄에 드라이런임을 밝힌다.

## 사전 점검 (setup 라우트)

주제와 제작 의사가 확정된 뒤, 회차 폴더를 만들거나 기존 회차 제작을 재개하기 전에 시크릿과 토큰을 확인한다. 주제 발굴·추천만 할 때는 실행하지 않는다.

```
python3 -m tools.check_env
```

- 종료 코드 0이면 새 회차는 1단계로, 기존 회차는 마지막 통과 단계 다음으로 간다. 드라이런은 항상 통과한다
- 1이면 `.env`가 없거나 값이 빠졌거나(TTS·Transistor 키) YouTube 토큰이 없는 것이다
  - **대화형 세션**: podcast-setup 스킬을 실행한다. 사람이 키를 발급받고 브라우저로 인증해야 하므로 무인 원칙의 예외다. setup이 끝나 `check_env`가 0을 내면 선택된 주제를 유지하고 새 회차는 1단계부터, 기존 회차는 마지막 통과 단계 다음부터 진행한다
  - **무인 실행**(`claude -p`): setup을 할 수 없다. 환경 오류로 바로 중단하고, report.md에 `check_env` 출력과 "대화형 세션에서 /podcast-setup 실행"을 사람이 할 일로 남긴다. 회차 폴더가 아직 없으면 채팅으로만 알린다
- 그 밖의 종료 코드는 도구 환경 오류다. 재시도하지 않고 중단한다

## 회차 폴더

`episodes/<YYYYMMDD>-<slug>/` 를 만든다. slug는 주제의 영문 소문자 하이픈 표기.

```
brief.md           확정 주제·범위, 사용자 자료, 받은 시각; 발굴 경유 시 회차별 선택 스냅샷
sources.json       자료 목록 (podcast-research)
research.md        출처 id가 달린 핵심 사실 노트
script.json        대본 (src 원문 + tts 음차)
gates/*.json       게이트 결과
audio/             segment wav, timings.json, episode.wav
episode.mp3 / subtitles.srt / episode.mp4
upload.json        YouTube 업로드 결과
transistor.json    Transistor 업로드 결과
state.json         진행 상태
logs/run.log       실행 로그
report.md          최종 보고
```

## 단계와 게이트

| 단계 | 스킬 | 게이트 (실행 주체) |
|---|---|---|
| 0. 주제 발굴 (조건부) | podcast-discover | discovery.md의 명시적 후보 선택 + 제작 의사. 선택 전에는 종료하며, 확정 주제의 제작 요청은 건너뜀 |
| 1. 자료 수집 | podcast-research | `links` (`python3 -m tools.check_links`) |
| 2. 대본 초안 | podcast-script | `factcheck` (스킬이 직접 작성) |
| 3. TTS 정규화 | tech-term-hangul | `script_lint` (`python3 -m tools.lint_script`) |
| 4. 음성 합성 | podcast-tts | `audio` (`tools.check_audio`), `stt` (`tools.verify_stt`) |
| 5. 영상 | podcast-video | 렌더 성공 여부 |
| 6. 업로드 | podcast-upload | `upload.json`(YouTube), `transistor.json`(Transistor, `transistor.enabled`일 때) 생성 여부. 두 곳은 독립이라 한쪽이 실패해도 다른 쪽을 올린다 |

모든 명령은 저장소 루트에서 실행한다. 게이트 스크립트는 통과 시 종료 코드 0, 실패 시 1, 환경 오류 시 그 밖의 코드를 낸다.

## 재시도 규칙

`podcast.yaml`의 `retry.max_attempts`(기본 3)가 게이트별 최대 시도 횟수다.

- 게이트가 실패하면 `gates/<gate>.json`의 `problems`를 읽고, **실패한 부분만** 고친 뒤 그 게이트를 다시 돌린다. 앞 단계 전체를 다시 하지 않는다
  - `links` 실패: 죽은 출처를 대체 출처로 바꾸거나 빼고, 그 출처에만 기대던 사실을 research.md에서 정리한다
  - `factcheck` 실패: 근거 없는 주장을 고치거나 삭제한다
  - `script_lint` 실패: 지적된 segment의 tts만 고친다
  - `audio`/`stt` 실패: podcast-tts 스킬의 복구 절차를 따른다
- 앞 단계 산출물을 고쳤다면 그 뒤 게이트는 모두 다시 돌린다 (예: 대본을 고치면 lint부터)
- 환경 오류(인증 없음, 도구 미설치, 네트워크 장애)는 재시도하지 않고 바로 중단한다. 고칠 수 없는 원인이기 때문이다
- 횟수를 다 쓰면 **중단**한다. 업로드는 절대 하지 않는다

## state.json

주제가 확정되어 제작을 시작한 뒤 단계마다 갱신한다. 중단 후 같은 회차로 다시 부르면 이 파일을 읽고 마지막 통과 단계 다음부터 이어 간다. 선택 전 상태는 discovery.md에 있으므로 이 파일에 discover 단계를 추가하지 않는다.

```json
{"episode": "<id>", "stage": "tts", "status": "running|done|stopped",
 "attempts": {"links": 1, "factcheck": 2}, "stopped_reason": null}
```

## report.md

회차 제작이 끝나거나 멈추면 반드시 쓴다. 제작 결과의 최종 보고다. 주제 발굴만 했거나 선택 대기 중이면 discovery.md와 채팅으로 보고한다.

- 결과 한 줄: 업로드 완료(YouTube 비공개 URL, Transistor 초안 URL) 또는 중단(단계, 이유)
- Transistor에 올렸다면 사람이 할 일: 대시보드에서 초안을 확인하고 공개 발행하면 Spotify에 반영된다. 쇼가 아직 Spotify에 등록되지 않았다면 podcast-setup의 Spotify 등록 단계를 안내한다
- 게이트 요약: 게이트별 통과 여부와 시도 횟수
- 자동으로 바뀐 것: 대체된 출처, 삭제된 주장, 학습 사전에 추가된 표기
- 중단이면 사람이 할 일: 무엇을 고치면 이어서 돌릴 수 있는지
- 공개 전 확인 포인트: 확신이 낮았던 tts_notes, CER이 기준에 가까웠던 segment

마지막에 채팅에도 report.md 경로와 결과 한 줄을 알린다.
