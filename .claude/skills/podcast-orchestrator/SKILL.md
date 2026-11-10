---
name: podcast-orchestrator
description: 기술 팟캐스트 한 회차를 주제와 참고 자료만 받아 자료 수집부터 대본, TTS, 영상, YouTube 비공개 업로드와 Transistor.fm 초안 업로드(Spotify 배포용)까지 사람 개입 없이 끝까지 진행한다. "팟캐스트 만들어줘", "이 주제로 에피소드", "회차 제작", 주제와 링크를 주며 오디오나 영상 콘텐츠를 만들어 달라는 요청이면 반드시 이 스킬로 시작한다. 단계 스킬(podcast-research, podcast-script, tech-term-hangul, podcast-tts, podcast-video, podcast-upload)을 순서대로 부르고 품질 게이트로 진행 여부를 정한다.
---

# 팟캐스트 오케스트레이터

## 원칙

- **무인 실행이다.** 중간에 사용자에게 묻지 않는다. 판단이 필요하면 아래 규칙으로 정하고 이유를 로그에 남긴다.
- **사람 검토 대신 게이트가 막는다.** 게이트를 통과하지 못한 산출물은 다음 단계로 넘기지 않는다.
- **최종 안전망은 비공개 업로드다.** YouTube는 비공개, Transistor는 초안으로 올린다. 공개 전환과 발행은 사용자가 직접 한다. 이 스킬은 공개 상태를 바꾸지 않는다. Spotify는 Transistor에서 발행된 회차를 RSS로 가져가므로 사람이 발행하기 전에는 Spotify에도 나가지 않는다.
- **AI 생성 콘텐츠로 표시해 올린다.** 음성이 TTS 합성이므로 업로드 시 YouTube의 변경·합성 콘텐츠 항목을 켠다 (`podcast.yaml`의 `youtube.contains_synthetic_media`, 기본 true).
- **멈출 때는 정직하게 멈춘다.** 게이트를 우회하거나 기준을 낮춰 통과시키지 않는다.

## 입력

사용자 메시지에서 **주제**, **참고 링크·문서**(없을 수 있음), 원하면 **회차 제목 힌트**를 꺼낸다. 주제가 없으면 시작하지 않고 그 사실만 알린다. 이것이 유일하게 멈춰서 묻는 경우다.

`podcast.yaml`의 `tts.engine`이 `dryrun`이면 **드라이런**이다. API 비용 없이 흐름만 검증하는 모드라서 `stt` 게이트와 업로드를 건너뛰고, report.md 첫 줄에 드라이런임을 밝힌다.

## 사전 점검 (setup 라우트)

회차 폴더를 만들기 전에 시크릿과 토큰을 확인한다.

```
python3 -m tools.check_env
```

- 종료 코드 0이면 1단계로 간다. 드라이런은 항상 통과한다
- 1이면 `.env`가 없거나 값이 빠졌거나(TTS·Transistor 키) YouTube 토큰이 없는 것이다
  - **대화형 세션**: podcast-setup 스킬을 실행한다. 사람이 키를 발급받고 브라우저로 인증해야 하므로 무인 원칙의 예외다. setup이 끝나 `check_env`가 0을 내면 원래 요청으로 돌아와 1단계부터 진행한다
  - **무인 실행**(`claude -p`): setup을 할 수 없다. 환경 오류로 바로 중단하고, report.md에 `check_env` 출력과 "대화형 세션에서 /podcast-setup 실행"을 사람이 할 일로 남긴다. 회차 폴더가 아직 없으면 채팅으로만 알린다
- 그 밖의 종료 코드는 도구 환경 오류다. 재시도하지 않고 중단한다

## 회차 폴더

`episodes/<YYYYMMDD>-<slug>/` 를 만든다. slug는 주제의 영문 소문자 하이픈 표기.

```
brief.md           주제, 사용자가 준 링크·문서, 받은 시각
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

단계마다 갱신한다. 중단 후 같은 회차로 다시 부르면 이 파일을 읽고 마지막 통과 단계 다음부터 이어 간다.

```json
{"episode": "<id>", "stage": "tts", "status": "running|done|stopped",
 "attempts": {"links": 1, "factcheck": 2}, "stopped_reason": null}
```

## report.md

끝나거나 멈추면 반드시 쓴다. 사용자가 보는 유일한 보고다.

- 결과 한 줄: 업로드 완료(YouTube 비공개 URL, Transistor 초안 URL) 또는 중단(단계, 이유)
- Transistor에 올렸다면 사람이 할 일: 대시보드에서 초안을 확인하고 공개 발행하면 Spotify에 반영된다. 쇼가 아직 Spotify에 등록되지 않았다면 podcast-setup의 Spotify 등록 단계를 안내한다
- 게이트 요약: 게이트별 통과 여부와 시도 횟수
- 자동으로 바뀐 것: 대체된 출처, 삭제된 주장, 학습 사전에 추가된 표기
- 중단이면 사람이 할 일: 무엇을 고치면 이어서 돌릴 수 있는지
- 공개 전 확인 포인트: 확신이 낮았던 tts_notes, CER이 기준에 가까웠던 segment

마지막에 채팅에도 report.md 경로와 결과 한 줄을 알린다.
