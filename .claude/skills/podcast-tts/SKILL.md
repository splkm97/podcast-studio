---
name: podcast-tts
description: script.json의 tts 텍스트를 화자별 목소리로 합성해 episode.mp3를 만들고, 오디오 길이·무음 검사와 STT 역검증으로 발음 오류를 잡아 음차 사전에 되먹인다. podcast-orchestrator의 4단계이며, 대본을 음성 파일로 만들거나 TTS 발음 문제를 고칠 때 사용한다.
---

# 음성 합성과 검증

## 엔진

엔진은 `podcast.yaml`의 `tts.engine`으로 고른다. 화자별 목소리는 `tts.voices`에 있고, 그 값은 엔진 요청 필드로 그대로 전달된다. 새 엔진은 `tools/tts/`에 `TTSEngine`을 구현하고 `tools/tts/__init__.py`에 등록하면 된다. 모든 엔진은 같은 WAV 형식을 내야 한다. segment를 샘플 단위로 이어 붙여 그 시각이 자막 타이밍이 되기 때문이다.

## 절차

```
python3 -m tools.synth episodes/<id>          # 합성 + 이어 붙이기 + mp3
python3 -m tools.check_audio episodes/<id>    # audio 게이트
python3 -m tools.verify_stt episodes/<id>     # stt 게이트 (드라이런이면 생략)
```

`tools.synth`는 tts 텍스트와 목소리가 그대로인 segment를 다시 합성하지 않는다. 그래서 고친 segment만 비용이 든다.

## 복구 절차

### audio 게이트 실패

- segment의 초당 글자 수가 이상하면 응답이 잘렸거나 깨진 것이다. `python3 -m tools.synth episodes/<id> --only <segment-id>`로 다시 합성한다. 지정한 ID는 캐시를 우회한다. `--force`는 정상 segment까지 전부 재합성하므로 국소 복구에 사용하지 않는다.
- 긴 무음이 특정 segment 안에 있으면 그 segment의 tts에 엔진이 처리 못 하는 문자가 있는지 보고, 고친 뒤 다시 합성한다
- 총 길이 초과는 대본 문제다. 오케스트레이터에 대본 단계로 되돌릴 것을 알린다

### stt 게이트 실패

`gates/stt.json`의 `expected`와 `heard`를 segment별로 비교해 원인을 가른다.

1. **용어 발음 문제**: 특정 음차 표기가 다르게 들린다 (예: 엣시디 → 이티시디). tts 표기를 바꾼다. 띄어쓰기 조정, 다른 관용 표기, 조각 분리 순으로 시도한다
2. **문장 전체가 무너짐**: 너무 긴 문장, 숫자 나열, 영어 잔여 등. 문장을 나누거나 숫자를 말로 풀어 쓴다. 문장을 나눌 때는 src도 같이 나눠 짝을 맞춘다
3. **인식기 쪽 오류로 보임**: 음차가 정상이고 인식 결과만 엉뚱하다. 그래도 기준을 낮추거나 게이트를 건너뛰지 않는다. 같은 뜻의 다른 문장으로 바꿔 다시 시도하고, 횟수를 다 쓰면 중단하고 report에 해당 segment를 남긴다

segment ID 목록이 그대로이고 해당 segment의 tts만 고쳤다면 고친 ID만 다시 검증한다. 추가·분할·삭제로 ID 목록이 달라졌으면 아래 부분 검증 대신 `python3 -m tools.verify_stt episodes/<id>`로 전체 STT를 다시 실행한다. 현재 모든 segment에 검증 결과가 있어야 게이트를 통과한다.

```
python3 -m tools.synth episodes/<id> --only s012
python3 -m tools.verify_stt episodes/<id> --only s012
python3 -m tools.check_audio episodes/<id>
```

### 사전 되먹임

1번 원인으로 바꾼 표기가 재검증을 통과하면 `.claude/skills/tech-term-hangul/references/glossary-learned.md`에 추가한다. 다음 회차부터 같은 실수를 하지 않게 하기 위해서다.

```
- etcd = 엣씨디  # 20261109-etcd-backup, 이전: 엣시디
```

같은 영어 항목이 이미 있으면 새 줄을 더하지 말고 그 줄을 고친다. 2, 3번 원인은 사전에 넣지 않는다. 용어 표기 문제가 아니기 때문이다.
