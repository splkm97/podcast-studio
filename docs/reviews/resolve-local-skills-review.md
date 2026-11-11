# 로컬 스킬 리뷰 피드백 반영

- 모드: reception
- 분류: 7건 모두 accepted. questionable 항목 및 반박 초안 없음.
- 원격 상태 변경, 커밋, 실제 인증, TTS API, 업로드·발행 실행 없음.
- 기존 episodes/ 산출물과 자격 증명 파일은 변경하지 않음.

## 항목별 처리

| # | 원본 피드백 | 분류 | 조치 | 검증 |
|---|---|---|---|---|
| 1 | 초안 업로드가 실제로는 공개 발행됨 | accepted | `tools/upload_transistor.py`에서 draft 외 설정을 차단하고 자동 publish 분기를 제거. `tools/upload_youtube.py`에서 private 외 설정을 차단. podcast.yaml을 draft로 수정하고 upload 스킬의 필수 조건 명시 | `tests.test_upload_safety` 3개 통과. 잘못된 설정은 인증·네트워크 전 중단, draft 업로드에는 publish 요청 없음 |
| 2 | 승인하지 않은 회차까지 발행될 수 있음 | accepted | `tools/publish_transistor.py`는 --yes 실행에 명시적 회차 경로를 요구. publish 스킬은 승인 목록을 고정하고 모든 경로를 전달 | `tests.test_publish_scope` 2개 통과. 목록 없는 --yes 거부, 확인 후 추가된 초안 제외 |
| 3 | 문장 분할 후 새 segment가 STT 검사에서 빠짐 | accepted | `tools/verify_stt.py`가 현재 segment의 누락 결과를 실패로 처리. tts 스킬은 ID 목록 변경 시 전체 검증을 요구 | `tests.test_stt_coverage` 3개 통과. 새 segment 누락 실패, 전체 재검증 성공, 다른 segment의 기존 실패 보존 |
| 4 | 단일 segment 복구가 회차 전체를 재합성함 | accepted | tts 스킬의 국소 복구 명령에서 --force 제거. --only가 선택 ID 캐시를 우회함을 명시 | 임시 WAV 스모크 통과. 실제 synth.main에 --only s012를 전달하여 대상 WAV 교체와 정상 WAV 바이트 보존 확인. 합성 엔진·ffmpeg는 대체 |
| 5 | 긴 문장의 뒷부분이 자막에서 사라짐 | accepted | `tools/render_video.py`는 줄바꿈 결과 전체를 세 줄씩 추가 cue로 분할하고 글자 수 비례 시간을 배분. video 스킬 갱신 | `tests.test_subtitles` 3개 통과. 96/97/300자 경계, 여러 문장·기술 표기 보존, 시간 연속성·최종 시각 검증 |
| 6 | 만료된 토큰을 복구하지 않고 설정 완료로 종료함 | accepted | setup 스킬이 존재 검사와 인증 복구를 구분. 토큰 만료·갱신 실패 진입 시 check_env=0이어도 --auth 성공 필요 | 콜드 모델 기반 문서 시나리오 3개 통과. 만료→재인증, 정상 초기 점검→종료, 재인증 취소→미해결 |
| 7 | 같은 탐색의 다른 후보 선택이 기존 회차 조사를 막음 | accepted | discover/orchestrator/research가 회차 brief.md의 선택 스냅샷을 고정된 조사 근거로 사용. 현재 탐색 상태는 과거 선택을 무효화하지 않음. 스냅샷 없는 과거 승인은 추정하지 않음 | 콜드 모델 기반 문서 시나리오 5개 통과. 선택 변경·탐색 파일 부재에도 C1 유지, 기록 누락 차단, 새 후보 미선택 대기, 발굴 없는 직접 조사 허용 |

## 실행한 검증

아래 명령을 각 해당 항목 수정 후 실행했다. 총 11개 unittest가 통과했다.

```text
.venv/bin/python -m unittest tests.test_upload_safety -v
.venv/bin/python -m unittest tests.test_publish_scope -v
.venv/bin/python -m unittest tests.test_stt_coverage -v
.venv/bin/python -m unittest tests.test_subtitles -v
```

추가로 국소 합성 스모크 1건과 문서 기반 시나리오 8건이 통과했다. 스모크의 임시 회차는 종료 시 제거했다. 영구 회귀 테스트는 표준 unittest를 사용하며 tests 패키지 초기화에서 로컬 .env 로드를 막는다.

## 검증 한계

- 문서 시나리오는 스킬을 읽은 모델의 행동 판정 검증이다. 실제 파일 인계·브라우저 OAuth·회차 제작을 수행한 것은 아니다.
- 자막 검증은 생성된 SRT의 내용과 타이밍을 대상으로 했다. 실제 영상 렌더링·시청 검증은 수행하지 않았다.
- 업로드·발행 테스트는 외부 API 경계를 대체한다. 실제 플랫폼 동작은 실행하지 않았다.
- README에 변경된 안전 조건, 선택 스냅샷, 복구 규칙과 회귀 테스트 실행 방법을 반영했다.
