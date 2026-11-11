---
name: podcast-tts
description: script.json의 tts 텍스트를 화자별 목소리로 합성해 episode.mp3를 만들고, 오디오 길이·무음 검사로 결과를 확인한다. 사람이 들어서 찾은 발음 오류는 음차 사전에 되먹인다. podcast-orchestrator의 4단계이며, 대본을 음성 파일로 만들거나 TTS 발음 문제를 고칠 때 사용한다.
---

# 음성 합성과 검증

## 엔진

엔진은 `podcast.yaml`의 `tts.engine`으로 고른다. 화자별 목소리는 `tts.voices`에 있고, 그 값은 엔진 요청 필드로 그대로 전달된다. 새 엔진은 `tools/tts/`에 `TTSEngine`을 구현하고 `tools/tts/__init__.py`에 등록하면 된다. 모든 엔진은 같은 WAV 형식을 내야 한다. segment를 샘플 단위로 이어 붙여 그 시각이 자막 타이밍이 되기 때문이다.

## 절차

```
python3 -m tools.synth episodes/<id>          # 합성 + 이어 붙이기 + mp3
python3 -m tools.check_audio episodes/<id>    # audio 게이트
```

`tools.synth`는 tts 텍스트와 목소리가 그대로인 segment를 다시 합성하지 않는다. 그래서 고친 segment만 비용이 든다.

## 복구 절차

### audio 게이트 실패

- segment의 초당 글자 수가 이상하면 응답이 잘렸거나 깨진 것이다. `python3 -m tools.synth episodes/<id> --only <segment-id>`로 다시 합성한다. 지정한 ID는 캐시를 우회한다. `--force`는 정상 segment까지 전부 재합성하므로 국소 복구에 사용하지 않는다.
- 긴 무음이 특정 segment 안에 있으면 그 segment의 tts에 엔진이 처리 못 하는 문자가 있는지 보고, 고친 뒤 다시 합성한다
- 총 길이 초과는 대본 문제다. 오케스트레이터에 대본 단계로 되돌릴 것을 알린다

### 발음 오류 (사람이 들어서 찾은 경우)

발음은 자동으로 검증하지 않는다. 확신이 낮은 표기는 `tts_notes`에 남고, report.md의 공개 전 확인 포인트로 넘어간다. 사람이 들어 보고 잘못 들리는 segment를 알려 주면 그 tts 표기를 고친다. 띄어쓰기 조정, 다른 관용 표기, 조각 분리 순으로 시도한다. 문장 전체가 어색하면 문장을 나누거나 숫자를 말로 풀어 쓴다. 문장을 나눌 때는 src도 같이 나눠 짝을 맞춘다.

```
python3 -m tools.synth episodes/<id> --only s012
python3 -m tools.check_audio episodes/<id>
```

### 사전 되먹임

용어 표기를 바꿔서 고쳐졌으면 `.claude/skills/tech-term-hangul/references/glossary-learned.md`에 추가한다. 다음 회차부터 같은 실수를 하지 않게 하기 위해서다.

```
- etcd = 엣씨디  # 20261109-etcd-backup, 이전: 엣시디
```

같은 영어 항목이 이미 있으면 새 줄을 더하지 말고 그 줄을 고친다. 문장을 나누거나 바꿔 쓴 경우는 사전에 넣지 않는다. 용어 표기 문제가 아니기 때문이다.
